from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import hashlib


MANIFEST_COLUMNS = [
    "dataset",
    "version",
    "doi",
    "license",
    "access_date",
    "source_url",
    "record_id",
    "local_path",
    "sha256",
    "included",
    "exclusion_reason",
]


@dataclass(frozen=True)
class ManifestRow:
    dataset: str
    version: str
    doi: str
    license: str
    access_date: str
    source_url: str
    record_id: str
    local_path: Path
    sha256: str
    included: bool
    exclusion_reason: str


@dataclass(frozen=True)
class ManifestValidation:
    row_count: int
    record_count: int
    checked_file_count: int
    missing_files: tuple[str, ...]
    checksum_mismatches: tuple[str, ...]
    missing_record_files: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not (
            self.missing_files
            or self.checksum_mismatches
            or self.missing_record_files
        )


def read_manifest(path: str | Path) -> list[ManifestRow]:
    manifest_path = Path(path)
    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != MANIFEST_COLUMNS:
            raise ValueError(
                f"Unexpected manifest columns in {manifest_path}: {reader.fieldnames}"
            )
        rows: list[ManifestRow] = []
        for row in reader:
            rows.append(
                ManifestRow(
                    dataset=row["dataset"],
                    version=row["version"],
                    doi=row["doi"],
                    license=row["license"],
                    access_date=row["access_date"],
                    source_url=row["source_url"],
                    record_id=row["record_id"],
                    local_path=Path(row["local_path"]),
                    sha256=row["sha256"],
                    included=row["included"].lower() == "true",
                    exclusion_reason=row["exclusion_reason"],
                )
            )
    return rows


def manifest_records(rows: list[ManifestRow]) -> list[str]:
    return sorted(
        {row.record_id for row in rows if row.record_id != "_metadata" and row.included}
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(path: str | Path) -> ManifestValidation:
    rows = read_manifest(path)
    missing_files: list[str] = []
    checksum_mismatches: list[str] = []
    checked_file_count = 0

    for row in rows:
        if not row.included:
            continue
        if not row.local_path.exists():
            missing_files.append(row.local_path.as_posix())
            continue
        checked_file_count += 1
        if row.sha256 and sha256_file(row.local_path) != row.sha256:
            checksum_mismatches.append(row.local_path.as_posix())

    missing_record_files: list[str] = []
    by_record: dict[str, set[str]] = {}
    for row in rows:
        if row.record_id == "_metadata" or not row.included:
            continue
        by_record.setdefault(row.record_id, set()).add(row.local_path.suffix)
    for record_id, suffixes in by_record.items():
        for suffix in (".dat", ".hea", ".ecg"):
            if suffix not in suffixes:
                missing_record_files.append(f"{record_id}{suffix}")

    return ManifestValidation(
        row_count=len(rows),
        record_count=len(by_record),
        checked_file_count=checked_file_count,
        missing_files=tuple(missing_files),
        checksum_mismatches=tuple(checksum_mismatches),
        missing_record_files=tuple(sorted(missing_record_files)),
    )
