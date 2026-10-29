# Regional extreme-rainfall catalog: exploratory results

## Scope and status

This phase uses actual NOAA CPC daily precipitation for the five-state domain, 1978–2025. It extends the six-station pilot in `../REPORT.md`. The dominant result is **method sensitivity**: two provisional methods produce opposite conclusions about whether seasonal counts are overdispersed. Neither method has been validated as a catalog of independent meteorological storms. These results are not publication-ready attribution or operational forecasts.

## Data and processing

Daily 0.25-degree CPC US precipitation files are the NOAA PSL historical series through 2006 and the separate real-time series for 2007 onward: https://psl.noaa.gov/thredds/catalog/Datasets/cpc_us_precip/catalog.html and https://psl.noaa.gov/thredds/catalog/Datasets/cpc_us_precip/RT/catalog.html. Daily accumulation is the 12 UTC-to-12 UTC reporting window. Historical and real-time product differences, shifting station density, interpolation and resolution may produce inhomogeneities. Source file versions and hashes are in `output/source_manifest.csv`; the five-state Natural Earth 1:110m domain includes a grid point if its center lies within a state polygon. This is a coarse approximation to state and coastal boundaries, not a fractional-area or exact coastal mask.

Cells with at least 99% finite values across 1978–2025 are retained: 1,045 grid cells. Days with less than 95% of retained cells observed are excluded, which occurred once; seasons with less than 95% eligible days are excluded. The fixed domain and retained cells use whole-record coverage, a minor retrospective selection; this is not a fully real-time processing system. DJF means winter ending in the named year. Counts cover 46 winters ending 1980–2025 and 47 summers 1979–2025. A different seasonal threshold is derived at each cell for each calendar season, using 1981–2010 days with at least 1 mm precipitation; the primary event threshold is the 99th percentile of those wet days. Thresholds use calendar-year 1981–2010 data and are held fixed. All forecast test seasons start in 2012, after the end of the entire threshold period. Threshold uncertainty is not propagated.

## Two provisional event methods

1. **Connected extreme footprints (tracked):** connect extreme grid cells within a day and at matching or immediately adjacent cells on consecutive days, then retain components with at least four distinct footprint cells. Connect all dates before assigning each component to the season containing the day of greatest extreme-cell count. This uses only thresholded daily rain, a coarse 0.25-degree grid, and one-cell-per-day displacement. It can split fast-moving or discontinuous systems and merge unrelated overlapping systems. It is not a verified storm tracker.
2. **Regional active-day runs (runs):** a day is active when at least four domain cells exceed their local threshold. Group active days separated by at most one intervening inactive day. Assign each run to its peak day. This can merge independent storms in different places, and the four cells need not form a coherent object. A day with missing coverage can terminate or separate events, and the 95% season coverage rule cannot remove every missing-observation bias.

These procedures are intentionally different sensitivity definitions, not independent physical validation of either catalog. The 2016 Louisiana flood period illustrates why: the 12–14 August connected catalog includes a large footprint and another small footprint on 12 August. Identifying whether those belong to the same rain-producing system requires manual synoptic tracking. The temporal-runs method also merges sequences as long as 12 days. The four-cell threshold is exploratory, not an externally validated storm footprint size.

## Seasonal count distributions

Primary 99th-percentile thresholds:

| Definition | Season | Years | Mean count | Variance | Variance / mean | Bootstrap 95% interval for ratio |
|---|---|---:|---:|---:|---:|---:|
| Connected footprints | DJF | 46 | 11.85 | 40.40 | 3.41 | 2.23–4.77 |
| Regional active-day runs | DJF | 46 | 6.09 | 4.97 | 0.82 | 0.50–1.19 |
| Connected footprints | JJA | 47 | 20.51 | 59.60 | 2.91 | 1.79–4.04 |
| Regional active-day runs | JJA | 47 | 9.64 | 4.45 | 0.46 | 0.29–0.61 |

Intervals resample three-year blocks of observed season counts; they do not include threshold or event-identification uncertainty. A 10,000-replicate plug-in stationary Poisson simulation gives a one-sided dispersion-tail estimate of 0.0001 for both connected-footprint seasons and 0.807 and 0.999 for run-defined DJF and JJA, respectively. The lower limit is the simulation resolution with a plus-one correction. This test holds the estimated rate and event definitions fixed, does not account for climate trends or product changes, and is not a test for causal dependence. Multiple regional components produced by one meteorological system could inflate connected-footprint dispersion; the runs procedure can suppress variability by merging separate storms. Neither result proves or disproves clustering of independent storms.

Threshold sensitivity reinforces the caution. At the 95th, 99th and 99.5th percentiles, DJF variance-to-mean ratios are 2.68, 3.41 and 3.44 for connected footprints, but 0.43, 0.82 and 0.92 for regional runs. JJA values are 3.04, 2.91 and 2.34 versus 0.65, 0.46 and 0.67, respectively. The runs method can yield fewer episodes at a lower threshold because more active days join into long runs. See `output/sensitivity.csv` for means, variances and count probabilities.

## Retrospective ENSO association

