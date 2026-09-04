from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import httpx


def load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text())
    records = manifest.get("records", [])
    if not records:
        raise ValueError("Manifest contains no records")
    required = {"dataset_key", "filename", "size_bytes", "sha256", "url"}
    for index, record in enumerate(records):
        missing = required.difference(record)
        if missing:
            raise ValueError(f"Manifest record {index} is missing {sorted(missing)}")
    return manifest


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_file(path: Path, record: dict) -> None:
    actual_size = path.stat().st_size
    if actual_size != record["size_bytes"]:
        raise ValueError(
            f"Size mismatch for {path.name}: expected {record['size_bytes']}, got {actual_size}"
        )
    actual_hash = sha256_file(path)
    if actual_hash != record["sha256"]:
        raise ValueError(
            f"SHA-256 mismatch for {path.name}: expected {record['sha256']}, got {actual_hash}"
        )


def download_record(record: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / record["filename"]
    if destination.exists():
        validate_file(destination, record)
        print(f"Verified existing {destination.name}")
        return destination

    partial = destination.with_suffix(destination.suffix + ".part")
    with httpx.stream(
        "GET", record["url"], follow_redirects=True, timeout=300.0
    ) as response:
        response.raise_for_status()
        with partial.open("wb") as target:
            for chunk in response.iter_bytes(chunk_size=1024 * 1024):
                target.write(chunk)
    partial.replace(destination)
    validate_file(destination, record)
    print(f"Downloaded and verified {destination.name}")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    for record in manifest["records"]:
        download_record(record, args.output_dir)


if __name__ == "__main__":
    main()

