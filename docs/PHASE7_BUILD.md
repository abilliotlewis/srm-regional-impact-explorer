# Phase 7 reproducible build

Phase 7 reuses the Phase 3 and 4 monthly ESGF manifests and the Phase 6 geographic definitions. Raw NetCDF files remain outside Git.

```bash
python -m pip install -r requirements.txt
python scripts/build_phase7.py --download
python scripts/make_phase7_figures.py
pytest
```

`build_phase7.py` verifies source byte counts, SHA-256 checksums, embedded experiment identity, variant, grid, tracking ID when available, and parent-run metadata. It then creates `data/processed/phase7_monthly_native_yearly.parquet`, an ignored resumable cache. A later run reuses this cache by default. Use `--rebuild-native` only when the source data or preparation code changes.

The default statistical build uses 10,000 circular moving-block bootstrap replicates and five-year blocks. A lower replicate count may be supplied only for development checks:

```bash
python scripts/build_phase7.py --bootstrap-replicates 200
```

Do not publish development outputs generated with fewer than 10,000 replicates. The committed per-model table records the replicate count and block length on every row.

The build writes:

- `data/published/phase7_monthly_regional_timeseries.csv.gz`
- `data/published/phase7_paired_differences.csv.gz`
- `docs/phase7_per_model_temporal_variability.csv`
- `docs/phase7_ensemble_temporal_summary.csv`
- `docs/phase7_block_length_sensitivity.csv`
- `docs/phase7_jja_tasmax_temporal_intervals.png`
- `docs/phase7_cross_result_robustness.png`

The versioned `data/reference_outputs_phase1_6.json` inventory and the full test suite verify that the Phase 1-6 scientific outputs remain byte-identical.
