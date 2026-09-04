import hashlib
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from download_manifest import load_manifest, sha256_file, validate_file
from build_phase1 import validate_matched_experiments
from build_phase4 import model_identities


def test_phase1_manifest_is_complete():
    path = ROOT / "data" / "manifests" / "ipsl_tasmax_amon.json"
    manifest = load_manifest(path)
    assert {record["experiment_id"] for record in manifest["records"]} == {
        "G6solar",
        "G6sulfur",
        "ssp585",
        "ssp245",
    }
    assert all(record["variant_label"] == "r1i1p1f1" for record in manifest["records"])
    assert all(len(record["sha256"]) == 64 for record in manifest["records"])


def test_mpi_manifest_covers_analysis_period():
    path = ROOT / "data" / "manifests" / "mpi_lr_tasmax_amon.json"
    manifest = load_manifest(path)
    assert {record["experiment_id"] for record in manifest["records"]} == {
        "G6solar",
        "G6sulfur",
        "ssp585",
        "ssp245",
    }
    assert len(manifest["records"]) == 12
    assert all(record["variant_label"] == "r2i1p1f1" for record in manifest["records"])
    assert all(record["filename"].endswith(".nc") for record in manifest["records"])


def test_checksum_validation(tmp_path):
    path = tmp_path / "sample.bin"
    content = b"verified climate data"
    path.write_bytes(content)
    record = {
        "size_bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }
    validate_file(path, record)
    assert sha256_file(path) == record["sha256"]


def test_manifest_rejects_incomplete_records(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"records": [{"filename": "missing.nc"}]}))
    try:
        load_manifest(path)
    except ValueError as error:
        assert "missing" in str(error).lower()
    else:
        raise AssertionError("Expected incomplete-manifest validation error")


def test_matched_experiment_validation_rejects_parent_variant_mix():
    manifest = {
        "source_id": "TEST-ESM",
        "parent_experiment_id": "ssp585",
        "parent_variant_label": "r1i1p1f1",
        "records": [
            {"experiment_id": "G6solar", "variant_label": "r1i1p1f1", "grid_label": "gn"},
            {"experiment_id": "G6sulfur", "variant_label": "r2i1p1f1", "grid_label": "gn"},
            {"experiment_id": "ssp585", "variant_label": "r2i1p1f1", "grid_label": "gn"},
        ],
    }
    try:
        validate_matched_experiments(manifest)
    except ValueError as error:
        assert "variant-matched" in str(error)
    else:
        raise AssertionError("Expected parent-variant mismatch validation error")


def test_phase4_precipitation_manifests_match_phase3_model_set():
    expected = {
        ("CNRM-ESM2-1", "r1i1p1f2", "gr"),
        ("IPSL-CM6A-LR", "r1i1p1f1", "gr"),
        ("MPI-ESM1-2-LR", "r2i1p1f1", "gn"),
        ("UKESM1-0-LL", "r1i1p1f2", "gn"),
    }
    observed = set()
    for path in sorted((ROOT / "data/manifests").glob("*_pr_amon.json")):
        manifest = load_manifest(path)
        validate_matched_experiments(manifest)
        identities = {
            (manifest["source_id"], record["variant_label"], record["grid_label"])
            for record in manifest["records"]
        }
        assert len(identities) == 1
        observed.update(identities)
        assert manifest["variable_id"] == "pr"
        assert manifest["analysis_period"] == "2071-2100"
        assert all(record.get("tracking_id") for record in manifest["records"])
        assert all(record["size_bytes"] > 0 for record in manifest["records"])
    assert observed == expected


def test_model_identity_helper_preserves_variant_and_grid():
    frame = pd.DataFrame(
        {
            "model": ["TEST", "TEST"],
            "variant_label": ["r1", "r2"],
            "grid_label": ["gn", "gn"],
        }
    )
    assert model_identities(frame) == {("TEST", "r1", "gn"), ("TEST", "r2", "gn")}
