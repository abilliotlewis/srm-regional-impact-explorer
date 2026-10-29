# Storm identity and circulation: exploratory validation checkpoint

## Scope

This checkpoint follows the five-state CPC catalog in `../regional/RESULTS.md`. It uses actual rainfall observations, Atlantic HURDAT2 storm tracks and NCEP/NCAR Reanalysis 1 monthly 500-hPa geopotential heights. It screens possible split events and examines circulation associations. It does **not** validate all events as independent storms, attribute rainfall to tropical cyclones, or demonstrate operational forecast skill.

All connected components were reconstructed from the 99th-percentile CPC fields and checked against the previously published event IDs, dates, and footprint sizes before adding location or tropical-cyclone information. There are 2,699 connected footprints across all months of the 1978–2025 loaded record. Winters and summers below use the complete-season windows from the prior analysis.

## Targeted case audit

These cases were selected to diagnose possible problems, not to estimate overall catalog accuracy. CPC dates represent 24-hour periods ending at 12 UTC. The component footprints and tracks are coarse and the comparison does not establish causal attribution.

| Case and independent reference | What the catalog shows | Interpretation |
|---|---|---|
| Tropical Storm Fay, 18–27 August 2008. NHC documents an extended, heavy-rain-producing storm: https://www.nhc.noaa.gov/data/tcr/AL062008_Fay.pdf | Three components overlap the window, IDs 1635, 1636 and 1637. All have Fay as their closest same-day HURDAT2 track, with minimum grid-cell-to-track distances of approximately 4, 80 and 272 km. Component 1635 lasts 19–27 August. | Consistent with possible splitting of rainfall around one cyclone. Proximity alone cannot prove that every component was produced by Fay. |
| Louisiana flood, 11–14 August 2016. NWS describes a slow-moving low and deep tropical moisture: https://www.weather.gov/lix/August2016flood | ID 2135 covers 12–14 August and 86 extreme grid cells across roughly 29.4–31.4°N, 93.9–90.1°W. A separate five-cell component, ID 2136, appears 12 August farther east. Neither has a same-day HURDAT2 track in the screen. | The large component captures the timing and broad Louisiana footprint of the documented event. Whether the eastern component is part of the same weather system requires analysis beyond this test. A tropical moisture source does not imply a HURDAT2 cyclone. |
| Harvey, 25–31 August 2017. NWS reports extensive heavy rain in southeast Texas and southwest Louisiana: https://www.weather.gov/lch/2017Harvey | ID 2208 spans 27–31 August, with a nearest Harvey track point about 4 km from an extreme cell. ID 2209 spans 30–31 August and is 436 km from a Harvey track point. ID 2210 is 529 km from the closest track point and falls outside the 500-km screen. | The main footprint coincides with Harvey in time and space. The secondary components show both possible splitting and sensitivity to an arbitrary proximity radius. |

For each footprint, the audit file records the date and the closest six-hourly or special HURDAT2 track point to any extreme cell during the same CPC reporting day. CPC's 12 UTC day boundary is handled explicitly. Proximity records include tropical depressions, storms, hurricanes, subtropical systems, extratropical systems and lows when present in HURDAT2. It is possible for a nearby cyclone and rain to be unrelated; tropical moisture or predecessor rain events far from a center may also be missed. HURDAT2 does not include every tropical disturbance. NOAA's own rainfall attribution workflow uses additional radar, satellite, maps and reports: https://www.wpc.ncep.noaa.gov/tropical/rain/TCrainmethodology.html .

## Tropical-cyclone proximity sensitivity

The screen identifies 223, 293 and 337 of 2,699 all-season footprints within 250, 500 and 750 km, respectively, of at least one qualifying same-day Atlantic track point. These are counts of nearby footprints, not numbers of distinct hurricanes or confirmed storm-attributed events. At 500 km, 293 components have 135 distinct nearest storm IDs. Multiple components close to the same storm are consistent with possible splitting, but do not establish it.

| Summer connected-footprint definition | Mean episodes per summer | Variance / mean |
|---|---:|---:|
| All components | 20.51 | 2.91 |
| Exclude components within 250 km of a track | 18.30 | 2.90 |
| Exclude components within 500 km of a track | 17.15 | 2.91 |
| Exclude components within 750 km of a track | 16.53 | 2.85 |
| Keep at most one 500-km-near component per nearest cyclone ID and season | 18.55 | 2.74 |

