# Manuscript methods specification

## Experimental scope

The analysis compares the Geoengineering Model Intercomparison Project Phase 6 experiments G6solar and G6sulfur with each other and, where contextual baselines are shown, with SSP5-8.5. G6solar reduces incoming solar radiation, whereas G6sulfur represents stratospheric sulfur injection. Both G6 experiments branch from a high-emissions climate and were designed to moderate warming toward a lower-forcing trajectory. The manuscript's primary contrast is G6solar minus G6sulfur over 2071-2100.

## Model selection and experiment matching

The monthly ensemble contains four source-model/member/grid identities:

| Source model | Institution | Variant | Grid | Experiments |
|---|---|---|---|---|
| CNRM-ESM2-1 | CNRM-CERFACS | `r1i1p1f2` | `gr` | G6solar, G6sulfur, SSP5-8.5 |
| IPSL-CM6A-LR | IPSL | `r1i1p1f1` | `gr` | G6solar, G6sulfur, SSP5-8.5 |
| MPI-ESM1-2-LR | MPI-M | `r2i1p1f1` | `gn` | G6solar, G6sulfur, SSP5-8.5 |
| UKESM1-0-LL | MOHC | `r1i1p1f2` | `gn` | G6solar, G6sulfur, SSP5-8.5 |

Inclusion required usable 2071-2100 monthly `tasmax` for all three experiments, exact variant agreement, compatible grid labels, and acceptable parent metadata. CNRM's three experiments are matched siblings from historical `r1i1p1f2`; the IPSL G6 runs declare the selected SSP5-8.5 parent; MPI and UKESM retain direct parent consistency. CESM2-WACCM was excluded because the available G6solar and G6sulfur variants differ and the G6sulfur run lacks a declared parent. MPI-ESM1-2-HR was excluded because no usable three-experiment `tasmax` triplet was found. The identical four-model identities were then required for `pr`; no model was added only to increase precipitation sample size.

## Provenance and integrity

JSON manifests under `data/manifests/` store the ESGF source URL, dataset version, tracking identifier when available, byte count, SHA-256 checksum, institution, source ID, experiment ID, variant label, grid label, variable, table, and license for each source file. The acquisition pipeline rejects wrong identities and incomplete temporal coverage and verifies file size and checksum. Raw NetCDF files are excluded from Git. Compact derived tables, figures, selection logs, and checkpoint documents are version controlled.

## Temporal aggregation

Monthly data cover 2071-2100. Monthly values are weighted by the number of days in each model's native calendar. Complete seasonal-year means are constructed for MAM, JJA, SON, and annual means for 30 years. DJF is labeled by the January-February year: December of year `y-1` is combined with January and February of year `y`, yielding 29 complete winters for 2072-2100. December 2100 is omitted because January-February 2101 are outside the analysis period. Seasonal years are equally weighted when calculating 30-year or 29-winter climatologies.

Temperature is converted from kelvin to degrees Celsius before reporting. Precipitation flux in kilograms per square meter per second is multiplied by 86,400 to report millimeters per day. The monthly variable names in the compact products are `tasmax_mean` and `pr_mean`.

## Geographic definitions and native-grid regional statistics

The historical comparison domain is the rectangle 24-38 degrees N, 100-74 degrees W. Phase 6 added fixed land and subregional masks, all clipped to that rectangle:

- Southeast land: Alabama, Arkansas, Florida, Georgia, Kentucky, Louisiana, Mississippi, North Carolina, Oklahoma, South Carolina, Tennessee, Texas, Virginia, and West Virginia.
- Gulf Coast: Texas, Louisiana, Mississippi, Alabama, and Florida.
- Lower Mississippi: Arkansas, Louisiana, Mississippi, and Tennessee.
- Atlantic Southeast: Florida, Georgia, South Carolina, North Carolina, and Virginia.
- Appalachian interior: Kentucky, Tennessee, West Virginia, and Virginia.

State boundaries are from the 2025 US Census Bureau 1:20,000,000 Cartographic Boundary File. The land mask is Natural Earth 10 m Physical Vectors version 5.1.1. Source URLs, checksums, and derived geometries are documented in `PHASE6_GEOGRAPHY.md`.

