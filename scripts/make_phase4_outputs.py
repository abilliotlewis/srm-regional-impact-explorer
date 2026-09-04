"""Create Phase 4 precipitation tables and publication figures."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from srm_explorer.analysis import (  # noqa: E402
    ensemble_statistics,
    intervention_differences,
    load_metrics,
    regional_differences,
)

SEASONS = ["DJF", "MAM", "JJA", "SON", "ANN"]
COLORS = {"G6solar - SSP5-8.5": "#2166ac", "G6sulfur - SSP5-8.5": "#b35806"}


def calculate(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for season in SEASONS:
        for scenario, comparison in (
            ("G6solar", "G6solar - SSP5-8.5"),
            ("G6sulfur", "G6sulfur - SSP5-8.5"),
        ):
            values = regional_differences(frame, scenario, "pr_mean", season)
            for record in values.to_dict("records"):
                rows.append(
                    {
                        "model": record["model"],
                        "season": season,
                        "comparison": comparison,
                        "target_variant_label": record["variant_label"],
                        "reference_variant_label": frame.loc[
                            (frame.model == record["model"])
                            & (frame.scenario == "ssp585")
                            & (frame.metric == "pr_mean"),
                            "variant_label",
                        ].iloc[0],
                        "grid_label": record["grid_label"],
                        "value_mm_day": record["value"],
                    }
                )
        values = intervention_differences(frame, "pr_mean", season)
        for record in values.to_dict("records"):
            rows.append(
                {
                    "model": record["model"],
                    "season": season,
                    "comparison": "G6solar - G6sulfur",
                    "target_variant_label": record["solar_variant_label"],
                    "reference_variant_label": record["sulfur_variant_label"],
                    "grid_label": record["solar_grid_label"],
                    "value_mm_day": record["value"],
                }
            )
    per_model = pd.DataFrame(rows).sort_values(["season", "comparison", "model"])
    stats_input = per_model.rename(
        columns={"comparison": "scenario", "value_mm_day": "value"}
    )
    ensemble = ensemble_statistics(stats_input).rename(
        columns={"scenario": "comparison"}
    )
    ensemble["units"] = "mm/day"
    return per_model, ensemble


def make_jja_figure(per_model: pd.DataFrame, ensemble: pd.DataFrame, output: Path) -> None:
    selected = per_model[per_model.season == "JJA"]
    models = sorted(selected.model.unique())
    x = np.arange(len(models))
    fig, axes = plt.subplots(
        1, 2, figsize=(12.2, 5.1), gridspec_kw={"width_ratios": [1.65, 1]},
        constrained_layout=True,
    )
    for offset, comparison in zip([-0.10, 0.10], COLORS, strict=True):
        values = selected[selected.comparison == comparison].set_index("model")
        y = np.array([values.loc[model, "value_mm_day"] for model in models])
        axes[0].scatter(
            x + offset, y, s=54, color=COLORS[comparison], label=comparison, zorder=3
        )
        summary = ensemble[
            (ensemble.season == "JJA") & (ensemble.comparison == comparison)
        ].iloc[0]
        axes[0].errorbar(
            len(models) + offset, summary["mean"], yerr=summary["std"], fmt="D",
            capsize=5, color=COLORS[comparison], markersize=6, zorder=4,
        )
    axes[0].axhline(0, color="#333333", linewidth=0.9)
    axes[0].set_xticks(
        np.arange(len(models) + 1), models + ["Ensemble\nmean ± 1 SD"],
        rotation=18, ha="right",
    )
    axes[0].set_ylabel("Regional precipitation response (mm/day)")
    axes[0].set_title("Intervention responses relative to SSP5-8.5")
    axes[0].legend(frameon=False, fontsize=9)
    axes[0].grid(axis="y", alpha=0.22)

    difference = selected[selected.comparison == "G6solar - G6sulfur"].set_index("model")
    y = np.array([difference.loc[model, "value_mm_day"] for model in models])
    axes[1].scatter(x, y, s=58, color="#542788", zorder=3)
    axes[1].axhline(0, color="#333333", linewidth=0.9)
    summary = ensemble[
        (ensemble.season == "JJA") & (ensemble.comparison == "G6solar - G6sulfur")
    ].iloc[0]
    axes[1].errorbar(
        len(models), summary["mean"], yerr=summary["std"], fmt="D", capsize=5,
        color="#542788", markersize=6, zorder=4,
    )
    axes[1].set_xticks(
        np.arange(len(models) + 1), models + ["Ensemble\nmean ± 1 SD"],
        rotation=22, ha="right",
    )
    axes[1].set_ylabel("G6solar minus G6sulfur (mm/day)")
    axes[1].set_title("Intervention difference")
    axes[1].grid(axis="y", alpha=0.22)
    fig.suptitle(
        "Southeast U.S. JJA precipitation response, 2071-2100\n"
        "Individual native-grid regional means and multimodel spread",
        fontsize=14,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_seasonal_figure(per_model: pd.DataFrame, ensemble: pd.DataFrame, output: Path) -> None:
    selected = per_model[per_model.comparison == "G6solar - G6sulfur"]
    fig, ax = plt.subplots(figsize=(8.6, 5.3), constrained_layout=True)
    for _, values in selected.groupby("model"):
        ordered = values.set_index("season").loc[SEASONS]
        ax.plot(SEASONS, ordered.value_mm_day, color="#8c8c8c", alpha=0.65, linewidth=1.2)
        ax.scatter(SEASONS, ordered.value_mm_day, color="#8c8c8c", alpha=0.8, s=20)
    summary = ensemble[
        ensemble.comparison == "G6solar - G6sulfur"
    ].set_index("season").loc[SEASONS]
    ax.fill_between(
        SEASONS, summary.minimum, summary.maximum, color="#8073ac", alpha=0.18,
        label="Model range",
    )
    ax.plot(
        SEASONS, summary["mean"], color="#542788", marker="D", linewidth=2.4,
        label="Multimodel mean",
    )
    ax.axhline(0, color="#333333", linewidth=0.9)
    ax.set(
        ylabel="G6solar minus G6sulfur response (mm/day)",
        title="Seasonal intervention difference and inter-model spread\n"
        "Southeast U.S., 2071-2100",
    )
    ax.grid(axis="y", alpha=0.22)
    ax.legend(frameon=False)
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data", type=Path, default=ROOT / "data/processed/regional_metrics.csv"
    )
    parser.add_argument("--docs", type=Path, default=ROOT / "docs")
    args = parser.parse_args()
    frame = load_metrics(args.data)
    per_model, ensemble = calculate(frame)
    per_model.to_csv(args.docs / "phase4_per_model.csv", index=False, float_format="%.6f")
    ensemble.to_csv(
        args.docs / "phase4_ensemble_summary.csv", index=False, float_format="%.6f"
    )
    make_jja_figure(per_model, ensemble, args.docs / "phase4_pr_ensemble.png")
    make_seasonal_figure(per_model, ensemble, args.docs / "phase4_pr_seasonal.png")
    print(f"Wrote {len(per_model)} per-model rows and {len(ensemble)} ensemble rows")


if __name__ == "__main__":
    main()
