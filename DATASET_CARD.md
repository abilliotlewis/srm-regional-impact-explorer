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

The Phase 5 model-derived build adds daily extremes from MPI-ESM1-2-LR `r2i1p1f1` on `gn` for G6solar, G6sulfur, and SSP5-8.5 during 2071-2100. Historical data from 1981-2010 supply model-specific percentile thresholds. Metrics include TXx, TX90 heatwave event count, heatwave days, longest heatwave duration, Rx1day, Rx5day, consecutive dry days, and R95pTOT. The federated availability audit found only this one complete matched daily model, so the daily result does not represent an ensemble.

The build retains the Phase 4 monthly `tasmax` and `pr` sample from CNRM-ESM2-1, IPSL-CM6A-LR, MPI-ESM1-2-LR, and UKESM1-0-LL. The gridded derived CSV is generated locally and is not committed to Git. Compact regional tables are versioned under `docs/`, and exact source records and checksums are stored under `data/manifests/`.

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

The daily-extremes release contains one model and one ensemble member. It cannot quantify structural model uncertainty, internal variability, statistical significance, or observational bias. Seasonal spells and five-day windows are truncated at period boundaries.
