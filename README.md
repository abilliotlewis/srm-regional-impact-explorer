# SRM Regional Impact Explorer

An open, reproducible starter project for comparing regional climate responses under solar radiation modification scenarios.

The first scientific question is:

> How do solar-irradiance reduction and stratospheric aerosol intervention differ in their effects on Southeast US heat and precipitation indicators?

## Current status

The project now has a reproducible two-model checkpoint from official ESGF-hosted data. The comparison uses monthly `tasmax` from IPSL-CM6A-LR and MPI-ESM1-2-LR for 2071–2100. Raw NetCDF files and the generated analysis table stay outside Git, while exact source URLs, versions, byte counts, SHA-256 checksums, licenses, and parent-run metadata are versioned in the repository.

The repository retains a deterministic synthetic-data generator for interface tests. The app clearly identifies whether its active records are synthetic or model-derived.

## Current result

For the two-model mean, the 2071–2100 JJA area-weighted box-mean `tasmax` difference from SSP5-8.5 is -2.09 °C under G6solar and -1.72 °C under G6sulfur. Both models show stronger JJA cooling under G6solar. This remains a checkpoint, not a robust ensemble conclusion.

![Two-model regional tasmax comparison](docs/phase2_tasmax_regional.png)

See [the Phase 2 checkpoint](docs/PHASE2_CHECKPOINT.md) for results and limitations. The [Phase 1 result note](docs/PHASE1_RESULT.md) preserves the initial single-model milestone.

## Scenarios

- `ssp585`: high-forcing reference scenario
- `ssp245`: moderate-forcing comparison scenario
- `G6solar`: solar-irradiance reduction against the SSP5-8.5 background
- `G6sulfur`: stratospheric sulfate intervention against the SSP5-8.5 background

## Included metrics

- `tasmax_mean`: mean daily maximum near-surface air temperature
- `pr_mean`: mean precipitation rate
- `rx1day`: annual or seasonal maximum one-day precipitation
- `cdd`: maximum consecutive dry days

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

The real-data manifests contain matched monthly `tasmax` files for IPSL-CM6A-LR and MPI-ESM1-2-LR. Download, verify, and process them with:

```bash
python scripts/build_phase1.py --download
python scripts/make_multimodel_figure.py
```

The downloader validates every file against its official ESGF byte count and SHA-256 checksum before the analysis begins. Raw NetCDF and derived CSV files remain untracked by Git.

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
scripts/build_phase1.py        First IPSL real-data build
scripts/make_multimodel_figure.py  Native-grid regional comparison figure
data/manifests/                Versioned source records and checksums
data/processed/               Generated or explorer-ready tables
docs/DATA_PLAN.md             Real-data acquisition and validation plan
docs/PHASE1_RESULT.md         First result, method, and limitations
docs/PHASE2_CHECKPOINT.md      Two-model checkpoint and limitations
tests/                         Automated checks
```

## Scientific guardrails

- Always display whether records are synthetic or model-derived.
- Preserve model identity instead of presenting an ensemble mean alone.
- Report spread and model count with every multi-model result.
- Do not treat `G6solar` as a complete engineering representation of satellite mirrors. It is a climate-model experiment based on reduced solar irradiance.
- Distinguish equal global forcing targets from equal regional outcomes.

## Suggested public title

**Regional Climate Responses to Solar Intervention: Comparing G6solar and G6sulfur over the Southeast United States**
