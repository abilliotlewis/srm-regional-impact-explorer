#!/usr/bin/env python3
"""Acquire source files without changing previously downloaded files."""
import argparse, pathlib, urllib.request
p=argparse.ArgumentParser();p.add_argument('--raw',type=pathlib.Path,required=True);a=p.parse_args();a.raw.mkdir(parents=True,exist_ok=True)
for y in range(1978,2026):
 f=a.raw/f'{y}.nc'
 if f.exists():continue
 u=f'https://psl.noaa.gov/thredds/fileServer/Datasets/cpc_us_precip/{"" if y<=2006 else "RT/"}precip.V1.0.{y}.nc'; tmp=f.with_suffix('.tmp');print(y,flush=True)
 try:urllib.request.urlretrieve(u,tmp);tmp.replace(f)
 finally:tmp.unlink(missing_ok=True)
