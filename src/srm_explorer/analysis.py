from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "model",
    "scenario",
    "season",
    "metric",
    "lat",
    "lon",
    "value",
    "units",
    "period",
    "is_demo",
}

SCENARIO_LABELS = {
    "ssp585": "SSP5-8.5",
    "ssp245": "SSP2-4.5",
    "G6solar": "G6solar: reduced irradiance",
    "G6sulfur": "G6sulfur: sulfate aerosol",
}

METRIC_LABELS = {
    "tasmax_mean": "Mean daily maximum temperature",
    "pr_mean": "Mean precipitation rate",
    "rx1day": "Maximum one-day precipitation",
    "cdd": "Consecutive dry days",
}


def load_metrics(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    frame["is_demo"] = frame["is_demo"].astype(str).str.lower().map(
        {"true": True, "false": False}
    )
    if frame["is_demo"].isna().any():
        raise ValueError("is_demo must contain only true or false")
    if frame[["lat", "lon", "value"]].isna().any().any():
        raise ValueError("lat, lon, and value cannot contain missing values")
    if frame["is_demo"].nunique() != 1:
        raise ValueError("Do not mix demonstration and model-derived records in one explorer file")
    key = ["model", "scenario", "season", "metric", "lat", "lon", "period"]
    if frame.duplicated(key).any():
        raise ValueError(f"Duplicate records found for key {key}")
    return frame


def _selection(
    frame: pd.DataFrame, scenario: str, metric: str, season: str
) -> pd.DataFrame:
    selected = frame[
        (frame["scenario"] == scenario)
        & (frame["metric"] == metric)
        & (frame["season"] == season)
    ].copy()
    if selected.empty:
        raise ValueError(
            f"No records for scenario={scenario}, metric={metric}, season={season}"
        )
    return selected


def grid_mean(
    frame: pd.DataFrame, scenario: str, metric: str, season: str
) -> pd.DataFrame:
    selected = _selection(frame, scenario, metric, season)
    grouped = (
        selected.groupby(["lat", "lon"], as_index=False)
        .agg(value=("value", "mean"), model_spread=("value", "std"), model_count=("model", "nunique"))
        .fillna({"model_spread": 0.0})
    )
    return grouped


def difference_grid(
    frame: pd.DataFrame,
    scenario: str,
    metric: str,
    season: str,
    reference: str = "ssp585",
) -> pd.DataFrame:
    target = _selection(frame, scenario, metric, season)[
        ["model", "lat", "lon", "value"]
    ].rename(columns={"value": "target_value"})
    baseline = _selection(frame, reference, metric, season)[
        ["model", "lat", "lon", "value"]
    ].rename(columns={"value": "reference_value"})
    matched = target.merge(baseline, on=["model", "lat", "lon"], validate="one_to_one")
    if matched.empty:
        raise ValueError(f"No matched model-grid records for {scenario} and {reference}")
    matched["difference"] = matched["target_value"] - matched["reference_value"]
    return (
        matched.groupby(["lat", "lon"], as_index=False)
        .agg(
            value=("difference", "mean"),
            model_spread=("difference", "std"),
            model_count=("model", "nunique"),
        )
        .fillna({"model_spread": 0.0})
    )


def make_map(
    frame: pd.DataFrame,
    scenario: str,
    metric: str,
    season: str,
    mode: str = "Difference from SSP5-8.5",
):
    selected = _selection(frame, scenario, metric, season)
    if mode == "Difference from SSP5-8.5" and scenario != "ssp585":
        gridded = difference_grid(frame, scenario, metric, season)
        title_suffix = "minus SSP5-8.5"
        cmap = "RdBu_r"
        bound = float(np.nanmax(np.abs(gridded["value"])))
        vmin, vmax = -bound, bound
    else:
        gridded = grid_mean(frame, scenario, metric, season)
        title_suffix = "ensemble mean"
        cmap = "viridis"
        vmin = vmax = None

    pivot = gridded.pivot(index="lat", columns="lon", values="value").sort_index()
    fig, ax = plt.subplots(figsize=(8.2, 5.1), constrained_layout=True)
    mesh = ax.pcolormesh(
        pivot.columns,
        pivot.index,
        pivot.values,
        shading="nearest",
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
    )
    units = selected["units"].iloc[0]
    fig.colorbar(mesh, ax=ax, label=units)
    ax.set(
        xlabel="Longitude",
        ylabel="Latitude",
        title=f"{SCENARIO_LABELS.get(scenario, scenario)} | {METRIC_LABELS.get(metric, metric)}\n{season}, {title_suffix}",
    )
    ax.grid(alpha=0.18)
    return fig


def summarize_region(
    frame: pd.DataFrame,
    scenario: str,
    metric: str,
    season: str,
    mode: str = "Absolute ensemble mean",
) -> tuple[pd.DataFrame, str]:
    selected = _selection(frame, scenario, metric, season)

    def weighted_model_means(values: pd.DataFrame) -> pd.DataFrame:
        weighted = values.assign(weight=np.cos(np.deg2rad(values["lat"])))
        weighted["weighted_value"] = weighted["value"] * weighted["weight"]
        totals = weighted.groupby("model", as_index=False).agg(
            weighted_value=("weighted_value", "sum"), weight=("weight", "sum")
        )
        totals["value"] = totals["weighted_value"] / totals["weight"]
        return totals[["model", "value"]]

    if mode == "Difference from SSP5-8.5" and scenario != "ssp585":
        baseline = _selection(frame, "ssp585", metric, season)[
            ["model", "lat", "lon", "value"]
        ].rename(columns={"value": "reference_value"})
        matched = selected.merge(
            baseline, on=["model", "lat", "lon"], validate="one_to_one"
        )
        matched["value"] = matched["value"] - matched["reference_value"]
        per_model = weighted_model_means(matched)
        statistic_label = "Regional mean difference"
        model_label = "Matched models"
    else:
        per_model = weighted_model_means(selected)
        statistic_label = "Regional mean"
        model_label = "Models"
    units = selected["units"].iloc[0]
    summary = pd.DataFrame(
        {
            "Statistic": [statistic_label, "Inter-model minimum", "Inter-model maximum", model_label],
            "Value": [
                f"{per_model['value'].mean():.2f} {units}",
                f"{per_model['value'].min():.2f} {units}",
                f"{per_model['value'].max():.2f} {units}",
                str(per_model['model'].nunique()),
            ],
        }
    )
    provenance = (
        "SYNTHETIC DEMONSTRATION DATA. These values are interface test data, not climate projections."
        if bool(selected["is_demo"].all())
        else f"Model-derived records for {selected['period'].iloc[0]}. Review source metadata before interpretation."
    )
    return summary, provenance
