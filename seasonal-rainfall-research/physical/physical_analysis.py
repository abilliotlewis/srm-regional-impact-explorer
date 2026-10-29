#!/usr/bin/env python3
"""Exploratory spatial audit, TC proximity screen, coastal split, and circulation composite."""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np,pandas as pd,xarray as xr
from scipy import ndimage, spatial
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'regional'))
from run_regional import load_data,mask_states,extreme_days,objects,counts,summaries

def coords3(lon,lat):
 lat=np.deg2rad(lat);lon=np.deg2rad(lon);return np.stack([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)],axis=-1)
def coast_distance(lat,lon):
 x=json.loads((HERE/'coastline.geojson').read_text());points=[]
 for f in x['features']:
  geo=f['geometry'];lines=geo['coordinates'] if geo['type']=='MultiLineString' else [geo['coordinates']]
  for line in lines:
   v=np.asarray(line)
   if len(v)<2 or not np.any((v[:,0]>-100)&(v[:,0]<-75)&(v[:,1]>20)&(v[:,1]<40)):continue
   for a,b in zip(v[:-1],v[1:]):
    n=max(1,int(np.ceil(np.linalg.norm(b-a)/.03)));points.extend(a+(b-a)*(i/n) for i in range(n))
 xx,yy=np.meshgrid(lon,lat);tree=spatial.cKDTree(coords3(np.array(points)[:,0],np.array(points)[:,1]));dist=tree.query(coords3(xx.ravel(),yy.ravel()))[0];return (2*6371*np.arcsin(np.clip(dist/2,0,1))).reshape(xx.shape)

def hurdat(file):
 rec=[];storm=stormname=None
 for line in file.read_text().splitlines():
  x=[p.strip() for p in line.split(',')]
  if x[0].startswith('AL'):storm=x[0];stormname=x[1];continue
  if len(x)<7 or not x[0].isdigit() or not 1978<=int(x[0][:4])<=2025:continue
  lat=float(x[4][:-1])*(-1 if x[4].endswith('S') else 1);lon=float(x[5][:-1])*(-1 if x[5].endswith('W') else 1)
  rec.append({'storm':storm,'name':stormname,'time':pd.to_datetime(x[0]+x[1],format='%Y%m%d%H%M'),'status':x[3],'lat':lat,'lon':lon})
 return pd.DataFrame(rec)

def rainfall_day(times):
 return (times-pd.Timedelta(hours=12)-pd.Timedelta(nanoseconds=1)).dt.normalize()+pd.Timedelta(days=1)

def catalog(ex,dates,lat,lon,tracks):
 label,n=ndimage.label(ex,structure=np.ones((3,3,3),np.uint8));sl=ndimage.find_objects(label);tracks=tracks[tracks.status.isin(['TD','TS','HU','SD','SS','EX','LO'])].copy();tracks['day']=rainfall_day(tracks.time)
 byday={day:g for day,g in tracks.groupby('day')}; rows=[]
 for ident,box in enumerate(sl,1):
  if box is None:continue
  z=label[box]==ident; footprint=z.any(axis=0)
  if footprint.sum()<4:continue
  daily=z.sum(axis=(1,2));j=int(np.argmax(daily));start=box[0].start;end=box[0].stop-1;peak=start+j
  iy,ix=np.where(footprint);lats=lat[box[1]][iy];lons=lon[box[2]][ix];best=99999.;bestrow=None
  for k in range(z.shape[0]):
   day=dates[start+k]; t=byday.get(day)
   if t is None or not z[k].any():continue
   iy,ix=np.where(z[k]); grid=coords3(lon[box[2]][ix],lat[box[1]][iy]);stormpts=coords3(t.lon.to_numpy(),t.lat.to_numpy());closest=spatial.distance.cdist(stormpts,grid).min(axis=1);p=int(np.argmin(closest));dist=2*6371*np.arcsin(np.clip(closest[p]/2,0,1))
   if dist<best:best=dist;bestrow=t.iloc[p]
  rows.append({'start':dates[start],'end':dates[end],'peak':dates[peak],'footprint_cells':int(footprint.sum()),'peak_cells':int(daily[j]),'cell_days':int(z.sum()),'lat_min':lats.min(),'lat_max':lats.max(),'lon_min':lons.min(),'lon_max':lons.max(),'nearest_track_km':float(best) if bestrow is not None else np.nan,'nearest_track_id':bestrow.storm if bestrow is not None else '', 'nearest_track_name':bestrow['name'] if bestrow is not None else '', 'nearest_track_status':bestrow.status if bestrow is not None else '', 'nearest_track_time':bestrow.time if bestrow is not None else pd.NaT})
 e=pd.DataFrame(rows).sort_values('start').reset_index(drop=True);e.insert(0,'event_id',np.arange(1,len(e)+1));e['season']=e.peak.dt.month.map({12:'DJF',1:'DJF',2:'DJF',3:'MAM',4:'MAM',5:'MAM',6:'JJA',7:'JJA',8:'JJA',9:'SON',10:'SON',11:'SON'});e['season_year']=e.peak.dt.year+(e.peak.dt.month==12)
 return e

