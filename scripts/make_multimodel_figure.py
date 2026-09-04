"""Plot native-grid regional responses without regridding model fields."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from srm_explorer.analysis import load_metrics, regional_differences


def build_figure(data_path: Path, output_path: Path) -> None:
    frame = load_metrics(data_path)
    seasons = ["DJF", "MAM", "JJA", "SON", "ANN"]
    scenarios = ["G6solar", "G6sulfur"]
    colors = {"G6solar": "#2f6f9f", "G6sulfur": "#b66a3c"}
    models = sorted(frame["model"].unique())

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)

    x = np.arange(len(models))
    width = 0.36
    for offset, scenario in zip([-width / 2, width / 2], scenarios, strict=True):
        values = regional_differences(frame, scenario, "tasmax_mean", "JJA").set_index("model")
        axes[0].bar(
            x + offset,
            [values.loc[model, "value"] for model in models],
            width,
            label=scenario,
            color=colors[scenario],
        )
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_xticks(x, models, rotation=15, ha="right")
    axes[0].set_ylabel("Difference from SSP5-8.5 (°C)")
    axes[0].set_title("JJA box-mean response by model")
    axes[0].legend(frameon=False)
    axes[0].grid(axis="y", alpha=0.2)

    for scenario in scenarios:
        seasonal = []
        lows = []
        highs = []
        for season in seasons:
            values = regional_differences(frame, scenario, "tasmax_mean", season)["value"]
            seasonal.append(values.mean())
            lows.append(values.min())
            highs.append(values.max())
        axes[1].plot(seasons, seasonal, marker="o", label=scenario, color=colors[scenario])
        axes[1].fill_between(seasons, lows, highs, color=colors[scenario], alpha=0.15)
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_ylabel("Two-model mean difference (°C)")
    axes[1].set_title("Seasonal mean and model range")
    axes[1].legend(frameon=False)
    axes[1].grid(axis="y", alpha=0.2)

    fig.suptitle(
        "Regional tasmax response, 2071–2100\n"
        "24–38°N, 100–74°W; native model grids"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=Path,
        default=ROOT / "data" / "processed" / "regional_metrics.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs" / "phase2_tasmax_regional.png",
    )
    args = parser.parse_args()
    build_figure(args.data, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
