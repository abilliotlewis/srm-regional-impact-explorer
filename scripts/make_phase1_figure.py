"""Create the first reproducible Phase 1 result figure."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from srm_explorer.analysis import difference_grid, load_metrics, summarize_region


def build_figure(data_path: Path, output_path: Path, season: str = "JJA") -> None:
    frame = load_metrics(data_path)
    scenarios = ["G6solar", "G6sulfur"]
    grids = {
        scenario: difference_grid(frame, scenario, "tasmax_mean", season)
        for scenario in scenarios
    }
    bound = max(float(np.abs(grid["value"]).max()) for grid in grids.values())
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True, sharey=True)

    mesh = None
    for ax, scenario in zip(axes, scenarios, strict=True):
        grid = grids[scenario]
        pivot = grid.pivot(index="lat", columns="lon", values="value").sort_index()
        mesh = ax.pcolormesh(
            pivot.columns,
            pivot.index,
            pivot.values,
            shading="nearest",
            cmap="RdBu_r",
            vmin=-bound,
            vmax=bound,
        )
        summary, _ = summarize_region(
            frame,
            scenario,
            "tasmax_mean",
            season,
            "Difference from SSP5-8.5",
        )
        ax.set_title(f"{scenario} minus SSP5-8.5\nBox mean: {summary.iloc[0]['Value']}")
        ax.set_xlabel("Longitude")
        ax.grid(alpha=0.18)

    axes[0].set_ylabel("Latitude")
    fig.colorbar(mesh, ax=axes, label="Mean daily maximum temperature difference (°C)")
    fig.suptitle(
        f"IPSL-CM6A-LR {season} tasmax response, 2071–2100\n"
        "24–38°N, 100–74°W; one model and one realization"
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
        "--output", type=Path, default=ROOT / "docs" / "phase1_tasmax_jja.png"
    )
    parser.add_argument("--season", default="JJA")
    args = parser.parse_args()
    build_figure(args.data, args.output, args.season)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
