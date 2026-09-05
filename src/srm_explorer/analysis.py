from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "model",
    "scenario",
    "variant_label",
    "grid_label",
    "parent_experiment_id",
    "parent_variant_label",
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
    "txx": "Maximum daily maximum temperature",
    "hwn_tx90_3d": "Heatwave event count (TX90, 3-day minimum)",
    "hwf_tx90_3d": "Heatwave days (TX90, 3-day minimum)",
    "hwd_tx90_3d": "Longest heatwave duration (TX90, 3-day minimum)",
    "rx5day": "Maximum consecutive five-day precipitation",
    "r95ptot": "Very-wet-day precipitation total",
}

COMPARISON_LABELS = {
    "G6solar - SSP5-8.5": "G6solar minus SSP5-8.5",
    "G6sulfur - SSP5-8.5": "G6sulfur minus SSP5-8.5",
    "G6solar - G6sulfur": "G6solar minus G6sulfur",
}


def available_phase6_selections(frame: pd.DataFrame) -> list[tuple[str, str, str, str]]:
    """Return only model, metric, season, comparison combinations in the data."""
    required = {"model", "metric", "season", "comparison", "value"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing Phase 6 explorer columns: {sorted(missing)}")
    return sorted(
        frame[["model", "metric", "season", "comparison"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )


def phase6_selection(frame, model, metric, season, comparison):
    available = set(available_phase6_selections(frame))
    key = (model, metric, season, comparison)
    if key not in available:
        raise ValueError(f"Unavailable Phase 6 selection: {key}")
    return frame[
        (frame.model == model) & (frame.metric == metric)
        & (frame.season == season) & (frame.comparison == comparison)
    ].copy()


def make_phase6_map(frame, model, metric, season, comparison):
    selected = phase6_selection(frame, model, metric, season, comparison)
    pivot = selected.pivot(index="lat", columns="lon", values="value").sort_index()
    bound = float(np.nanmax(np.abs(pivot.values)))
    fig, ax = plt.subplots(figsize=(8.2, 5.1), constrained_layout=True)
    mesh = ax.pcolormesh(pivot.columns, pivot.index, pivot.values, shading="nearest",
                         cmap="RdBu_r", vmin=-bound, vmax=bound)
    fig.colorbar(mesh, ax=ax, label=selected.units.iloc[0])
    ax.set(xlabel="Longitude", ylabel="Latitude",
           title=f"{model} | {METRIC_LABELS.get(metric, metric)}\n{season}, {COMPARISON_LABELS.get(comparison, comparison)}")
    ax.grid(alpha=.18)
    return fig


def summarize_phase6_selection(frame, model, metric, season, comparison):
    selected = phase6_selection(frame, model, metric, season, comparison)
    units = selected.units.iloc[0]
    mean=np.average(selected.value,weights=selected.weight)
    summary = pd.DataFrame({"Statistic":["Area-weighted map mean","Map-cell minimum","Map-cell maximum","Model count"],
                            "Value":[f"{mean:.3f} {units}",f"{selected.value.min():.3f} {units}",f"{selected.value.max():.3f} {units}",str(int(selected.model_count.iloc[0]))]})
    scope=selected.model_scope.iloc[0]; domain=selected.domain.iloc[0]; period=selected.period.iloc[0]; grid=selected.grid_kind.iloc[0]
    note=f"**Model-derived Phase 6 result.** {scope}; domain: {domain}; period: {period}; units: {units}; model count: {int(selected.model_count.iloc[0])}; display grid: {grid}."
    return summary,note


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
    key = [
        "model",
        "scenario",
        "variant_label",
        "grid_label",
        "season",
        "metric",
        "lat",
        "lon",
        "period",
    ]
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
    if selected[["model", "grid_label"]].drop_duplicates().shape[0] != 1:
        raise ValueError("Map calculations require exactly one model on one native grid")
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
    matched = _matched_model_grids(frame, scenario, metric, season, reference)
    if matched["model"].nunique() != 1:
        raise ValueError("Difference maps require exactly one matched model grid")
    if matched.empty:
        raise ValueError(f"No matched model-grid records for {scenario} and {reference}")
    matched["difference"] = matched["value"] - matched["reference_value"]
    return (
        matched.groupby(["lat", "lon"], as_index=False)
        .agg(
            value=("difference", "mean"),
            model_spread=("difference", "std"),
            model_count=("model", "nunique"),
        )
        .fillna({"model_spread": 0.0})
    )


def regional_model_means(values: pd.DataFrame) -> pd.DataFrame:
    """Return cosine-latitude-weighted means without mixing model grids."""
    weighted = values.assign(weight=np.cos(np.deg2rad(values["lat"])))
    weighted["weighted_value"] = weighted["value"] * weighted["weight"]
    identity = [column for column in ["model", "variant_label", "grid_label"] if column in values]
    totals = weighted.groupby(identity, as_index=False).agg(
        weighted_value=("weighted_value", "sum"), weight=("weight", "sum")
    )
    totals["value"] = totals["weighted_value"] / totals["weight"]
    return totals[identity + ["value"]]


def _matched_model_grids(
    frame: pd.DataFrame,
    scenario: str,
    metric: str,
    season: str,
    reference: str = "ssp585",
) -> pd.DataFrame:
    """Return target/reference cells only after explicit branch compatibility checks."""
    target = _selection(frame, scenario, metric, season).copy()
    baseline = _selection(frame, reference, metric, season).copy()
    for label, selected in ((scenario, target), (reference, baseline)):
        counts = selected.groupby("model").agg(
            variants=("variant_label", "nunique"), grids=("grid_label", "nunique")
        )
        if (counts > 1).any().any():
            raise ValueError(f"{label} mixes variants or grids within a model")

    target_identity = target[
        [
            "model",
            "variant_label",
            "grid_label",
            "parent_experiment_id",
            "parent_variant_label",
        ]
    ].drop_duplicates()
    reference_identity = baseline[
        [
            "model",
            "variant_label",
            "grid_label",
            "parent_experiment_id",
            "parent_variant_label",
        ]
    ].drop_duplicates()
    identity = target_identity.merge(
        reference_identity,
        on="model",
        how="inner",
        suffixes=("", "_reference"),
        validate="one_to_one",
    )
    direct_parent = (
        (identity["parent_experiment_id"] == reference)
        & (identity["parent_variant_label"] == identity["variant_label_reference"])
        & (identity["variant_label"] == identity["variant_label_reference"])
    )
    common_parent = (
        (identity["parent_experiment_id"] == identity["parent_experiment_id_reference"])
        & (identity["parent_variant_label"] == identity["parent_variant_label_reference"])
        & (identity["variant_label"] == identity["variant_label_reference"])
    )
    incompatible = identity[
        ~(direct_parent | common_parent)
        | (identity["grid_label"] != identity["grid_label_reference"])
    ]
    if not incompatible.empty:
        raise ValueError(
            "Incompatible target/reference branches for models: "
            + ", ".join(sorted(incompatible["model"]))
        )
    if identity.empty:
        raise ValueError(f"No matched models for {scenario} and {reference}")

    allowed = identity[["model"]]
    target = target.merge(allowed, on="model", validate="many_to_one")
    baseline = baseline.merge(allowed, on="model", validate="many_to_one")
    baseline = baseline[
        ["model", "grid_label", "lat", "lon", "value"]
    ].rename(columns={"value": "reference_value"})
    return target.merge(
        baseline,
        on=["model", "grid_label", "lat", "lon"],
        validate="one_to_one",
    )


def regional_differences(
    frame: pd.DataFrame,
    scenario: str,
    metric: str,
    season: str,
    reference: str = "ssp585",
) -> pd.DataFrame:
    """Return one regional difference per model on each model's native grid."""
    matched = _matched_model_grids(frame, scenario, metric, season, reference)
    matched["value"] = matched["value"] - matched["reference_value"]
    result = regional_model_means(matched)
    result["scenario"] = scenario
    result["reference"] = reference
    result["season"] = season
    result["metric"] = metric
    return result


def intervention_differences(
    frame: pd.DataFrame, metric: str, season: str
) -> pd.DataFrame:
    """Return G6solar minus G6sulfur regional response for every matched model."""
    solar = regional_differences(frame, "G6solar", metric, season).rename(
        columns={
            "value": "solar_value",
            "variant_label": "solar_variant_label",
            "grid_label": "solar_grid_label",
        }
    )
    sulfur = regional_differences(frame, "G6sulfur", metric, season).rename(
        columns={
            "value": "sulfur_value",
            "variant_label": "sulfur_variant_label",
            "grid_label": "sulfur_grid_label",
        }
    )
    keep = [
        "model",
        "sulfur_variant_label",
        "sulfur_grid_label",
        "sulfur_value",
    ]
    matched = solar.merge(sulfur[keep], on="model", validate="one_to_one")
    if (matched["solar_grid_label"] != matched["sulfur_grid_label"]).any():
        raise ValueError("G6solar and G6sulfur grids differ within a model")
    matched["value"] = matched["solar_value"] - matched["sulfur_value"]
    matched["scenario"] = "G6solar-minus-G6sulfur"
    return matched[
        [
            "model",
            "solar_variant_label",
            "sulfur_variant_label",
            "solar_grid_label",
            "season",
            "metric",
            "scenario",
            "value",
        ]
    ]


def ensemble_statistics(per_model: pd.DataFrame) -> pd.DataFrame:
    """Summarize an ensemble while retaining explicit sign disagreement metrics."""
    group_columns = [column for column in ["scenario", "season", "metric"] if column in per_model]

    def summarize(group: pd.DataFrame) -> pd.Series:
        values = group["value"]
        positive = float((values > 0).mean())
        negative = float((values < 0).mean())
        return pd.Series(
            {
                "mean": values.mean(),
                "median": values.median(),
                "std": values.std(ddof=1) if len(values) > 1 else 0.0,
                "minimum": values.min(),
                "maximum": values.max(),
                "model_count": values.size,
                "fraction_positive": positive,
                "fraction_negative": negative,
                "sign_agreement": max(positive, negative),
            }
        )

    result = per_model.groupby(group_columns, as_index=False).apply(
        summarize, include_groups=False
    ).reset_index(drop=True)
    result["model_count"] = result["model_count"].astype(int)
    return result


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

    if mode == "Difference from SSP5-8.5" and scenario != "ssp585":
        per_model = regional_differences(frame, scenario, metric, season)
        statistic_label = "Regional mean difference"
        model_label = "Matched models"
    else:
        per_model = regional_model_means(selected)
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
