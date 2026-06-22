from __future__ import annotations

from pathlib import Path
from typing import Any
import csv

import pandas as pd

from physio_signal_lab.io.sleep_edf import download_file, sha256_file
from physio_signal_lab.manifest import MANIFEST_COLUMNS


REQUIRED_EXTENSIONS = ("hea", "dat", "st", "ecg")


def mit_bih_psg_records(config: dict[str, Any], records: list[str] | None = None) -> list[str]:
    if records is not None:
        return list(records)
    return [str(record) for record in config["selection"]["pilot_records"]]


def _selected_extensions(config: dict[str, Any]) -> list[str]:
    extensions = [str(item).lstrip(".") for item in config["selection"].get("files", [])]
    return extensions or list(REQUIRED_EXTENSIONS)


def build_mit_bih_psg_manifest(
    config: dict[str, Any],
    *,
    records: list[str] | None = None,
) -> pd.DataFrame:
    dataset = config["dataset"]
    base_url = str(dataset["source_base_url"]).rstrip("/")
    raw_root = Path(str(dataset["raw_dir"]))
    rows: list[dict[str, str]] = []
    for record_id in mit_bih_psg_records(config, records):
        for extension in _selected_extensions(config):
            filename = f"{record_id}.{extension}"
            rows.append(
                {
                    "dataset": str(dataset["name"]),
                    "version": str(dataset["version"]),
                    "doi": str(dataset["doi"]),
                    "license": str(dataset["license"]),
                    "access_date": str(dataset["access_date"]),
                    "source_url": f"{base_url}/{filename}",
                    "record_id": record_id,
                    "local_path": (raw_root / filename).as_posix(),
                    "sha256": "",
                    "included": "true",
                    "exclusion_reason": "",
                }
            )
    return pd.DataFrame(rows, columns=MANIFEST_COLUMNS)


def write_mit_bih_psg_manifest(
    config: dict[str, Any],
    *,
    records: list[str] | None = None,
    output_path: str | Path | None = None,
) -> Path:
    manifest = build_mit_bih_psg_manifest(config, records=records)
    out = Path(output_path or config["outputs"]["manifest_csv"])
    out.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(out, index=False)
    return out


def download_mit_bih_psg_selection(
    config: dict[str, Any],
    *,
    records: list[str] | None = None,
    overwrite: bool = False,
) -> pd.DataFrame:
    manifest = build_mit_bih_psg_manifest(config, records=records)
    rows: list[dict[str, Any]] = []
    for _, item in manifest.iterrows():
        result = download_file(
            str(item["source_url"]),
            str(item["local_path"]),
            overwrite=overwrite,
        )
        rows.append(
            {
                "record_id": str(item["record_id"]),
                "file_extension": Path(str(item["local_path"])).suffix.lstrip("."),
                **result,
            }
        )
    return pd.DataFrame(rows)


def update_mit_bih_psg_manifest_checksums(
    manifest_csv: str | Path,
    *,
    output_path: str | Path | None = None,
    records: list[str] | None = None,
) -> Path:
    manifest_path = Path(manifest_csv)
    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if fieldnames != MANIFEST_COLUMNS:
            raise ValueError(f"Unexpected MIT-BIH PSG manifest columns: {fieldnames}")
        rows = [dict(row) for row in reader]

    wanted = set(records) if records is not None else None
    for row in rows:
        if row.get("included", "").lower() != "true":
            continue
        if wanted is not None and row.get("record_id") not in wanted:
            continue
        local_path = Path(row["local_path"])
        if local_path.exists():
            row["sha256"] = sha256_file(local_path)

    out = Path(output_path or manifest_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return out


def validate_mit_bih_psg_manifest(
    manifest_csv: str | Path,
    *,
    records: list[str] | None = None,
) -> pd.DataFrame:
    manifest = pd.read_csv(manifest_csv)
    if records is not None:
        wanted = set(records)
        manifest = manifest[manifest["record_id"].isin(wanted)].copy()
    if manifest.empty:
        raise ValueError("No MIT-BIH PSG manifest rows selected for validation")

    rows: list[dict[str, Any]] = []
    for _, item in manifest.iterrows():
        local_path = Path(str(item["local_path"]))
        expected_sha = "" if pd.isna(item["sha256"]) else str(item["sha256"])
        exists = local_path.exists()
        actual_sha = sha256_file(local_path) if exists else ""
        rows.append(
            {
                "record_id": str(item["record_id"]),
                "file_extension": local_path.suffix.lstrip("."),
                "local_path": local_path.as_posix(),
                "exists": exists,
                "bytes": local_path.stat().st_size if exists else 0,
                "expected_sha256": expected_sha,
                "actual_sha256": actual_sha,
                "checksum_ok": bool(expected_sha) and exists and actual_sha == expected_sha,
            }
        )
    validation = pd.DataFrame(rows)
    required = set(REQUIRED_EXTENSIONS)
    record_extension_map = (
        validation[validation["exists"]]
        .groupby("record_id")["file_extension"]
        .apply(lambda values: set(str(value) for value in values))
        .to_dict()
    )
    validation["required_file_set_complete"] = validation["record_id"].map(
        lambda record_id: required <= record_extension_map.get(str(record_id), set())
    )
    return validation
