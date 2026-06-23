from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.request import urlopen
import csv
import hashlib
import re

import pandas as pd


SLEEP_EDF_FILENAME_RE = re.compile(
    r"^(?P<cohort>SC|ST)(?P<subject_id>\d{3})(?P<night>\d)"
    r"(?P<code>[A-Z0-9]{2})-(?P<kind>PSG|Hypnogram)\.edf$"
)


@dataclass(frozen=True)
class SleepEdfFile:
    filename: str
    cohort_code: str
    cohort: str
    subject_id: int
    night: int
    code: str
    kind: str

    @property
    def recording_id(self) -> str:
        return f"{self.cohort_code}{self.subject_id:03d}{self.night}"


def parse_sleep_edf_filename(filename: str) -> SleepEdfFile:
    match = SLEEP_EDF_FILENAME_RE.match(Path(filename).name)
    if match is None:
        raise ValueError(f"Unsupported Sleep-EDF filename: {filename!r}")
    cohort_code = match.group("cohort")
    cohort = "sleep-cassette" if cohort_code == "SC" else "sleep-telemetry"
    return SleepEdfFile(
        filename=Path(filename).name,
        cohort_code=cohort_code,
        cohort=cohort,
        subject_id=int(match.group("subject_id")),
        night=int(match.group("night")),
        code=match.group("code"),
        kind=match.group("kind"),
    )


def extract_edf_filenames(index_html: str) -> list[str]:
    filenames = re.findall(r'href="([^"]+\.edf)"', index_html)
    return sorted({Path(filename).name for filename in filenames})


def fetch_text(url: str, timeout_seconds: float = 30.0) -> str:
    with urlopen(url, timeout=timeout_seconds) as response:
        return response.read().decode("utf-8")


def fetch_edf_filenames(index_url: str) -> list[str]:
    return extract_edf_filenames(fetch_text(index_url))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_file(
    url: str,
    output_path: str | Path,
    *,
    overwrite: bool = False,
    timeout_seconds: float = 120.0,
    chunk_size: int = 1024 * 1024,
) -> dict[str, Any]:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    existed_before = out.exists()
    if existed_before and not overwrite:
        return {
            "source_url": url,
            "local_path": out.as_posix(),
            "status": "skipped_existing",
            "bytes": out.stat().st_size,
            "local_observed_sha256": sha256_file(out),
            "sha256": "",
            "verified_against_upstream": False,
        }

    temporary = out.with_name(f"{out.name}.part")
    if temporary.exists():
        temporary.unlink()
    with urlopen(url, timeout=timeout_seconds) as response, temporary.open("wb") as f:
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
    temporary.replace(out)
    return {
        "source_url": url,
        "local_path": out.as_posix(),
        "status": "downloaded_overwrite" if existed_before else "downloaded",
        "bytes": out.stat().st_size,
        "local_observed_sha256": sha256_file(out),
        "sha256": sha256_file(out),
        "verified_against_upstream": False,
    }


def _paired_files(files: list[SleepEdfFile]) -> dict[tuple[int, int], dict[str, SleepEdfFile]]:
    pairs: dict[tuple[int, int], dict[str, SleepEdfFile]] = {}
    for file in files:
        if file.cohort != "sleep-cassette":
            continue
        pairs.setdefault((file.subject_id, file.night), {})[file.kind] = file
    return pairs


def build_sleep_cassette_selection(
    filenames: list[str],
    *,
    benchmark_subjects: list[int],
    pilot_subjects: list[int],
    source_base_url: str,
    raw_dir: str | Path,
) -> pd.DataFrame:
    files = [parse_sleep_edf_filename(filename) for filename in filenames]
    pairs = _paired_files(files)
    rows: list[dict[str, Any]] = []
    base = source_base_url.rstrip("/")
    raw_root = Path(raw_dir)
    for subject_id in benchmark_subjects:
        available_nights = sorted(
            night
            for (candidate_subject, night), pair in pairs.items()
            if candidate_subject == subject_id and {"PSG", "Hypnogram"} <= set(pair)
        )
        if not available_nights:
            raise ValueError(f"No paired SC PSG/Hypnogram files found for subject {subject_id}")
        night = available_nights[0]
        pair = pairs[(subject_id, night)]
        psg = pair["PSG"]
        hypnogram = pair["Hypnogram"]
        role = "pilot" if subject_id in set(pilot_subjects) else "benchmark"
        rows.append(
            {
                "cohort": "sleep-cassette",
                "subject_id": subject_id,
                "night": night,
                "role": role,
                "recording_id": psg.recording_id,
                "psg_filename": psg.filename,
                "hypnogram_filename": hypnogram.filename,
                "psg_url": f"{base}/sleep-cassette/{psg.filename}",
                "hypnogram_url": f"{base}/sleep-cassette/{hypnogram.filename}",
                "psg_local_path": (raw_root / "sleep-cassette" / psg.filename).as_posix(),
                "hypnogram_local_path": (
                    raw_root / "sleep-cassette" / hypnogram.filename
                ).as_posix(),
            }
        )
    return pd.DataFrame(rows)


