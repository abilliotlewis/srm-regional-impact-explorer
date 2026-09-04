# SRM Regional Impact Explorer

An open, reproducible starter project for comparing regional climate responses under solar radiation modification scenarios.

The first scientific question is:

> How do solar-irradiance reduction and stratospheric aerosol intervention differ in their effects on Southeast US heat and precipitation indicators?

## Current status

The included dataset is a **synthetic demonstration dataset**. It exists only to test the data schema, analysis functions, charts, and interface. It must not be interpreted as a climate projection or research result.

The project is designed so the demonstration CSV can later be replaced with processed GeoMIP/CMIP6 output while keeping the explorer unchanged.

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

The app creates the deterministic demonstration CSV automatically when it is missing. Run `python scripts/generate_demo_data.py` directly when you want to regenerate it before launching the app.

Run tests:

```bash
pytest
```

## Replace the demonstration data

1. Download monthly or daily GeoMIP/CMIP6 files from an ESGF node for `ssp585`, `ssp245`, `G6solar`, and `G6sulfur`.
2. Place files under `data/raw/<scenario>/<model>/`.
3. Use `scripts/prepare_geomip.py` to convert gridded climatologies to the explorer schema.
4. Write the combined file to `data/processed/regional_metrics.csv`.
5. Set `is_demo` to `false` for verified model-derived records.

See [docs/DATA_PLAN.md](docs/DATA_PLAN.md) for variables, time periods, quality checks, and publication criteria.

## Repository structure

```text
app.py                         Gradio application
src/srm_explorer/analysis.py  Data loading, validation, summaries, plots
scripts/generate_demo_data.py Deterministic demonstration data generator
scripts/prepare_geomip.py     NetCDF-to-explorer preprocessing starter
data/processed/               Generated or explorer-ready tables
docs/DATA_PLAN.md             Real-data acquisition and validation plan
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
