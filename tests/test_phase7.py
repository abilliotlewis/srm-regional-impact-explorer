from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_geomip import SEASON_MONTHS, seasonal_time_series
from srm_explorer.temporal import (
    ensemble_summary,
    interval_classification,
    paired_series,
    paired_temporal_statistics,
)


def monthly_data() -> xr.DataArray:
    time = pd.date_range("2071-01-01", "2100-12-01", freq="MS")
    return xr.DataArray(
        np.arange(time.size, dtype=float)[:, None, None],
        coords={"time": time, "lat": [30.0], "lon": [-85.0]},
        dims=("time", "lat", "lon"),
    )


def test_exact_annual_and_seasonal_time_series_lengths():
    data = monthly_data()
    for season, months in SEASON_MONTHS.items():
        result = seasonal_time_series(data, season, months, 2071, 2100)
        expected = 29 if season == "DJF" else 30
        assert result.sizes["period_year"] == expected


def test_djf_is_labeled_by_january_year():
    result = seasonal_time_series(monthly_data(), "DJF", [12, 1, 2], 2071, 2100)
    assert tuple(result.period_year.values) == tuple(range(2072, 2101))


def test_paired_year_alignment_and_difference():
    values = pd.DataFrame(
        {
            "scenario": ["G6solar"] * 3 + ["G6sulfur"] * 3,
            "period_year": [2071, 2072, 2073] * 2,
            "value": [1, 2, 4, 3, 3, 3],
        }
    )
    result = paired_series(values, "G6solar", "G6sulfur")
    assert result["difference"].tolist() == [-2, -1, 1]


def test_paired_year_mismatch_is_rejected():
    values = pd.DataFrame(
        {
            "scenario": ["G6solar", "G6solar", "G6sulfur"],
            "period_year": [2071, 2072, 2071],
            "value": [1, 2, 1],
        }
    )
    try:
        paired_series(values, "G6solar", "G6sulfur")
    except ValueError as error:
        assert "different period years" in str(error)
    else:
        raise AssertionError("A missing paired year was accepted")


def test_block_bootstrap_summary_is_reproducible():
    values = np.linspace(-2, 1, 30)
    first = paired_temporal_statistics(values, "same", replicates=200)
    second = paired_temporal_statistics(values, "same", replicates=200)
    assert first == second


def test_paired_effect_size_uses_sample_sd():
    result = paired_temporal_statistics(np.array([1.0, 2.0, 3.0]), "effect", 50, 2)
    assert np.isclose(result["paired_interannual_sd"], 1.0)
    assert np.isclose(result["standardized_effect_size"], 2.0)
    assert np.isclose(result["standard_error"], 1 / np.sqrt(3))


def test_interval_ordering_and_zero_classification():
    assert interval_classification(-2, 1) == "includes_zero"
    assert interval_classification(0.1, 2) == "above_zero"
    assert interval_classification(-2, -0.1) == "below_zero"
    try:
        interval_classification(2, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("An inverted interval was accepted")


def test_ensemble_spread_uses_model_means_only():
    per_model = pd.DataFrame(
        {
            "domain": ["d"] * 3,
            "metric": ["m"] * 3,
            "units": ["u"] * 3,
            "season": ["JJA"] * 3,
            "comparison": ["c"] * 3,
            "mean_difference": [-2.0, -1.0, 3.0],
            "paired_interannual_sd": [100.0, 200.0, 300.0],
            "interval_classification": ["below_zero", "includes_zero", "above_zero"],
        }
    )
    result = ensemble_summary(per_model).iloc[0]
    assert np.isclose(result["inter_model_sd"], np.std([-2, -1, 3], ddof=1))
    assert result["temporal_ci_includes_zero_count"] == 1
    assert "ci_lower" not in result.index


def test_phase1_to_6_reference_outputs_are_unchanged():
    expected = json.loads((ROOT / "data/reference_outputs_phase1_6.json").read_text())
    for name, digest in expected.items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        assert actual == digest


def test_phase7_published_output_completeness():
    per_model = pd.read_csv(ROOT / "docs/phase7_per_model_temporal_variability.csv")
    ensemble = pd.read_csv(ROOT / "docs/phase7_ensemble_temporal_summary.csv")
    regional = pd.read_csv(
        ROOT / "data/published/phase7_monthly_regional_timeseries.csv.gz"
    )
    sensitivity = pd.read_csv(ROOT / "docs/phase7_block_length_sensitivity.csv")
    assert len(per_model) == 360
    assert len(ensemble) == 90
    assert len(regional) == 10_728
    assert len(sensitivity) == 36
    assert set(sensitivity["tested_block_length_years"]) == {3, 5, 7}
    assert set(per_model["model"]) == {
        "CNRM-ESM2-1",
        "IPSL-CM6A-LR",
        "MPI-ESM1-2-LR",
        "UKESM1-0-LL",
    }
    assert set(per_model["domain"]) == {
        "original_box",
        "southeast_land",
        "gulf_coast",
    }
    assert set(per_model["year_count"]) == {29, 30}
    primary = per_model[
        (per_model["comparison"] == "G6solar - G6sulfur")
        & (per_model["metric"] == "tasmax_mean")
        & (per_model["season"] == "JJA")
    ]
    assert len(primary) == 12


def test_phase7_reproduces_phase6_climatological_means():
    phase7 = pd.read_csv(ROOT / "docs/phase7_per_model_temporal_variability.csv")
    phase6 = pd.read_csv(ROOT / "docs/phase6_domain_per_model.csv")
    phase7 = phase7[phase7["comparison"] == "G6solar - G6sulfur"]
    phase6 = phase6[
        phase6["domain"].isin(["original_box", "southeast_land", "gulf_coast"])
    ]
    keys = ["model", "domain", "metric", "season", "comparison", "units"]
    merged = phase7.merge(phase6, on=keys, validate="one_to_one")
    assert len(merged) == 120
    assert np.allclose(merged["mean_difference"], merged["value"], atol=5e-7)
