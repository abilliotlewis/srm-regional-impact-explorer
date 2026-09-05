"""Fetch and subset the versioned boundary inputs used by Phase 6."""
import hashlib, io, json, zipfile
from pathlib import Path
import httpx, shapefile
from shapely.geometry import box, mapping, shape
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/"data/raw/geography"; OUTPUT=ROOT/"data/geography"; BOX=box(-100,24,-74,38)
STATE_CODES={"AL","AR","FL","GA","KY","LA","MS","NC","OK","SC","TN","TX","VA","WV"}
SOURCES={
"states":{"url":"https://www2.census.gov/geo/tiger/GENZ2025/shp/cb_2025_us_state_20m.zip","sha256":"9340b6d995e971b2b4230518f4fa85e6cd9e7fe6811afabc90a6a8b1191530f6","filename":"cb_2025_us_state_20m.zip","base":"cb_2025_us_state_20m"},
"land":{"url":"https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip","sha256":"e547d749445eaa0964aba76738090ec88f5e63c4585122170f98c67a7ea922dc","filename":"ne_10m_land.zip","base":"ne_10m_land"}}
def sha256(path):
 d=hashlib.sha256()
 with path.open("rb") as s:
  for c in iter(lambda:s.read(1024*1024),b""):d.update(c)
 return d.hexdigest()
def fetch(name):
 r=SOURCES[name]; RAW.mkdir(parents=True,exist_ok=True); p=RAW/r["filename"]
 if not p.exists():
  with httpx.stream("GET",r["url"],follow_redirects=True,timeout=120) as response:
   response.raise_for_status()
   with p.open("wb") as f:
    for c in response.iter_bytes():f.write(c)
 if sha256(p)!=r["sha256"]:raise ValueError(f"Checksum mismatch for {p.name}")
 return p
def reader(path,base):
 with zipfile.ZipFile(path) as a:return shapefile.Reader(shp=io.BytesIO(a.read(f"{base}.shp")),shx=io.BytesIO(a.read(f"{base}.shx")),dbf=io.BytesIO(a.read(f"{base}.dbf")))
def write_geojson():
 OUTPUT.mkdir(parents=True,exist_ok=True); r=SOURCES["states"]; states=reader(fetch("states"),r["base"]); features=[]
 for item in states.iterShapeRecords():
  rec=item.record.as_dict()
  if rec["STUSPS"] in STATE_CODES:features.append({"type":"Feature","properties":{"state":rec["STUSPS"],"name":rec["NAME"],"statefp":rec["STATEFP"]},"geometry":mapping(shape(item.shape.__geo_interface__).intersection(BOX))})
 collection={"type":"FeatureCollection","metadata":{"source":"U.S. Census Bureau 2025 Cartographic Boundary Files, states, 1:20,000,000","url":r["url"],"source_sha256":r["sha256"],"selection":sorted(STATE_CODES),"clip":[-100,24,-74,38]},"features":features}
 (OUTPUT/"southeast_states_2025.geojson").write_text(json.dumps(collection,separators=(",",":"))+"\n")
 r=SOURCES["land"]; land=reader(fetch("land"),r["base"]); features=[]
 for item in land.iterShapeRecords():
  g=shape(item.shape.__geo_interface__)
  if g.intersects(BOX):
   g=g.intersection(BOX)
   if not g.is_empty:features.append({"type":"Feature","properties":{},"geometry":mapping(g)})
 collection={"type":"FeatureCollection","metadata":{"source":"Natural Earth 10m Physical Vectors, Land, version 5.1.1","url":r["url"],"source_sha256":r["sha256"],"clip":[-100,24,-74,38]},"features":features}
 (OUTPUT/"natural_earth_land_10m_southeast.geojson").write_text(json.dumps(collection,separators=(",",":"))+"\n")
if __name__=="__main__":write_geojson()
