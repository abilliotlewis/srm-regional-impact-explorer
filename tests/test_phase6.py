from pathlib import Path
import hashlib,json,sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from srm_explorer.analysis import available_phase6_selections,phase6_selection
from srm_explorer.geography import coordinate_bounds,domain_geometry,domain_weights,weighted_domain_means
from srm_explorer.spatial import bilinear_regrid,conservative_regrid,ensemble_grid_statistics,matched_native_difference
from srm_explorer.uncertainty import independent_difference_interval,moving_block_means

def simple_grid(value=1.0):
 return pd.DataFrame({"model":["M"]*4,"grid_label":["gn"]*4,"lat":[25,25,37,37],"lon":[-99,-75,-99,-75],"value":[value]*4})

def test_coordinate_bounds_are_inferred_from_centers():
 assert np.allclose(coordinate_bounds([0,2,4]),[[-1,1],[1,3],[3,5]])

def test_original_box_weights_have_positive_area_and_fractions():
 w=domain_weights(simple_grid(),"original_box"); assert (w.represented_area_km2>0).all(); assert w.region_fraction.between(0,1).all()

def test_land_domain_is_clipped_to_original_box():
 assert domain_geometry("southeast_land").within(domain_geometry("original_box"))

def test_weighted_domain_mean_uses_fractional_cell_area():
 x=simple_grid(); x["value"]=[0,10,0,10]; result=weighted_domain_means(x,"original_box"); assert 0<result.value.iloc[0]<10

def test_bilinear_regridding_preserves_constant_field():
 x=pd.DataFrame([{"lat":lat,"lon":lon,"value":3.0} for lat in [23.5,38.5] for lon in [-100.5,-73.5]])
 assert np.allclose(bilinear_regrid(x).value,3)

def test_conservative_regridding_preserves_constant_field():
 x=pd.DataFrame([{"lat":lat,"lon":lon,"value":2.0} for lat in np.arange(23.5,39,1) for lon in np.arange(-100.5,-73,1)])
 assert np.allclose(conservative_regrid(x).value,2)

def test_ensemble_counts_and_signs_are_explicit():
 x=pd.DataFrame({"metric":["m"]*3,"season":["JJA"]*3,"comparison":["c"]*3,"lat":[1]*3,"lon":[2]*3,"regridding_method":["x"]*3,"value":[-2,-1,1]})
 r=ensemble_grid_statistics(x).iloc[0]; assert (r.model_count,r.positive_count,r.negative_count)==(3,1,2); assert np.isclose(r.sign_agreement,2/3)

def test_matched_difference_rejects_variant_mixing():
 rows=[]
 for scenario,value,variant,parent in [("ssp585",0,"r1","historical"),("G6solar",1,"r2","ssp585")]: rows.append(dict(model="M",scenario=scenario,variant_label=variant,grid_label="gn",parent_experiment_id=parent,parent_variant_label="r1",metric="m",season="JJA",lat=30,lon=-85,value=value))
 try: matched_native_difference(pd.DataFrame(rows),"G6solar - SSP5-8.5","m","JJA")
 except ValueError as e: assert "Incompatible" in str(e)
 else: raise AssertionError("variant mismatch accepted")

def test_matched_difference_counts_only_common_models():
 rows=[]
 for scenario,value,parent in [("ssp585",1,"historical"),("G6solar",3,"ssp585")]: rows.append(dict(model="M",scenario=scenario,variant_label="r1",grid_label="gn",parent_experiment_id=parent,parent_variant_label="r1",metric="m",season="JJA",lat=30,lon=-85,value=value))
 result=matched_native_difference(pd.DataFrame(rows),"G6solar - SSP5-8.5","m","JJA"); assert len(result)==1 and result.value.iloc[0]==2

def test_unavailable_explorer_selection_is_rejected():
 x=pd.DataFrame({"model":["M"],"metric":["m"],"season":["JJA"],"comparison":["a"],"value":[1]}); assert available_phase6_selections(x)==[("M","m","JJA","a")]
 try: phase6_selection(x,"M","m","DJF","a")
 except ValueError as e: assert "Unavailable" in str(e)
 else: raise AssertionError("unavailable selection accepted")

def test_block_bootstrap_is_reproducible_and_keeps_length():
 a=moving_block_means(np.arange(10),replicates=20,seed=9); b=moving_block_means(np.arange(10),replicates=20,seed=9); assert len(a)==20 and np.array_equal(a,b)

def test_independent_interval_does_not_pair_calendar_year_weather():
 r=independent_difference_interval(np.arange(30),np.arange(30)+1,"test",replicates=50); assert r["difference"]==-1 and r["target_years"]==30

def test_phase3_to_5_reference_outputs_are_unchanged():
 expected=json.loads((ROOT/"data/reference_outputs_phase3_5.json").read_text())
 for name,digest in expected.items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
 ensemble=pd.read_csv(ROOT/"docs/phase6_domain_ensemble.csv"); assert len(ensemble)==180 and set(ensemble.model_count)=={4}
 explorer=pd.read_csv(ROOT/"data/published/phase6_explorer.csv.gz"); assert (explorer.weight>0).all(); assert {"Ensemble","Single model"}==set(explorer.model_scope)
 yearly=pd.read_parquet(ROOT/"data/published/phase6_daily_yearly_native.parquet"); assert len(yearly)==668712; assert yearly.groupby("season").period_year.nunique().to_dict()["DJF"]==29
