"""Matched native-grid differences and documented Phase 6 remapping."""
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from .geography import grid_cells, spherical_rectangle_area_km2
COMMON_LATS=np.arange(24.5,38.0,1.0); COMMON_LONS=np.arange(-99.5,-74.0,1.0)

def matched_native_difference(frame,comparison,metric,season):
    pairs={"G6solar - SSP5-8.5":("G6solar","ssp585"),"G6sulfur - SSP5-8.5":("G6sulfur","ssp585"),"G6solar - G6sulfur":("G6solar","G6sulfur")}
    if comparison not in pairs: raise ValueError(f"Unknown comparison: {comparison}")
    tn,rn=pairs[comparison]; selected=frame[(frame.metric==metric)&(frame.season==season)]; target=selected[selected.scenario==tn].copy(); reference=selected[selected.scenario==rn].copy()
    if target.empty or reference.empty: raise ValueError(f"Unavailable comparison {comparison} for {metric} {season}")
    identity=["model","grid_label","lat","lon"]
    cols=["model","variant_label","grid_label","parent_experiment_id","parent_variant_label"]
    branches=target[cols].drop_duplicates().merge(reference[cols].drop_duplicates(),on="model",suffixes=("","_reference"),validate="one_to_one")
    direct=(branches.parent_experiment_id==rn)&(branches.parent_variant_label==branches.variant_label_reference)&(branches.variant_label==branches.variant_label_reference)
    common=(branches.parent_experiment_id==branches.parent_experiment_id_reference)&(branches.parent_variant_label==branches.parent_variant_label_reference)&(branches.variant_label==branches.variant_label_reference)
    bad=branches[~(direct|common)|(branches.grid_label!=branches.grid_label_reference)]
    if not bad.empty: raise ValueError("Incompatible experiment branches: "+", ".join(bad.model))
    keep=[c for c in target.columns if c not in {"value","scenario"}]
    merged=target[keep+["value"]].merge(reference[identity+["value"]].rename(columns={"value":"reference_value"}),on=identity,validate="one_to_one")
    merged["value"]=merged.value-merged.reference_value; merged["comparison"]=comparison
    return merged.drop(columns="reference_value")

def _common_cells():
    return pd.DataFrame([{"lat":a,"lon":o,"lat_lower":a-.5,"lat_upper":a+.5,"lon_lower":o-.5,"lon_upper":o+.5} for a in COMMON_LATS for o in COMMON_LONS])

def bilinear_regrid(values):
    lats=np.sort(values.lat.unique()); lons=np.sort(values.lon.unique()); field=values.pivot(index="lat",columns="lon",values="value").loc[lats,lons]
    interp=RegularGridInterpolator((lats,lons),field.values,method="linear",bounds_error=False,fill_value=np.nan); target=_common_cells(); target["value"]=interp(target[["lat","lon"]].to_numpy()); return target.dropna(subset=["value"])

def conservative_regrid(values,minimum_coverage=.99):
    source=grid_cells(values).merge(values[["lat","lon","value"]],on=["lat","lon"],validate="one_to_one"); rows=[]
    for t in _common_cells().to_dict("records"):
        ta=spherical_rectangle_area_km2(t["lon_lower"],t["lat_lower"],t["lon_upper"],t["lat_upper"]); num=covered=0.0
        candidates=source[(source.lon_upper>t["lon_lower"])&(source.lon_lower<t["lon_upper"])&(source.lat_upper>t["lat_lower"])&(source.lat_lower<t["lat_upper"])]
        for x in candidates.to_dict("records"):
            area=spherical_rectangle_area_km2(max(t["lon_lower"],x["lon_lower"]),max(t["lat_lower"],x["lat_lower"]),min(t["lon_upper"],x["lon_upper"]),min(t["lat_upper"],x["lat_upper"])); num+=x["value"]*area; covered+=area
        if covered/ta>=minimum_coverage: rows.append({**t,"value":num/ta,"coverage":covered/ta})
    return pd.DataFrame(rows)

def regrid_native_differences(native,metric):
    method="bilinear" if metric=="tasmax_mean" else "first_order_conservative"; frames=[]
    for (model,variant,grid),group in native.groupby(["model","variant_label","grid_label"],sort=True):
        r=bilinear_regrid(group) if metric=="tasmax_mean" else conservative_regrid(group)
        frames.append(r.assign(model=model,variant_label=variant,grid_label=grid,metric=metric,season=group.season.iloc[0],comparison=group.comparison.iloc[0],regridding_method=method))
    return pd.concat(frames,ignore_index=True)

def ensemble_grid_statistics(remapped):
    group=["metric","season","comparison","lat","lon","regridding_method"]
    out=remapped.groupby(group,as_index=False).value.agg(mean="mean",median="median",std="std",minimum="min",maximum="max",model_count="size",positive_count=lambda v:int((v>0).sum()),negative_count=lambda v:int((v<0).sum()),zero_count=lambda v:int((v==0).sum()))
    out["std"]=out["std"].fillna(0); out["sign_agreement"]=out[["positive_count","negative_count"]].max(axis=1)/out.model_count; return out
