# Phase 6 geographic definitions

All regions are clipped to the original study rectangle, 24-38°N and 100-74°W. State groupings are intentionally broad because the four model grids do not support county-scale interpretation.

| ID | Definition |
|---|---|
| `original_box` | Complete original rectangle, including land and ocean |
| `southeast_land` | Land in AL, AR, FL, GA, KY, LA, MS, NC, OK, SC, TN, TX, VA, and WV |
| `gulf_coast` | Land in TX, LA, MS, AL, and FL |
| `lower_mississippi` | Land in AR, LA, MS, and TN |
| `atlantic_southeast` | Land in FL, GA, SC, NC, and VA |
| `appalachian_interior` | Land in KY, TN, WV, and VA |

## Sources

- State boundaries: U.S. Census Bureau 2025 Cartographic Boundary Files, states, 1:20,000,000. Source archive and SHA-256 are recorded in `scripts/fetch_phase6_geography.py` and embedded in `data/geography/southeast_states_2025.geojson`.
- Land: Natural Earth 10m Physical Vectors, Land, version 5.1.1. Source archive and SHA-256 are recorded in the same places.

The committed GeoJSON files are clipped derivatives. `python scripts/fetch_phase6_geography.py` downloads, checksum-validates, and regenerates them.

## Weighting

Each native regular latitude-longitude cell is intersected with the selected geometry. The intersection area is calculated on the WGS84 ellipsoid and used as the weight. Explicit one-dimensional coordinate bounds from the NetCDF are used when present; otherwise bounds are inferred from adjacent grid centers. Results report the number of intersecting cells, their summed regional fractions as equivalent cells, and represented area.

The authoritative regional calculations occur on each model's native grid. The common grid is not used to calculate regional means. These approximations resolve partial boundary cells but do not imply sub-grid or county-scale climate information.

