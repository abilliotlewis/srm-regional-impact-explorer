# Manuscript figure plan

Use no more than six main-text figures. Existing files are reproducible scientific sources; “regenerate” below means compose a manuscript-focused layout from the same committed tables, not rerun or alter the underlying analysis.

## Main-text figures

| Figure | Existing source | Use | Manuscript purpose | Recommended panels | Caption essentials |
|---|---|---|---|---|---|
| 1. Experiment-context regional responses | `phase3_tasmax_ensemble.png`; `phase4_pr_ensemble.png` | Regenerate as one compact figure | Establish G6solar and G6sulfur responses relative to SSP5-8.5 before focusing on their direct difference. | (a) original-box seasonal `tasmax`; (b) original-box seasonal `pr`; individual models plus ensemble summary. | Four matched models; 2071-2100; DJF 2072-2100; native-grid regional means; intervention-minus-SSP5-8.5 values. |
| 2. JJA temperature spatial robustness | `phase6_tasmax_jja_ensemble_maps.png` | Use directly if journal dimensions remain legible; otherwise regenerate typography only | Show the spatial structure of G6solar-SSP5-8.5, G6sulfur-SSP5-8.5, and G6solar-G6sulfur. | Retain three comparison panels and model-sign information. | Matched differences computed within model before bilinear remapping; one-degree grid is for visualization; native-grid regional means are authoritative; sign counts are descriptive. |
| 3. JJA precipitation spatial heterogeneity | `phase6_pr_jja_ensemble_maps.png` | Regenerate with a visually prominent sign-agreement layer | Contrast mixed precipitation agreement with the temperature result. | (a) ensemble mean difference; (b) positive/negative model count or sign agreement; optional intervention-baseline panels only if space permits. | First-order conservative remapping; 364 cells; 43 cells 4-0 positive, 212 cells 3-1, 87 cells 2-2, 22 cells 1-3. |
| 4. Geographic sensitivity | `phase6_domain_sensitivity.png` | Regenerate as a direct-comparison-only figure | Compare original box, Southeast land, Gulf Coast, Lower Mississippi, Atlantic Southeast, and Appalachian interior without overcrowding. | (a) JJA `tasmax`; (b) JJA and annual `pr`, with individual model values and equal-weight summaries. | Native-grid fractional geodesic weighting; broad domain definitions; represented area and contributing cells available in CSV; no county precision. |
| 5. JJA temperature temporal intervals | `phase7_jja_tasmax_temporal_intervals.png` | Use directly | Primary manuscript result: all model means negative, with domain-specific temporal interval strength. | Facet by original box, Southeast land, and Gulf Coast; one point and five-year interval per model. | 10,000-replicate circular moving-block bootstrap; five-year blocks; temporal sampling within model; no structural-uncertainty interpretation. |
| 6. Cross-result robustness | `phase7_cross_result_robustness.png` | Regenerate only if the final journal size obscures labels | Put JJA `tasmax`, MAM `tasmax`, JJA `pr`, and annual `pr` on a common interpretive page. | Separate temperature and precipitation scales; model means with temporal intervals, not ensemble bars alone. | Distinguish units; identify nominal-year-aligned differences; state model count and interval meaning. |

## Supplementary figures

- Phase 3 and Phase 4 full seasonal figures: `phase3_tasmax_seasonal.png`, `phase4_pr_seasonal.png`.
- Native-grid JJA maps for every model: `phase6_tasmax_jja_native.png`, `phase6_pr_jja_native.png`.
- The unabridged Phase 6 domain-sensitivity figure if Figure 4 is streamlined.
- A compact 3-, 5-, and 7-year block-length sensitivity plot generated from `phase7_block_length_sensitivity.csv`.
- Phase 5 daily-extreme figures `phase5_heat_extremes.png` and `phase5_hydro_extremes.png`, plus the Phase 6 land variability figure `phase6_daily_land_variability.png`.

## Caption-wide rules

Every caption should state the comparison direction, units, period, domain, model count, whether the value is a native-grid regional mean or a common-grid visualization, and the uncertainty definition. Avoid “confidence across models” for Phase 7 intervals. Use “interval excludes zero under the moving-block procedure” rather than “statistically significant” unless a later inferential framework justifies that term.
