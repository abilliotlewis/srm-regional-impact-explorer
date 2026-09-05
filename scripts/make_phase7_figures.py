"""Create manuscript-oriented Phase 7 temporal-variability figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SOURCE = DOCS / "phase7_per_model_temporal_variability.csv"
MODELS = ["CNRM-ESM2-1", "IPSL-CM6A-LR", "MPI-ESM1-2-LR", "UKESM1-0-LL"]
MODEL_LABELS = {
    "CNRM-ESM2-1": "CNRM-ESM2-1",
    "IPSL-CM6A-LR": "IPSL-CM6A-LR",
    "MPI-ESM1-2-LR": "MPI-ESM1-2-LR",
    "UKESM1-0-LL": "UKESM1-0-LL",
}
DOMAINS = ["original_box", "southeast_land", "gulf_coast"]
DOMAIN_LABELS = {
    "original_box": "Original box",
    "southeast_land": "Southeast land",
    "gulf_coast": "Gulf Coast",
}
COLORS = {
    "CNRM-ESM2-1": "#0072B2",
    "IPSL-CM6A-LR": "#D55E00",
    "MPI-ESM1-2-LR": "#009E73",
    "UKESM1-0-LL": "#CC79A7",
}


def interval_panel(ax, data: pd.DataFrame, standardized: bool = False) -> None:
    for row_index, model in enumerate(MODELS):
        row = data[data["model"] == model].iloc[0]
        scale = row["paired_interannual_sd"] if standardized else 1.0
        mean = row["mean_difference"] / scale
        lower = row["ci_lower"] / scale
        upper = row["ci_upper"] / scale
        ax.errorbar(
            mean,
            row_index,
            xerr=np.array([[mean - lower], [upper - mean]]),
            fmt="o",
            color=COLORS[model],
            ecolor=COLORS[model],
            capsize=3,
            markersize=5,
            linewidth=1.5,
        )
    ax.axvline(0, color="#555555", linewidth=0.9, linestyle="--")
    ax.set_yticks(range(len(MODELS)), [MODEL_LABELS[model] for model in MODELS])
    ax.grid(axis="x", color="#dddddd", linewidth=0.7)
    ax.spines[["top", "right"]].set_visible(False)


def main_temperature_figure(data: pd.DataFrame) -> None:
    selected = data[
        (data["comparison"] == "G6solar - G6sulfur")
        & (data["metric"] == "tasmax_mean")
        & (data["season"] == "JJA")
    ]
    figure, axes = plt.subplots(1, 3, figsize=(11.2, 4.2), sharex=True, sharey=True)
    for ax, domain in zip(axes, DOMAINS, strict=True):
        interval_panel(ax, selected[selected["domain"] == domain])
        ax.set_title(DOMAIN_LABELS[domain], fontsize=11)
        ax.set_xlabel("JJA tasmax difference (°C)")
    axes[0].set_ylabel("Model")
    axes[0].invert_yaxis()
    figure.suptitle(
        "G6solar minus G6sulfur: paired temporal uncertainty",
        fontsize=13,
        y=1.01,
    )
    figure.text(
        0.5,
        -0.01,
        "Points: 2071–2100 mean. Bars: 95% five-year moving-block bootstrap interval.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout()
    figure.savefig(DOCS / "phase7_jja_tasmax_temporal_intervals.png", dpi=300, bbox_inches="tight")
    plt.close(figure)


def robustness_figure(data: pd.DataFrame) -> None:
    panels = [
        ("tasmax_mean", "JJA", "JJA tasmax"),
        ("tasmax_mean", "MAM", "MAM tasmax"),
        ("pr_mean", "JJA", "JJA precipitation"),
        ("pr_mean", "ANN", "Annual precipitation"),
    ]
    selected = data[
        (data["comparison"] == "G6solar - G6sulfur")
        & (data["domain"] == "southeast_land")
    ]
    figure, axes = plt.subplots(2, 2, figsize=(9.2, 7.2), sharex=True, sharey=True)
    for ax, (metric, season, title) in zip(axes.flat, panels, strict=True):
        panel = selected[(selected["metric"] == metric) & (selected["season"] == season)]
        interval_panel(ax, panel, standardized=True)
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Standardized paired difference")
    axes[0, 0].set_ylabel("Model")
    axes[1, 0].set_ylabel("Model")
    axes[0, 0].invert_yaxis()
    figure.suptitle(
        "Cross-result robustness over Southeast land",
        fontsize=13,
        y=1.01,
    )
    figure.text(
        0.5,
        -0.01,
        "Mean and bootstrap interval divided by each model's paired interannual SD.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout()
    figure.savefig(DOCS / "phase7_cross_result_robustness.png", dpi=300, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    data = pd.read_csv(SOURCE)
    main_temperature_figure(data)
    robustness_figure(data)
    print("Wrote Phase 7 manuscript figures")


if __name__ == "__main__":
    main()
