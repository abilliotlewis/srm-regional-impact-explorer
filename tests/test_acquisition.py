import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from download_manifest import load_manifest, sha256_file, validate_file
from build_phase1 import validate_matched_experiments


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
