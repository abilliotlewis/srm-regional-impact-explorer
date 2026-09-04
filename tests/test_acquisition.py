import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from download_manifest import load_manifest, sha256_file, validate_file


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

