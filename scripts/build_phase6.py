"""Build the resumable Phase 6 monthly and daily scientific caches."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from build_phase1 import build_frame, experiment_metadata
from build_phase4 import PR_MANIFESTS,TASMAX_MANIFESTS,model_identities
from build_phase5 import MANIFESTS,RAW_DIRS,verified_sources
from download_manifest import load_manifest
from prepare_daily_extremes import build_thresholds,open_daily_region,prepare_daily_outputs
from srm_explorer.geography import DOMAIN_STATES,domain_weights,weighted_domain_means
from srm_explorer.spatial import ensemble_grid_statistics,matched_native_difference,regrid_native_differences
from srm_explorer.uncertainty import daily_variability_summary

PROCESSED=ROOT/"data/processed"; PUBLISHED=ROOT/"data/published"; DOCS=ROOT/"docs"
DOMAINS=["original_box",*DOMAIN_STATES]
SEASONS=["DJF","MAM","JJA","SON","ANN"]
METRICS=["tasmax_mean","pr_mean"]
COMPARISONS=["G6solar - SSP5-8.5","G6sulfur - SSP5-8.5","G6solar - G6sulfur"]
DAILY_PRIORITY=["txx","hwf_tx90_3d","rx5day","cdd"]

def build_monthly(download=False):
    tas=build_frame(TASMAX_MANIFESTS,ROOT/"data/raw/tasmax",download,3.0)
    pr=build_frame(PR_MANIFESTS,ROOT/"data/raw/pr",download,3.0)
    if model_identities(tas)!=model_identities(pr): raise ValueError("tasmax and pr identities differ")
    return pd.concat([tas,pr],ignore_index=True)

def monthly_products(monthly):
    native=[]; remapped=[]
    for metric in METRICS:
      for season in SEASONS:
       for comparison in COMPARISONS:
        n=matched_native_difference(monthly,comparison,metric,season)
        native.append(n); remapped.append(regrid_native_differences(n,metric))
    native=pd.concat(native,ignore_index=True); remapped=pd.concat(remapped,ignore_index=True)
    maps=ensemble_grid_statistics(remapped).merge(
        native[["metric","units","period"]].drop_duplicates("metric"),
        on="metric",validate="many_to_one")
    regional=pd.concat(
        [weighted_domain_means(native,domain) for domain in DOMAINS],
        ignore_index=True,
    )
    group=["domain","season","metric","comparison","units"]
    ensemble=regional.groupby(group,as_index=False).value.agg(mean="mean",median="median",std="std",minimum="min",maximum="max",model_count="size",positive_count=lambda v:int((v>0).sum()),negative_count=lambda v:int((v<0).sum()),zero_count=lambda v:int((v==0).sum()))
    ensemble["sign_agreement"]=ensemble[["positive_count","negative_count"]].max(axis=1)/ensemble.model_count
    area=regional.groupby(group,as_index=False).agg(represented_area_km2=("represented_area_km2","mean"),contributing_cells_min=("contributing_cells","min"),contributing_cells_max=("contributing_cells","max"),equivalent_cells_min=("equivalent_cells","min"),equivalent_cells_max=("equivalent_cells","max"))
    ensemble=ensemble.merge(area,on=group,validate="one_to_one")
    loo=[]
    for keys,g in regional.groupby(group,sort=True):
      for omitted in sorted(g.model.unique()):
       kept=g[g.model!=omitted].value
       full=g.value.mean(); value=kept.mean()
       loo.append(dict(zip(group,keys,strict=True))|{"omitted_model":omitted,"full_mean":full,"leave_one_out_mean":value,"full_sign":int(__import__('numpy').sign(full)),"leave_one_out_sign":int(__import__('numpy').sign(value)),"sign_changed":bool(__import__('numpy').sign(full)!=__import__('numpy').sign(value)),"model_count":len(kept)})
    return native,remapped,maps,regional,ensemble,pd.DataFrame(loo)

def build_daily(download=False):
    manifests={v:load_manifest(p) for v,p in MANIFESTS.items()}
    sources={v:verified_sources(m,RAW_DIRS[v],download) for v,m in manifests.items()}
    hist_t=open_daily_region(sources["tasmax"]["historical"],"tasmax",1981,2010,3.0)
    hist_p=open_daily_region(sources["pr"]["historical"],"pr",1981,2010,3.0)
    tx90,pr95=build_thresholds(hist_t,hist_p); climates=[]; years=[]; manifest=manifests["tasmax"]
    for scenario in ("ssp585","G6solar","G6sulfur"):
      records=[r for r in manifest["records"] if r["experiment_id"]==scenario]; meta=experiment_metadata(manifest,scenario)
      c,y=prepare_daily_outputs(sources["tasmax"][scenario],sources["pr"][scenario],scenario,manifest["source_id"],tx90,pr95,variant_label=records[0]["variant_label"],grid_label=records[0]["grid_label"],parent_experiment_id=meta["parent_experiment_id"],parent_variant_label=meta["parent_variant_label"],spatial_padding_degrees=3.0)
      c["dataset_key"]=records[0]["dataset_key"]; y["dataset_key"]=records[0]["dataset_key"]; climates.append(c); years.append(y)
    return pd.concat(climates,ignore_index=True),pd.concat(years,ignore_index=True)

def daily_products(climate,yearly):
    land_year=weighted_domain_means(yearly,"southeast_land")
    variability=daily_variability_summary(land_year,DAILY_PRIORITY,["ANN","JJA"])
    land_maps=climate[climate.metric.isin(DAILY_PRIORITY)].copy()
    land_maps=land_maps.merge(__import__('srm_explorer.geography',fromlist=['domain_weights']).domain_weights(land_maps,"southeast_land"),on=["model","grid_label","lat","lon"],validate="many_to_one")
    return land_maps,land_year,variability

def write_monthly(products):
    native,remapped,maps,regional,ensemble,loo=products
    DOCS.mkdir(exist_ok=True); PROCESSED.mkdir(parents=True,exist_ok=True); PUBLISHED.mkdir(parents=True,exist_ok=True)
    native.to_csv(DOCS/"phase6_monthly_native_differences.csv.gz",index=False,float_format="%.7f")
    maps.to_csv(DOCS/"phase6_monthly_common_grid.csv.gz",index=False,float_format="%.7f")
    regional.to_csv(DOCS/"phase6_domain_per_model.csv",index=False,float_format="%.7f")
    ensemble.to_csv(DOCS/"phase6_domain_ensemble.csv",index=False,float_format="%.7f")
    loo.to_csv(DOCS/"phase6_leave_one_model_out.csv",index=False,float_format="%.7f")
    key=ensemble[(ensemble.comparison=="G6solar - G6sulfur") & ensemble.domain.isin(["original_box","southeast_land","gulf_coast"])].copy()
    key.to_csv(DOCS/"phase6_key_results.csv",index=False,float_format="%.7f")
    weights=domain_weights(native,"original_box")[["model","grid_label","lat","lon","represented_area_km2"]]
    native_explorer=native.merge(weights,on=["model","grid_label","lat","lon"],validate="many_to_one")
    native_explorer=native_explorer[["model","comparison","season","metric","lat","lon","value","units","period","represented_area_km2"]].rename(columns={"represented_area_km2":"weight"}).assign(model_scope="Single model",model_count=1,domain="Original box",grid_kind="Native grid")
    ensemble_explorer=maps.rename(columns={"mean":"value"})
    ensemble_explorer=ensemble_explorer[["comparison","season","metric","lat","lon","value","units","period","model_count"]].assign(weight=lambda x:__import__('numpy').cos(__import__('numpy').deg2rad(x.lat)),model="Four-model ensemble",model_scope="Ensemble",domain="Original box",grid_kind="Common 1-degree grid")
    pd.concat([native_explorer,ensemble_explorer],ignore_index=True).to_csv(PUBLISHED/"phase6_explorer.csv.gz",index=False,float_format="%.7f")

def write_daily(products,yearly):
    land_maps,land_year,variability=products
    parquet=PUBLISHED/"phase6_daily_yearly_native.parquet"
    temporary=parquet.with_suffix(".parquet.tmp")
    yearly.to_parquet(temporary,index=False)
    if len(pd.read_parquet(temporary)) != len(yearly):
        raise RuntimeError("Year-level Parquet row-count verification failed")
    temporary.replace(parquet)
    land_maps.to_csv(DOCS/"phase6_daily_land_maps.csv.gz",index=False,float_format="%.7f")
    land_year.to_csv(DOCS/"phase6_daily_land_yearly.csv.gz",index=False,float_format="%.7f")
    variability.to_csv(DOCS/"phase6_daily_variability.csv",index=False,float_format="%.7f")
    climatology=land_year.groupby([c for c in land_year.columns if c not in {"period_year","value"}],dropna=False,as_index=False).value.mean()
    climatology.to_csv(DOCS/"phase6_daily_land_climatology.csv",index=False,float_format="%.7f")
    direct=[]
    climate=pd.read_parquet(PROCESSED/"phase6_daily_climatology_native.parquet")
    map_weights=domain_weights(climate,"southeast_land")[["model","grid_label","lat","lon","represented_area_km2"]]
    for metric in DAILY_PRIORITY:
      for season in ("ANN","JJA"):
       for comparison in COMPARISONS:
        values=matched_native_difference(climate,comparison,metric,season)
        values=values.merge(map_weights,on=["model","grid_label","lat","lon"],validate="many_to_one").rename(columns={"represented_area_km2":"weight"})
        direct.append(values[["model","comparison","season","metric","lat","lon","value","units","period","weight"]])
    daily_explorer=pd.concat(direct,ignore_index=True).assign(model_scope="Single model",model_count=1,domain="Southeast land-only",grid_kind="Native grid")
    explorer=PUBLISHED/"phase6_explorer.csv.gz"
    existing=pd.read_csv(explorer) if explorer.exists() else pd.DataFrame()
    pd.concat([existing,daily_explorer],ignore_index=True).to_csv(explorer,index=False,float_format="%.7f")

def main():
    p=argparse.ArgumentParser(); p.add_argument("--download",action="store_true"); p.add_argument("--stage",choices=["monthly","daily","all"],default="all"); a=p.parse_args()
    if a.stage in {"monthly","all"}:
      print("Building Phase 6 monthly native-grid cache",flush=True); monthly=build_monthly(a.download); monthly.to_parquet(PROCESSED/"phase6_monthly_native.parquet",index=False); write_monthly(monthly_products(monthly))
    if a.stage in {"daily","all"}:
      print("Building Phase 6 daily year-level cache",flush=True); climate,yearly=build_daily(a.download); climate.to_parquet(PROCESSED/"phase6_daily_climatology_native.parquet",index=False); write_daily(daily_products(climate,yearly),yearly)

if __name__=="__main__": main()