def _selection_download_rows(selection: pd.DataFrame) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for _, row in selection.iterrows():
        for file_role in ("psg", "hypnogram"):
            rows.append(
                {
                    "recording_id": str(row["recording_id"]),
                    "file_role": file_role,
                    "source_url": str(row[f"{file_role}_url"]),
                    "local_path": str(row[f"{file_role}_local_path"]),
                }
            )
    return rows


def download_sleep_edf_selection(
    selection_csv: str | Path,
    *,
    records: list[str] | None = None,
    overwrite: bool = False,
) -> pd.DataFrame:
    selection = pd.read_csv(selection_csv)
    if records is not None:
        wanted = set(records)
        selection = selection[selection["recording_id"].isin(wanted)].copy()
    if selection.empty:
        raise ValueError("No Sleep-EDF records selected for download")

    rows = []
    for item in _selection_download_rows(selection):
        result = download_file(
            item["source_url"],
            item["local_path"],
            overwrite=overwrite,
        )
        rows.append({**item, **result})
    return pd.DataFrame(rows)


def update_manifest_checksums(
    manifest_csv: str | Path,
    *,
    output_path: str | Path | None = None,
    records: list[str] | None = None,
    download_results: pd.DataFrame | None = None,
) -> Path:
    manifest_path = Path(manifest_csv)
    rows: list[dict[str, str]]
    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise ValueError(f"Manifest has no header: {manifest_path}")
        rows = [dict(row) for row in reader]

    wanted = set(records) if records is not None else None
    observed_by_path: dict[str, str] = {}
    if download_results is not None:
        for _, item in download_results.iterrows():
            local_path = str(item.get("local_path", ""))
            status = str(item.get("status", ""))
            observed = str(item.get("local_observed_sha256", item.get("sha256", "")))
            if local_path and observed and status.startswith("downloaded"):
                observed_by_path[Path(local_path).as_posix()] = observed
    for row in rows:
        if row.get("included", "").lower() != "true":
            continue
        if wanted is not None and row.get("record_id") not in wanted:
            continue
        local_path = Path(row["local_path"])
        if not local_path.exists():
            continue
        local_key = local_path.as_posix()
        if local_key in observed_by_path:
            row["sha256"] = observed_by_path[local_key]

    out = Path(output_path or manifest_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return out


def validate_sleep_edf_manifest(
    manifest_csv: str | Path,
    *,
    records: list[str] | None = None,
) -> pd.DataFrame:
    manifest = pd.read_csv(manifest_csv)
    if records is not None:
        wanted = set(records)
        manifest = manifest[manifest["record_id"].isin(wanted)].copy()
    if manifest.empty:
        raise ValueError("No Sleep-EDF manifest rows selected for validation")
    rows: list[dict[str, Any]] = []
    for _, row in manifest.iterrows():
        local_path = Path(str(row["local_path"]))
        expected_sha = "" if pd.isna(row["sha256"]) else str(row["sha256"])
        exists = local_path.exists()
        actual_sha = sha256_file(local_path) if exists else ""
        rows.append(
            {
                "record_id": row["record_id"],
                "local_path": local_path.as_posix(),
                "exists": exists,
                "bytes": local_path.stat().st_size if exists else 0,
                "expected_sha256": expected_sha,
                "actual_sha256": actual_sha,
                "checksum_ok": bool(expected_sha) and exists and actual_sha == expected_sha,
            }
        )
    return pd.DataFrame(rows)


def write_sleep_edf_manifest(
    selection: pd.DataFrame,
    *,
    output_path: str | Path,
    dataset: str,
    version: str,
    doi: str,
    license_name: str,
    access_date: str,
) -> Path:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    columns = [
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
    rows: list[dict[str, str]] = []
    for _, row in selection.iterrows():
        for file_role in ("psg", "hypnogram"):
            rows.append(
                {
                    "dataset": dataset,
                    "version": version,
                    "doi": doi,
                    "license": license_name,
                    "access_date": access_date,
                    "source_url": str(row[f"{file_role}_url"]),
                    "record_id": str(row["recording_id"]),
                    "local_path": str(row[f"{file_role}_local_path"]),
                    "sha256": "",
                    "included": "true",
                    "exclusion_reason": "",
                }
            )
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return out
