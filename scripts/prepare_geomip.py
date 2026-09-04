"""Convert pre-downloaded GeoMIP NetCDF fields into the explorer table schema.

This starter handles monthly gridded fields. Climate-extreme indices such as
Rx1day and CDD require daily data and should be calculated with xclim or an
equivalent CF-aware workflow before being passed to this script.
"""

from __future__ import annotations

import argparse
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
    if variable in {"tas", "tasmax"} and units.lower() in {"k", "kelvin"}:
        return data - 273.15, "degC"
    if variable == "pr" and units in {"kg m-2 s-1", "kg m**-2 s**-1"}:
        return data * 86400.0, "mm/day"
    return data, units


def prepare(
    source: Path,
    scenario: str,
    model: str,
    variable: str,
    metric: str,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    dataset = xr.open_mfdataset(str(source), combine="by_coords")
    data = normalize_longitude(dataset[variable])
    data = data.sel(time=slice(str(start_year), str(end_year)), lat=slice(24, 38), lon=slice(-100, -74))
    data, units = convert_units(data, variable)
    frames = []
    for season, months in SEASON_MONTHS.items():
        climatology = data.where(data.time.dt.month.isin(months), drop=True).mean("time")
        table = climatology.to_dataframe(name="value").reset_index()
        table = table[["lat", "lon", "value"]].dropna()
        table = table.assign(
            model=model,
            scenario=scenario,
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
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
