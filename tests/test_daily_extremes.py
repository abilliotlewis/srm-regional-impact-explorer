from pathlib import Path
import sys

import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_daily_extremes import (  # noqa: E402
    build_thresholds,
    calculate_period_metrics,
    coordinates_match,
    open_daily_region,
    select_period,
    validate_daily_coverage,
)


def test_coordinate_matching_uses_values_not_coordinate_metadata():
    left = xr.DataArray([30.0], dims="lat", attrs={"axis": "Y"})
    right = xr.DataArray([30.0], dims="lat", attrs={"standard_name": "latitude"})
    assert coordinates_match(left, right)
    assert not coordinates_match(left, xr.DataArray([31.0], dims="lat"))


def test_daily_coverage_accepts_complete_leap_period():
    time = pd.date_range("1999-01-01", "2000-12-31", freq="D")
    data = xr.DataArray(np.ones(len(time)), dims="time", coords={"time": time})
    validate_daily_coverage(data, 1999, 2000)


def test_daily_coverage_rejects_missing_day():
    time = pd.date_range("2000-01-01", "2000-12-31", freq="D").delete(100)
    data = xr.DataArray(np.ones(len(time)), dims="time", coords={"time": time})
    try:
        validate_daily_coverage(data, 2000, 2000)
    except ValueError as error:
        assert "Daily coverage" in str(error)
    else:
        raise AssertionError("Expected daily-coverage validation error")


def test_daily_region_rejects_missing_values(tmp_path):
    time = pd.date_range("2001-01-01", "2001-12-31", freq="D")
    values = np.full((len(time), 1, 1), 300.0)
    values[100, 0, 0] = np.nan
    path = tmp_path / "tasmax.nc"
    xr.Dataset(
        {"tasmax": (("time", "lat", "lon"), values, {"units": "K"})},
        coords={"time": time, "lat": [30.0], "lon": [-85.0]},
    ).to_netcdf(path, engine="h5netcdf")
    try:
        open_daily_region([path], "tasmax", 2001, 2001)
    except ValueError as error:
        assert "missing values" in str(error)
    else:
        raise AssertionError("Expected missing-data validation error")


def test_djf_selection_uses_cross_year_complete_winter():
    time = pd.date_range("2071-01-01", "2072-12-31", freq="D")
    data = xr.DataArray(np.ones(len(time)), dims="time", coords={"time": time})
    selected = select_period(data, "DJF", 2072)
    assert selected.sizes["time"] == 91
    assert str(selected.time.values[0])[:10] == "2071-12-01"
    assert str(selected.time.values[-1])[:10] == "2072-02-29"


def test_historical_thresholds_are_finite_and_model_specific():
    time = pd.date_range("1981-01-01", "1985-12-31", freq="D")
    coords = {"time": time, "lat": [30.0], "lon": [-85.0]}
    tasmax = xr.DataArray(
        np.full((len(time), 1, 1), 30.0),
        dims=("time", "lat", "lon"),
        coords=coords,
        attrs={"units": "degC"},
    )
    pr = xr.DataArray(
        np.full((len(time), 1, 1), 2.0),
        dims=("time", "lat", "lon"),
        coords=coords,
        attrs={"units": "mm/day"},
    )
    tx90, pr95 = build_thresholds(tasmax, pr)
    assert np.isfinite(tx90).all()
    assert np.isfinite(pr95).all()
    assert np.allclose(tx90, 30.0)
    assert np.allclose(pr95, 2.0)


def test_daily_extreme_index_definitions():
    time = pd.date_range("2001-07-01", periods=10, freq="D")
    coords = {"time": time, "lat": [30.0], "lon": [-85.0]}
    tasmax = xr.DataArray(
        np.arange(10.0).reshape(10, 1, 1),
        dims=("time", "lat", "lon"),
        coords=coords,
    )
    hot = xr.DataArray(
        np.array([0, 1, 1, 1, 0, 1, 1, 1, 1, 0], dtype=bool).reshape(10, 1, 1),
        dims=("time", "lat", "lon"),
        coords=coords,
    )
    pr = xr.DataArray(
        np.array([0, 0, 2, 5, 10, 0, 0, 0, 20, 0], dtype=float).reshape(10, 1, 1),
        dims=("time", "lat", "lon"),
        coords=coords,
    )
    pr95 = xr.DataArray([[9.0]], dims=("lat", "lon"), coords={"lat": [30.0], "lon": [-85.0]})
    result = calculate_period_metrics(tasmax, pr, hot, pr95)
    actual = {name: float(value.values.squeeze()) for name, value in result.items()}
    assert actual == {
        "txx": 9.0,
        "hwn_tx90_3d": 2.0,
        "hwf_tx90_3d": 7.0,
        "hwd_tx90_3d": 4.0,
        "rx1day": 20.0,
        "rx5day": 30.0,
        "cdd": 3.0,
        "r95ptot": 30.0,
    }
