"""Descriptive November ENSO category association; not an operational forecast."""
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import beta
from run_regional import nino
p=Path(__file__).parent/'output'; c=pd.read_csv(p/'season_counts.csv'); n=nino();base=n.loc[n.year.between(1981,2010),'nov'].mean(); n['anomaly']=n['nov']-base
c=c[(c.method=='tracked')&(c.season=='DJF')&c.eligible].copy();c['predictor_year']=c.year-1;c=c.merge(n,left_on='predictor_year',right_on='year',suffixes=('','_sst')).sort_values('year');c['active']=c['count']>=15
rng=np.random.default_rng(615);rows=[]
for name,cond in [('cold',c.anomaly<=-.5),('neutral',c.anomaly.between(-.5,.5,inclusive='neither')),('warm',c.anomaly>=.5)]:
 g=c[cond];nobs=len(g);success=int(g.active.sum());rate=success/nobs;lower=0 if success==0 else beta.ppf(.025,success,nobs-success+1);upper=1 if success==nobs else beta.ppf(.975,success+1,nobs-success);rr=rate/c.active.mean(); estimates=[];N=len(c)
 for i in range(5000):
  starts=rng.integers(0,N-2,size=int(np.ceil(N/3)));idx=np.concatenate([np.arange(j,j+3) for j in starts])[:N];z=c.iloc[idx]
  mask=z.anomaly<=-.5 if name=='cold' else (z.anomaly>=.5 if name=='warm' else z.anomaly.between(-.5,.5,inclusive='neither'))
  if mask.sum() and z.active.mean()>0:estimates.append(z.loc[mask,'active'].mean()/z.active.mean())
 lo,hi=np.percentile(estimates,[2.5,97.5]);rows.append({'phase':name,'n':nobs,'active_seasons':success,'probability':rate,'probability_low_exact':lower,'probability_high_exact':upper,'relative_to_all':rr,'rr_low_block':lo,'rr_high_block':hi,'all_n':N,'all_active':int(c.active.sum()),'threshold_k':15})
pd.DataFrame(rows).to_csv(p/'conditional_winter.csv',index=False)
print(pd.DataFrame(rows).round(3).to_string(index=False))
