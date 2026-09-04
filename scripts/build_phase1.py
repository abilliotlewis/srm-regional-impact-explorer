from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import pandas as pd
import xarray as xr

from download_manifest import download_record, load_manifest
from prepare_geomip import prepare


def validate_provenance(sources: list[Path], manifest: dict, experiment_id: str) -> None:
    """Check identity and G6 branch metadata stored inside every NetCDF file."""
    for source in sources:
        with xr.open_dataset(source, decode_times=False) as dataset:
            expected = {
                "source_id": manifest["source_id"],
                "experiment_id": experiment_id,
                "variant_label": next(
                    record["variant_label"]
                    for record in manifest["records"]
                    if record["experiment_id"] == experiment_id
                ),
            }
            if experiment_id.startswith("G6"):
                expected.update(
                    {
                        "parent_experiment_id": manifest["parent_experiment_id"],
                        "parent_variant_label": manifest["parent_variant_label"],
                    }
                )
            for attribute, value in expected.items():
                actual = dataset.attrs.get(attribute)
                if actual != value:
                    raise ValueError(
                        f"Provenance mismatch in {source.name}: {attribute}={actual!r}, expected {value!r}"
                    )


def build(manifest_paths: list[Path], raw_dir: Path, output: Path, download: bool) -> None:
    frames = []
    for manifest_path in manifest_paths:
        manifest = load_manifest(manifest_path)
        grouped: dict[str, list[dict]] = defaultdict(list)
        for record in manifest["records"]:
            grouped[record["experiment_id"]].append(record)

        for experiment_id, records in grouped.items():
            sources = []
            for record in sorted(records, key=lambda item: item["filename"]):
                source = raw_dir / record["filename"]
                if download:
                    source = download_record(record, raw_dir)
                if not source.exists():
                    raise FileNotFoundError(
                        f"Missing {source}. Run with --download or use download_manifest.py first."
                    )
                sources.append(source)
            validate_provenance(sources, manifest, experiment_id)
            frame = prepare(
                source=sources,
                scenario=experiment_id,
                model=manifest["source_id"],
                variable=manifest["variable_id"],
                metric="tasmax_mean",
                start_year=2071,
                end_year=2100,
            )
            frame["dataset_key"] = records[0]["dataset_key"]
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
        nargs="+",
        default=[
            Path("data/manifests/ipsl_tasmax_amon.json"),
            Path("data/manifests/mpi_lr_tasmax_amon.json"),
        ],
    )
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/tasmax"))
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
