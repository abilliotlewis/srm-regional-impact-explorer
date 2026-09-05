"""Versioned Phase 6 domains and fractional native-grid area weights."""
from functools import lru_cache
import json
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Geod
from shapely.geometry import box, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
GEOGRAPHY_DIR = ROOT / "data/geography"
GEOD = Geod(ellps="WGS84")
EARTH_RADIUS_KM = 6371.0088
ORIGINAL_BOX = (-100.0, 24.0, -74.0, 38.0)
DOMAIN_STATES = {
    "southeast_land": {"AL","AR","FL","GA","KY","LA","MS","NC","OK","SC","TN","TX","VA","WV"},
    "gulf_coast": {"TX","LA","MS","AL","FL"},
    "lower_mississippi": {"AR","LA","MS","TN"},
    "atlantic_southeast": {"FL","GA","SC","NC","VA"},
    "appalachian_interior": {"KY","TN","WV","VA"},
}
DOMAIN_LABELS = {
    "original_box": "Original 24-38°N, 100-74°W box",
    "southeast_land": "Southeast land-only", "gulf_coast": "Gulf Coast states",
    "lower_mississippi": "Lower Mississippi Valley states",
    "atlantic_southeast": "Atlantic Southeast states",
    "appalachian_interior": "Appalachian and interior states",
}

def _read_geojson(path): return json.loads(path.read_text())

@lru_cache(maxsize=1)
def state_geometries():
    c=_read_geojson(GEOGRAPHY_DIR/"southeast_states_2025.geojson")
    return {f["properties"]["state"]:shape(f["geometry"]) for f in c["features"]}

@lru_cache(maxsize=1)
def land_geometry():
    c=_read_geojson(GEOGRAPHY_DIR/"natural_earth_land_10m_southeast.geojson")
    return unary_union([shape(f["geometry"]) for f in c["features"]])

@lru_cache(maxsize=None)
def domain_geometry(domain):
    study=box(*ORIGINAL_BOX)
    if domain=="original_box": return study
    if domain not in DOMAIN_STATES: raise ValueError(f"Unknown Phase 6 domain: {domain}")
    states=state_geometries(); missing=DOMAIN_STATES[domain].difference(states)
    if missing: raise ValueError(f"Missing state boundaries for {sorted(missing)}")
    return unary_union([states[c] for c in DOMAIN_STATES[domain]]).intersection(land_geometry()).intersection(study)

def geodesic_area_km2(geometry):
    if geometry.is_empty: return 0.0
    area,_=GEOD.geometry_area_perimeter(geometry)
    return abs(float(area))/1_000_000.0

def spherical_rectangle_area_km2(lon_lower,lat_lower,lon_upper,lat_upper):
    return float(EARTH_RADIUS_KM**2*np.deg2rad(lon_upper-lon_lower)*(np.sin(np.deg2rad(lat_upper))-np.sin(np.deg2rad(lat_lower))))

def coordinate_bounds(centers):
    values=np.asarray(centers,dtype=float)
    if values.ndim!=1 or values.size<2 or not np.all(np.diff(values)>0):
        raise ValueError("Grid centers must be a strictly increasing one-dimensional array")
    mids=(values[:-1]+values[1:])/2
    edges=np.concatenate(([values[0]-(mids[0]-values[0])],mids,[values[-1]+(values[-1]-mids[-1])]))
    return np.column_stack([edges[:-1],edges[1:]])

def grid_cells(values):
    identity=[c for c in ("model","grid_label") if c in values]
    frames=[]; grouped=values.groupby(identity,sort=True) if identity else [((),values)]
    for keys,group in grouped:
        kv=keys if isinstance(keys,tuple) else (keys,); key=dict(zip(identity,kv,strict=True))
        lats=np.sort(group.lat.unique()); lons=np.sort(group.lon.unique())
        lat_map=dict(zip(lats,coordinate_bounds(lats),strict=True)); lon_map=dict(zip(lons,coordinate_bounds(lons),strict=True))
        cells=group[["lat","lon"]].drop_duplicates().copy()
        bc={"lat_lower","lat_upper","lon_lower","lon_upper"}
        if bc.issubset(group) and group[list(bc)].notna().all().all():
            explicit=group[["lat","lon","lat_lower","lat_upper","lon_lower","lon_upper"]].drop_duplicates(["lat","lon"])
            cells=cells.merge(explicit,on=["lat","lon"],validate="one_to_one")
        else:
            cells["lat_lower"]=cells.lat.map(lambda x:lat_map[x][0]); cells["lat_upper"]=cells.lat.map(lambda x:lat_map[x][1])
            cells["lon_lower"]=cells.lon.map(lambda x:lon_map[x][0]); cells["lon_upper"]=cells.lon.map(lambda x:lon_map[x][1])
        for c,v in key.items(): cells[c]=v
        frames.append(cells)
    return pd.concat(frames,ignore_index=True)

def domain_weights(values,domain):
    geometry=domain_geometry(domain); cells=grid_cells(values); rows=[]
    identity=[c for c in ("model","grid_label") if c in cells]
    for r in cells.to_dict("records"):
        cell=box(r["lon_lower"],r["lat_lower"],r["lon_upper"],r["lat_upper"])
        ca=geodesic_area_km2(cell); represented=geodesic_area_km2(cell.intersection(geometry))
        if represented<=0: continue
        row={c:r[c] for c in identity}; row.update(lat=r["lat"],lon=r["lon"],domain=domain,cell_area_km2=ca,represented_area_km2=represented,region_fraction=min(1.0,represented/ca)); rows.append(row)
    if not rows: raise ValueError(f"No grid cells overlap domain {domain}")
    return pd.DataFrame(rows)

def weighted_domain_means(values,domain):
    weights=domain_weights(values,domain); join=[c for c in ("model","grid_label","lat","lon") if c in values]
    merged=values.merge(weights,on=join,validate="many_to_one"); merged["weighted_value"]=merged.value*merged.represented_area_km2
    identity=[c for c in ("model","variant_label","grid_label","scenario","comparison","season","metric","units","period","period_year","calendar") if c in merged]
    out=merged.groupby(identity,as_index=False).agg(weighted_value=("weighted_value","sum"),represented_area_km2=("represented_area_km2","sum"),contributing_cells=("represented_area_km2","size"),equivalent_cells=("region_fraction","sum"))
    out["value"]=out.weighted_value/out.represented_area_km2; out["domain"]=domain
    return out.drop(columns="weighted_value")
