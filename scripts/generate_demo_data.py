from pathlib import Path

import numpy as np
import pandas as pd

SCENARIOS = ["ssp585", "ssp245", "G6solar", "G6sulfur"]
MODELS = ["DEMO-ESM-A", "DEMO-ESM-B", "DEMO-ESM-C"]
SEASONS = ["ANN", "DJF", "MAM", "JJA", "SON"]
METRICS = {
    "tasmax_mean": ("degC", 28.0),
    "pr_mean": ("mm/day", 3.2),
    "rx1day": ("mm", 62.0),
    "cdd": ("days", 17.0),
}


def scenario_effect(scenario: str, metric: str, lat: float, lon: float) -> float:
    if scenario == "ssp585":
        return 0.0
    if metric == "tasmax_mean":
        base = {"ssp245": -2.1, "G6solar": -1.9, "G6sulfur": -1.7}[scenario]
        return base + 0.015 * (lat - 30.0)
    if metric == "pr_mean":
        base = {"ssp245": 0.08, "G6solar": -0.10, "G6sulfur": -0.04}[scenario]
        return base + 0.003 * (lon + 85.0)
    if metric == "rx1day":
        return {"ssp245": -2.0, "G6solar": -4.5, "G6sulfur": -2.8}[scenario]
    return {"ssp245": -1.2, "G6solar": 2.5, "G6sulfur": 1.2}[scenario]


def build() -> pd.DataFrame:
    rng = np.random.default_rng(8127)
    records = []
    for model_i, model in enumerate(MODELS):
        for scenario in SCENARIOS:
            for season_i, season in enumerate(SEASONS):
                for metric, (units, base) in METRICS.items():
                    for lat in np.arange(25.0, 37.1, 2.0):
                        for lon in np.arange(-98.0, -74.9, 2.0):
                            spatial = 0.035 * (lat - 31.0) + 0.012 * (lon + 86.0)
                            seasonal = (season_i - 2) * 0.08
                            model_offset = (model_i - 1) * 0.15
                            noise_scale = 0.05 if metric in {"tasmax_mean", "pr_mean"} else 0.6
                            value = (
                                base
                                + spatial
                                + seasonal
                                + model_offset
                                + scenario_effect(scenario, metric, lat, lon)
                                + rng.normal(0, noise_scale)
                            )
                            records.append(
                                {
                                    "model": model,
                                    "scenario": scenario,
                                    "season": season,
                                    "metric": metric,
                                    "lat": lat,
                                    "lon": lon,
                                    "value": round(float(value), 4),
                                    "units": units,
                                    "period": "DEMONSTRATION ONLY",
                                    "is_demo": True,
                                }
                            )
    return pd.DataFrame.from_records(records)


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "data" / "processed" / "regional_metrics.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = build()
    frame.to_csv(output, index=False)
    print(f"Wrote {len(frame):,} demonstration records to {output}")