The last row is a deliberately strong grouping sensitivity: the remaining non-near components are counted individually, and all nearby components sharing a nearest cyclone ID in a season are counted once. It may merge unrelated rain or fail to merge cyclone rain beyond the radius. Even after this exercise, the catalog's summer variance remains well above the stationary Poisson expectation. This is not proof that distinct storms cluster, because the identification problem also affects non-tropical systems and the seasonal event rate may vary. Excluding 500-km-near components changes no winter counts in this sample. The results depend on threshold, product, region, and selected time period, and they do not amount to a definitive tropical versus non-tropical attribution.

## Coastal versus inland footprint counts

Grid-cell centers within 100 km great-circle distance of the Natural Earth 1:110m coastline are labeled coastal; all other retained five-state centers are inland. Florida's Atlantic coast is included. Distances use an interpolated simplified coastline and grid centers, not fractional land area or exact tidal coastlines. There are 377 coastal and 668 inland cells. Components are reconstructed separately within each subset and filtered to at least four unique cells in that subset. A storm crossing the boundary can be counted in both subsets, or split or omitted, so the categories are not additive or independent. Daily completeness was screened for the full region rather than separately by subregion.

| Area | Winter mean | Winter variance / mean | Summer mean | Summer variance / mean |
|---|---:|---:|---:|---:|
| Coastal, ≤100 km | 5.30 | 3.17 | 9.81 | 1.82 |
| Inland, >100 km | 8.11 | 2.17 | 12.11 | 2.96 |

No formal test of the difference between coastal and inland dispersion was conducted. Differences in area, event splitting and the coastal cutoff can explain part of these contrasts. Raw seasons and additional summaries are in `output/coastal_inland_counts.csv` and `output/coastal_inland_summary.csv`.

## Retrospective circulation composites

The atmospheric source is NOAA PSL NCEP/NCAR Reanalysis 1, a 2.5° monthly-mean geopotential-height dataset. The regional 500-hPa subset is downloaded for 1978–2025. This is a coarser reanalysis alternative to ERA5, not ERA5: https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.html . The downloaded subset uses 500 hPa, 10–70°N and 220–330°E. Seasonal means are equal-weight averages of three monthly means, rather than day-weighted means. DJF season years follow the rainfall catalog.

For each season, we sort the unmodified connected-footprint counts and compare upper-quartile active seasons with lower-quartile quiet seasons, including ties. Thus the composites use rainfall information from the same season and are explanatory comparisons, not pre-season predictors. At the 32.5°N, 90°W grid point:

| Season | Active vs quiet samples | 500-hPa height difference, active minus quiet |
|---|---:|---:|
| Winter | 13 vs 12 seasons | −25.4 m |
| Summer | 13 vs 14 seasons | −15.4 m |

See `output/height_composites.png` and the gridded CSV files. The maps show the observed difference between selected groups; they do not establish which circulation mechanism produced the rain. A lower seasonal-mean height is consistent with a difference in large-scale circulation, but monthly mean heights alone do not establish a jet shift, blocking, moisture transport, persistence, causal pathways or forecast lead-time skill. The stored single-grid permutation diagnostic ignores temporal dependence and spatial multiple comparisons and was not a prespecified confirmatory test. Selection of extreme wet and quiet years, dependence between years, reanalysis changes, and small samples constrain interpretation.

## Conclusions and next work

1. The catalog successfully locates broad footprints for documented high-impact events, while Fay and Harvey show why counting spatial components as independent storms is unsafe.
2. The tropical-track sensitivity does not remove summer excess variance for this footprint definition. Because proximity is not rainfall attribution and non-tropical split events remain, H1 for independent storms remains inconclusive.
3. Active and quiet seasons have different retrospective 500-hPa height composites. This is consistent with an atmospheric association, but H2's causal pathways and H3 residual storm dependence remain untested.
4. The prior winter ENSO hindcast is unchanged. No new pre-season circulation forecast validation was performed, and H4 remains unconfirmed.
5. The next meaningful step is a two-stage rain-object tracker using lower-threshold rain fields, displacement and synoptic continuity, with a blinded manual audit of a representative stratified event sample and multiple independent reviewers. This should be followed by an independent precipitation-product comparison, tropical-rainfall attribution, ERA5 moisture-flux and circulation-regime analysis, and archived-predictor forecast validation.

## Provenance and software

The source manifest records SHA-256 of the downloaded HURDAT2 file, the reanalysis subset used, and the included Natural Earth coastline. Exact source URLs and subset instructions are in `README.md` and `download_inputs.py`. Reanalysis subset metadata or bytes may change when the provider updates the product. The full CPC manifest is in `../regional/output/source_manifest.csv`. NCEP–NCAR Reanalysis 1 data are provided by NOAA PSL, Boulder, Colorado, https://psl.noaa.gov. HURDAT2 format documentation: https://www.nhc.noaa.gov/data/hurdat/hurdat2-format-atl-1851-2021.pdf .
