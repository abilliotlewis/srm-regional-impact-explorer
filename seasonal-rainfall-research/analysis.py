#!/usr/bin/env python3
"""Exploratory, station-based DJF precipitation analysis; see REPORT.md."""
from pathlib import Path
import calendar,json,gzip
import numpy as np,pandas as pd
from scipy.stats import poisson
from scipy.optimize import minimize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).resolve().parent; OUT=D/'output'; OUT.mkdir(exist_ok=True)
stations={'Baton Rouge':'USW00013970','New Orleans':'USW00012916','Jackson':'USW00003940','Mobile':'USW00013894','Atlanta':'USW00013874','Tallahassee':'USW00093805'}

def read_station(path):
 rows=[]
 for line in gzip.open(path, "rt"):
  if line[17:21]!='PRCP': continue
  y=int(line[11:15]); m=int(line[15:17])
  if not 1978<=y<=2025: continue
  for d in range(1,calendar.monthrange(y,m)[1]+1):
   p=21+(d-1)*8; v=int(line[p:p+5]); q=line[p+6:p+7]
   rows.append((pd.Timestamp(y,m,d), v/10 if v>=0 and q==' ' else np.nan))
 return pd.DataFrame(rows,columns=['date','mm']).drop_duplicates('date').set_index('date').sort_index()

def calc(df,quantile,gap):
 df=df.reindex(pd.date_range('1978-12-01','2025-02-28',freq='D')); df.index.name='date'
 df['year']=df.index.year+(df.index.month==12).astype(int)
 df['djf']=df.index.month.isin([12,1,2]); base=df[df.djf & df.year.between(1979,1998) & (df.mm>=1)].mm
 threshold=base.quantile(quantile)
 x=df[df.djf & df.year.between(1979,2025)].copy()
 coverage=x.groupby('year').mm.apply(lambda a:a.notna().mean()); valid=coverage[coverage>=.95].index
 # Declustering across DJF boundaries where applicable, with missing observations treated as boundaries.
 years=[]
 for year,g in x.groupby('year'):
  if year not in valid: continue
  dates=g.index[g.mm>threshold]; count=0; last=None
  for d in dates:
   if last is None or (d-last).days>gap+1 or g.loc[last:d,'mm'].isna().any(): count+=1
   last=d
  years.append((year,count,float(coverage.loc[year])))
 return threshold,pd.DataFrame(years,columns=['year','count','coverage'])

def nino():
 rows=[]
 for l in (D/'data/nino34.txt').read_text().splitlines()[1:]:
  v=l.split()
  if len(v)==13 and v[0].isdigit(): rows.append((int(v[0]),float(v[11]))) # November column
 a=pd.DataFrame(rows,columns=['year','nov_sst']); a=a[a.nov_sst>-90].copy(); a['anomaly']=a.nov_sst-a.loc[a.year.between(1981,2010),'nov_sst'].mean(); a['year']+=1
 return a[['year','anomaly']]

def fit(train,conditioned):
 x=np.column_stack([np.ones(len(train)),train.anomaly]) if conditioned else np.ones((len(train),1)); y=train['count'].to_numpy()
 def objective(b):
  z=np.clip(x@b,-20,20); return np.sum(np.exp(z)-y*z)+(.5*b[1]**2 if conditioned else 0)
 return minimize(objective,np.array([np.log(max(y.mean(),.01))]+([0.] if conditioned else [])),method='BFGS').x

def run():
 ns=nino(); records=[]; series={}; rng=np.random.default_rng(1783)
 for label,ident in stations.items():
  for q in [.95,.99,.995]:
   for gap in [1,3,5]:
    t,c=calc(read_station(D/'data'/f'{ident}.dly.gz'),q,gap); n=c['count'].to_numpy(); mu=n.mean(); var=n.var(ddof=1); sim=rng.poisson(mu,size=(20000,len(n))); ratio=sim.var(axis=1,ddof=1)/np.maximum(sim.mean(axis=1),1e-9); observed=var/mu
    records.append(dict(station=label,quantile=q,gap=gap,threshold_mm=t,seasons=len(n),mean=mu,variance=var,vmr=observed,p_overdispersion=(1+np.sum(ratio>=observed))/20001,p_ge_2=(n>=2).mean()))
    if q==.99 and gap==3: series[label]=c
 pd.DataFrame(records).to_csv(OUT/'sensitivity.csv',index=False)
 c=series['Baton Rouge'].merge(ns,on='year',how='inner'); c.to_csv(OUT/'baton_rouge_counts.csv',index=False)
 preds=[]
 for _,row in c[c.year>=2009].iterrows():
  train=c[c.year<row.year]
  if len(train)<20: continue
  for model,cond in [('climatology',False),('november_nino34',True)]:
   b=fit(train,cond); lam=np.exp(b[0]+(b[1]*row.anomaly if cond else 0)); p=poisson.sf(1,lam); preds.append(dict(year=int(row.year),model=model,observed=int(row['count']),p_ge_2=p,lambda_pred=lam))
 p=pd.DataFrame(preds); p.to_csv(OUT/'rolling_predictions.csv',index=False)
 metrics={}
 for model,g in p.groupby('model'):
  y=(g.observed>=2).astype(int); pp=np.clip(g.p_ge_2,1e-8,1-1e-8); metrics[model]={'n':len(g),'brier':float(np.mean((pp-y)**2)),'binary_log_loss':float(np.mean(-y*np.log(pp)-(1-y)*np.log(1-pp)))}
 (OUT/'forecast_scores.json').write_text(json.dumps(metrics,indent=2))
 fig,axes=plt.subplots(2,1,figsize=(10,7)); axes[0].bar(c.year,c['count'],color='#267b8e'); axes[0].set(title='Baton Rouge: winter extreme rainfall episodes',ylabel='Episodes per DJF'); axes[1].scatter(c.anomaly,c['count'],alpha=.7,color='#a95036'); axes[1].set(xlabel='November Niño 3.4 SST anomaly (°C)',ylabel='DJF episodes'); fig.tight_layout(); fig.savefig(OUT/'baton_rouge.png',dpi=180); plt.close(fig)
 print(pd.DataFrame(records).query('quantile==0.99 and gap==3').round(3).to_string(index=False)); print(json.dumps(metrics,indent=2))
if __name__=='__main__':run()