As an exploratory example, define an active winter as at least 15 connected-footprint episodes. The threshold was selected after inspecting this data and is not prespecified confirmation. November Niño 3.4 SST is centered on the 1981–2010 November mean; warm and cold categories use anomalies ≥ +0.5°C and ≤ −0.5°C, respectively. This is a single monthly SST measure, not the official multi-month ONI classification. Reconstructed SST is a revised historical series and may not match data available on a real-time issuance date.

| November category | Active winters / winters | Fraction | Exact binomial 95% interval |
|---|---:|---:|---:|
| Cold | 1 / 13 | 7.7% | 0.2%–36.0% |
| Neutral | 4 / 18 | 22.2% | 6.4%–47.6% |
| Warm | 8 / 15 | 53.3% | 26.6%–78.7% |
| All winters | 13 / 46 | 28.3% | Not calculated |

For warm November conditions, the active-season fraction divided by the all-winter fraction is 1.89, with a 95% three-year block-bootstrap interval of 1.04–2.74. The reference includes the warm seasons, and interval estimates are sensitive to the small sample, nonstationarity and selection of event definition and threshold. Exact binomial intervals assume independent, exchangeable winters within a category. These numbers show an association in this catalog; they do not show that ENSO causes additional independent storms or establish operational forecast skill. See `output/conditional_winter.csv` and `conditional_analysis.py`.

## Rolling forecast experiment

Four models use the same expanding training set: stationary Poisson, Poisson with a penalized linear trend, Poisson with a penalized preceding November (DJF) or May (JJA) Niño 3.4 SST, and negative binomial with the same SST predictor. Predictor standardization and model fitting use prior seasons only. The active threshold for each test year is the greater of two and the ceiling of the training count 75th percentile, so k can change between test years; all models in a given year use the same k. For each of 2012–2025, `output/hindcasts.csv` records k, observed count, predicted probability, Brier loss and count log score. November or May reconstructed SST is a proxy for prior-season conditions, not verified as available by the first day of the season. No operational release lag or reanalysis revision is modeled.

| Definition and season | Positive / test seasons | Constant Brier | ENSO-Poisson Brier | ENSO-NB Brier | Trend-Poisson Brier |
|---|---:|---:|---:|---:|---:|
| Connected footprints, DJF | 5 / 14 | 0.253 | 0.092 | 0.108 | 0.257 |
| Regional runs, DJF | 5 / 14 | 0.230 | 0.122 | 0.125 | 0.231 |
| Connected footprints, JJA | 7 / 14 | 0.312 | 0.304 | 0.279 | 0.308 |
| Regional runs, JJA | 5 / 14 | 0.231 | 0.235 | 0.235 | 0.257 |

Lower scores are better. The winter ENSO-Poisson Brier improvement over the constant model is 0.162 for connected footprints and 0.108 for runs. Three-year block bootstrap intervals computed over paired out-of-sample losses are 0.069–0.248 and 0.053–0.158, respectively. They condition on the already-fitted forecasts and do not include full model, threshold, experiment-selection or predictor-revision uncertainty; 14 years is a very small test sample, and the choices were explored rather than prospectively registered. The 14-year summer comparisons are inconsistent across event definitions. The scores are promising retrospective evidence for the particular proxy and definitions, not proof of operational forecast skill. A negative-binomial likelihood allows count variability but does not diagnose physical storm dependence. The code records convergence for all fits; all reported fits converged under the optimizer's criterion.

## Hypothesis assessment

| Hypothesis | Assessment |
|---|---|
| H1 seasonal overdispersion | Inconclusive for independent storms. Strong excess dispersion for connected footprints; the runs method shows no excess and may merge storms. |
| H2 climate-regime dependence | Exploratory support for an ENSO association with winter episode counts, with uncertain storm identity, product homogeneity, selection and physical pathway. |
| H3 residual dependence | Not tested. A negative-binomial forecast model is not a residual-dependence test. |
| H4 predictive skill | Promising retrospective winter hindcasts for the selected definitions; operational skill remains unestablished because predictor availability, sample size, sensitivity and preselection have not been adequately addressed. |

## Remaining work

- Validate distinct systems with rain-object motion, synoptic fields and manually reviewed historical cases; explicitly measure splits and merges. Improve handling of wide-area simultaneous storms and long chains.
- Assess CPC historical/real-time homogeneity against an independent product, storm metadata, and gauge network changes; test trends and longer baselines.
- Acquire ERA5 or another reanalysis to investigate circulation, moisture transport and regime frequency, persistence and within-regime rain probability. Track tropical cyclones with a rainfall-based attribution method.
- Test coastal versus inland domains, states, multiday precipitation, alternate spatial scales and event thresholds with uncertainty and multiple-test controls.
- Use genuinely archived predictors available before issuance, prespecified thresholds and independent periods or external datasets. Compare climatology, trend, ENSO and additional parsimonious models with calibration, count log score and uncertainty from nested blocked validation.

## Data references

- NOAA PSL CPC unified daily precipitation historical and real-time catalogs, linked above.
- NOAA PSL Niño 3.4 monthly SST, source file in `../data/nino34.txt`: https://psl.noaa.gov/data/correlation/nina34.data (the supplied file identifies ERSST v6).
- Natural Earth state boundaries: https://datahub.io/core/geo-boundaries-us-110m .
- The parent report `../REPORT.md` contains the literature review and original station pilot.
