# SRM Regional Impact Explorer

An open, reproducible starter project for comparing regional climate responses under solar radiation modification scenarios.

The current scientific question is:

> Do G6solar and G6sulfur produce different late-century Southeast U.S. daily heat, heavy-rainfall, and dry-spell responses relative to SSP5-8.5?

## Current status

Phase 5 provides a reproducible daily-extremes checkpoint from official CMIP6 archive data. The direct comparison uses daily `tasmax` and `pr` from MPI-ESM1-2-LR `r2i1p1f1` on its native `gn` grid for 2071-2100, with 1981-2010 historical data for percentile thresholds. It covers TXx, heatwave event count, heatwave frequency and duration, Rx1day, Rx5day, consecutive dry days, and R95pTOT. A federated archive audit found no second model with the complete matched daily experiment set, so Phase 5 is explicitly a single-model checkpoint, not an ensemble result.

Raw NetCDF files and the generated gridded analysis table stay outside Git. Exact source URLs, versions, tracking IDs, byte counts, SHA-256 checksums, licenses, variants, grids, and parent-run metadata are versioned in the repository.

The repository retains a deterministic synthetic-data generator for interface tests. The app clearly identifies whether its active records are synthetic or model-derived.

## Current result

In MPI-ESM1-2-LR, annual TXx is 1.986°C lower under G6solar and 1.651°C lower under G6sulfur relative to SSP5-8.5. G6solar also has 46.689 fewer annual heatwave days and a 10.684-day shorter longest annual heatwave than G6sulfur.

The hydroclimate result is less uniform. Relative to SSP5-8.5, both interventions reduce annual Rx1day, Rx5day, and R95pTOT in this run, with larger reductions under G6sulfur. G6solar has shorter dry spells than G6sulfur in every season, but the G6solar-minus-G6sulfur Rx5day difference reverses sign in JJA. Near-zero JJA Rx1day and R95pTOT differences provide little separation between interventions.

![Daily heat-extreme responses](docs/phase5_heat_extremes.png)

See [the Phase 5 checkpoint](docs/PHASE5_CHECKPOINT.md) for definitions, every seasonal comparison, validation, and limitations, and [the Phase 5 model-selection log](docs/PHASE5_MODEL_SELECTION.md) for the archive audit. [Phase 4](docs/PHASE4_CHECKPOINT.md) remains the matched four-model monthly precipitation checkpoint, [Phase 3](docs/PHASE3_CHECKPOINT.md) remains the matched four-model temperature checkpoint, and [Phase 2](docs/PHASE2_CHECKPOINT.md) remains the historical two-model result.

## Current experiments

- `ssp585`: high-forcing reference scenario
- `G6solar`: solar-irradiance reduction against the SSP5-8.5 background
- `G6sulfur`: stratospheric sulfate intervention against the SSP5-8.5 background

The deterministic demonstration generator and historical temperature manifests also retain `ssp245`, but it is not part of the Phase 5 direct comparison.

## Current metrics

- `tasmax_mean`: mean daily maximum near-surface air temperature
- `pr_mean`: mean precipitation rate
- `txx`: maximum daily maximum temperature
- `hwn_tx90_3d`: heatwave event count above historical TX90, three-day minimum
- `hwf_tx90_3d`: days participating in those heatwaves
- `hwd_tx90_3d`: longest qualifying heatwave
- `rx1day`: maximum one-day precipitation
- `rx5day`: maximum consecutive five-day precipitation
- `cdd`: maximum consecutive dry days below 1 mm/day
- `r95ptot`: precipitation on days above the historical wet-day 95th percentile

## Quick start

```bash
python -m pip install -r requirements.txt
python app.py
```

The app uses the real processed table when present. If it is missing, the app creates a deterministic demonstration CSV automatically. Run `python scripts/generate_demo_data.py` directly when you want to regenerate the demonstration data.

Run tests:

```bash
pytest
```

## Replace the demonstration data

The real-data manifests contain the matched monthly Phase 4 files and the daily MPI-ESM1-2-LR files used for Phase 5. Download, verify, process, and reproduce the current tables and figures with:

```bash
python scripts/build_phase5.py --download
python scripts/make_phase3_outputs.py
python scripts/make_phase4_outputs.py
python scripts/make_phase5_outputs.py
```

The downloader validates every file against its recorded byte count and SHA-256 checksum before the analysis begins. The build also checks embedded experiment, model, variant, grid, tracking, and parent metadata. Raw NetCDF and the gridded processed CSV remain untracked by Git; compact regional result tables are versioned under `docs/`.

For other models or variables:

1. Resolve exact files and checksums through the ESGF Search API.
2. Add a versioned manifest under `data/manifests/`.
3. Place downloaded files under `data/raw/`.
4. Use `scripts/prepare_geomip.py` to convert gridded climatologies to the explorer schema.
5. Write the combined file to `data/processed/regional_metrics.csv` with `is_demo=false`.

See [docs/DATA_PLAN.md](docs/DATA_PLAN.md) for variables, time periods, quality checks, and publication criteria.

## Repository structure

```text
app.py                         Gradio application
src/srm_explorer/analysis.py  Data loading, validation, summaries, plots
scripts/generate_demo_data.py Deterministic demonstration data generator
scripts/prepare_geomip.py     NetCDF-to-explorer preprocessing starter
scripts/download_manifest.py  Checksum-verifying ESGF downloader
scripts/build_phase1.py        Reusable single-variable validated build
scripts/build_phase4.py        Matched two-variable Phase 4 build
scripts/build_phase5.py        Matched daily-extremes Phase 5 build
scripts/prepare_daily_extremes.py Daily index calculation on native grids
scripts/make_phase3_outputs.py Phase 3 regional tables and figures
scripts/make_phase4_outputs.py Phase 4 precipitation tables and figures
scripts/make_phase5_outputs.py Phase 5 extremes table and figures
data/manifests/                Versioned source records and checksums
data/processed/               Generated or explorer-ready tables
docs/DATA_PLAN.md             Real-data acquisition and validation plan
docs/PHASE1_RESULT.md         First result, method, and limitations
docs/PHASE2_CHECKPOINT.md      Two-model checkpoint and limitations
docs/PHASE3_MODEL_SELECTION.md Model inclusion and exclusion audit
docs/PHASE3_CHECKPOINT.md      Four-model results, uncertainty, and limits
docs/PHASE4_MODEL_SELECTION.md Precipitation selection and provenance audit
docs/PHASE4_CHECKPOINT.md      Matched precipitation results and uncertainty
docs/PHASE5_MODEL_SELECTION.md Daily-data selection and exclusion audit
docs/PHASE5_CHECKPOINT.md      Daily-extremes result and limitations
tests/                         Automated checks
```

## Scientific guardrails

- Always display whether records are synthetic or model-derived.
- Preserve model identity instead of presenting an ensemble mean alone.
- Report spread and model count with every multi-model result.
- Label single-model results explicitly and do not calculate meaningless ensemble spread.
- Match variants and parent branches explicitly; never substitute an ensemble member silently.
- Calculate regional means on native grids before combining models.
- Do not treat `G6solar` as a complete engineering representation of satellite mirrors. It is a climate-model experiment based on reduced solar irradiance.
- Distinguish equal global forcing targets from equal regional outcomes.

## Suggested public title

**Regional Climate Responses to Solar Intervention: Comparing G6solar and G6sulfur over the Southeast United States**
