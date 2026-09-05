"""Paired temporal-variability statistics for Phase 7 monthly results."""

from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from srm_explorer.uncertainty import lag1_autocorrelation, moving_block_means

COMPARISONS = {
    "G6solar - G6sulfur": ("G6solar", "G6sulfur"),
    "G6solar - SSP5-8.5": ("G6solar", "ssp585"),
    "G6sulfur - SSP5-8.5": ("G6sulfur", "ssp585"),
}
EXPECTED_YEARS = {
    "ANN": tuple(range(2071, 2101)),
    "MAM": tuple(range(2071, 2101)),
    "JJA": tuple(range(2071, 2101)),
    "SON": tuple(range(2071, 2101)),
    "DJF": tuple(range(2072, 2101)),
}


def stable_seed(label: str) -> int:
    """Return a stable 32-bit seed derived from a complete analysis identity."""
    return int.from_bytes(hashlib.sha256(label.encode()).digest()[:4], "big")


def interval_classification(lower: float, upper: float) -> str:
    if lower > upper:
        raise ValueError("Confidence interval lower bound exceeds upper bound")
    if lower > 0:
        return "above_zero"
    if upper < 0:
        return "below_zero"
    return "includes_zero"


def paired_series(
    values: pd.DataFrame,
    target: str,
    reference: str,
) -> pd.DataFrame:
    """Align two experiments exactly by period year and subtract target-reference."""
    target_values = values.loc[
        values["scenario"] == target, ["period_year", "value"]
    ].sort_values("period_year")
    reference_values = values.loc[
        values["scenario"] == reference, ["period_year", "value"]
    ].sort_values("period_year")
    if target_values["period_year"].duplicated().any() or reference_values[
        "period_year"
    ].duplicated().any():
        raise ValueError("Each experiment must have one value per period year")
    target_years = tuple(target_values["period_year"].astype(int))
    reference_years = tuple(reference_values["period_year"].astype(int))
    if not target_years or target_years != reference_years:
        raise ValueError(
            f"Paired experiments have different period years: {target_years} vs {reference_years}"
        )
    paired = target_values.merge(
        reference_values,
        on="period_year",
        how="inner",
        validate="one_to_one",
        suffixes=("_target", "_reference"),
    )
    paired["difference"] = paired["value_target"] - paired["value_reference"]
    return paired


def paired_temporal_statistics(
    differences: np.ndarray,
    label: str,
    replicates: int = 10_000,
    block_length: int = 5,
) -> dict[str, float | int | str | bool]:
    """Summarize paired differences and their moving-block interval."""
    series = np.asarray(differences, dtype=float)
    if series.ndim != 1 or series.size < 2 or not np.isfinite(series).all():
        raise ValueError("Paired differences must be a finite one-dimensional series")
    standard_deviation = float(np.std(series, ddof=1))
    mean = float(np.mean(series))
    bootstrapped = moving_block_means(
        series,
        replicates=replicates,
        block_length=block_length,
        seed=stable_seed(label),
    )
    lower, upper = np.quantile(bootstrapped, [0.025, 0.975])
    classification = interval_classification(float(lower), float(upper))
    return {
        "mean_difference": mean,
        "median_difference": float(np.median(series)),
        "paired_interannual_sd": standard_deviation,
        "standard_error": standard_deviation / np.sqrt(series.size),
        "standardized_effect_size": mean / standard_deviation
        if standard_deviation
        else np.nan,
        "minimum_difference": float(np.min(series)),
        "maximum_difference": float(np.max(series)),
        "year_count": int(series.size),
        "fraction_positive": float(np.mean(series > 0)),
        "fraction_negative": float(np.mean(series < 0)),
        "fraction_zero": float(np.mean(series == 0)),
        "lag1_autocorrelation": lag1_autocorrelation(series),
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "interval_classification": classification,
        "zero_inside_interval": classification == "includes_zero",
        "bootstrap_replicates": int(replicates),
        "block_length_years": int(block_length),
    }


def validate_expected_years(values: pd.DataFrame) -> None:
    """Require the exact complete-period convention for every time series."""
    identity = ["model", "domain", "metric", "scenario", "season"]
    for keys, group in values.groupby(identity, sort=True):
        season = keys[-1]
        observed = tuple(sorted(group["period_year"].astype(int)))
        expected = EXPECTED_YEARS[season]
        if observed != expected:
            label = dict(zip(identity, keys, strict=True))
            raise ValueError(f"Unexpected period years for {label}: {observed}")


def build_per_model_summary(
    regional: pd.DataFrame,
    replicates: int = 10_000,
    block_length: int = 5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build paired year-level differences and model-level temporal summaries."""
    validate_expected_years(regional)
    identity = [
        "model",
        "variant_label",
        "grid_label",
        "domain",
        "metric",
        "units",
        "season",
    ]
    paired_rows: list[pd.DataFrame] = []
    summary_rows: list[dict] = []
    for keys, group in regional.groupby(identity, sort=True):
        metadata = dict(zip(identity, keys, strict=True))
        for comparison, (target, reference) in COMPARISONS.items():
            paired = paired_series(group, target, reference)
            label = "|".join(str(metadata[column]) for column in identity) + f"|{comparison}"
            summary = paired_temporal_statistics(
                paired["difference"].to_numpy(),
                label,
                replicates=replicates,
                block_length=block_length,
            )
            summary_rows.append(metadata | {"comparison": comparison} | summary)
            paired_rows.append(
                paired[["period_year", "difference"]].assign(
                    **metadata,
                    comparison=comparison,
                )
            )
    return pd.concat(paired_rows, ignore_index=True), pd.DataFrame(summary_rows)


def ensemble_summary(per_model: pd.DataFrame) -> pd.DataFrame:
    """Summarize model means without blending temporal and structural uncertainty."""
    identity = ["domain", "metric", "units", "season", "comparison"]
    rows = []
    for keys, group in per_model.groupby(identity, sort=True):
        values = group["mean_difference"].to_numpy(dtype=float)
        rows.append(
            dict(zip(identity, keys, strict=True))
            | {
                "model_count": int(values.size),
                "positive_mean_count": int(np.sum(values > 0)),
                "negative_mean_count": int(np.sum(values < 0)),
                "zero_mean_count": int(np.sum(values == 0)),
                "temporal_ci_positive_count": int(
                    np.sum(group["interval_classification"] == "above_zero")
                ),
                "temporal_ci_negative_count": int(
                    np.sum(group["interval_classification"] == "below_zero")
                ),
                "temporal_ci_includes_zero_count": int(
                    np.sum(group["interval_classification"] == "includes_zero")
                ),
                "ensemble_mean_difference": float(np.mean(values)),
                "ensemble_median_difference": float(np.median(values)),
                "inter_model_sd": float(np.std(values, ddof=1)),
                "minimum_model_mean": float(np.min(values)),
                "maximum_model_mean": float(np.max(values)),
            }
        )
    return pd.DataFrame(rows)
