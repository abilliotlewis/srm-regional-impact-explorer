from pathlib import Path
import sys

import pandas as pd
import numpy as np
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from generate_demo_data import build
from prepare_geomip import convert_units, prepare
from srm_explorer.analysis import (
    difference_grid,
    ensemble_statistics,
    intervention_differences,
    load_metrics,
    regional_differences,
    regional_model_means,
    summarize_region,
)


def test_demo_schema_round_trip(tmp_path):
    path = tmp_path / "metrics.csv"
    build().to_csv(path, index=False)
    frame = load_metrics(path)
    assert len(frame) > 1_000
    assert set(frame.scenario) == {"ssp585", "ssp245", "G6solar", "G6sulfur"}
    assert frame.is_demo.all()


def test_g6solar_demo_is_cooler_than_ssp585():
    frame = build()
    frame = frame[frame.model == "DEMO-ESM-A"]
    diff = difference_grid(frame, "G6solar", "tasmax_mean", "JJA")
    assert diff.value.mean() < 0


def test_summary_reports_three_models():
    summary, provenance = summarize_region(build(), "G6solar", "pr_mean", "ANN")
    model_row = summary.loc[summary.Statistic == "Models", "Value"].iloc[0]
    assert model_row == "3"
    assert "SYNTHETIC" in provenance


def test_difference_summary_matches_map_direction():
    summary, _ = summarize_region(
        build(), "G6solar", "tasmax_mean", "JJA", "Difference from SSP5-8.5"
    )
    mean_text = summary.loc[
        summary.Statistic == "Regional mean difference", "Value"
    ].iloc[0]
    assert float(mean_text.split()[0]) < 0


def test_regional_differences_preserve_models():
    result = regional_differences(build(), "G6solar", "tasmax_mean", "JJA")
    assert result.model.nunique() == 3
    assert (result.value < 0).all()


def test_loader_rejects_missing_column(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"value": [1]}).to_csv(path, index=False)
    try:
        load_metrics(path)
    except ValueError as error:
        assert "Missing required columns" in str(error)
    else:
        raise AssertionError("Expected missing-column validation error")


def test_monthly_netcdf_preparation(tmp_path):
    times = pd.date_range("2071-01-01", periods=24, freq="MS")
    source = tmp_path / "tasmax.nc"
    values = np.full((24, 2, 2), 300.0)
    dataset = xr.Dataset(
        {"tasmax": (("time", "lat", "lon"), values, {"units": "K"})},
        coords={"time": times, "lat": [28.0, 32.0], "lon": [260.0, 270.0]},
    )
    dataset.to_netcdf(source, engine="h5netcdf")
    frame = prepare(source, "G6solar", "TEST-ESM", "tasmax", "tasmax_mean", 2071, 2072)
    assert set(frame.season) == {"ANN", "DJF", "MAM", "JJA", "SON"}
    assert np.isclose(frame.value.mean(), 26.85)
    assert not frame.is_demo.any()


def test_precipitation_flux_converts_to_mm_per_day(tmp_path):
    times = pd.date_range("2071-01-01", periods=24, freq="MS")
    source = tmp_path / "pr.nc"
    values = np.full((24, 1, 1), 1.0e-5)
    xr.Dataset(
        {"pr": (("time", "lat", "lon"), values, {"units": "kg m-2 s-1"})},
        coords={"time": times, "lat": [30.0], "lon": [-85.0]},
    ).to_netcdf(source, engine="h5netcdf")
    frame = prepare(source, "G6solar", "TEST", "pr", "pr_mean", 2071, 2072)
    assert set(frame.units) == {"mm/day"}
    assert np.allclose(frame.value, 0.864)


def test_unsupported_precipitation_units_are_rejected():
    data = xr.DataArray([1.0], attrs={"units": "inches fortnight-1"})
    try:
        convert_units(data, "pr")
    except ValueError as error:
        assert "Unsupported pr units" in str(error)
    else:
        raise AssertionError("Expected unsupported-unit validation error")


