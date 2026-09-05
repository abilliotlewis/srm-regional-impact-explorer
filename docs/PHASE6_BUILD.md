# Reproducing Phase 6

Install and validate:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

Regenerate boundaries:

```bash
python scripts/fetch_phase6_geography.py
```

Build from already verified raw files:

```bash
python scripts/build_phase6.py --stage monthly
python scripts/build_phase6.py --stage daily
python scripts/make_phase6_outputs.py
```

Add `--download` to a build stage only when its manifest-controlled raw files are absent. The downloader resumes from valid cached files and rejects incorrect byte counts or SHA-256 checksums.

Monthly and daily stages are separate resumable checkpoints. The monthly stage writes native-grid differences, common-grid ensemble maps, fractional-area domain summaries, leave-one-model-out results, and the initial explorer data. The daily stage writes the compact year-level Parquet file, land-only summaries, variability estimates, and appends available daily displays.

The common spatial display grid has 1° cells centered at 24.5-37.5°N and 99.5-74.5°W. Matched differences are computed before regridding. `tasmax` uses bilinear interpolation; precipitation uses first-order area-conservative remapping with at least 99% target-cell coverage. Regional tables never use the common grid.

Daily uncertainty intervals use 2,000 independent circular moving-block bootstrap resamples with five-year blocks. The two experiment series are resampled independently because matching nominal years does not synchronize weather. These intervals characterize temporal sampling variability within one model-member simulation, not structural model uncertainty. Grid cells are not treated as replicates.

