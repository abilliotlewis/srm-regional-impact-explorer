---
pretty_name: SRM Regional Impact Explorer Data
license: other
task_categories:
  - tabular-regression
tags:
  - climate
  - geomip
  - solar-radiation-modification
  - geospatial
---

# SRM Regional Impact Explorer Data

This repository defines a reproducible workflow for regional climatologies derived from official ESGF-hosted GeoMIP/CMIP6 output. It also contains a deterministic synthetic-data generator used for interface tests.

## Current release status

The Phase 3 model-derived build covers monthly `tasmax` from CNRM-ESM2-1 `r1i1p1f2`, IPSL-CM6A-LR `r1i1p1f1`, MPI-ESM1-2-LR `r2i1p1f1`, and UKESM1-0-LL `r1i1p1f2` for G6solar, G6sulfur, and SSP5-8.5 during 2071–2100. The gridded derived CSV is generated locally and is not committed to Git. Compact per-model and ensemble regional tables are versioned under `docs/`. Exact source records and checksums are stored under `data/manifests/`.

Source licenses differ by institution. CNRM-CERFACS and IPSL files state CC BY-NC-SA 4.0; MPI-M and MOHC files state CC BY-SA 4.0. Consult each manifest and the NetCDF global attributes before redistribution.

Records generated from `scripts/generate_demo_data.py` have `is_demo=true` and `period=DEMONSTRATION ONLY`. They are not observational or modeled climate data.

## Columns

| Column | Description |
| --- | --- |
| `model` | Earth system model or clearly marked demonstration model |
| `scenario` | CMIP/GeoMIP experiment identifier |
| `variant_label` | Exact CMIP6 ensemble-member label |
| `grid_label` | Exact CMIP6 grid label |
| `parent_experiment_id` | Parent experiment recorded in the source file |
| `parent_variant_label` | Parent variant recorded in the source file |
| `season` | ANN, DJF, MAM, JJA or SON |
| `metric` | Climate indicator identifier |
| `lat`, `lon` | Grid-cell coordinates |
| `value` | Metric value |
| `units` | Physical units |
| `period` | Climatological period or demonstration marker |
| `is_demo` | Provenance safety flag |
| `dataset_key` | Versioned source-dataset identifier when model-derived |

## Limitations

G6solar is an idealized solar-irradiance experiment. It is useful for studying Earth-system response to reduced incoming sunlight, but it does not represent the engineering, orbital geometry, control behavior or failure modes of a particular satellite-mirror design.
