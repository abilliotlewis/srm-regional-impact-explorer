# GeoMIP Data Plan

## Current publishable question

How do `G6solar` and `G6sulfur` differ from `ssp585` in late-century Southeast U.S. daily heat, heavy-precipitation, and dry-spell behavior?

## Current scope

- Region: 24–38°N, 100–74°W
- Future climatology: 2071–2100
- Direct-comparison scenarios: `ssp585`, `G6solar`, `G6sulfur`
- Seasons: annual, DJF, MAM, JJA, SON
- Variables completed: monthly and daily `tasmax` and `pr`
- Phase 5 daily sample: MPI-ESM1-2-LR `r2i1p1f1` on `gn`, the only audited complete matched daily set
- Historical threshold period: 1981-2010 from the same MPI-ESM1-2-LR member and grid

## Phase roadmap

| Phase | Scope | Status |
|---|---|---|
| 1 | Initial single-model monthly `tasmax` workflow | Historical checkpoint |
| 2 | Two-model monthly `tasmax` comparison | Historical checkpoint |
| 3 | Defensible four-model monthly `tasmax` ensemble | Complete |
| 4 | Monthly `pr` for the same matched four-model sample | Complete |
| 5 | TXx, TX90 heatwaves, Rx1day, Rx5day, CDD, and R95pTOT | Complete, single-model checkpoint |
| 6 | Predefined subregional analysis | Later work |
| 7 | Spatial agreement and uncertainty maps | Later work |

## Candidate CMIP variables

| Explorer metric | CMIP variable | Frequency | Processing |
| --- | --- | --- | --- |
| Mean maximum temperature | `tasmax` | monthly or daily | Convert K to °C, seasonal mean |
| Mean precipitation | `pr` | monthly or daily | Convert kg m-2 s-1 to mm/day, seasonal mean |
| Maximum one-day rain | `pr` | daily | Annual or seasonal maximum |
| Maximum five-day rain | `pr` | daily | Maximum consecutive five-day total |
| Consecutive dry days | `pr` | daily | Maximum run with precipitation below 1 mm/day |
| Very-wet-day total | `pr` | daily | Total above the historical wet-day 95th percentile |
| TXx | `tasmax` | daily | Annual or seasonal maximum |
| TX90 heatwaves | `tasmax` | daily | Events, participating days, and longest duration above calendar-day TX90 |

## Model-selection rules

1. Require G6solar, G6sulfur, and SSP5-8.5 from a demonstrably compatible model branch for direct comparisons.
2. Preserve the exact ensemble member selected for each model; do not substitute members to increase model count.
3. Preserve institution, source ID, experiment ID, variant label, grid label and file tracking IDs.
4. Do not silently mix native and regridded products.
5. Report exactly which models contribute to every result.

## Quality checks

- Coordinates and longitude conventions are normalized.
- Temperature and precipitation units are converted explicitly.
- Time coverage is complete for the chosen period.
- Seasonal sample counts are checked, including DJF year boundaries.
- Missing-value masks are inspected.
- Regional means use latitude-aware area weights.
- Each scenario difference uses matched models.
- Results are compared with published GeoMIP direction and approximate magnitude as a reasonableness check, not forced to agree.

## Publication threshold

Remove the demonstration warning only when:

- all records come from traceable GeoMIP/CMIP files;
- the processing workflow is reproducible from a clean environment;
- model matching, units, calendars and area weighting have automated tests;
- at least one experienced climate-model researcher has reviewed the methodology;
- the dataset card lists limitations and excludes deployment recommendations.

## Possible AI component after the scientific baseline

An emulator remains outside the current scope. If added later, outputs should be distributions or quantiles rather than a single falsely precise prediction, and evaluation should use leave-one-model-out validation so performance reflects generalization across climate models rather than random grid-cell interpolation.
