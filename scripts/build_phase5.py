"""Build the Phase 5 single-model daily-extremes checkpoint."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import pandas as pd

from build_phase1 import (
    experiment_metadata,
    validate_matched_experiments,
    validate_provenance,
)
from build_phase4 import build_phase4
from download_manifest import download_record, load_manifest, validate_file
from prepare_daily_extremes import (
    build_thresholds,
    open_daily_region,
    prepare_daily_extremes,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = {
    "tasmax": ROOT / "data/manifests/mpi_lr_tasmax_day.json",
    "pr": ROOT / "data/manifests/mpi_lr_pr_day.json",
}
RAW_DIRS = {
    "tasmax": ROOT / "data/raw/daily/tasmax",
    "pr": ROOT / "data/raw/daily/pr",
}


def verified_sources(manifest: dict, raw_dir: Path, download: bool) -> dict[str, list[Path]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in manifest["records"]:
        grouped[record["experiment_id"]].append(record)
    output = {}
    for experiment_id, records in grouped.items():
        sources = []
        for record in sorted(records, key=lambda item: item["filename"]):
            source = raw_dir / record["filename"]
            if download:
                source = download_record(record, raw_dir)
            if not source.exists():
                raise FileNotFoundError(f"Missing {source}. Run with --download first.")
            validate_file(source, record)
            sources.append(source)
        validate_provenance(sources, records, manifest, experiment_id)
        output[experiment_id] = sources
    return output


def build_daily(download: bool = False) -> pd.DataFrame:
    manifests = {variable: load_manifest(path) for variable, path in MANIFESTS.items()}
    for variable, manifest in manifests.items():
        if manifest["variable_id"] != variable or manifest["table_id"] != "day":
            raise ValueError(f"Incorrect daily manifest identity for {variable}")
        validate_matched_experiments(manifest)
    sources = {
        variable: verified_sources(manifest, RAW_DIRS[variable], download)
        for variable, manifest in manifests.items()
    }
    historical_tasmax = open_daily_region(
        sources["tasmax"]["historical"], "tasmax", 1981, 2010
    )
    historical_pr = open_daily_region(
        sources["pr"]["historical"], "pr", 1981, 2010
    )
    tx90, pr95 = build_thresholds(historical_tasmax, historical_pr)
    frames = []
    manifest = manifests["tasmax"]
    for experiment_id in ("ssp585", "G6solar", "G6sulfur"):
        metadata = experiment_metadata(manifest, experiment_id)
        records = [
            record
            for record in manifest["records"]
            if record["experiment_id"] == experiment_id
        ]
        frame = prepare_daily_extremes(
            sources["tasmax"][experiment_id],
            sources["pr"][experiment_id],
            scenario=experiment_id,
            model=manifest["source_id"],
            tx90=tx90,
            pr95=pr95,
            variant_label=records[0]["variant_label"],
            grid_label=records[0]["grid_label"],
            parent_experiment_id=metadata["parent_experiment_id"],
            parent_variant_label=metadata["parent_variant_label"],
        )
        frame["dataset_key"] = records[0]["dataset_key"]
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "data/processed/regional_metrics.csv"
    )
    args = parser.parse_args()
    monthly = build_phase4(download=args.download)
    daily = build_daily(download=args.download)
    combined = pd.concat([monthly, daily], ignore_index=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(args.output, index=False)
    print(f"Wrote {len(combined):,} validated Phase 5 records to {args.output}")


if __name__ == "__main__":
    main()
