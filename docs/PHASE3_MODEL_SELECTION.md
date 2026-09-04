# Phase 3 model selection

Version: 1.0 (Phase 3 selection frozen, 2026-09-04)

## Purpose

Phase 3 compares late-century regional `tasmax` responses to G6solar and G6sulfur over the same Southeast United States domain used in Phases 1 and 2. The objective is the strongest defensible multimodel comparison, not the largest possible model count.

The analysis period is 2071-2100. A model is eligible for the direct ensemble only when usable monthly `tasmax` exists for G6solar, G6sulfur, and SSP5-8.5, the intervention runs can be matched to an appropriate SSP5-8.5 parent or reference member, and the provenance is sufficiently clear to reproduce the comparison. Each model is processed on its own native grid before regional values are combined.

## Selection rules

A model is included only if all of the following hold:

1. Monthly `tasmax` covers every month required for the 2071-2100 annual and seasonal calculations.
2. G6solar, G6sulfur, and SSP5-8.5 data are available without substituting an undeclared ensemble member.
3. Exact experiment, variant, grid, version, institution, and source identifiers are retained.
4. G6 parent experiment and parent variant metadata are compatible with the selected SSP5-8.5 run, where parent metadata is supplied.
5. Files pass byte-count and SHA-256 verification and can be read as CF-style NetCDF.
6. The three experiments can be compared on the model's own grid. No grid-cell averaging across models is used.

Failure of any rule excludes the model from the direct ensemble. An excluded model may be reconsidered only through a new, documented version of this file and its data manifest.

## Availability audit

The [PCMDI GeoMIP holdings inventory](https://pcmdi.llnl.gov/CMIP6/ArchiveStatistics/esgf_data_holdings/GeoMIP/) identifies six CMIP6 source models with G6solar and G6sulfur contributions. Holdings at the experiment level are not treated as proof that `tasmax` is present. Each source model was therefore checked at the variable, table, experiment, variant, grid, and file level.

| Model | Institution | G6solar | G6sulfur | SSP5-8.5 | Decision | Reason |
|---|---|---|---|---|---|---|
| CNRM-ESM2-1 | CNRM-CERFACS | `r1i1p1f2`, `gr`, Amon | `r1i1p1f2`, `gr`, Amon | `r1i1p1f2`, `gr`, Amon | Include | The three runs use one variant and grid and identify the same historical `r1i1p1f2` parent. Files pass checksum, identity, and coverage checks. |
| IPSL-CM6A-LR | IPSL | `r1i1p1f1`, `gr`, Amon | `r1i1p1f1`, `gr`, Amon | `r1i1p1f1`, `gr`, Amon | Include | Existing Phase 1 files pass checksum and embedded identity/parent checks. Both G6 runs identify SSP5-8.5 `r1i1p1f1` as parent. |
| MPI-ESM1-2-LR | MPI-M | `r2i1p1f1`, `gn`, Amon | `r2i1p1f1`, `gn`, Amon | `r2i1p1f1`, `gn`, Amon | Include | Existing Phase 2 files pass checksum and embedded identity/parent checks. Both G6 runs identify SSP5-8.5 `r2i1p1f1` as parent. |
| UKESM1-0-LL | MOHC | `r1i1p1f2`, `gn`, Amon | `r1i1p1f2`, `gn`, Amon | `r1i1p1f2`, `gn`, Amon | Include | Both G6 files identify SSP5-8.5 `r1i1p1f2` as parent. Files pass checksum, identity, and coverage checks. |
| CESM2-WACCM | NCAR | `r1i1p1f1`, `gn`, Amon | `r2i1p1f2`, `gn`, Amon | `r1i1p1f1` available | Exclude | The available G6solar and G6sulfur `tasmax` use different variants. G6solar identifies SSP5-8.5 `r1i1p1f1` as parent, while the inspected G6sulfur file reports no parent. This does not meet the matched-run rule. |
| MPI-ESM1-2-HR | MPI-M | no usable `tasmax` found | no usable `tasmax` found | not evaluated further | Exclude | Experiment holdings exist, but the inspected atmospheric monthly and daily archives do not provide the required `tasmax` triplet. Available monthly variables do not justify substituting `tas` for `tasmax`. |

## Selected file sets

The authoritative record-level provenance is stored in versioned JSON manifests under `data/manifests/`. Those manifests retain the source URL, dataset version, tracking ID when supplied by the file, byte count, SHA-256 checksum, institution, source ID, experiment ID, variant label, grid label, and license. Raw NetCDF files remain outside Git.

The frozen Phase 3 ensemble contains four models: CNRM-ESM2-1, IPSL-CM6A-LR, MPI-ESM1-2-LR, and UKESM1-0-LL. CNRM uses a documented matched-sibling pattern: G6solar, G6sulfur, and SSP5-8.5 all identify historical `r1i1p1f2` as their parent. The other three models use G6 runs that identify the selected SSP5-8.5 variant directly. The analysis code accepts these two explicit matching patterns and rejects undeclared substitutions, mixed grids, and unrelated parent branches.

## Known data and quality issues

- CMIP6 archive coverage can be experiment-complete but variable-incomplete. The selection audit therefore distinguishes experiment holdings from usable `tasmax` files.
- Grid labels differ among selected models. Regional calculations remain native-grid calculations with latitude-aware area weights; model fields are not regridded and then averaged cell by cell.
- DJF requires special treatment across calendar-year boundaries. Phase 3 uses only complete winters and reports the exact seasonal-year range.
- A small ensemble does not imply robustness. Results will report every model, spread, extrema, count, sign agreement, and disagreement alongside means and medians.

## Change log

- 0.1: Added explicit eligibility rules and the six-model GeoMIP/CMIP6 availability audit. Marked CNRM-ESM2-1 and UKESM1-0-LL provisional pending file-level verification; excluded CESM2-WACCM and MPI-ESM1-2-HR from the direct comparison with reasons.
- 1.0: Froze the four-model ensemble after file-level checksum, time coverage, identity, grid, variant, tracking-ID, license, and parent-metadata validation. Documented CNRM's matched historical-parent sibling branches.
