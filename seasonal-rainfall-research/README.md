# Seasonal clustering of extreme rainfall

Exploratory research on whether extreme rainfall episodes cluster within seasons in the southeastern United States and whether climate conditions improve forecasts of multiple-event seasons.

## Current status

This repository contains a preliminary station-level pilot and an exploratory five-state gridded episode analysis, not a validated independent-storm catalog. See [REPORT.md](REPORT.md) for methods, findings, limitations, references, and the plan for future work. The six station records do not identify distinct storms across a region. The rare-event forecast comparison has no positive outcomes in the test period and is inconclusive.

The regional episode analysis is documented in [regional/RESULTS.md](regional/RESULTS.md). The new [storm identity and circulation checkpoint](physical/VALIDATION.md) adds case audits, tropical-track sensitivity, a coastal split, and retrospective reanalysis composites. Both are exploratory.

## Contents

- `physical/`: event-identity audits, tropical-cyclone proximity sensitivity, and atmospheric composites.
- `regional/`: gridded event definitions, seasonal summaries, exploratory hindcasts, and source manifest.
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