def test_djf_uses_complete_cross_year_season_and_day_weights(tmp_path):
    times = pd.date_range("2071-01-01", periods=24, freq="MS")
    values = np.full((24, 1, 1), 273.15)
    values[11, 0, 0] = 283.15  # December 2071
    values[12, 0, 0] = 293.15  # January 2072
    values[13, 0, 0] = 303.15  # February 2072
    source = tmp_path / "tasmax.nc"
    xr.Dataset(
        {"tasmax": (("time", "lat", "lon"), values, {"units": "K"})},
        coords={"time": times, "lat": [30.0], "lon": [-85.0]},
    ).to_netcdf(source, engine="h5netcdf")
    frame = prepare(source, "G6solar", "TEST", "tasmax", "tasmax_mean", 2071, 2072)
    actual = frame.loc[frame.season == "DJF", "value"].iloc[0]
    expected = (10 * 31 + 20 * 31 + 30 * 29) / (31 + 31 + 29)
    assert np.isclose(actual, expected)


def test_preparation_rejects_missing_month(tmp_path):
    times = pd.date_range("2071-01-01", periods=12, freq="MS").delete(5)
    source = tmp_path / "tasmax.nc"
    xr.Dataset(
        {"tasmax": (("time", "lat", "lon"), np.ones((11, 1, 1)), {"units": "K"})},
        coords={"time": times, "lat": [30.0], "lon": [-85.0]},
    ).to_netcdf(source, engine="h5netcdf")
    try:
        prepare(source, "G6solar", "TEST", "tasmax", "tasmax_mean", 2071, 2071)
    except ValueError as error:
        assert "Monthly coverage" in str(error)
    else:
        raise AssertionError("Expected missing-month validation error")


def test_regional_mean_uses_latitude_weights():
    values = pd.DataFrame(
        {
            "model": ["TEST", "TEST"],
            "variant_label": ["r1", "r1"],
            "grid_label": ["gn", "gn"],
            "lat": [0.0, 60.0],
            "value": [0.0, 10.0],
        }
    )
    result = regional_model_means(values)
    assert np.isclose(result.value.iloc[0], 10.0 / 3.0)


def test_variant_mismatch_is_rejected():
    frame = build()
    frame.loc[frame.scenario == "G6solar", "parent_variant_label"] = "r9i9p9f9"
    try:
        regional_differences(frame, "G6solar", "tasmax_mean", "JJA")
    except ValueError as error:
        assert "Incompatible" in str(error)
    else:
        raise AssertionError("Expected variant mismatch validation error")


def test_phase3_ensemble_counts_and_intervention_difference():
    frame = build()
    per_model = regional_differences(frame, "G6solar", "tasmax_mean", "JJA")
    summary = ensemble_statistics(per_model)
    assert summary.model_count.iloc[0] == 3
    assert 0 <= summary.sign_agreement.iloc[0] <= 1
    comparison = intervention_differences(frame, "tasmax_mean", "JJA")
    assert comparison.model.nunique() == 3


def test_phase4_published_summary_has_complete_four_model_counts():
    summary = pd.read_csv(ROOT / "docs" / "phase4_ensemble_summary.csv")
    assert len(summary) == 15
    assert set(summary.model_count) == {4}
    assert set(summary.season) == {"ANN", "DJF", "MAM", "JJA", "SON"}
    assert set(summary.comparison) == {
        "G6solar - SSP5-8.5",
        "G6sulfur - SSP5-8.5",
        "G6solar - G6sulfur",
    }
    jja_sulfur = summary[
        (summary.season == "JJA")
        & (summary.comparison == "G6sulfur - SSP5-8.5")
    ].iloc[0]
    assert jja_sulfur.sign_agreement == 0.5


def test_phase5_published_daily_results_are_complete_and_single_model():
    results = pd.read_csv(ROOT / "docs" / "phase5_daily_extremes.csv")
    assert len(results) == 120
    assert set(results.model) == {"MPI-ESM1-2-LR"}
    assert set(results.variant_label) == {"r2i1p1f1"}
    assert set(results.grid_label) == {"gn"}
    assert set(results.season) == {"ANN", "DJF", "MAM", "JJA", "SON"}
    assert set(results.metric) == {
        "txx",
        "hwn_tx90_3d",
        "hwf_tx90_3d",
        "hwd_tx90_3d",
        "rx1day",
        "rx5day",
        "cdd",
        "r95ptot",
    }
    assert set(results.comparison) == {
        "G6solar - SSP5-8.5",
        "G6sulfur - SSP5-8.5",
        "G6solar - G6sulfur",
    }
    assert not results.value.isna().any()
    assert not results.duplicated(["model", "season", "metric", "comparison"]).any()

    annual_txx = results[
        (results.season == "ANN")
        & (results.metric == "txx")
        & (results.comparison == "G6solar - G6sulfur")
    ].value.iloc[0]
    assert np.isclose(annual_txx, -0.335221, atol=1e-6)
