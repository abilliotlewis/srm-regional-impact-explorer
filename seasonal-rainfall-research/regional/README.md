# Regional rainfall pilot

This exploratory analysis counts CPC precipitation footprints in Louisiana, Mississippi, Alabama, Georgia, and Florida. **Its event labels are provisional and do not establish independent storms.** Read [RESULTS.md](RESULTS.md) for definitions, results, uncertainty, and limitations.

## Reproduce

From the rainfall project directory, with Python 3.10+:

```bash
python -m pip install -r requirements.txt
python -m pip install -r regional/requirements.txt
python regional/download_data.py --raw /path/to/cpc_raw
python regional/run_regional.py --raw /path/to/cpc_raw
python regional/conditional_analysis.py
python -m unittest discover -s regional -p 'test_*.py' -v
```

The downloader acquires 48 full CONUS NetCDFs, about 500 MB. Keep them outside Git. `output/source_manifest.csv` records exact URLs, sizes and SHA-256 hashes of the files used for the published results; if a source changes, rerunning may yield different results. The code checks each year has its complete daily time coordinate. The included `states.geojson` is a five-state subset of Natural Earth 1:110m boundaries, distributed in public domain by Natural Earth and sourced via https://datahub.io/core/geo-boundaries-us-110m . Center points determine state membership and are approximate near coastlines and state borders.

The raw inputs combine the CPC historical product through 2006 and its real-time product beginning 2007. The supplied ENSO SST values are retrospectively revised and are not an archive of what was available at each forecast issuance. All intervals and model comparisons are exploratory. See [RESULTS.md](RESULTS.md).
