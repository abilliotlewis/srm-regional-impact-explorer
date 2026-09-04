"""Create Phase 5 daily-extremes tables and publication figures."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from srm_explorer.analysis import (  # noqa: E402
    intervention_differences,
    load_metrics,
    regional_differences,
)

SEASONS = ["DJF", "MAM", "JJA", "SON", "ANN"]
METRICS = [
    "txx",
    "hwn_tx90_3d",
    "hwf_tx90_3d",
    "hwd_tx90_3d",
    "rx1day",
    "rx5day",
    "cdd",
    "r95ptot",
]
LABELS = {
    "txx": "TXx",
    "hwn_tx90_3d": "Heatwave events",
    "hwf_tx90_3d": "Heatwave days",
    "hwd_tx90_3d": "Longest heatwave",
    "rx1day": "Rx1day",
    "rx5day": "Rx5day",
    "cdd": "Consecutive dry days",
    "r95ptot": "R95pTOT",
}
COLORS = {
    "G6solar - SSP5-8.5": "#2166ac",
    "G6sulfur - SSP5-8.5": "#b35806",
    "G6solar - G6sulfur": "#542788",
}


def calculate(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in METRICS:
        units = frame.loc[frame.metric == metric, "units"].iloc[0]
        for season in SEASONS:
            for scenario, comparison in (
                ("G6solar", "G6solar - SSP5-8.5"),
                ("G6sulfur", "G6sulfur - SSP5-8.5"),
            ):
                values = regional_differences(frame, scenario, metric, season)
                for record in values.to_dict("records"):
                    rows.append(
                        {
                            "model": record["model"],
                            "variant_label": record["variant_label"],
                            "grid_label": record["grid_label"],
                            "season": season,
                            "metric": metric,
                            "comparison": comparison,
                            "value": record["value"],
                            "units": units,
                        }
                    )
            values = intervention_differences(frame, metric, season)
            for record in values.to_dict("records"):
                rows.append(
                    {
                        "model": record["model"],
                        "variant_label": record["solar_variant_label"],
                        "grid_label": record["solar_grid_label"],
                        "season": season,
                        "metric": metric,
                        "comparison": "G6solar - G6sulfur",
                        "value": record["value"],
                        "units": units,
                    }
                )
    return pd.DataFrame(rows).sort_values(["metric", "season", "comparison"])


def make_figure(results: pd.DataFrame, metrics: list[str], title: str, output: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.2), constrained_layout=True)
    for ax, metric in zip(axes.flat, metrics, strict=True):
        selected = results[results.metric == metric]
        for comparison, color in COLORS.items():
            ordered = selected[selected.comparison == comparison].set_index("season").loc[SEASONS]
            ax.plot(
                SEASONS,
                ordered.value,
                marker="o",
                linewidth=2,
                color=color,
                label=comparison,
            )
        units = selected.units.iloc[0]
        ax.axhline(0, color="#333333", linewidth=0.8)
        ax.set_title(LABELS[metric])
        ax.set_ylabel(f"Response ({units})")
        ax.grid(axis="y", alpha=0.22)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3, frameon=False)
    fig.suptitle(title, fontsize=14)
    output.parent.mkdir(parents=True, exist_ok=True)
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
    results = calculate(frame)
    results.to_csv(args.docs / "phase5_daily_extremes.csv", index=False, float_format="%.6f")
    make_figure(
        results,
        METRICS[:4],
        "Southeast U.S. daily heat-extreme responses, 2071-2100\n"
        "MPI-ESM1-2-LR r2i1p1f1",
        args.docs / "phase5_heat_extremes.png",
    )
    make_figure(
        results,
        METRICS[4:],
        "Southeast U.S. daily hydroclimate-extreme responses, 2071-2100\n"
        "MPI-ESM1-2-LR r2i1p1f1",
        args.docs / "phase5_hydro_extremes.png",
    )
    print(f"Wrote {len(results)} Phase 5 comparison rows")


if __name__ == "__main__":
    main()
