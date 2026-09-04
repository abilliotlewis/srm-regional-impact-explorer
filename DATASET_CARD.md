---
pretty_name: SRM Regional Impact Explorer Data
license: cc-by-4.0
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

The first model-derived build covers monthly `tasmax` from IPSL-CM6A-LR realization `r1i1p1f1` for G6solar, G6sulfur, SSP5-8.5, and SSP2-4.5 during 2071–2100. The derived CSV is generated locally and is not committed to Git. Exact source records and checksums are stored in `data/manifests/ipsl_tasmax_amon.json`.

Records generated from `scripts/generate_demo_data.py` have `is_demo=true` and `period=DEMONSTRATION ONLY`. They are not observational or modeled climate data.

## Intended expansion

The next release will add matched models for `ssp585`, `ssp245`, `G6solar`, and `G6sulfur`, then expand to precipitation and daily extremes.

## Columns

| Column | Description |
| --- | --- |
| `model` | Earth system model or clearly marked demonstration model |
| `scenario` | CMIP/GeoMIP experiment identifier |
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
