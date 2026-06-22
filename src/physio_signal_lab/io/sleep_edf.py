from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.request import urlopen
import csv
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
