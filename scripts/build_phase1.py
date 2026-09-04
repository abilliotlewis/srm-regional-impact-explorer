from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from download_manifest import download_record, load_manifest
from prepare_geomip import prepare


def build(manifest_path: Path, raw_dir: Path, output: Path, download: bool) -> None:
    manifest = load_manifest(manifest_path)
    frames = []
    for record in manifest["records"]:
        source = raw_dir / record["filename"]
        if download:
            source = download_record(record, raw_dir)
        if not source.exists():
            raise FileNotFoundError(
                f"Missing {source}. Run with --download or use download_manifest.py first."
            )
        frame = prepare(
            source=source,
            scenario=record["experiment_id"],
            model=manifest["source_id"],
            variable=manifest["variable_id"],
            metric="tasmax_mean",
            start_year=2071,
            end_year=2100,
        )
        frame["dataset_key"] = record["dataset_key"]
        frames.append(frame)
    combined = pd.concat(frames, ignore_index=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output, index=False)
    print(f"Wrote {len(combined):,} verified model-derived records to {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/manifests/ipsl_tasmax_amon.json"),
    )
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/ipsl_tasmax"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/regional_metrics.csv"),
    )
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    build(args.manifest, args.raw_dir, args.output, args.download)


if __name__ == "__main__":
    main()

