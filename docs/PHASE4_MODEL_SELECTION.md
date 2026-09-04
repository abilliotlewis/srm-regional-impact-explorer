# Phase 4 precipitation model selection

Version: 1.0 (Phase 4 selection frozen, 2026-09-04)

## Objective

Phase 4 adds monthly mean precipitation (`pr`) to the existing Southeast U.S. comparison of G6solar, G6sulfur, and SSP5-8.5. The domain, 2071-2100 analysis period, seasons, native-grid regional calculations, and uncertainty reporting remain unchanged from Phase 3.

The primary ensemble is deliberately restricted to the four Phase 3 models. This preserves a common model sample across `tasmax` and `pr`, allowing cross-variable comparisons without changing model composition. Phase 4 does not include daily precipitation extremes, new regional boundaries, an emulator, or spatial agreement maps.

## Eligibility rules

A model is eligible only when:

1. Monthly `pr` is available for G6solar, G6sulfur, and SSP5-8.5 through December 2100.
2. The exact Phase 3 variant and grid can be used for all three precipitation experiments.
3. The parent or matched-sibling relationship remains compatible with the Phase 3 comparison.
4. File-level version, tracking ID, byte count, SHA-256 checksum, institution, source ID, experiment, variant, grid, source URL, and license are retained.
5. The files pass embedded metadata, time-coverage, unit, and missing-data validation.

No ensemble-member substitution is allowed to increase model count.

## Availability audit

The ESGF Search API was queried at file level for `table_id=Amon`, `variable_id=pr`, the exact Phase 3 variants, and the three required experiments.

| Model | Variant | Grid | G6solar | G6sulfur | SSP5-8.5 | Status |
|---|---|---|---|---|---|---|
| CNRM-ESM2-1 | `r1i1p1f2` | `gr` | 2015-2100 | 2015-2100 | 2015-2100 | Include |
| IPSL-CM6A-LR | `r1i1p1f1` | `gr` | 2020-2100 | 2020-2100 | 2015-2100 | Include |
| MPI-ESM1-2-LR | `r2i1p1f1` | `gn` | segmented through 2100 | segmented through 2100 | segmented through 2100 | Include |
| UKESM1-0-LL | `r1i1p1f2` | `gn` | 2050-2100 | 2050-2100 | 2050-2100 | Include |

All four models passed file-size and SHA-256 checks, embedded source and experiment identity checks, tracking-ID checks, parent and variant compatibility checks, exact monthly coverage checks, and precipitation-unit validation. The 18 source files comprise three each for CNRM-ESM2-1, IPSL-CM6A-LR, and UKESM1-0-LL and nine segmented MPI-ESM1-2-LR files.

## Comparability with Phase 3

The precipitation records use the same variants and grids as the Phase 3 temperature records. CNRM-ESM2-1 retains the matched-sibling structure in which all three experiments identify historical `r1i1p1f2` as parent. IPSL-CM6A-LR, MPI-ESM1-2-LR, and UKESM1-0-LL retain G6 runs associated with their selected SSP5-8.5 variant. Embedded metadata was checked rather than inferred from filenames alone. No member, grid, or parent branch was substituted.

## Exclusions and scope

No Phase 3 model was excluded because all four exact model-member-grid combinations had a complete precipitation triplet. Models excluded from Phase 3 were not reintroduced: doing so would change the model sample across variables and weaken direct comparison with the temperature checkpoint. This is a deliberate comparability decision, not a claim that no other GeoMIP model has precipitation output.

Daily precipitation and derived extremes are excluded because Phase 4 is restricted to monthly mean precipitation. Raw NetCDF remains outside Git; the manifests are the versioned source record.

## Change log

- 0.1: Defined the fixed four-model Phase 4 sample and recorded file-level monthly precipitation availability for the exact Phase 3 variants.
- 1.0: Froze the four-model selection after all 18 files passed checksum, identity, parent, tracking, units, and 2071-2100 coverage validation.
