"""Build and validate compact manuscript-support tables from published outputs."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PER_MODEL = DOCS / "phase7_per_model_temporal_variability.csv"
ENSEMBLE = DOCS / "phase7_ensemble_temporal_summary.csv"
PHASE6 = DOCS / "phase6_domain_per_model.csv"
OUTPUT = DOCS / "MANUSCRIPT_KEY_RESULTS.csv"

DOMAINS = ("original_box", "southeast_land", "gulf_coast")
RESULTS = (
    ("tasmax_mean", "JJA"),
    ("tasmax_mean", "MAM"),
    ("pr_mean", "JJA"),
    ("pr_mean", "ANN"),
)
MODELS = {
    "CNRM-ESM2-1",
    "IPSL-CM6A-LR",
    "MPI-ESM1-2-LR",
    "UKESM1-0-LL",
}
FIGURES = (
    "phase3_tasmax_ensemble.png",
    "phase4_pr_ensemble.png",
    "phase6_domain_sensitivity.png",
    "phase6_pr_jja_ensemble_maps.png",
    "phase6_tasmax_jja_ensemble_maps.png",
    "phase7_cross_result_robustness.png",
    "phase7_jja_tasmax_temporal_intervals.png",
)


def validate_published_inputs(per_model: pd.DataFrame, ensemble: pd.DataFrame) -> None:
    """Reject incomplete or internally inconsistent manuscript inputs."""
    if set(per_model["model"]) != MODELS:
        raise ValueError("Phase 7 model set is not the verified four-model ensemble")

    phase7_direct = per_model[
        (per_model["comparison"] == "G6solar - G6sulfur")
        & per_model["domain"].isin(DOMAINS)
    ]
    phase6 = pd.read_csv(PHASE6)
    phase6 = phase6[
        (phase6["comparison"] == "G6solar - G6sulfur")
        & phase6["domain"].isin(DOMAINS)
    ]
    keys = ["model", "domain", "metric", "season", "comparison", "units"]
    merged = phase7_direct.merge(phase6, on=keys, validate="one_to_one")
    if len(merged) != 120 or not np.allclose(
        merged["mean_difference"], merged["value"], atol=5e-7
    ):
        raise ValueError("Phase 7 means do not reproduce Phase 6 regional means")

    if len(ensemble) != 90:
        raise ValueError("Phase 7 ensemble summary is incomplete")
    missing_figures = [name for name in FIGURES if not (DOCS / name).is_file()]
    if missing_figures:
        raise FileNotFoundError(f"Missing source figures: {missing_figures}")


def build_key_results() -> pd.DataFrame:
    """Return the 48 model rows most likely to be cited in the manuscript."""
    per_model = pd.read_csv(PER_MODEL)
    ensemble = pd.read_csv(ENSEMBLE)
    validate_published_inputs(per_model, ensemble)

    requested = pd.DataFrame(RESULTS, columns=["metric", "season"])
    subset = per_model[
        (per_model["comparison"] == "G6solar - G6sulfur")
        & per_model["domain"].isin(DOMAINS)
    ].merge(requested, on=["metric", "season"], validate="many_to_one")
    summary = ensemble[
        (ensemble["comparison"] == "G6solar - G6sulfur")
        & ensemble["domain"].isin(DOMAINS)
    ].merge(requested, on=["metric", "season"], validate="many_to_one")

    summary_columns = [
        "domain",
        "metric",
        "units",
        "season",
        "comparison",
        "model_count",
        "positive_mean_count",
        "negative_mean_count",
        "temporal_ci_positive_count",
        "temporal_ci_negative_count",
        "temporal_ci_includes_zero_count",
        "ensemble_mean_difference",
        "ensemble_median_difference",
        "inter_model_sd",
    ]
    result = subset.merge(
        summary[summary_columns],
        on=["domain", "metric", "units", "season", "comparison"],
        validate="many_to_one",
    )
    result["variable"] = result["metric"].map(
        {"tasmax_mean": "tasmax", "pr_mean": "pr"}
    )
    result["sign_fraction_direction"] = np.where(
        result["mean_difference"] < 0, "negative", "positive"
    )
    result["sign_fraction"] = np.where(
        result["mean_difference"] < 0,
        result["fraction_negative"],
        result["fraction_positive"],
    )
    result["source_per_model"] = "docs/phase7_per_model_temporal_variability.csv"
    result["source_ensemble"] = "docs/phase7_ensemble_temporal_summary.csv"
    result = result.rename(
        columns={
            "paired_interannual_sd": "paired_sd",
            "standardized_effect_size": "effect_size",
            "ci_lower": "bootstrap_lower",
            "ci_upper": "bootstrap_upper",
            "ensemble_mean_difference": "ensemble_mean",
        }
    )

    columns = [
        "domain",
        "variable",
        "season",
        "comparison",
        "model",
        "variant_label",
        "grid_label",
        "units",
        "mean_difference",
        "paired_sd",
        "effect_size",
        "bootstrap_lower",
        "bootstrap_upper",
        "interval_classification",
        "sign_fraction",
        "sign_fraction_direction",
        "fraction_positive",
        "fraction_negative",
        "ensemble_mean",
        "ensemble_median_difference",
        "inter_model_sd",
        "model_count",
        "positive_mean_count",
        "negative_mean_count",
        "temporal_ci_positive_count",
        "temporal_ci_negative_count",
        "temporal_ci_includes_zero_count",
        "source_per_model",
        "source_ensemble",
    ]
    result = result[columns].sort_values(
        ["variable", "season", "domain", "model"]
    )
    if len(result) != 48:
        raise ValueError(f"Expected 48 manuscript rows, found {len(result)}")
    return result.reset_index(drop=True)


def main() -> None:
    result = build_key_results()
    result.to_csv(OUTPUT, index=False, float_format="%.7f")
    print(f"Wrote {len(result)} verified manuscript rows to {OUTPUT}")


if __name__ == "__main__":
    main()
