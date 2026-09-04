# GeoMIP Data Plan

## First publishable question

How do `G6solar` and `G6sulfur` differ from `ssp585` in late-century Southeast US summer heat and precipitation, and how consistent are those differences across participating Earth system models?

## Phase 1 scope

- Region: 24–38°N, 100–74°W
- Future climatology: 2071–2100
- Scenarios: `ssp585`, `ssp245`, `G6solar`, `G6sulfur`
- Seasons: annual, DJF, MAM, JJA, SON
- Start with monthly `tasmax` and `pr`
- Add daily `tasmax` and `pr` only after the monthly workflow passes validation

## Candidate CMIP variables

| Explorer metric | CMIP variable | Frequency | Processing |
| --- | --- | --- | --- |
| Mean maximum temperature | `tasmax` | monthly or daily | Convert K to °C, seasonal mean |
| Mean precipitation | `pr` | monthly or daily | Convert kg m-2 s-1 to mm/day, seasonal mean |
| Maximum one-day rain | `pr` | daily | Annual or seasonal maximum |
| Consecutive dry days | `pr` | daily | Maximum run with precipitation below 1 mm/day |

## Model-selection rules

1. Require all four scenarios from the same model when making direct four-way comparisons.
2. Use a single ensemble member per model for the first release, preferably `r1i1p1f1` when available.
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

## AI component after the scientific baseline

Train a lightweight emulator only after the multi-model table is validated. Inputs can include latitude, longitude, season, scenario and baseline climatology. Outputs should be distributions or quantiles, not a single falsely precise prediction. Evaluate with leave-one-model-out validation so performance reflects generalization across climate models rather than random grid-cell interpolation.

