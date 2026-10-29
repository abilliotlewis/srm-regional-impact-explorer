# Seasonal clustering of extreme rainfall

Exploratory research on whether extreme rainfall episodes cluster within seasons in the southeastern United States and whether climate conditions improve forecasts of multiple-event seasons.

## Current status

This repository contains a **preliminary station-level winter pilot**, not a completed regional storm-tracking study. See [REPORT.md](REPORT.md) for methods, findings, limitations, references, and the plan for future work. The six station records do not identify distinct storms across a region. The rare-event forecast comparison has no positive outcomes in the test period and is inconclusive.

## Contents

- `analysis.py`: analysis of GHCN-Daily station records and November Niño 3.4 SST.
- `data/`: gzip-compressed frozen NOAA station observations and checksums.
- `output/`: pilot result tables, forecast scores, and an exploratory figure.
- `REPORT.md`: literature review, pilot report, and further research plan.

## Reproduce the pilot

Use Python 3.10 or later. Install the packages listed in `requirements.txt`, then run:

```sh
python -m pip install -r requirements.txt
python analysis.py
```

The script writes results to `output/`. Input files were retrieved on October 29, 2026. The random seed is 1783. See the report before interpreting the results and for original data sources.