def tc_counts(e,dates,valid):
 rows=[]
 for radius in [0,250,500,750]:
  keep=e if radius==0 else e[~(e.nearest_track_km<=radius)]
  c=counts(keep,dates,valid);c['method']=f'proximity_{radius}';c['radius_km']=radius;rows.append(c)
 near=e[e.nearest_track_km<=500].sort_values('peak').drop_duplicates(['season','season_year','nearest_track_id'])
 other=e[~(e.nearest_track_km<=500)]; merged=pd.concat([near,other],ignore_index=True)
 c=counts(merged,dates,valid);c['method']='merge_near_500';c['radius_km']=500;rows.append(c)
 return pd.concat(rows,ignore_index=True)

def composite(c,zfile,out):
 with xr.open_dataset(zfile) as ds:
  a=ds.hgt.sel(level=500).sel(time=slice('1978-01-01','2025-12-31')).load()
 rows=[];mapdata=[]
 for season in ['DJF','JJA']:
  sub=c[(c.season==season)&(c.method=='proximity_0')&c.eligible].copy().sort_values('year');q25=sub['count'].quantile(.25);q75=sub['count'].quantile(.75);low=sub[sub['count']<=q25];high=sub[sub['count']>=q75]
  fields=[];years=[]
  for y in sub.year:
   months=[(y-1,12),(y,1),(y,2)] if season=='DJF' else [(y,6),(y,7),(y,8)]
   fields.append(np.mean([a.sel(time=f'{yr}-{mo:02d}-01').values for yr,mo in months],axis=0));years.append(y)
  fields=np.array(fields);years=np.array(years);h=np.isin(years,high.year);l=np.isin(years,low.year);diff=fields[h].mean(0)-fields[l].mean(0)
  i=int(np.argmin(abs(a.lat.values-32.5)));j=int(np.argmin(abs(a.lon.values-270)));gulf=diff[i,j]
  rng=np.random.default_rng(523);obs=abs(gulf);v=fields[:,i,j];diffs=[]
  # Permutation is conditional on sampled season labels and ignores temporal correlation.
  for k in range(5000):
   perm=rng.permutation(len(v));diffs.append(abs(v[perm[:h.sum()]].mean()-v[perm[h.sum():h.sum()+l.sum()]].mean()))
  p=(1+np.sum(np.array(diffs)>=obs))/5001
  rows.append({'season':season,'n_high':int(h.sum()),'n_low':int(l.sum()),'low_count_max':int(q25),'high_count_min':int(np.ceil(q75)),'gulf_grid_lat':float(a.lat[i]),'gulf_grid_lon':float(a.lon[j]-360),'gulf_high_minus_low_m':float(gulf),'gulf_permutation_p_exploratory':float(p),'high_years':','.join(map(str,years[h])),'low_years':','.join(map(str,years[l]))})
  mapdata.append((season,diff))
  pd.DataFrame(diff,index=a.lat.values,columns=a.lon.values-360).to_csv(out/f'height_composite_{season}.csv',index_label='latitude')
 fig,axs=plt.subplots(2,1,figsize=(10,7),constrained_layout=True);levels=np.arange(-90,100,15)
 for ax,(season,diff) in zip(axs,mapdata):
  m=ax.contourf(a.lon.values-360,a.lat.values,diff,levels=levels,cmap='RdBu_r',extend='both')
  for feature in json.loads((HERE/'coastline.geojson').read_text())['features']:
   geo=feature['geometry']; lines=geo['coordinates'] if geo['type']=='MultiLineString' else [geo['coordinates']]
   for line in lines:
    xy=np.asarray(line); ax.plot(xy[:,0],xy[:,1],color='0.35',lw=.45)
  ax.plot(-90,32.5,marker='x',color='black',markersize=5);ax.set_xlim(-140,-30);ax.set_ylim(10,70);ax.contour(a.lon.values-360,a.lat.values,diff,levels=[0],colors='black',linewidths=.7);ax.set(xlabel='Longitude',ylabel='Latitude',title=f'{season}: active minus quiet season, 500-hPa height (m)')
 fig.colorbar(m,ax=axs,label='Geopotential-height difference (m)');fig.savefig(out/'height_composites.png',dpi=160);plt.close(fig);return pd.DataFrame(rows)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cpc',type=Path,required=True);ap.add_argument('--hurdat',type=Path,required=True);ap.add_argument('--z500',type=Path,required=True);args=ap.parse_args();out=HERE/'output';out.mkdir(exist_ok=True)
 data,dates,lat,lon,manifest=load_data(args.cpc);mask,_=mask_states(lat,lon);ex,valid,ok,thr=extreme_days(data,dates,mask,.99);tracks=hurdat(args.hurdat);e=catalog(ex,dates,lat,lon,tracks)
 prior=pd.read_csv(HERE.parent/'regional/output/event_catalog.csv');old=prior[prior.method=='tracked'];cols=['event_id','start','end','peak','footprint_cells','peak_cells','cell_days'];new=e[cols].copy()
 for col in ['start','end','peak']:new[col]=new[col].dt.strftime('%Y-%m-%d')
 pd.testing.assert_frame_equal(new.reset_index(drop=True),old[cols].reset_index(drop=True),check_dtype=False)
 e.to_csv(out/'connected_events_with_track_screen.csv',index=False);cnt=tc_counts(e,dates,valid);cnt.to_csv(out/'tc_screen_season_counts.csv',index=False);s=summaries(cnt);s.to_csv(out/'tc_screen_summaries.csv',index=False)
 distance=coast_distance(lat,lon);area=[];coast=(distance<=100)&ok
 for name,mask2 in [('coastal_100km',coast),('inland_100km',ok&~coast)]:
  extreme=ex&mask2[None,:,:];events=objects(extreme,dates,'tracked');c=counts(events,dates,valid);c['method']=name;c['cells']=int(mask2.sum());area.append(c)
 ac=pd.concat(area,ignore_index=True);ac.to_csv(out/'coastal_inland_counts.csv',index=False);summaries(ac).to_csv(out/'coastal_inland_summary.csv',index=False)
 comp=composite(cnt,args.z500,out);comp.to_csv(out/'circulation_summary.csv',index=False)
 provenance=[]
 for name,f,url in [('hurdat2',args.hurdat,'https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-02272026.txt'),('ncep_z500_subset',args.z500,'https://psl.noaa.gov/thredds/ncss/grid/Datasets/ncep.reanalysis/Monthlies/pressure/hgt.mon.mean.nc'),('natural_earth_coastline',HERE/'coastline.geojson','https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_coastline.geojson')]:
  provenance.append({'dataset':name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'url':url})
 pd.DataFrame(provenance).to_csv(out/'source_manifest.csv',index=False)
 print('Events',len(e),'near track 500km',int((e.nearest_track_km<=500).sum()),'coastal/inland cells',coast.sum(),(ok&~coast).sum());print(s[s.k==5].to_string(index=False));print(summaries(ac).query('k==5').to_string(index=False));print(comp.to_string(index=False))
if __name__=='__main__':main()