Regional statistics are calculated separately on each model's native grid. Cell boundaries are taken from coordinate bounds where supplied and otherwise inferred from adjacent centers. Each cell and region intersection is evaluated as WGS84 geodesic area. The weight for a cell is its intersection area, equivalently cell area multiplied by its fractional regional coverage. Missing values are excluded from the numerator and denominator. Each output reports represented area, contributing-cell count, and equivalent full-cell count. These broad summaries do not imply county-scale resolution.

## Spatial synthesis

Within each model, experiment climatologies and G6solar-minus-G6sulfur differences are calculated before regridding. Ensemble-map products use a documented one-degree common grid with centers from 24.5 to 37.5 degrees N and 99.5 to 74.5 degrees W, totaling 364 cells. `tasmax` is bilinearly interpolated. `pr` is remapped by a first-order conservative, cell-overlap method with minimum accepted destination-cell coverage of 0.99. Models are then equally weighted cell by cell. The common grid supports visualization and spatial sign-count summaries only; it is never used to replace authoritative native-grid regional means.

For each common-grid cell, outputs contain the ensemble mean, median, sample SD, minimum, maximum, model count, and counts of positive, negative, and zero model differences. Sign agreement is the larger signed count divided by the nonzero model count. It is descriptive, not a probability or statistical significance test.

## Ensemble and geographic robustness

Every model receives equal weight. Regional ensemble products report the mean, median, sample SD across model climatological means, minimum, maximum, model count, and model-sign counts. Leave-one-model-out sensitivity omits each model in turn and recomputes the equal-weight mean for every domain, season, metric, and comparison. A sign change is recorded when the reduced ensemble's sign differs from the full ensemble. This diagnoses model influence but does not constitute an independence-weighted or performance-weighted ensemble analysis.

## Seasonal-year differences and temporal variability

For Phase 7, the fixed native-grid geographic weights are applied to every model, experiment, variable, domain, season, and seasonal year before comparisons are made. The required domains are the original box, Southeast land, and Gulf Coast. For each model and comparison, scenario time series are aligned by `period_year` and subtracted year by year. The primary series is

\[
D_t = X_{\mathrm{G6solar},t} - X_{\mathrm{G6sulfur},t}.
\]

Contextual G6solar-minus-SSP5-8.5 and G6sulfur-minus-SSP5-8.5 series are retained in the full Phase 7 outputs. For each series, the analysis reports the mean, median, sample standard deviation, conventional standard error \(s_D/\sqrt{n}\), minimum, maximum, number of years, fractions positive, negative, and exactly zero, and lag-one autocorrelation.

The standardized paired-difference effect size is

\[
d_z = \frac{\bar{D}}{s_D},
\]

where \(s_D\) is the sample standard deviation of the nominal-year-aligned difference series. It is undefined if \(s_D=0\). Because nominal calendar years do not synchronize weather realizations across independent experiment integrations, the manuscript should call this a *nominal-year-aligned standardized difference*, avoid a classical matched-weather interpretation, and treat its magnitude descriptively.

## Moving-block bootstrap

The primary 95% temporal interval uses a circular moving-block bootstrap with 10,000 replicates and five-year blocks. For a series of length \(n\), random block starts are sampled with replacement, `ceil(n/5)` circular blocks are concatenated, the series is truncated to \(n\), and the mean is calculated. The interval is the 2.5th to 97.5th percentiles of bootstrap means. A reproducible seed is derived from the complete analysis identity, so the result is stable across row order and reruns. The primary JJA `tasmax` result is also recalculated with 3-, 5-, and 7-year blocks.

These intervals characterize uncertainty associated with finite temporal sampling and serial dependence within a single model simulation under the nominal-year alignment and block-resampling assumptions. They do not measure uncertainty across GeoMIP models, do not create synchronized weather between experiments, and should not automatically be labeled statistical significance tests. The sample SD of model climatological means is reported separately as inter-model structural spread. One ensemble member per model also means that the time series do not sample the full internal-variability distribution of each model.

## Reproducible manuscript sources

The main manuscript subset is rebuilt with:

```bash
python scripts/build_manuscript_support.py
```

The script verifies model identity, Phase 6 to Phase 7 mean reproduction, source-figure presence, and the expected 48-row manuscript table. Full scientific rebuild commands remain in `PHASE7_BUILD.md`; manuscript verification does not require downloading raw files.
