# Phase 5 daily-extremes model selection

Version: 1.0 (selection frozen and all files validated, 2026-09-04)

## Objective

Phase 5 tests whether the Phase 3 and Phase 4 mean responses translate into changes in daily heat, heavy precipitation, and dry-spell behavior over the same Southeast U.S. domain. It retains the 2071-2100 period, G6solar and G6sulfur comparisons against SSP5-8.5, native-grid regional calculations, and exact-variant provenance rules.

## Planned indices

| Index | Daily input | Definition |
|---|---|---|
| TXx | `tasmax` | Maximum daily maximum temperature within each year or season, averaged across complete periods. |
| HWN-TX90 | `tasmax` | Number of heatwave events with at least three consecutive days above the model's calendar-day 90th percentile. |
| HWF-TX90 | `tasmax` | Number of days participating in those heatwave events. |
| HWD-TX90 | `tasmax` | Duration of the longest qualifying heatwave event. |
| Rx1day | `pr` | Maximum one-day precipitation within each year or season. |
| Rx5day | `pr` | Maximum consecutive five-day precipitation total within each year or season. |
| CDD | `pr` | Maximum run of days with precipitation below 1 mm/day. |
| R95pTOT | `pr` | Total precipitation from wet days above the model's historical wet-day 95th percentile. |

Percentile thresholds will use the selected model's 1981-2010 historical member. TX90 uses a centered five-day calendar window. R95p uses wet days with precipitation at least 1 mm/day. Because the indices are evaluated outside the reference period, in-base bootstrap adjustment is not required.

## Eligibility rules

A model is eligible for the direct daily comparison only when:

1. Daily `tasmax` and `pr` are available for G6solar, G6sulfur, and SSP5-8.5 through December 2100.
2. All three future experiments use a compatible variant, grid, and parent branch.
3. Historical daily `tasmax` and `pr` from the same variant and grid cover 1981-2010 for percentile thresholds.
4. Every source file has a versioned URL, tracking ID, byte count, SHA-256 checksum, institution, experiment, variant, grid, and license record.
5. Files pass checksum, embedded metadata, calendar, exact daily coverage, units, and missing-data validation.

No daily variable, ensemble member, experiment, or grid may be silently substituted.

## Federated ESGF availability audit

The ESGF file index was queried for CMIP6 `day` data for G6solar and G6sulfur, followed by exact checks for SSP5-8.5 and historical coverage.

| Model | Daily G6solar | Daily G6sulfur | Decision | Reason |
|---|---|---|---|---|
| CNRM-ESM2-1 | Not found | `tasmax` and `pr` available | Exclude | No daily G6solar counterpart exists in the indexed archive. |
| IPSL-CM6A-LR | Not found | Not found | Exclude | Neither daily G6 experiment is available for the required variables. |
| MPI-ESM1-2-LR | `tasmax` and `pr` available | `tasmax` and `pr` available | Include | Exact Phase 4 member `r2i1p1f1`, grid `gn`, is complete through 2100 and has matching SSP5-8.5 and historical data. |
| UKESM1-0-LL | Daily data exists only for variants different from Phase 4 | Not found | Exclude | No matched daily G6sulfur counterpart and no exact Phase 4 daily triplet. |
| CESM2-WACCM | `tasmax` and `pr` available | Not found | Exclude | No daily G6sulfur counterpart exists in the indexed archive. |
| MPI-ESM1-2-HR | Not found | Not found | Exclude | No indexed daily G6solar/G6sulfur pair for the required variables. |

## Consequence for interpretation

Phase 5 will be a single-model process study using MPI-ESM1-2-LR `r2i1p1f1`, not a multimodel ensemble. It can identify whether daily extremes within this exact model-member pair differ from the monthly means and can establish a reproducible extremes workflow. It cannot quantify structural model uncertainty or support a general GeoMIP extremes conclusion.

## Frozen source selection

The two daily manifests contain 24 files: 12 `tasmax` and 12 `pr`. Each variable uses three historical files spanning 1970-2014 and three files for each future experiment spanning 2055-2100. The analysis reads 1981-2010 from historical and 2071-2100 from each future experiment.

| Experiment | Variant | Grid | Parent experiment | Parent variant | Validation |
|---|---|---|---|---|---|
| historical | `r2i1p1f1` | `gn` | piControl | `r1i1p1f1` | Passed for `tasmax` and `pr` |
| SSP5-8.5 | `r2i1p1f1` | `gn` | historical | `r2i1p1f1` | Passed for `tasmax` and `pr` |
| G6solar | `r2i1p1f1` | `gn` | SSP5-8.5 | `r2i1p1f1` | Passed for `tasmax` and `pr` |
| G6sulfur | `r2i1p1f1` | `gn` | SSP5-8.5 | `r2i1p1f1` | Passed for `tasmax` and `pr` |

Every file passed its recorded byte count and SHA-256 checksum. Embedded source ID, experiment ID, variant, grid, parent experiment, parent variant, tracking ID, units, and calendar were also checked. All selected files use the proleptic Gregorian calendar. Source URLs, archive version `v20190710`, tracking IDs, sizes, checksums, institution, license, and branch metadata are preserved in `data/manifests/mpi_lr_tasmax_day.json` and `data/manifests/mpi_lr_pr_day.json`.

## Change log

- 0.1: Defined indices and thresholds, audited the federated daily archive, and provisionally selected the only complete exact-member pair.
- 1.0: Froze MPI-ESM1-2-LR `r2i1p1f1` on `gn` after all 24 files passed checksum, provenance, coverage, calendar, unit, and missing-data validation.
