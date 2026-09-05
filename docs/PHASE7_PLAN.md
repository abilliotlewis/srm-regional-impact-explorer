# Phase 7 implementation plan

## Objective

Determine whether the Phase 6 G6solar-minus-G6sulfur regional differences are large relative to paired year-to-year variability within each of the four matched monthly simulations, while keeping that temporal variability separate from structural spread across models.

## Reusable Phase 6 foundation

- Exact manifest-controlled model, experiment, member, grid, parent-run, and checksum validation.
- Calendar-aware monthly unit conversion and complete-period rules.
- Fractional WGS84 geodesic cell-area weights on native grids.
- Existing `original_box`, `southeast_land`, and `gulf_coast` definitions.
- Stable hashed random seeds and circular moving-block resampling.
- Compact committed outputs and checksum-based historical-output regression tests.

## Implementation sequence

1. Preserve every committed Phase 1-6 scientific output with a versioned SHA-256 inventory.
2. Extend monthly preparation to retain each complete annual and seasonal mean at every native cell before climatological averaging. Keep 30 periods for ANN, MAM, JJA, and SON and 29 winters for DJF 2072-2100.
3. Apply the unchanged Phase 6 fractional geodesic weights to produce model-level regional time series for all three experiments and the original-box, Southeast-land, and Gulf-Coast domains.
4. Validate exact scenario-year alignment and calculate paired differences within model, domain, metric, and season before any temporal statistic.
5. Report paired mean, median, sample SD, standard error, paired standardized effect size, range, sample count, positive and negative fractions, lag-1 autocorrelation, and reproducibly seeded 95% circular moving-block bootstrap intervals.
6. Define paired standardized effect size as the paired-difference mean divided by the sample SD of the paired-difference series. This is a standardized within-simulation contrast, not an across-model effect.
7. Use five-year blocks and 10,000 bootstrap replicates. Five years is long enough to preserve short multi-year persistence while leaving roughly six blocks in a 30-year sample. Report whether each interval is below zero, above zero, or includes zero.
8. Synthesize model means without combining uncertainty types: model sign counts, temporal-interval classifications, equally weighted ensemble mean and median, and sample SD across four model climatological means.
9. Produce a primary JJA `tasmax` model-by-domain interval figure and a compact robustness figure for JJA `tasmax`, MAM `tasmax`, JJA `pr`, and annual `pr`.
10. Create manuscript-ready CSV tables and `docs/PHASE7_CHECKPOINT.md`, then extend tests for periods, pairing, DJF, bootstrap behavior, effect size, interval classification, structural spread, completeness, and historical preservation.
11. Run the full test suite, byte-check all Phase 1-6 outputs, and only then update the README and publish Phase 7.

## Scope controls

Phase 7 adds no variables, models, regions, scenarios, daily indices, emulator, machine learning, or application features. It does not start Phase 8.
