"""Convert pre-downloaded GeoMIP NetCDF fields into the explorer table schema.

This starter handles monthly gridded fields. Climate-extreme indices such as
Rx1day and CDD require daily data and should be calculated with xclim or an
equivalent CF-aware workflow before being passed to this script.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import pandas as pd
import xarray as xr

SEASON_MONTHS = {
    "ANN": list(range(1, 13)),
    "DJF": [12, 1, 2],
    "MAM": [3, 4, 5],
    "JJA": [6, 7, 8],
    "SON": [9, 10, 11],
}


def normalize_longitude(data: xr.DataArray) -> xr.DataArray:
    if float(data.lon.max()) > 180:
        data = data.assign_coords(lon=((data.lon + 180) % 360) - 180).sortby("lon")
    return data


def convert_units(data: xr.DataArray, variable: str) -> tuple[xr.DataArray, str]:
    units = str(data.attrs.get("units", "unknown"))
    if variable in {"tas", "tasmax"}:
        if units.lower() in {"k", "kelvin"}:
            return data - 273.15, "degC"
        if units.lower() in {"degc", "degree_celsius", "degrees_celsius"}:
            return data, "degC"
        raise ValueError(f"Unsupported {variable} units: {units!r}")
    if variable == "pr":
        normalized = " ".join(units.replace("**", "").split()).lower()
        if normalized in {"kg m-2 s-1", "kg/m2/s", "mm s-1"}:
            return data * 86400.0, "mm/day"
        if normalized in {"mm/day", "mm d-1"}:
            return data, "mm/day"
        raise ValueError(f"Unsupported pr units: {units!r}")
    raise ValueError(f"Unsupported variable: {variable!r}")


def validate_monthly_coverage(data: xr.DataArray, start_year: int, end_year: int) -> None:
    """Require one and only one value for every requested calendar month."""
    years = data.time.dt.year.values.astype(int)
    months = data.time.dt.month.values.astype(int)
    observed = list(zip(years, months, strict=True))
    expected = [
        (year, month)
        for year in range(start_year, end_year + 1)
        for month in range(1, 13)
    ]
    if observed != expected:
        missing = sorted(set(expected).difference(observed))
        duplicates = sorted({item for item in observed if observed.count(item) > 1})
        raise ValueError(
            "Monthly coverage must contain exactly one ordered value per month "
            f"from {start_year}-01 through {end_year}-12; "
            f"missing={missing[:6]}, duplicates={duplicates[:6]}"
        )


def seasonal_climatology(
    data: xr.DataArray,
    season: str,
    months: list[int],
    start_year: int,
    end_year: int,
) -> xr.DataArray:
    """Calculate a day-weighted climatology from complete seasonal years."""
    selected = data.where(data.time.dt.month.isin(months), drop=True)
    years = selected.time.dt.year.astype(int)
    if season == "DJF":
        season_year = years + (selected.time.dt.month == 12).astype(int)
        first_year = start_year + 1
    else:
        season_year = years
        first_year = start_year
    season_year = season_year.rename("season_year")
    selected = selected.where(
        (season_year >= first_year) & (season_year <= end_year), drop=True
    )
    season_year = season_year.where(
        (season_year >= first_year) & (season_year <= end_year), drop=True
    )

    counts = xr.ones_like(selected.time, dtype=int).groupby(season_year).sum("time")
    if not bool((counts == len(months)).all()):
        raise ValueError(f"{season} contains an incomplete seasonal year")

    weights = selected.time.dt.days_in_month.astype(float)
    numerator = (selected * weights).groupby(season_year).sum("time")
    denominator = weights.groupby(season_year).sum("time")
    return (numerator / denominator).mean("season_year")


def prepare(
    source: Path | Sequence[Path],
    scenario: str,
    model: str,
    variable: str,
    metric: str,
    start_year: int,
    end_year: int,
    variant_label: str = "unspecified",
    grid_label: str = "unspecified",
    parent_experiment_id: str = "not_applicable",
    parent_variant_label: str = "not_applicable",
) -> pd.DataFrame:
    sources = [str(path) for path in source] if isinstance(source, Sequence) else str(source)
    dataset = xr.open_mfdataset(
        sources,
        combine="by_coords",
        data_vars="minimal",
        coords="minimal",
        compat="override",
    )
    data = normalize_longitude(dataset[variable])
    data = data.sel(time=slice(str(start_year), str(end_year)))
    validate_monthly_coverage(data, start_year, end_year)
    data = data.where((data.lat >= 24) & (data.lat <= 38), drop=True)
    data = data.where((data.lon >= -100) & (data.lon <= -74), drop=True)
    if data.sizes.get("lat", 0) == 0 or data.sizes.get("lon", 0) == 0:
        raise ValueError("No grid-cell centers fall inside the Southeast U.S. domain")
    data, units = convert_units(data, variable)
    frames = []
    for season, months in SEASON_MONTHS.items():
        climatology = seasonal_climatology(data, season, months, start_year, end_year)
        table = climatology.to_dataframe(name="value").reset_index()
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
            units=units,
            period=f"{start_year}-{end_year}",
            is_demo=False,
        )
        frames.append(table)
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="NetCDF path or glob")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--variable", required=True, choices=["tas", "tasmax", "pr"])
    parser.add_argument("--metric", required=True)
    parser.add_argument("--variant-label", default="unspecified")
    parser.add_argument("--grid-label", default="unspecified")
    parser.add_argument("--parent-experiment-id", default="not_applicable")
    parser.add_argument("--parent-variant-label", default="not_applicable")
    parser.add_argument("--start-year", type=int, default=2071)
    parser.add_argument("--end-year", type=int, default=2100)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    frame = prepare(
        source=args.source,
        scenario=args.scenario,
        model=args.model,
        variable=args.variable,
        metric=args.metric,
        start_year=args.start_year,
        end_year=args.end_year,
        variant_label=args.variant_label,
        grid_label=args.grid_label,
        parent_experiment_id=args.parent_experiment_id,
        parent_variant_label=args.parent_variant_label,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
