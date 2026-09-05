from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import pandas as pd
import xarray as xr

from download_manifest import download_record, load_manifest, validate_file
from prepare_geomip import prepare, prepare_time_series

REQUIRED_EXPERIMENTS = {"G6solar", "G6sulfur", "ssp585"}
VARIABLE_METRICS = {"tasmax": "tasmax_mean", "pr": "pr_mean"}


def experiment_metadata(manifest: dict, experiment_id: str) -> dict:
    metadata = manifest.get("experiments", {}).get(experiment_id, {}).copy()
    if experiment_id.startswith("G6"):
        metadata.setdefault("parent_experiment_id", manifest.get("parent_experiment_id"))
        metadata.setdefault("parent_variant_label", manifest.get("parent_variant_label"))
    return metadata


def validate_matched_experiments(manifest: dict) -> None:
    """Reject missing, mixed, or parent-incompatible direct comparisons."""
    records = manifest["records"]
    available = {record["experiment_id"] for record in records}
    missing = REQUIRED_EXPERIMENTS.difference(available)
    if missing:
        raise ValueError(
            f"{manifest['source_id']} is missing required experiments {sorted(missing)}"
        )

    identities = {}
    for experiment_id in REQUIRED_EXPERIMENTS:
        selected = [r for r in records if r["experiment_id"] == experiment_id]
        variants = {r["variant_label"] for r in selected}
        grids = {r["grid_label"] for r in selected}
        if len(variants) != 1 or len(grids) != 1:
            raise ValueError(
                f"{manifest['source_id']} {experiment_id} mixes variants or grids: "
                f"variants={sorted(variants)}, grids={sorted(grids)}"
            )
        identities[experiment_id] = (next(iter(variants)), next(iter(grids)))

    reference_variant, reference_grid = identities["ssp585"]
    reference_metadata = experiment_metadata(manifest, "ssp585")
    for experiment_id in ("G6solar", "G6sulfur"):
        metadata = experiment_metadata(manifest, experiment_id)
        direct_parent = (
            metadata.get("parent_experiment_id") == "ssp585"
            and metadata.get("parent_variant_label") == reference_variant
        )
        common_parent = (
            metadata.get("parent_experiment_id")
            == reference_metadata.get("parent_experiment_id")
            and metadata.get("parent_variant_label")
            == reference_metadata.get("parent_variant_label")
            and identities[experiment_id][0] == reference_variant
            and metadata.get("parent_experiment_id") is not None
        )
        if not (direct_parent or common_parent):
            raise ValueError(
                f"{manifest['source_id']} {experiment_id} is neither a direct SSP5-8.5 "
                "branch nor a variant-matched sibling with the same parent"
            )
        if identities[experiment_id][1] != reference_grid:
            raise ValueError(
                f"{manifest['source_id']} {experiment_id} grid does not match SSP5-8.5"
            )


def validate_provenance(
    sources: list[Path], records: list[dict], manifest: dict, experiment_id: str
) -> None:
    """Check identity and G6 branch metadata stored inside every NetCDF file."""
    records_by_name = {record["filename"]: record for record in records}
    metadata = experiment_metadata(manifest, experiment_id)
    for source in sources:
        record = records_by_name[source.name]
        with xr.open_dataset(source, decode_times=False) as dataset:
            expected = {
                "source_id": manifest["source_id"],
                "experiment_id": experiment_id,
                "variant_label": record["variant_label"],
                "grid_label": record["grid_label"],
            }
            if metadata.get("parent_experiment_id"):
                expected.update(
                    {
                        "parent_experiment_id": metadata["parent_experiment_id"],
                        "parent_variant_label": metadata["parent_variant_label"],
                    }
                )
            if record.get("tracking_id"):
                expected["tracking_id"] = record["tracking_id"]
            for attribute, value in expected.items():
                actual = dataset.attrs.get(attribute)
                if actual != value:
                    raise ValueError(
                        f"Provenance mismatch in {source.name}: {attribute}={actual!r}, expected {value!r}"
                    )


def build_frame(
    manifest_paths: list[Path], raw_dir: Path, download: bool = False,
    spatial_padding_degrees: float = 0.0,
) -> pd.DataFrame:
    """Build one validated variable table from matched model manifests."""
    frames = []
    for manifest_path in manifest_paths:
        manifest = load_manifest(manifest_path)
        validate_matched_experiments(manifest)
        grouped: dict[str, list[dict]] = defaultdict(list)
        for record in manifest["records"]:
            if record["experiment_id"] in REQUIRED_EXPERIMENTS:
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
                validate_file(source, record)
                sources.append(source)
            validate_provenance(sources, records, manifest, experiment_id)
            metadata = experiment_metadata(manifest, experiment_id)
            variable = manifest["variable_id"]
            if variable not in VARIABLE_METRICS:
                raise ValueError(f"No explorer metric is defined for variable {variable!r}")
            frame = prepare(
                source=sources,
                scenario=experiment_id,
                model=manifest["source_id"],
                variable=variable,
                metric=VARIABLE_METRICS[variable],
                start_year=2071,
                end_year=2100,
                variant_label=records[0]["variant_label"],
                grid_label=records[0]["grid_label"],
                parent_experiment_id=metadata.get(
                    "parent_experiment_id", "not_applicable"
                ),
                parent_variant_label=metadata.get(
                    "parent_variant_label", "not_applicable"
                ),
                spatial_padding_degrees=spatial_padding_degrees,
            )
            frame["dataset_key"] = records[0]["dataset_key"]
            frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def build_time_series_frame(
    manifest_paths: list[Path],
    raw_dir: Path,
    download: bool = False,
    spatial_padding_degrees: float = 0.0,
) -> pd.DataFrame:
    """Build validated native-grid seasonal-year fields for matched manifests."""
    frames = []
    for manifest_path in manifest_paths:
        manifest = load_manifest(manifest_path)
        validate_matched_experiments(manifest)
        grouped: dict[str, list[dict]] = defaultdict(list)
        for record in manifest["records"]:
            if record["experiment_id"] in REQUIRED_EXPERIMENTS:
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
                validate_file(source, record)
                sources.append(source)
            validate_provenance(sources, records, manifest, experiment_id)
            metadata = experiment_metadata(manifest, experiment_id)
            variable = manifest["variable_id"]
            frame = prepare_time_series(
                source=sources,
                scenario=experiment_id,
                model=manifest["source_id"],
                variable=variable,
                metric=VARIABLE_METRICS[variable],
                start_year=2071,
                end_year=2100,
                variant_label=records[0]["variant_label"],
                grid_label=records[0]["grid_label"],
                parent_experiment_id=metadata.get(
                    "parent_experiment_id", "not_applicable"
                ),
                parent_variant_label=metadata.get(
                    "parent_variant_label", "not_applicable"
                ),
                spatial_padding_degrees=spatial_padding_degrees,
            )
            frame["dataset_key"] = records[0]["dataset_key"]
            frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def build(manifest_paths: list[Path], raw_dir: Path, output: Path, download: bool) -> None:
    combined = build_frame(manifest_paths, raw_dir, download)
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
            Path("data/manifests/cnrm_tasmax_amon.json"),
            Path("data/manifests/ukesm_tasmax_amon.json"),
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
