#!/usr/bin/env python3
"""Download HURDAT2 and the monthly NCEP Z500 subset, keeping data out of Git."""
import argparse,pathlib,urllib.parse,urllib.request
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
h='https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-02272026.txt'
q={'var':'hgt','north':70,'south':10,'west':220,'east':330,'time_start':'1978-01-01T00:00:00Z','time_end':'2025-12-31T23:59:59Z','vertCoord':500,'accept':'netcdf4'}
z='https://psl.noaa.gov/thredds/ncss/grid/Datasets/ncep.reanalysis/Monthlies/pressure/hgt.mon.mean.nc?'+urllib.parse.urlencode(q)
for name,url in [('hurdat2-1851-2025.txt',h),('ncep_z500.nc',z)]:
 f=a.out/name
 if f.exists(): print('Existing:',f);continue
 tmp=f.with_suffix('.tmp'); print('Downloading',name,flush=True)
 try:urllib.request.urlretrieve(url,tmp);tmp.replace(f)
 finally:tmp.unlink(missing_ok=True)
