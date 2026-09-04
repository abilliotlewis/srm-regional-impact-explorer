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

This repository currently contains deterministic synthetic records used to develop and test the SRM Regional Impact Explorer.

## Critical status

`data/processed/regional_metrics.csv` is not observational or modeled climate data. Every included row has `is_demo=true` and `period=DEMONSTRATION ONLY`.

## Intended replacement dataset

The production dataset will contain traceable regional climatologies and indices derived from matched GeoMIP/CMIP6 models for `ssp585`, `ssp245`, `G6solar`, and `G6sulfur`.

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

## Limitations

G6solar is an idealized solar-irradiance experiment. It is useful for studying Earth-system response to reduced incoming sunlight, but it does not represent the engineering, orbital geometry, control behavior or failure modes of a particular satellite-mirror design.

