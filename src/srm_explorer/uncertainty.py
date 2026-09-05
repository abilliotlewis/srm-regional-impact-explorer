"""Time-series uncertainty summaries for the single-member daily case study."""
import hashlib
import numpy as np
import pandas as pd

def moving_block_means(values,replicates=2000,block_length=5,seed=0):
    series=np.asarray(values,dtype=float)
    if series.ndim!=1 or series.size<block_length: raise ValueError("Series must be one-dimensional and at least one block long")
    if not np.isfinite(series).all(): raise ValueError("Bootstrap series contains missing or infinite values")
    rng=np.random.default_rng(seed); blocks=int(np.ceil(series.size/block_length)); starts=rng.integers(0,series.size,size=(replicates,blocks)); idx=(starts[...,None]+np.arange(block_length))%series.size
    return series[idx].reshape(replicates,-1)[:,:series.size].mean(axis=1)
def _stable_seed(text): return int.from_bytes(hashlib.sha256(text.encode()).digest()[:4],"big")
def lag1_autocorrelation(values):
    s=np.asarray(values,dtype=float)
    if s.size<3 or np.std(s[:-1])==0 or np.std(s[1:])==0:return 0.0
    return float(np.corrcoef(s[:-1],s[1:])[0,1])
def independent_difference_interval(target,reference,label,replicates=2000,block_length=5):
    t=np.asarray(target,dtype=float); r=np.asarray(reference,dtype=float); seed=_stable_seed(label); dif=moving_block_means(t,replicates,block_length,seed)-moving_block_means(r,replicates,block_length,seed+1); pooled=float(np.sqrt((np.var(t,ddof=1)+np.var(r,ddof=1))/2)); estimate=float(t.mean()-r.mean())
    return {"difference":estimate,"ci_lower":float(np.quantile(dif,.025)),"ci_upper":float(np.quantile(dif,.975)),"target_mean":float(t.mean()),"reference_mean":float(r.mean()),"target_year_sd":float(np.std(t,ddof=1)),"reference_year_sd":float(np.std(r,ddof=1)),"pooled_year_sd":pooled,"standardized_difference":estimate/pooled if pooled else np.nan,"target_lag1":lag1_autocorrelation(t),"reference_lag1":lag1_autocorrelation(r),"target_years":int(t.size),"reference_years":int(r.size),"bootstrap_replicates":replicates,"block_length_years":block_length}
def daily_variability_summary(regional_yearly,metrics,seasons):
    pairs={"G6solar - SSP5-8.5":("G6solar","ssp585"),"G6sulfur - SSP5-8.5":("G6sulfur","ssp585"),"G6solar - G6sulfur":("G6solar","G6sulfur")}; rows=[]
    for metric in metrics:
      for season in seasons:
       s=regional_yearly[(regional_yearly.metric==metric)&(regional_yearly.season==season)]; units=s.units.iloc[0]
       for comparison,(tn,rn) in pairs.items():
        t=s[s.scenario==tn].sort_values("period_year").value; r=s[s.scenario==rn].sort_values("period_year").value
        if t.empty or r.empty: raise ValueError(f"Missing daily time series for {comparison}, {metric}, {season}")
        rows.append({"metric":metric,"season":season,"comparison":comparison,"units":units,**independent_difference_interval(t.to_numpy(),r.to_numpy(),f"{comparison}|{metric}|{season}")})
    return pd.DataFrame(rows)
