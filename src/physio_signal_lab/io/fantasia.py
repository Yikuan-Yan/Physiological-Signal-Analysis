from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import numpy as np
import pandas as pd
import wfdb

from physio_signal_lab.manifest import ManifestRow, manifest_records, read_manifest


AGE_SEX_RE = re.compile(r"Age:\s*(?P<age>\d+)\s+Sex:\s*(?P<sex>[FM])")


@dataclass(frozen=True)
class FantasiaRecordSummary:
    record_id: str
    age: int | None
    sex: str | None
    cohort: str
    sampling_rate_hz: float
    sample_count: int
    duration_seconds: float
    channel_names: tuple[str, ...]
    has_bp: bool
    annotation_count: int
    ecg_nonfinite_count: int


@dataclass(frozen=True)
class FantasiaRecordData:
    record_id: str
    sampling_rate_hz: float
    ecg: np.ndarray
    respiration: np.ndarray | None
    blood_pressure: np.ndarray | None
    reference_peak_samples: np.ndarray
    annotation_symbols: tuple[str, ...]
    ecg_nonfinite_count: int
    age: int | None
    sex: str | None
    cohort: str


def load_manifest_rows(manifest_path: str | Path) -> list[ManifestRow]:
    return read_manifest(manifest_path)


def record_ids_from_manifest(manifest_path: str | Path) -> list[str]:
    return manifest_records(read_manifest(manifest_path))


def record_base_path(record_id: str, raw_dir: str | Path) -> Path:
    return Path(raw_dir) / record_id


def cohort_from_record_id(record_id: str) -> str:
    if "y" in record_id:
        return "young"
    if "o" in record_id:
        return "old"
    return "unknown"


def age_sex_from_comments(comments: list[str]) -> tuple[int | None, str | None]:
    for comment in comments:
        match = AGE_SEX_RE.search(comment)
        if match:
            return int(match.group("age")), match.group("sex")
    return None, None


def _channel_index(sig_name: list[str], channel_name: str) -> int:
    try:
        return sig_name.index(channel_name)
    except ValueError as exc:
        raise ValueError(f"Missing channel {channel_name!r}; channels={sig_name}") from exc


def interpolate_nonfinite(signal: np.ndarray) -> tuple[np.ndarray, int]:
    finite = np.isfinite(signal)
    nonfinite_count = int((~finite).sum())
    if nonfinite_count == 0:
        return signal, 0
    if not finite.any():
        raise ValueError("Signal contains no finite samples")

    repaired = signal.copy()
    indices = np.arange(signal.shape[0], dtype=np.float64)
    repaired[~finite] = np.interp(indices[~finite], indices[finite], signal[finite])
    return repaired, nonfinite_count


def load_record(
    record_id: str,
    raw_dir: str | Path,
    *,
    ecg_channel: str = "ECG",
) -> FantasiaRecordData:
    base = record_base_path(record_id, raw_dir)
    record = wfdb.rdrecord(str(base), physical=True)
    annotation = wfdb.rdann(str(base), "ecg")

    if record.p_signal is None:
        raise ValueError(f"Record has no physical signal: {record_id}")

    sig_name = list(record.sig_name)
    ecg_idx = _channel_index(sig_name, ecg_channel)
    resp_idx = sig_name.index("RESP") if "RESP" in sig_name else None
    bp_idx = sig_name.index("BP") if "BP" in sig_name else None
    age, sex = age_sex_from_comments(record.comments)

    ecg_raw = np.asarray(record.p_signal[:, ecg_idx], dtype=np.float64)
    ecg, ecg_nonfinite_count = interpolate_nonfinite(ecg_raw)
    respiration = (
        np.asarray(record.p_signal[:, resp_idx], dtype=np.float64)
        if resp_idx is not None
        else None
    )
    blood_pressure = (
        np.asarray(record.p_signal[:, bp_idx], dtype=np.float64)
        if bp_idx is not None
        else None
    )
    reference_peak_samples = np.asarray(annotation.sample, dtype=np.int64)

    if ecg.ndim != 1:
        raise ValueError(f"ECG signal must be one-dimensional: {record_id}")
    if np.any(np.diff(reference_peak_samples) <= 0):
        raise ValueError(f"Annotation samples are not strictly increasing: {record_id}")

    return FantasiaRecordData(
        record_id=record_id,
        sampling_rate_hz=float(record.fs),
        ecg=ecg,
        respiration=respiration,
        blood_pressure=blood_pressure,
        reference_peak_samples=reference_peak_samples,
        annotation_symbols=tuple(annotation.symbol),
        ecg_nonfinite_count=ecg_nonfinite_count,
        age=age,
        sex=sex,
        cohort=cohort_from_record_id(record_id),
    )


def summarize_record(
    record_id: str,
    raw_dir: str | Path,
    *,
    ecg_channel: str = "ECG",
) -> FantasiaRecordSummary:
    data = load_record(record_id, raw_dir, ecg_channel=ecg_channel)
    channel_names = ["ECG"]
    if data.respiration is not None:
        channel_names.insert(0, "RESP")
    if data.blood_pressure is not None:
        channel_names.append("BP")
    sample_count = int(data.ecg.shape[0])
    return FantasiaRecordSummary(
        record_id=data.record_id,
        age=data.age,
        sex=data.sex,
        cohort=data.cohort,
        sampling_rate_hz=data.sampling_rate_hz,
        sample_count=sample_count,
        duration_seconds=sample_count / data.sampling_rate_hz,
        channel_names=tuple(channel_names),
        has_bp=data.blood_pressure is not None,
        annotation_count=int(data.reference_peak_samples.shape[0]),
        ecg_nonfinite_count=data.ecg_nonfinite_count,
    )


def build_inventory(
    record_ids: list[str],
    raw_dir: str | Path,
    *,
    ecg_channel: str = "ECG",
) -> pd.DataFrame:
    rows = []
    for record_id in record_ids:
        summary = summarize_record(record_id, raw_dir, ecg_channel=ecg_channel)
        rows.append(
            {
                "record_id": summary.record_id,
                "cohort": summary.cohort,
                "age": summary.age,
                "sex": summary.sex,
                "sampling_rate_hz": summary.sampling_rate_hz,
                "sample_count": summary.sample_count,
                "duration_seconds": summary.duration_seconds,
                "duration_minutes": summary.duration_seconds / 60.0,
                "channel_names": "|".join(summary.channel_names),
                "has_bp": summary.has_bp,
                "annotation_count": summary.annotation_count,
                "ecg_nonfinite_count": summary.ecg_nonfinite_count,
                "ecg_nonfinite_fraction": summary.ecg_nonfinite_count
                / summary.sample_count,
            }
        )
    return pd.DataFrame(rows)
