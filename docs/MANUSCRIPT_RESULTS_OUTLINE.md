# Manuscript results outline

This outline follows the scientific argument rather than repository phase order. All differences are G6solar minus G6sulfur unless a baseline comparison is explicitly named.

## 3.1 Matched model ensemble and baseline comparison

- Four exact model/member/grid identities support both monthly `tasmax` and `pr`: CNRM-ESM2-1 `r1i1p1f2`/`gr`, IPSL-CM6A-LR `r1i1p1f1`/`gr`, MPI-ESM1-2-LR `r2i1p1f1`/`gn`, and UKESM1-0-LL `r1i1p1f2`/`gn`.
- The experiment triplet is G6solar, G6sulfur, and SSP5-8.5 for every identity. CESM2-WACCM and MPI-ESM1-2-HR were excluded rather than mixing variants or incomplete triplets.
- Phase 3 and Phase 4 original-box results establish how each intervention differs from SSP5-8.5; the paper's main contrast is G6solar minus G6sulfur.

Best support: a regenerated two-variable overview based on `phase3_ensemble_summary.csv` and `phase4_ensemble_summary.csv`.

Caveat: the four-model ensemble is intentionally matched and fixed, not exhaustive.

## 3.2 JJA temperature response and model consistency

- Original-box model means are -0.2939, -0.3486, -0.4019, and -0.1878 degrees Celsius; the equal-weight ensemble mean is -0.3080 degrees Celsius and inter-model SD is 0.0915 degrees Celsius.
- Southeast-land model means are -0.3785, -0.4335, -0.4470, and -0.2388 degrees Celsius; ensemble mean -0.3745 and SD 0.0952 degrees Celsius.
- Gulf Coast model means are -0.4329, -0.3738, -0.4834, and -0.2000 degrees Celsius; ensemble mean -0.3725 and SD 0.1234 degrees Celsius.
- Thus all 12 model-domain climatological means are negative, with UKESM the weakest in magnitude in every domain.

Best figure: `phase7_jja_tasmax_temporal_intervals.png`.

Caveat: negative values mean lower regional JJA `tasmax` under G6solar than G6sulfur. They do not mean that either experiment restores observed climate.

## 3.3 Geographic and spatial robustness of the JJA temperature ordering

- The JJA ensemble difference is negative in all six Phase 6 domains. It ranges from -0.2569 degrees Celsius in the Atlantic Southeast to -0.4257 degrees Celsius in the Lower Mississippi region.
- Every one of the 24 leave-one-model-out JJA temperature means remains negative. For the three Phase 7 domains, reduced-ensemble ranges are -0.3481 to -0.2767 degrees Celsius for the original box, -0.4197 to -0.3503 for Southeast land, and -0.4300 to -0.3356 for the Gulf Coast.
- On the one-degree spatial synthesis grid, all 364 cellwise ensemble means are negative. Model signs are 4 negative/0 positive in 326 cells and 3 negative/1 positive in 38 cells.
- The land-only ensemble mean is 0.0664 degrees Celsius more negative than the original-box mean, but this descriptive contrast is not itself an uncertainty-tested land-ocean effect.

Best figures: `phase6_tasmax_jja_ensemble_maps.png` and the temperature panel of `phase6_domain_sensitivity.png`.

Caveat: regional means are calculated on native grids. The common one-degree grid is only for spatial display and sign-count aggregation.

## 3.4 Temporal variability and effect-size context

- Five-year block intervals lie below zero for all four original-box and all four Southeast-land simulations. Gulf Coast intervals lie below zero for CNRM and MPI but include zero for IPSL and UKESM.
- Original-box effect sizes range from -0.279 to -0.678; Southeast-land values range from -0.226 to -0.526; Gulf values range from -0.182 to -0.500.
- The fraction of summers with a negative nominal-year-aligned difference ranges from 0.53 to 0.73 across the 12 model-domain series. The climatological ordering is therefore more consistent than a claim that every summer has the same sign.
- The block-length sensitivity is mostly stable but identifies weaker cases: UKESM original and land intervals include zero with three-year blocks, IPSL Gulf changes from below zero at three years to including zero at five and seven years, and UKESM Gulf includes zero at all tested lengths.

Best figure: `phase7_jja_tasmax_temporal_intervals.png`.

Caveat: the intervals are temporal-sampling intervals within each model simulation. Inter-model SD is a separate structural-spread statistic.

## 3.5 Seasonal contrast in temperature

- MAM has two positive and two negative model means in every Phase 7 domain, unlike JJA's uniform negative model signs.
- MAM ensemble means are -0.2490 degrees Celsius for the original box, -0.2285 for Southeast land, and -0.2349 for the Gulf Coast, but each mean combines a 2-2 sign split.
- MPI is the only model whose five-year MAM interval lies below zero in all three domains; the other nine model-domain intervals include zero.
- The Gulf Coast MAM ensemble sign becomes positive when MPI is omitted, demonstrating dependence on one model.

Best figure: the MAM `tasmax` portion of `phase7_cross_result_robustness.png`.

Caveat: a negative ensemble mean is not evidence of cross-model agreement when model signs split evenly.

## 3.6 Precipitation response and geographic sensitivity

- JJA precipitation ensemble means are positive but small: +0.1274 mm/day for the original box, +0.1087 for Southeast land, and +0.1291 for the Gulf Coast.
- Model signs are 3 positive/1 negative for the original box and land, but 2/2 for the Gulf Coast. Gulf Coast model means range from -0.1854 to +0.3767 mm/day.
- Five-year intervals are above zero in two models for the original box, one for Southeast land, and two for the Gulf Coast; all remaining JJA precipitation intervals include zero.
- Annual precipitation is positive in all four original-box means, with ensemble +0.0485 mm/day, but all four temporal intervals include zero. Southeast land has a 2-2 sign split and ensemble +0.0169 mm/day; again all intervals include zero.

Best figures: `phase6_pr_jja_ensemble_maps.png` and the precipitation portion of `phase7_cross_result_robustness.png`.

Caveat: precipitation signs and interval classifications depend on domain and model. Positive ensemble means should not be presented alone.

## 3.7 Why precipitation conclusions are weaker than temperature conclusions

- JJA precipitation on the common grid has four positive signs in 43 of 364 cells, a 3-1 positive split in 212, a 2-2 split in 87, and a 1-3 split in 22. This is much less spatially uniform than JJA temperature.
- Across all Phase 6 domains and seasons, 15 direct-comparison leave-one-model-out cases across 14 domain-season combinations change ensemble sign. By contrast, none of the 24 JJA temperature leave-one-out results changes sign.
- Annual precipitation demonstrates the difference between model-mean sign and temporal separation: all four original-box means are positive, but every interval includes zero.
- The appropriate conclusion is that precipitation ordering is weaker, more geographically dependent, and more structurally variable than the JJA temperature ordering.

Best figure: a focused precipitation panel from `phase6_pr_jja_ensemble_maps.png`, paired with the precipitation rows of `phase7_cross_result_robustness.png`.

Caveat: the result does not show that precipitation effects are absent. It shows that their direction and separation are less consistent in this ensemble and analysis period.
