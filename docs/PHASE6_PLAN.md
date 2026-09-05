# Phase 6 implementation plan

## Objective

Determine where the established G6solar and G6sulfur results persist across the Southeast United States, where the four monthly models disagree, and how conclusions depend on geography, individual models, and within-simulation annual variability.

## Reused foundation

Phase 6 preserves the Phase 3 to 5 manifests, exact members, raw-file checksums, monthly definitions, daily index definitions, native calendars, and committed reference outputs. Raw NetCDF files remain outside Git. The existing 24-38°N, 100-74°W box remains the comparison domain.

## Work packages

1. Version Census state boundaries and Natural Earth land geometry with source URLs and checksums. Define land-only and four broad state-based subregions, including the Gulf Coast.
2. Calculate fractional geodesic cell-area weights on every native model grid. Report contributing cells, equivalent cells, represented area, and boundary coverage.
3. Form G6solar-minus-SSP5-8.5, G6sulfur-minus-SSP5-8.5, and G6solar-minus-G6sulfur within each matched model before aggregation.
4. Preserve authoritative regional summaries on native grids. Remap matched differences to a documented 1° common grid using bilinear temperature and first-order conservative precipitation methods only for spatial ensemble displays.
5. Report ensemble mean, median, spread, range, count, positive and negative counts, and descriptive sign agreement. Add equal-weight leave-one-model-out sensitivity.
6. Preserve MPI-ESM1-2-LR annual and seasonal daily indices by period year. Add land-only maps and variability summaries for TXx, heatwave days, Rx5day, and CDD.
7. Restrict the explorer to committed, available combinations and label model scope, domain, period, units, count, and grid type.
8. Validate masks, weights, regridding, matching, counts, missing selections, temporal resampling, and byte-for-byte preservation of Phase 3 to 5 outputs.

## Scope exclusions

No new scenarios, indices, AI emulation, regional boundaries, or impact applications are added in this phase.

