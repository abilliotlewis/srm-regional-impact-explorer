from pathlib import Path
import sys

import pandas as pd
import numpy as np
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from generate_demo_data import build
from prepare_geomip import prepare
from srm_explorer.analysis import (
    difference_grid,
    load_metrics,
    regional_differences,
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
