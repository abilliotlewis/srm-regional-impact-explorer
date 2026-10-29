# Physical context and event identity checkpoint

Read [VALIDATION.md](VALIDATION.md) before interpreting these results. Event footprints and the tropical-track screen are not verified independent storms.

From the rainfall project directory, after downloading CPC data as described in `regional/README.md`:

```bash
python -m pip install -r requirements.txt -r regional/requirements.txt
python physical/download_inputs.py --out /path/to/physical_raw
python physical/physical_analysis.py \
  --cpc /path/to/cpc_raw \
  --hurdat /path/to/physical_raw/hurdat2-1851-2025.txt \
  --z500 /path/to/physical_raw/ncep_z500.nc
python -m unittest discover -s regional -p 'test_*.py' -v
python -m unittest discover -s physical -p 'test_*.py' -v
```

This reruns the regional calculation and verifies the tracked event catalog exactly matches the prior phase. NOAA HURDAT2 and CPC source data are downloaded externally. The monthly NCEP subset request is embedded in `download_inputs.py`; the subset covers 500 hPa, 10–70°N, 220–330°E, 1978–2025, at 2.5° resolution. Original files are not committed. Their SHA-256 values and URLs are in `output/source_manifest.csv`; provider updates can change results. Coastline coordinates are included as Natural Earth public-domain data and were obtained from https://github.com/nvkelso/natural-earth-vector/tree/master/geojson .
