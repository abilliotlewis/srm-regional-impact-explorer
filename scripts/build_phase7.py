"""Build Phase 7 paired monthly temporal-variability products."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from build_phase1 import build_time_series_frame
from build_phase4 import PR_MANIFESTS, TASMAX_MANIFESTS, model_identities
from srm_explorer.geography import weighted_domain_means
from srm_explorer.temporal import (
    build_per_model_summary,
    ensemble_summary,
    paired_temporal_statistics,
)

DOMAINS = ["original_box", "southeast_land", "gulf_coast"]
PROCESSED = ROOT / "data/processed"
PUBLISHED = ROOT / "data/published"
DOCS = ROOT / "docs"
NATIVE_CACHE = PROCESSED / "phase7_monthly_native_yearly.parquet"
REGIONAL_OUTPUT = PUBLISHED / "phase7_monthly_regional_timeseries.csv.gz"
PAIRED_OUTPUT = PUBLISHED / "phase7_paired_differences.csv.gz"
PER_MODEL_OUTPUT = DOCS / "phase7_per_model_temporal_variability.csv"
ENSEMBLE_OUTPUT = DOCS / "phase7_ensemble_temporal_summary.csv"
BLOCK_SENSITIVITY_OUTPUT = DOCS / "phase7_block_length_sensitivity.csv"


def build_native(download: bool = False) -> pd.DataFrame:
    tasmax = build_time_series_frame(
        TASMAX_MANIFESTS,
        ROOT / "data/raw/tasmax",
        download=download,
        spatial_padding_degrees=3.0,
    )
    precipitation = build_time_series_frame(
        PR_MANIFESTS,
        ROOT / "data/raw/pr",
        download=download,
        spatial_padding_degrees=3.0,
    )
    if model_identities(tasmax) != model_identities(precipitation):
        raise ValueError("tasmax and pr identities differ")
    return pd.concat([tasmax, precipitation], ignore_index=True)


def build_regional(native: pd.DataFrame) -> pd.DataFrame:
    regional = pd.concat(
        [weighted_domain_means(native, domain) for domain in DOMAINS],
        ignore_index=True,
    )
    expected_rows = 4 * 2 * 3 * 3 * (30 * 4 + 29)
    if len(regional) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows:,} regional scenario-year rows, got {len(regional):,}"
        )
    return regional


def write_products(
    regional: pd.DataFrame,
    paired: pd.DataFrame,
    per_model: pd.DataFrame,
    ensemble: pd.DataFrame,
) -> None:
    PUBLISHED.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    gzip_options = {"method": "gzip", "mtime": 0}
    regional.to_csv(
        REGIONAL_OUTPUT,
        index=False,
        float_format="%.7f",
        compression=gzip_options,
    )
    paired.to_csv(
        PAIRED_OUTPUT,
        index=False,
        float_format="%.7f",
        compression=gzip_options,
    )
    per_model.to_csv(PER_MODEL_OUTPUT, index=False, float_format="%.7f")
    ensemble.to_csv(ENSEMBLE_OUTPUT, index=False, float_format="%.7f")
    print(f"Wrote {len(regional):,} regional scenario-year values to {REGIONAL_OUTPUT}")
    print(f"Wrote {len(paired):,} paired year differences to {PAIRED_OUTPUT}")
    print(f"Wrote {len(per_model):,} per-model summaries to {PER_MODEL_OUTPUT}")
    print(f"Wrote {len(ensemble):,} ensemble summaries to {ENSEMBLE_OUTPUT}")


def build_block_sensitivity(paired: pd.DataFrame) -> pd.DataFrame:
    """Stress-test the primary result with three plausible block lengths."""
    identity = [
        "model",
        "variant_label",
        "grid_label",
        "domain",
        "metric",
        "units",
        "season",
    ]
    primary = paired[
        (paired["comparison"] == "G6solar - G6sulfur")
        & (paired["metric"] == "tasmax_mean")
        & (paired["season"] == "JJA")
    ]
    rows = []
    for keys, group in primary.groupby(identity, sort=True):
        metadata = dict(zip(identity, keys, strict=True))
        label = "|".join(str(metadata[column]) for column in identity)
        label += "|G6solar - G6sulfur"
        series = group.sort_values("period_year")["difference"].to_numpy()
        for block_length in (3, 5, 7):
            result = paired_temporal_statistics(
                series,
                label,
                replicates=10_000,
                block_length=block_length,
            )
            rows.append(
                metadata
                | {
                    "comparison": "G6solar - G6sulfur",
                    "tested_block_length_years": block_length,
                    "mean_difference": result["mean_difference"],
                    "ci_lower": result["ci_lower"],
                    "ci_upper": result["ci_upper"],
                    "interval_classification": result["interval_classification"],
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument(
        "--rebuild-native",
        action="store_true",
        help="Ignore the resumable native-grid yearly cache.",
    )
    parser.add_argument("--bootstrap-replicates", type=int, default=10_000)
    args = parser.parse_args()

    PROCESSED.mkdir(parents=True, exist_ok=True)
    if NATIVE_CACHE.exists() and not args.rebuild_native:
        print(f"Reusing {NATIVE_CACHE}", flush=True)
        native = pd.read_parquet(NATIVE_CACHE)
    else:
        print("Building verified native-grid monthly time series", flush=True)
        native = build_native(download=args.download)
        native.to_parquet(NATIVE_CACHE, index=False)
        print(f"Cached {len(native):,} native-grid values at {NATIVE_CACHE}", flush=True)

    regional = build_regional(native)
    paired, per_model = build_per_model_summary(
        regional,
        replicates=args.bootstrap_replicates,
        block_length=5,
    )
    ensemble = ensemble_summary(per_model)
    write_products(regional, paired, per_model, ensemble)
    sensitivity = build_block_sensitivity(paired)
    sensitivity.to_csv(
        BLOCK_SENSITIVITY_OUTPUT, index=False, float_format="%.7f"
    )
    print(f"Wrote {len(sensitivity):,} block-length checks to {BLOCK_SENSITIVITY_OUTPUT}")


if __name__ == "__main__":
    main()
