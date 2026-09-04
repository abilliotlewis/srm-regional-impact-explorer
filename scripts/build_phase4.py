"""Build the matched Phase 4 tasmax and precipitation explorer table."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from build_phase1 import build_frame

ROOT = Path(__file__).resolve().parents[1]
TASMAX_MANIFESTS = [
    ROOT / "data/manifests/cnrm_tasmax_amon.json",
    ROOT / "data/manifests/ipsl_tasmax_amon.json",
    ROOT / "data/manifests/mpi_lr_tasmax_amon.json",
    ROOT / "data/manifests/ukesm_tasmax_amon.json",
]
PR_MANIFESTS = [
    ROOT / "data/manifests/cnrm_pr_amon.json",
    ROOT / "data/manifests/ipsl_pr_amon.json",
    ROOT / "data/manifests/mpi_lr_pr_amon.json",
    ROOT / "data/manifests/ukesm_pr_amon.json",
]


def model_identities(frame: pd.DataFrame) -> set[tuple[str, str, str]]:
    return set(
        frame[["model", "variant_label", "grid_label"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )


def build_phase4(download: bool = False) -> pd.DataFrame:
    tasmax = build_frame(TASMAX_MANIFESTS, ROOT / "data/raw/tasmax", download)
    precipitation = build_frame(PR_MANIFESTS, ROOT / "data/raw/pr", download)
    if model_identities(tasmax) != model_identities(precipitation):
        raise ValueError("tasmax and pr do not use the same model, variant, and grid set")
    return pd.concat([tasmax, precipitation], ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "data/processed/regional_metrics.csv"
    )
    args = parser.parse_args()
    combined = build_phase4(args.download)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(args.output, index=False)
    print(f"Wrote {len(combined):,} validated Phase 4 records to {args.output}")


if __name__ == "__main__":
    main()
