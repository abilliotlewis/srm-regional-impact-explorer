#!/usr/bin/env python3
"""Build one ZIP of the 193 RTMA analyses, with LPIA98_KWBR names."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

BASE = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/rtma/prod'
START = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
TIMES = [START + timedelta(minutes=15*i) for i in range(193)]

def validate(path, expected):
    size = path.stat().st_size
    count = 0
    with path.open('rb') as f:
        while f.tell() < size:
            pos = f.tell()
            header = f.read(16)
            if len(header) != 16 or header[:4] != b'GRIB' or header[7] != 2:
                raise ValueError(f'Invalid GRIB2 header in {path.name} at {pos}')
            length = int.from_bytes(header[8:16], 'big')
            if length < 41 or pos+length > size:
                raise ValueError(f'Truncated GRIB2 in {path.name}')
            section = f.read(21)
            if section[4] != 1:
                raise ValueError('Missing GRIB2 identification section')
            actual = datetime(int.from_bytes(section[12:14], 'big'),
                              *section[14:19], tzinfo=timezone.utc)
            if actual != expected:
                raise ValueError(f'Timestamp mismatch: {path.name}: {actual}')
            f.seek(pos+length-4)
            if f.read(4) != b'7777':
                raise ValueError(f'Invalid GRIB2 ending in {path.name}')
            count += 1
    if not count:
        raise ValueError('Empty GRIB2 file')
    return size, count

def download(t, staging):
    name = 'LPIA98_KWBR_' + t.strftime('%Y%m%d%H%M')
    path = staging / name
    url = f'{BASE}/rtma2p5_ru.{t:%Y%m%d}/rtma2p5_ru.t{t:%H%M}z.2dvaranl_ndfd.grb2'
    subprocess.run(['curl','--fail','--location','--silent','--show-error',
        '--retry','5','--retry-delay','5','--connect-timeout','30',
        '--max-time','1200','--continue-at','-','--output',str(path),url],check=True)
    size, count = validate(path, t)
    return path, size, count

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path,
        default=Path('RTMA_15min_20261009_12Z_to_20261011_12Z.zip'))
    parser.add_argument('--limit', type=int, default=193)
    args = parser.parse_args()
    if not 1 <= args.limit <= 193:
        parser.error('--limit must be between 1 and 193')
    times = TIMES[:args.limit]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='rtma-') as tmp:
        staging = Path(tmp)
        with ThreadPoolExecutor(max_workers=4) as pool, zipfile.ZipFile(
                args.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1,
                allowZip64=True) as archive:
            pending = [pool.submit(download,t,staging) for t in times[:4]]
            for i,t in enumerate(times):
                path,size,count = pending.pop(0).result()
                archive.write(path,arcname=path.name)
                path.unlink()
                print(f'{i+1}/{len(times)} {t:%Y-%m-%d %H:%MZ}: '
                      f'{size} bytes, {count} validated GRIB2 records',flush=True)
                if i+4 < len(times):
                    pending.append(pool.submit(download,times[i+4],staging))
    with zipfile.ZipFile(args.output) as archive:
        expected = ['LPIA98_KWBR_'+t.strftime('%Y%m%d%H%M') for t in times]
        assert archive.namelist() == expected
        bad = archive.testzip()
        if bad:
            raise ValueError(f'ZIP checksum failed: {bad}')
    print(f'COMPLETE: {args.output}, {args.output.stat().st_size} bytes',flush=True)

if __name__ == '__main__':
    main()
