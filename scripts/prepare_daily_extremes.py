"""Calculate calendar-aware daily climate-extreme indices on native model grids."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from xclim.core.calendar import percentile_doy, resample_doy
from xclim.indices import run_length

from prepare_geomip import convert_units, normalize_longitude

SEASON_MONTHS = {
    "ANN": list(range(1, 13)),
    "DJF": [12, 1, 2],
    "MAM": [3, 4, 5],
    "JJA": [6, 7, 8],
    "SON": [9, 10, 11],
}

METRIC_UNITS = {
    "txx": "degC",
    "hwn_tx90_3d": "events",
    "hwf_tx90_3d": "days",
    "hwd_tx90_3d": "days",
    "rx1day": "mm",
    "rx5day": "mm",
    "cdd": "days",
    "r95ptot": "mm",
}


def coordinates_match(left: xr.DataArray, right: xr.DataArray) -> bool:
    """Compare coordinate values without treating harmless metadata as grid identity."""
    return left.shape == right.shape and np.array_equal(left.values, right.values)


def validate_daily_coverage(data: xr.DataArray, start_year: int, end_year: int) -> None:
    """Require one ordered value for every native-calendar day in the period."""
    calendar = data.time.dt.calendar
    expected = xr.date_range(
        start=f"{start_year}-01-01",
        end=f"{end_year}-12-31",
        freq="D",
        calendar=calendar,
        use_cftime=True,
    )
    observed_parts = np.column_stack(
        [data.time.dt.year.values, data.time.dt.month.values, data.time.dt.day.values]
    ).astype(int)
    expected_parts = np.array(
        [(date.year, date.month, date.day) for date in expected], dtype=int
    )
    if observed_parts.shape != expected_parts.shape or not np.array_equal(
        observed_parts, expected_parts
    ):
        raise ValueError(
            "Daily coverage must contain exactly one ordered value for every "
            f"{calendar} calendar day from {start_year}-01-01 through {end_year}-12-31"
        )


def open_daily_region(
    sources: Sequence[Path], variable: str, start_year: int, end_year: int
) -> xr.DataArray:
    dataset = xr.open_mfdataset(
        [str(path) for path in sources],
        combine="by_coords",
        data_vars="minimal",
        coords="minimal",
        compat="override",
        chunks={"time": 366},
    )
    data = normalize_longitude(dataset[variable])
    data = data.sel(time=slice(str(start_year), str(end_year)))
    validate_daily_coverage(data, start_year, end_year)
    data = data.where((data.lat >= 24) & (data.lat <= 38), drop=True)
    data = data.where((data.lon >= -100) & (data.lon <= -74), drop=True)
    if data.sizes.get("lat", 0) == 0 or data.sizes.get("lon", 0) == 0:
        raise ValueError("No grid-cell centers fall inside the Southeast U.S. domain")
    # The cropped native-grid subset is small. Materializing it once prevents each
    # annual and seasonal index from rereading the much larger global source files.
    data = data.load()
    dataset.close()
    if bool(data.isnull().any()):
        raise ValueError("Daily regional data contain missing values")
    data, units = convert_units(data, variable)
    data.attrs["units"] = units
    return data


def build_thresholds(
    historical_tasmax: xr.DataArray, historical_pr: xr.DataArray
) -> tuple[xr.DataArray, xr.DataArray]:
    """Return TX90 calendar-day and wet-day PR95 thresholds for 1981-2010."""
    if not coordinates_match(
        historical_tasmax.lat, historical_pr.lat
    ) or not coordinates_match(historical_tasmax.lon, historical_pr.lon):
        raise ValueError("Historical tasmax and pr grids do not match")
    tx90 = percentile_doy(historical_tasmax, window=5, per=90).squeeze(drop=True)
    wet = historical_pr.where(historical_pr >= 1.0)
    pr95 = wet.quantile(0.95, dim="time", skipna=True).squeeze(drop=True)
    if bool(tx90.isnull().any()) or bool(pr95.isnull().any()):
        raise ValueError("Historical percentile thresholds contain missing grid cells")
    return tx90.load(), pr95.load()


def select_period(data: xr.DataArray, season: str, period_year: int) -> xr.DataArray:
    years = data.time.dt.year
    months = data.time.dt.month
    if season == "ANN":
        mask = years == period_year
    elif season == "DJF":
        mask = ((years == period_year - 1) & (months == 12)) | (
            (years == period_year) & months.isin([1, 2])
        )
    else:
        mask = (years == period_year) & months.isin(SEASON_MONTHS[season])
    selected = data.where(mask, drop=True)
    if selected.sizes.get("time", 0) == 0:
        raise ValueError(f"No daily data for {season} {period_year}")
    return selected


def calculate_period_metrics(
    tasmax: xr.DataArray,
    pr: xr.DataArray,
    hot_days: xr.DataArray,
    pr95: xr.DataArray,
) -> dict[str, xr.DataArray]:
    """Calculate all indices within one complete year or season."""
    rx5 = pr.rolling(time=5, min_periods=5).sum().max("time")
    return {
        "txx": tasmax.max("time"),
        "hwn_tx90_3d": run_length.windowed_run_events(hot_days, window=3),
        "hwf_tx90_3d": run_length.windowed_run_count(hot_days, window=3),
        "hwd_tx90_3d": run_length.rle_statistics(
            hot_days, reducer="max", window=3
        ).fillna(0),
        "rx1day": pr.max("time"),
        "rx5day": rx5,
        "cdd": run_length.rle_statistics(
            pr < 1.0, reducer="max", window=1
        ).fillna(0),
        "r95ptot": pr.where(pr > pr95, 0).sum("time"),
    }


def calculate_climatologies(
    tasmax: xr.DataArray,
    pr: xr.DataArray,
    tx90: xr.DataArray,
    pr95: xr.DataArray,
    start_year: int,
    end_year: int,
) -> dict[tuple[str, str], xr.DataArray]:
    """Average annual and seasonal index values over complete periods."""
    hot_days = tasmax > resample_doy(tx90, tasmax)
    output: dict[tuple[str, str], xr.DataArray] = {}
    for season in SEASON_MONTHS:
        first_year = start_year + 1 if season == "DJF" else start_year
        yearly: dict[str, list[xr.DataArray]] = {metric: [] for metric in METRIC_UNITS}
        for period_year in range(first_year, end_year + 1):
            metrics = calculate_period_metrics(
                select_period(tasmax, season, period_year),
                select_period(pr, season, period_year),
                select_period(hot_days, season, period_year),
                pr95,
            )
            for metric, values in metrics.items():
                yearly[metric].append(values.expand_dims(period_year=[period_year]))
        for metric, values in yearly.items():
            output[(season, metric)] = xr.concat(values, dim="period_year").mean(
                "period_year"
            )
    return output


def prepare_daily_extremes(
    tasmax_sources: Sequence[Path],
    pr_sources: Sequence[Path],
    scenario: str,
    model: str,
    tx90: xr.DataArray,
    pr95: xr.DataArray,
    start_year: int = 2071,
    end_year: int = 2100,
    variant_label: str = "unspecified",
    grid_label: str = "unspecified",
    parent_experiment_id: str = "not_applicable",
    parent_variant_label: str = "not_applicable",
) -> pd.DataFrame:
    tasmax = open_daily_region(tasmax_sources, "tasmax", start_year, end_year)
    pr = open_daily_region(pr_sources, "pr", start_year, end_year)
    if not coordinates_match(tasmax.lat, pr.lat) or not coordinates_match(
        tasmax.lon, pr.lon
    ):
        raise ValueError("Daily tasmax and pr grids do not match")
    if not coordinates_match(tasmax.time, pr.time):
        raise ValueError("Daily tasmax and pr calendars do not match")
    climatologies = calculate_climatologies(
        tasmax, pr, tx90, pr95, start_year, end_year
    )
    frames = []
    for (season, metric), values in climatologies.items():
        table = values.compute().to_dataframe(name="value").reset_index()
        table = table[["lat", "lon", "value"]].dropna()
        table = table.assign(
            model=model,
            scenario=scenario,
            variant_label=variant_label,
            grid_label=grid_label,
            parent_experiment_id=parent_experiment_id,
            parent_variant_label=parent_variant_label,
            season=season,
            metric=metric,
            units=METRIC_UNITS[metric],
            period=f"{start_year}-{end_year}",
            is_demo=False,
        )
        frames.append(table)
    return pd.concat(frames, ignore_index=True)
