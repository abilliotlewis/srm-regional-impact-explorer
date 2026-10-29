#!/usr/bin/env python3
"""Exploratory CPC regional extreme precipitation catalog and simple hindcasts."""
import argparse, calendar, hashlib, json
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr
from scipy import ndimage, optimize, stats
from matplotlib.path import Path as MPath
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
STATES={'Louisiana','Mississippi','Alabama','Georgia','Florida'}
SEASON={12:'DJF',1:'DJF',2:'DJF',3:'MAM',4:'MAM',5:'MAM',6:'JJA',7:'JJA',8:'JJA',9:'SON',10:'SON',11:'SON'}

def load_data(raw):
 arrays=[]; dates=[]; manifest=[]; lat=lon=None
 for y in range(1978,2026):
  f=raw/f'{y}.nc'
  if not f.exists(): raise FileNotFoundError(f)
  with xr.open_dataset(f) as ds:
   a=ds.precip.sel(lat=slice(24,36),lon=slice(265,280)); lats=a.lat.values; lons=a.lon.values-360
   if lat is not None and (not np.array_equal(lat,lats) or not np.array_equal(lon,lons)): raise ValueError('Grid changed')
   lat,lon=lats,lons
   d=pd.DatetimeIndex(a.time.values).normalize(); exp=pd.date_range(f'{y}-01-01',f'{y}-12-31')
   if not d.equals(exp): raise ValueError(f'Incomplete, duplicated or unexpected dates: {y}')
   arrays.append(a.values.astype('float32'));dates.extend(d)
  manifest.append({'year':y,'product':'historical' if y<=2006 else 'RT','file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'url':f'https://psl.noaa.gov/thredds/fileServer/Datasets/cpc_us_precip/{"" if y<=2006 else "RT/"}precip.V1.0.{y}.nc'})
 return np.concatenate(arrays),pd.DatetimeIndex(dates),lat,lon,pd.DataFrame(manifest)

def mask_states(lat,lon):
 X,Y=np.meshgrid(lon,lat); points=np.column_stack((X.ravel(),Y.ravel())); mask=np.zeros(len(points),bool); labels=np.full(len(points),'',object)
 features=json.loads((HERE/'states.geojson').read_text())['features']
 for f in features:
  name=f['properties']['name']; geo=f['geometry']
  if name not in STATES:continue
  poly=geo['coordinates'] if geo['type']=='MultiPolygon' else [geo['coordinates']]
  inside=np.zeros(len(points),bool)
  for part in poly:
   cur=MPath(np.asarray(part[0])).contains_points(points)
   for hole in part[1:]:cur &= ~MPath(np.asarray(hole)).contains_points(points)
   inside |= cur
  mask |= inside;labels[inside]=name
 return mask.reshape(X.shape),labels.reshape(X.shape)

def thresholds(data,dates,mask,q):
 seas=np.array([SEASON[x] for x in dates.month]); base=(dates.year>=1981)&(dates.year<=2010)
 out={}
 for s in ['DJF','MAM','JJA','SON']:
  x=data[base&(seas==s)][:,mask].copy();x[(x<1)|~np.isfinite(x)]=np.nan
  out[s]=np.nanquantile(x,q,axis=0).astype('float32')
 return out

def extreme_days(data,dates,mask,q):
 # Exclude cells with excessive missing values before defining the analysis domain.
 ok=(np.isfinite(data).mean(axis=0)>=.99)&mask; threshold=thresholds(data,dates,ok,q)
 exceed=np.zeros(data.shape,dtype=bool); months=dates.month.to_numpy(); valid=np.isfinite(data[:,ok]).mean(axis=1)
 for s in ['DJF','MAM','JJA','SON']:
  ix=np.flatnonzero(np.array([SEASON[x] for x in months])==s)
  z=np.zeros((len(ix),)+data.shape[1:],bool);z[:,ok]=data[ix][:,ok]>threshold[s];exceed[ix]=z
 # If fewer than 95% of retained domain cells are observed, mark as excluded.
 exceed[valid<.95]=False
 return exceed,valid,ok,threshold

def objects(exceed,dates,kind,mincells=4,gap=1):
 events=[]
 if kind=='tracked':
  # 26-neighbor connectivity: one grid cell of displacement/day.
  label,n=ndimage.label(exceed,structure=np.ones((3,3,3),dtype=np.uint8))
  for ident,sl in enumerate(ndimage.find_objects(label),1):
   if sl is None:continue
   obj=label[sl]==ident; occupied=np.any(obj,axis=0)
   if occupied.sum()<mincells:continue
   daily=obj.sum(axis=(1,2)); pk=int(np.argmax(daily)); start=sl[0].start; end=sl[0].stop-1; peak=start+pk
   events.append([dates[start],dates[end],dates[peak],int(occupied.sum()),int(daily[pk]),int(obj.sum())])
 else:
  ix=np.flatnonzero(exceed.sum(axis=(1,2))>=mincells)
  if len(ix):
   groups=np.split(ix,np.flatnonzero(np.diff(ix)>gap+1)+1)
   for g in groups:
    daily=exceed[g].sum(axis=(1,2));peak=g[np.argmax(daily)]
    events.append([dates[g[0]],dates[g[-1]],dates[peak],int(np.any(exceed[g],axis=0).sum()),int(daily.max()),int(daily.sum())])
 e=pd.DataFrame(events,columns=['start','end','peak','footprint_cells','peak_cells','cell_days'])
 if e.empty: return e
 e=e.sort_values('start').reset_index(drop=True);e.insert(0,'event_id',np.arange(1,len(e)+1));e['duration_days']=(e.end-e.start).dt.days+1;e['season']=e.peak.dt.month.map(SEASON);e['season_year']=e.peak.dt.year+(e.peak.dt.month==12);e['method']=kind
 return e

def counts(e,dates,valid):
 rows=[]
 for season,years,months in [('DJF',range(1980,2026),[12,1,2]),('JJA',range(1979,2026),[6,7,8])]:
  for y in years:
   sy=dates.year+(dates.month==12); idx=(sy==y)&dates.month.isin(months); cov=float(np.mean(valid[idx]>=.95))
   rows.append({'season':season,'year':y,'count':int(((e.season==season)&(e.season_year==y)).sum()),'valid_day_fraction':cov,'eligible':cov>=.95})
 return pd.DataFrame(rows)

def summaries(c):
 rng=np.random.default_rng(393); rows=[]
 for (method,season),g in c[c.eligible].groupby(['method','season']):
  y=g['count'].to_numpy(); mu=y.mean(); vm=y.var(ddof=1)/mu
  sims=rng.poisson(mu,size=(10000,len(y))); simvm=sims.var(axis=1,ddof=1)/np.maximum(sims.mean(axis=1),1e-9)
  for k in [3,5,10]:
   rows.append({'method':method,'season':season,'k':k,'n':len(y),'mean':mu,'variance':y.var(ddof=1),'vmr':vm,'p_vmr_upper':(1+(simvm>=vm).sum())/10001,'observed_p_ge_k':(y>=k).mean(),'poisson_p_ge_k':stats.poisson.sf(k-1,mu),'max_count':int(y.max())})
 return pd.DataFrame(rows)

def nino():
 rows=[]
 for line in (HERE.parent/'data/nino34.txt').read_text().splitlines()[1:]:
  x=line.split()
  if len(x)==13 and x[0].isdigit():
   y=int(x[0]); rows.append((y,float(x[5]),float(x[11])))
 return pd.DataFrame(rows,columns=['year','may','nov'])

def forecast(c):
 n=nino(); predictions=[]
 for method in ['tracked','runs']:
  for season in ['DJF','JJA']:
   x=c[(c.method==method)&(c.season==season)&c.eligible].copy(); x['predictor_year']=x.year-(season=='DJF');x=x.merge(n,left_on='predictor_year',right_on='year',suffixes=('','_sst')); x['sst']=x['nov' if season=='DJF' else 'may']; x=x[x.sst>-90]
   for _,row in x[x.year>=2012].iterrows():
    train=x[x.year<row.year];y=train['count'].to_numpy(); k=max(2,int(np.ceil(np.quantile(y,.75))));target=int(row['count']>=k)
    for model in ['constant','trend','enso','enso_nb']:
     x0=train.year.to_numpy() if model=='trend' else train.sst.to_numpy(); test=row.year if model=='trend' else row.sst
     center=x0.mean();scale=max(x0.std(),1e-8);z=(x0-center)/scale;ztest=(test-center)/scale
     X=np.ones((len(train),1)) if model=='constant' else np.column_stack((np.ones(len(train)),z))
     def loss(b):
      pred=np.clip(X@b[:X.shape[1]],-15,15);mu=np.exp(pred)
      if model=='enso_nb':
       alpha=np.exp(np.clip(b[-1],-5,3));nsize=1/alpha
       return -np.sum(stats.nbinom.logpmf(y,nsize,nsize/(nsize+mu)))+b[1]**2+0.1*b[-1]**2
      return np.sum(mu-y*pred)+(1.0*b[1]**2 if len(b)>1 else 0)
     init=[np.log(max(y.mean(),.01))]+([0.] if model!='constant' else [])+([-1.] if model=='enso_nb' else [])
     fit=optimize.minimize(loss,init,method='L-BFGS-B',options={'maxiter':1000,'ftol':1e-10})
     if not np.isfinite(fit.fun): raise RuntimeError('Nonfinite model fit')
     b=fit.x;lam=float(np.exp(np.clip(b[0]+(b[1]*ztest if model!='constant' else 0),-15,15)))
     if model=='enso_nb':
      alpha=np.exp(np.clip(b[-1],-5,3));nsize=1/alpha;p=float(stats.nbinom.sf(k-1,nsize,nsize/(nsize+lam))); logscore=-stats.nbinom.logpmf(int(row['count']),nsize,nsize/(nsize+lam))
     else: p=float(stats.poisson.sf(k-1,lam));logscore=-stats.poisson.logpmf(int(row['count']),lam)
     predictions.append({'method':method,'season':season,'year':int(row.year),'model':model,'observed':int(row['count']),'k':k,'positive':target,'lambda':lam,'p_active':p,'brier':(p-target)**2,'count_log_score':logscore,'converged':bool(fit.success)})
 return pd.DataFrame(predictions)


def bootstrap(cnt,pred,out):
 rng=np.random.default_rng(994); rows=[]
 # Moving blocks of three adjacent seasons. Intervals are descriptive and do not include threshold or model-selection uncertainty.
 for (method,season),g in cnt[cnt.eligible].groupby(['method','season']):
  y=g.sort_values('year')['count'].to_numpy(); n=len(y); sims=[]
  for i in range(3000):
   starts=rng.integers(0,n-2,size=int(np.ceil(n/3))); idx=np.concatenate([np.arange(j,j+3) for j in starts])[:n]; yy=y[idx];sims.append(yy.var(ddof=1)/yy.mean())
  lo,hi=np.percentile(sims,[2.5,97.5]);rows.append({'method':method,'season':season,'metric':'vmr','model':'','difference':y.var(ddof=1)/y.mean(),'low':lo,'high':hi,'bootstrap':'3-year moving block'})
  a=pred[(pred.method==method)&(pred.season==season)]
  base=a[a.model=='constant'].set_index('year')
  for model in ['trend','enso','enso_nb']:
   other=a[a.model==model].set_index('year'); paired=base.join(other,lsuffix='_base',rsuffix='_model');d=(paired.brier_base-paired.brier_model).to_numpy();n=len(d); sims=[]
   for i in range(3000):
    starts=rng.integers(0,n-2,size=int(np.ceil(n/3))); idx=np.concatenate([np.arange(j,j+3) for j in starts])[:n];sims.append(d[idx].mean())
   lo,hi=np.percentile(sims,[2.5,97.5]);rows.append({'method':method,'season':season,'metric':'brier_improvement','model':model,'difference':d.mean(),'low':lo,'high':hi,'bootstrap':'3-year moving block'})
 pd.DataFrame(rows).to_csv(out/'bootstrap_intervals.csv',index=False)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--raw',type=Path,required=True);parser.add_argument('--out',type=Path,default=HERE/'output');args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
 data,dates,lat,lon,manifest=load_data(args.raw);manifest.to_csv(args.out/'source_manifest.csv',index=False);mask,states=mask_states(lat,lon)
 allcounts=[]; evs=[]; sensitivity=[]
 for q in [.95,.99,.995]:
  ex,valid,ok,thr=extreme_days(data,dates,mask,q)
  for method in ['tracked','runs']:
   e=objects(ex,dates,method);c=counts(e,dates,valid);c['method']=method;c['quantile']=q
   if q==.99:allcounts.append(c);e['quantile']=q;evs.append(e)
   summary=summaries(c);summary['quantile']=q;sensitivity.append(summary)
  print('quantile',q,'cells',ok.sum(),'missing days',(valid<.95).sum(),flush=True)
 cnt=pd.concat(allcounts,ignore_index=True);events=pd.concat(evs,ignore_index=True); sm=pd.concat(sensitivity,ignore_index=True);pred=forecast(cnt)
 events.to_csv(args.out/'event_catalog.csv',index=False);cnt.to_csv(args.out/'season_counts.csv',index=False);sm.to_csv(args.out/'sensitivity.csv',index=False);pred.to_csv(args.out/'hindcasts.csv',index=False)
 scores=pred.groupby(['method','season','model']).agg(n=('year','size'),positive=('positive','sum'),brier=('brier','mean'),count_log_score=('count_log_score','mean')).reset_index();scores.to_csv(args.out/'hindcast_scores.csv',index=False)
 fig,ax=plt.subplots(2,1,figsize=(10,6),sharex=True)
 for i,s in enumerate(['DJF','JJA']):
  for m,col in [('tracked','#206e83'),('runs','#cb713b')]:
   g=cnt[(cnt.season==s)&(cnt.method==m)&cnt.eligible];ax[i].plot(g.year,g['count'],label=m,color=col,alpha=.8)
  ax[i].set(title=s,ylabel='Episodes');ax[i].axvline(2007,color='gray',ls=':',lw=1)
 ax[0].legend(frameon=False);ax[1].set_xlabel('Season year');fig.suptitle('CPC five-state extreme-precipitation episode counts');fig.tight_layout();fig.savefig(args.out/'seasonal_counts.png',dpi=170);plt.close(fig)
 print(sm[(sm['quantile']==.99)&(sm.k==5)].to_string(index=False));print(scores.to_string(index=False)); bootstrap(cnt,pred,args.out)
if __name__=='__main__':main()
