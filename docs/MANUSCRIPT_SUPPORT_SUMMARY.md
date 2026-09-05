# Manuscript support summary

## Central manuscript claim

Within the four-model matched monthly ensemble, the G6solar-minus-G6sulfur JJA `tasmax` ordering is consistently negative across the original Southeast box, Southeast land, and Gulf Coast domains. This ordering survives every Phase 6 leave-one-model-out test, is spatially negative in the one-degree ensemble mean across all 364 mapped cells, and has five-year temporal intervals below zero in all four models for the original box and Southeast land. Precipitation and MAM temperature do not show comparable model, geographic, spatial, and temporal consistency.

This wording is stronger than “the ensemble mean is negative” but deliberately narrower than a claim that one intervention is generally more effective.

## Strongest supporting evidence

1. All 12 JJA `tasmax` model-domain means are negative. Equal-weight means are -0.3080 degrees Celsius for the original box, -0.3745 for Southeast land, and -0.3725 for the Gulf Coast, with inter-model SDs of 0.0915, 0.0952, and 0.1234 degrees Celsius.
2. All 24 JJA `tasmax` leave-one-model-out means across six Phase 6 domains remain negative. On the spatial synthesis grid, all 364 cellwise ensemble means are negative; 326 cells have four negative model values and 38 have three negative values.
3. With the primary five-year moving-block procedure, all four original-box and all four Southeast-land model intervals exclude zero below. Two of four Gulf Coast intervals exclude zero below. Effect sizes and sign fractions show that the climatological signal is modest relative to individual-summer variability, rather than universal year by year.

## Weakest and unresolved results

- MAM `tasmax` has a 2-2 model-sign split in all three primary domains. Only MPI's interval is below zero, and the Gulf ensemble sign reverses when MPI is omitted.
- JJA `pr` ensemble means are positive, but model signs are 3-1 for the original box and land and 2-2 for the Gulf Coast. Most Southeast-land model intervals include zero.
- Annual original-box `pr` is positive in all four model means, but all four temporal intervals include zero. The land-only annual result is a 2-2 model-sign split.
- The four matched models are a limited structural sample. The package does not establish whether they span the broader GeoMIP response distribution.

## Top three methodological caveats

1. **Temporal versus structural uncertainty:** moving-block intervals describe temporal sampling within one simulation. Inter-model SD describes variation among four model climatological means. They are not combined and must not be described as the same uncertainty.
2. **Nominal-year alignment:** scenario series are subtracted by seasonal-year label for a reproducible difference series, but independent integrations do not share synchronized weather. Avoid a classical paired-weather or causal-year interpretation.
3. **Scale and sampling:** one member per model and broad model-grid domains do not resolve full internal variability or county-scale impacts. Common-grid maps are visualization products; native-grid fractional-area regional summaries are authoritative.

## Recommended main figures

1. A compact regenerated baseline overview from the Phase 3 `tasmax` and Phase 4 `pr` ensemble tables.
2. `phase6_tasmax_jja_ensemble_maps.png` for spatial temperature robustness.
3. A focused regeneration of `phase6_pr_jja_ensemble_maps.png` emphasizing mixed model-sign counts.
4. A streamlined direct-comparison version of `phase6_domain_sensitivity.png`.
5. `phase7_jja_tasmax_temporal_intervals.png` as the primary uncertainty figure.
6. `phase7_cross_result_robustness.png` for the JJA/MAM and temperature/precipitation contrast.

## Recommended supplementary material

- Full seasonal Phase 3 and Phase 4 figures and tables.
- Per-model native-grid JJA maps and the complete common-grid CSV.
- All six-domain regional and leave-one-model-out tables.
- The 3-, 5-, and 7-year block-length sensitivity table or a compact plot derived from it.
- Phase 5 and Phase 6 daily-extreme outputs, explicitly labeled MPI-ESM1-2-LR single-model, single-member.
- Model-selection logs, manifest schema, geographic-source record, represented areas, and contributing-cell counts.

## Remaining tasks before manuscript drafting

1. Perform a targeted literature update to establish novelty and add Southeast US observational context. The current literature file cannot support a “first study” claim.
2. Choose a target journal and format dataset, software, experiment-design, and statistical-method citations to its requirements.
3. Regenerate only the selected composite figures at journal dimensions, preserving the committed source tables and documented scales.
4. Decide whether to add a formal statistical-method reference for the block-bootstrap design and nominal-year-aligned effect size.
5. Draft the manuscript from `MANUSCRIPT_RESULTS_OUTLINE.md`, then fact-check every numerical sentence against `MANUSCRIPT_EVIDENCE_TABLE.md` and `MANUSCRIPT_KEY_RESULTS.csv`.

No new scientific phase is required unless manuscript review identifies an actual methodological inconsistency.

## Package integrity

`MANUSCRIPT_KEY_RESULTS.csv` is deterministically generated from the committed Phase 7 per-model and ensemble tables. Its build script verifies that Phase 7 reproduces the overlapping Phase 6 model means. A checksum inventory protects the existing Phase 1-7 scientific outputs, and tests check claim-critical model, spatial, leave-one-out, interval, and block-sensitivity counts.
