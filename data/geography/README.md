# Phase 6 geographic inputs

Phase 6 freezes the U.S. Census Bureau 2025 state Cartographic Boundary File at 1:20,000,000 and Natural Earth 10m Physical Vectors Land version 5.1.1. State membership and visible boundaries come from Census; land versus water comes from Natural Earth. Both are clipped to 24–38°N, 100–74°W. The boundary detail does not create county-scale climate information.

Regenerate and checksum-verify the committed subsets with `python scripts/fetch_phase6_geography.py`.
