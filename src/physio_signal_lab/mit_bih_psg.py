from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from physio_signal_lab.io.mit_bih_psg import (
    mit_bih_psg_records,
    validate_mit_bih_psg_manifest,
)
from physio_signal_lab.sleep_outputs import clean_output_prefix


RESPIRATORY_EVENT_TOKENS = {"H", "HA", "OA", "X", "CA", "CAA"}
HYPOPNEA_TOKENS = {"H", "HA"}
OBSTRUCTIVE_APNEA_TOKENS = {"OA", "X"}
CENTRAL_APNEA_TOKENS = {"CA", "CAA"}
AROUSAL_ASSOCIATED_RESPIRATORY_TOKENS = {"HA", "X", "CAA"}
LEG_MOVEMENT_TOKENS = {"L", "LA"}


@dataclass(frozen=True)
class ParsedAuxNote:
    sleep_stage_raw: str
    mapped_stage: str
    included: bool
    included_sleep: bool
    event_tokens: tuple[str, ...]


@dataclass(frozen=True)
class MitBihPsgPilotOutputs:
    annotation_epochs_csv: Path
    respiratory_metrics_csv: Path
    source_alignment_csv: Path
    oxygen_metrics_csv: Path
    oxygen_artifact_review_csv: Path
    event_windows_csv: Path
    channel_quality_csv: Path
    clinical_indicators_csv: Path
    report_md: Path


def parse_aux_note(
    aux_note: str,
    *,
    stage_mapping: dict[str, str],
    excluded_stage_tokens: set[str],
) -> ParsedAuxNote:
    tokens = str(aux_note).replace("\x00", "").strip().split()
    if not tokens:
        return ParsedAuxNote("", "", False, False, ())
    stage_raw = tokens[0]
    event_tokens = tuple(tokens[1:])
    mapped_stage = str(stage_mapping.get(stage_raw, ""))
    included = bool(mapped_stage)
    included_sleep = mapped_stage in {"N1", "N2", "N3", "REM"}
    if stage_raw in excluded_stage_tokens:
        included = False
        included_sleep = False
    return ParsedAuxNote(stage_raw, mapped_stage, included, included_sleep, event_tokens)


def _count_tokens(tokens: tuple[str, ...], target: set[str]) -> int:
    return sum(1 for token in tokens if token in target)


def _base_path(raw_dir: str | Path, record_id: str) -> Path:
    return Path(raw_dir) / record_id


def _scoped_mit_bih_output_path(output_prefix: str, suffix: str) -> Path:
    prefix = clean_output_prefix(output_prefix)
    return Path("results") / "mit_bih_psg" / f"{prefix}_{suffix}"


def _scoped_mit_bih_report_path(output_prefix: str, suffix: str) -> Path:
    prefix = clean_output_prefix(output_prefix)
    return Path("reports") / f"mit_bih_psg_{prefix}_{suffix}"


def _output_paths(
    outputs: dict[str, Any],
    output_prefix: str | None,
) -> dict[str, Path]:
    if output_prefix is None:
        return {
            "annotation_epochs_csv": Path(outputs["annotation_epochs_csv"]),
            "respiratory_metrics_csv": Path(outputs["respiratory_metrics_csv"]),
            "source_alignment_csv": Path(
                outputs.get(
                    "source_alignment_csv",
                    "results/mit_bih_psg/pilot_source_ahi_alignment.csv",
                )
            ),
            "oxygen_metrics_csv": Path(outputs["oxygen_metrics_csv"]),
            "oxygen_artifact_review_csv": Path(
                outputs.get(
                    "oxygen_artifact_review_csv",
                    "results/mit_bih_psg/pilot_oxygen_artifact_review.csv",
                )
            ),
            "event_windows_csv": Path(outputs["event_windows_csv"]),
            "channel_quality_csv": Path(outputs["channel_quality_csv"]),
            "clinical_indicators_csv": Path(outputs["clinical_indicators_csv"]),
            "report_md": Path(outputs["report_md"]),
            "event_plot_dir": Path(outputs["event_plot_dir"]),
        }
    prefix = clean_output_prefix(output_prefix)
    return {
        "annotation_epochs_csv": _scoped_mit_bih_output_path(
            prefix,
            "annotation_epochs.csv",
        ),
        "respiratory_metrics_csv": _scoped_mit_bih_output_path(
            prefix,
            "respiratory_metrics.csv",
        ),
        "source_alignment_csv": _scoped_mit_bih_output_path(
            prefix,
            "source_ahi_alignment.csv",
        ),
        "oxygen_metrics_csv": _scoped_mit_bih_output_path(prefix, "oxygen_metrics.csv"),
        "oxygen_artifact_review_csv": _scoped_mit_bih_output_path(
            prefix,
            "oxygen_artifact_review.csv",
        ),
        "event_windows_csv": _scoped_mit_bih_output_path(prefix, "event_windows.csv"),
        "channel_quality_csv": _scoped_mit_bih_output_path(prefix, "channel_quality.csv"),
        "clinical_indicators_csv": _scoped_mit_bih_output_path(
            prefix,
            "clinical_indicators.csv",
        ),
        "report_md": _scoped_mit_bih_report_path(prefix, "respiratory_pilot.md"),
        "event_plot_dir": Path("figures") / "mit_bih_psg" / prefix,
    }


def read_annotation_epochs(
    *,
    record_id: str,
    raw_dir: str | Path,
    epoch_seconds: float,
    stage_mapping: dict[str, str],
    excluded_stage_tokens: set[str],
) -> pd.DataFrame:
    if epoch_seconds <= 0:
        raise ValueError("epoch_seconds must be positive")
    try:
        import wfdb
    except ImportError as exc:
        raise RuntimeError("wfdb is required for MIT-BIH PSG WFDB files") from exc

    base = _base_path(raw_dir, record_id).as_posix()
    header = wfdb.rdheader(base)
    if float(header.fs) <= 0:
        raise ValueError(f"Invalid sampling rate for {record_id}: {header.fs}")
    annotation = wfdb.rdann(base, "st")
    aux_notes = getattr(annotation, "aux_note", None)
    if aux_notes is None:
        raise ValueError(f"No .st aux_note annotations found for {record_id}")

    rows: list[dict[str, Any]] = []
    for epoch_index, (sample, aux_note) in enumerate(zip(annotation.sample, aux_notes)):
        parsed = parse_aux_note(
            str(aux_note),
            stage_mapping=stage_mapping,
            excluded_stage_tokens=excluded_stage_tokens,
        )
        respiratory_count = _count_tokens(parsed.event_tokens, RESPIRATORY_EVENT_TOKENS)
        hypopnea_count = _count_tokens(parsed.event_tokens, HYPOPNEA_TOKENS)
        obstructive_count = _count_tokens(parsed.event_tokens, OBSTRUCTIVE_APNEA_TOKENS)
        central_count = _count_tokens(parsed.event_tokens, CENTRAL_APNEA_TOKENS)
        arousal_resp_count = _count_tokens(
            parsed.event_tokens,
            AROUSAL_ASSOCIATED_RESPIRATORY_TOKENS,
        )
        leg_count = _count_tokens(parsed.event_tokens, LEG_MOVEMENT_TOKENS)
        arousal_count = _count_tokens(parsed.event_tokens, {"A"})
        rows.append(
            {
                "record_id": record_id,
                "epoch_index": int(epoch_index),
                "sample": int(sample),
                "onset_seconds": float(sample) / float(header.fs),
                "epoch_seconds": float(epoch_seconds),
                "sleep_stage_raw": parsed.sleep_stage_raw,
                "mapped_stage": parsed.mapped_stage,
                "included": parsed.included,
                "included_sleep": parsed.included_sleep,
                "event_tokens": " ".join(parsed.event_tokens),
                "respiratory_event_count": int(respiratory_count),
                "respiratory_event_epoch": bool(respiratory_count > 0),
                "hypopnea_count": int(hypopnea_count),
                "obstructive_apnea_count": int(obstructive_count),
                "central_apnea_count": int(central_count),
                "arousal_associated_respiratory_count": int(arousal_resp_count),
                "leg_movement_count": int(leg_count),
                "arousal_count": int(arousal_count),
            }
        )
    epochs = pd.DataFrame(rows)
    if epochs.empty:
        raise ValueError(f"No MIT-BIH PSG .st epochs parsed for {record_id}")
    return epochs


def _safe_per_sleep_hour(count: float, sleep_hours: float) -> float:
    if sleep_hours <= 0:
        return math.nan
    return float(count) / float(sleep_hours)


def _severity_from_ahi_style_burden(value: float) -> str:
    if not math.isfinite(value):
        return "unavailable"
    if value < 5.0:
        return "minimal_range"
    if value < 15.0:
        return "mild_range"
    if value < 30.0:
        return "moderate_range"
    return "severe_range"


def _source_ahi_alignment_status(delta: float, source_note: str) -> str:
    if source_note:
        return "source_ahi_estimated_annotation_unavailable"
    if math.isfinite(delta) and abs(delta) > 10.0:
        return "needs_manual_review"
    return "roughly_aligned"


def respiratory_metrics(
    epochs: pd.DataFrame,
    *,
    source_reported_ahi: dict[str, float],
    source_ahi_notes: dict[str, str] | None = None,
    epoch_seconds: float,
) -> pd.DataFrame:
    if epoch_seconds <= 0:
        raise ValueError("epoch_seconds must be positive")
    rows: list[dict[str, Any]] = []
    epoch_minutes = float(epoch_seconds) / 60.0
    for record_id, group in epochs.groupby("record_id", sort=True):
        total_epochs = int(len(group))
        included_sleep = group[group["included_sleep"]].copy()
        sleep_epochs = int(len(included_sleep))
        sleep_minutes = float(sleep_epochs) * epoch_minutes
        sleep_hours = sleep_minutes / 60.0
        sleep_resp_count = int(included_sleep["respiratory_event_count"].sum())
        sleep_resp_epoch_count = int(included_sleep["respiratory_event_epoch"].sum())
        ahi_style = _safe_per_sleep_hour(sleep_resp_count, sleep_hours)
        reported = source_reported_ahi.get(str(record_id), math.nan)
        source_note = (source_ahi_notes or {}).get(str(record_id), "")
        row = {
            "record_id": str(record_id),
            "epoch_seconds": float(epoch_seconds),
            "total_epochs": total_epochs,
            "recording_minutes_from_annotations": float(total_epochs) * epoch_minutes,
            "sleep_epochs": sleep_epochs,
            "sleep_minutes": sleep_minutes,
            "sleep_hours": sleep_hours,
            "wake_minutes": float((group["mapped_stage"] == "WAKE").sum()) * epoch_minutes,
            "movement_or_excluded_minutes": float((~group["included"]).sum()) * epoch_minutes,
            "sleep_respiratory_event_count": sleep_resp_count,
            "sleep_respiratory_event_epochs": sleep_resp_epoch_count,
            "all_epoch_respiratory_event_count": int(group["respiratory_event_count"].sum()),
            "ahi_style_events_per_sleep_hour": ahi_style,
            "respiratory_event_epochs_per_sleep_hour": _safe_per_sleep_hour(
                sleep_resp_epoch_count,
                sleep_hours,
            ),
            "hypopnea_events_per_sleep_hour": _safe_per_sleep_hour(
                int(included_sleep["hypopnea_count"].sum()),
                sleep_hours,
            ),
            "obstructive_apnea_events_per_sleep_hour": _safe_per_sleep_hour(
                int(included_sleep["obstructive_apnea_count"].sum()),
                sleep_hours,
            ),
            "central_apnea_events_per_sleep_hour": _safe_per_sleep_hour(
                int(included_sleep["central_apnea_count"].sum()),
                sleep_hours,
            ),
            "arousal_associated_respiratory_events_per_sleep_hour": _safe_per_sleep_hour(
                int(included_sleep["arousal_associated_respiratory_count"].sum()),
                sleep_hours,
            ),
            "source_reported_ahi": float(reported),
            "source_ahi_note": source_note,
            "ahi_style_minus_source_reported_ahi": (
                ahi_style - float(reported) if math.isfinite(float(reported)) else math.nan
            ),
        }
        row["ahi_style_learning_severity"] = _severity_from_ahi_style_burden(ahi_style)
        delta = float(row["ahi_style_minus_source_reported_ahi"])
        row["source_ahi_alignment_status"] = _source_ahi_alignment_status(delta, source_note)
        rows.append(row)
    return pd.DataFrame(rows)


def _finite_or_nan(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return math.nan
    return numeric if math.isfinite(numeric) else math.nan


def _dominant_respiratory_event_type(row: pd.Series) -> str:
    candidates = {
        "hypopnea": _finite_or_nan(row.get("hypopnea_events_per_sleep_hour", math.nan)),
        "obstructive_apnea": _finite_or_nan(
            row.get("obstructive_apnea_events_per_sleep_hour", math.nan)
        ),
        "central_apnea": _finite_or_nan(row.get("central_apnea_events_per_sleep_hour", math.nan)),
    }
    finite_candidates = {
        key: value for key, value in candidates.items() if math.isfinite(value)
    }
    if not finite_candidates:
        return "unavailable"
    event_type, rate = max(finite_candidates.items(), key=lambda item: item[1])
    return event_type if rate > 0 else "none"


def source_ahi_alignment(metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in metrics.iterrows():
        record_id = str(row["record_id"])
        annotation_ahi = _finite_or_nan(row.get("ahi_style_events_per_sleep_hour", math.nan))
        source_ahi = _finite_or_nan(row.get("source_reported_ahi", math.nan))
        delta = _finite_or_nan(row.get("ahi_style_minus_source_reported_ahi", math.nan))
        source_note = str(row.get("source_ahi_note", ""))
        abs_delta = abs(delta) if math.isfinite(delta) else math.nan
        percent_delta = (
            delta / source_ahi * 100.0
            if math.isfinite(delta) and math.isfinite(source_ahi) and source_ahi != 0
            else math.nan
        )
        alignment_status = str(row.get("source_ahi_alignment_status", ""))
        dominant_event_type = _dominant_respiratory_event_type(row)
        if source_note:
            review_priority = "separate_source_review"
            review_focus = (
                "Source AHI is estimated and apnea annotations are unavailable; do not "
                "interpret annotation burden as true no-OSA evidence."
            )
        elif not math.isfinite(source_ahi):
            review_priority = "source_ahi_missing"
            review_focus = "Add or verify source AHI before alignment review."
        elif math.isfinite(abs_delta) and abs_delta > 10.0:
            review_priority = "manual_review_high"
            review_focus = (
                "Inspect event tokens, sleep/wake exclusion, and source scoring assumptions."
            )
        elif math.isfinite(abs_delta) and abs_delta > 5.0:
            review_priority = "manual_review_medium"
            review_focus = "Review scoring assumptions if this record is used as an example."
        else:
            review_priority = "low"
            review_focus = "Token burden is close enough for the current educational proxy."
        rows.append(
            {
                "record_id": record_id,
                "annotation_ahi_style_events_per_sleep_hour": annotation_ahi,
                "source_reported_ahi": source_ahi,
                "delta_events_per_sleep_hour": delta,
                "absolute_delta_events_per_sleep_hour": abs_delta,
                "percent_delta_vs_source_ahi": percent_delta,
                "alignment_status": alignment_status,
                "review_priority": review_priority,
                "dominant_respiratory_event_type": dominant_event_type,
                "source_ahi_note": source_note,
                "sleep_respiratory_event_count": int(row["sleep_respiratory_event_count"]),
                "sleep_hours": _finite_or_nan(row.get("sleep_hours", math.nan)),
                "hypopnea_events_per_sleep_hour": _finite_or_nan(
                    row.get("hypopnea_events_per_sleep_hour", math.nan)
                ),
                "obstructive_apnea_events_per_sleep_hour": _finite_or_nan(
                    row.get("obstructive_apnea_events_per_sleep_hour", math.nan)
                ),
                "central_apnea_events_per_sleep_hour": _finite_or_nan(
                    row.get("central_apnea_events_per_sleep_hour", math.nan)
                ),
                "review_focus": review_focus,
            }
        )
    priority_rank = {
        "manual_review_high": 0,
        "separate_source_review": 1,
        "manual_review_medium": 2,
        "source_ahi_missing": 3,
        "low": 4,
    }
    alignment = pd.DataFrame(rows)
    if alignment.empty:
        return alignment
    alignment["_priority_rank"] = alignment["review_priority"].map(priority_rank).fillna(99)
    alignment = alignment.sort_values(
        ["_priority_rank", "absolute_delta_events_per_sleep_hour", "record_id"],
        ascending=[True, False, True],
        na_position="last",
    ).drop(columns=["_priority_rank"])
    return alignment.reset_index(drop=True)


def channel_quality(
    *,
    records: list[str],
    raw_dir: str | Path,
    sample_seconds: float,
) -> pd.DataFrame:
    if sample_seconds <= 0:
        raise ValueError("sample_seconds must be positive")
    try:
        import wfdb
    except ImportError as exc:
        raise RuntimeError("wfdb is required for MIT-BIH PSG WFDB files") from exc

    rows: list[dict[str, Any]] = []
    for record_id in records:
        base = _base_path(raw_dir, record_id).as_posix()
        header = wfdb.rdheader(base)
        fs = float(header.fs)
        if fs <= 0:
            raise ValueError(f"Invalid sampling rate for {record_id}: {header.fs}")
        sample_count = min(int(header.sig_len), int(round(sample_seconds * fs)))
        record = wfdb.rdrecord(base, sampfrom=0, sampto=sample_count, physical=True)
        signals = np.asarray(record.p_signal, dtype=np.float64)
        if signals.ndim != 2:
            raise ValueError(f"Unexpected signal shape for {record_id}: {signals.shape}")
        for index, channel in enumerate(record.sig_name):
            signal = signals[:, index]
            finite = np.isfinite(signal)
            finite_count = int(finite.sum())
            finite_fraction = float(finite_count) / float(len(signal)) if len(signal) else 0.0
            finite_signal = signal[finite]
            standard_deviation = (
                float(np.std(finite_signal, dtype=np.float64)) if finite_count > 0 else math.nan
            )
            lower_name = str(channel).lower()
            rows.append(
                {
                    "record_id": record_id,
                    "channel_index": int(index),
                    "channel_name": str(channel),
                    "unit": str(record.units[index]) if index < len(record.units) else "",
                    "sampling_rate_hz": fs,
                    "record_duration_hours": float(header.sig_len) / fs / 3600.0,
                    "sampled_seconds": float(sample_count) / fs,
                    "finite_fraction_pct": finite_fraction * 100.0,
                    "standard_deviation": standard_deviation,
                    "is_respiration_channel": "resp" in lower_name,
                    "is_spo2_channel": any(
                        marker in lower_name
                        for marker in ("so2", "spo2", "sao2", "oxygen", "oxim")
                    ),
                    "has_dynamic_signal": bool(
                        finite_fraction >= 0.99
                        and math.isfinite(standard_deviation)
                        and standard_deviation > 1e-9
                    ),
                }
            )
    return pd.DataFrame(rows)


def _is_respiration_channel(channel_name: str) -> bool:
    return "resp" in str(channel_name).lower()


def _is_spo2_channel(channel_name: str) -> bool:
    lower_name = str(channel_name).lower()
    return any(marker in lower_name for marker in ("so2", "spo2", "sao2", "oxygen", "oxim"))


def _channel_indices(record: Any, predicate: Any) -> list[int]:
    return [index for index, channel in enumerate(record.sig_name) if predicate(str(channel))]


def _scaled_plausible_spo2(signal: np.ndarray) -> np.ndarray:
    values = np.asarray(signal, dtype=np.float64)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return values
    median = float(np.median(finite))
    maximum = float(np.max(finite))
    if 0.0 <= median <= 1.5 and maximum <= 1.5:
        values = values * 100.0
    return values


def _count_threshold_segments(
    mask: np.ndarray,
    *,
    fs: float,
    min_duration_seconds: float,
) -> tuple[int, float]:
    if fs <= 0:
        raise ValueError("fs must be positive")
    if min_duration_seconds <= 0:
        raise ValueError("min_duration_seconds must be positive")
    values = np.asarray(mask, dtype=bool)
    if values.size == 0:
        return 0, 0.0
    padded = np.concatenate(([False], values, [False]))
    changes = np.diff(padded.astype(np.int8))
    starts = np.flatnonzero(changes == 1)
    stops = np.flatnonzero(changes == -1)
    min_samples = int(math.ceil(min_duration_seconds * fs))
    count = 0
    total_samples = 0
    for start, stop in zip(starts, stops):
        length = int(stop - start)
        if length >= min_samples:
            count += 1
            total_samples += length
    return count, float(total_samples) / fs


def _pre_event_rolling_baseline(
    signal: np.ndarray,
    plausible: np.ndarray,
    *,
    fs: float,
    baseline_window_seconds: float,
) -> np.ndarray:
    if fs <= 0:
        raise ValueError("fs must be positive")
    if baseline_window_seconds <= 0:
        raise ValueError("baseline_window_seconds must be positive")
    values = np.asarray(signal, dtype=np.float64)
    valid = np.asarray(plausible, dtype=bool)
    if values.shape != valid.shape:
        raise ValueError("signal and plausible mask must have the same shape")
    if values.size == 0:
        return np.asarray([], dtype=np.float64)
    window_samples = max(1, int(round(baseline_window_seconds * fs)))
    baseline_source = np.where(valid, values, np.nan)
    rolling = pd.Series(baseline_source).rolling(
        window=window_samples,
        min_periods=1,
    )
    return rolling.max().shift(1).to_numpy(dtype=np.float64)


def _count_desaturation_events(
    signal: np.ndarray,
    *,
    baseline: np.ndarray,
    plausible: np.ndarray,
    scope: np.ndarray,
    fs: float,
    drop_pct: float,
    min_duration_seconds: float,
) -> tuple[int, float]:
    if drop_pct <= 0:
        raise ValueError("drop_pct must be positive")
    values = np.asarray(signal, dtype=np.float64)
    baseline_values = np.asarray(baseline, dtype=np.float64)
    plausible_mask = np.asarray(plausible, dtype=bool)
    scope_mask = np.asarray(scope, dtype=bool)
    if not (
        values.shape == baseline_values.shape == plausible_mask.shape == scope_mask.shape
    ):
        raise ValueError("signal, baseline, plausible, and scope arrays must match")
    desaturation_mask = (
        scope_mask
        & plausible_mask
        & np.isfinite(values)
        & np.isfinite(baseline_values)
        & ((baseline_values - values) >= float(drop_pct))
    )
    return _count_threshold_segments(
        desaturation_mask,
        fs=fs,
        min_duration_seconds=min_duration_seconds,
    )


def _sleep_sample_mask(
    record_epochs: pd.DataFrame,
    *,
    sample_count: int,
    fs: float,
) -> np.ndarray:
    if sample_count < 0:
        raise ValueError("sample_count must be non-negative")
    if fs <= 0:
        raise ValueError("fs must be positive")
    mask = np.zeros(int(sample_count), dtype=bool)
    if mask.size == 0 or record_epochs.empty:
        return mask
    sleep_epochs = record_epochs[record_epochs["included_sleep"].astype(bool)]
    for _, epoch in sleep_epochs.iterrows():
        onset_seconds = float(epoch["onset_seconds"])
        epoch_seconds = float(epoch["epoch_seconds"])
        if not math.isfinite(onset_seconds) or not math.isfinite(epoch_seconds):
            continue
        if epoch_seconds <= 0:
            continue
        start = max(0, int(math.floor(onset_seconds * fs)))
        stop = min(mask.size, int(math.ceil((onset_seconds + epoch_seconds) * fs)))
        if stop > start:
            mask[start:stop] = True
    return mask


def oxygen_saturation_metrics(
    *,
    records: list[str],
    raw_dir: str | Path,
    respiratory: pd.DataFrame,
    epochs: pd.DataFrame,
    drop_thresholds_pct: list[float],
    low_spo2_thresholds_pct: list[float],
    min_desaturation_seconds: float,
    baseline_window_seconds: float,
) -> pd.DataFrame:
    if min_desaturation_seconds <= 0:
        raise ValueError("min_desaturation_seconds must be positive")
    if baseline_window_seconds <= 0:
        raise ValueError("baseline_window_seconds must be positive")
    try:
        import wfdb
    except ImportError as exc:
        raise RuntimeError("wfdb is required for MIT-BIH PSG WFDB files") from exc

    sleep_hours_by_record = {
        str(row["record_id"]): float(row["sleep_hours"]) for _, row in respiratory.iterrows()
    }
    epochs_by_record = {
        str(record_id): group.copy() for record_id, group in epochs.groupby("record_id", sort=True)
    }
    rows: list[dict[str, Any]] = []
    for record_id in records:
        base = _base_path(raw_dir, record_id).as_posix()
        header = wfdb.rdheader(base)
        fs = float(header.fs)
        if fs <= 0:
            raise ValueError(f"Invalid sampling rate for {record_id}: {header.fs}")
        spo2_indices = _channel_indices(header, _is_spo2_channel)
        sleep_hours = sleep_hours_by_record.get(record_id, math.nan)
        if not spo2_indices:
            row: dict[str, Any] = {
                "record_id": record_id,
                "spo2_channel_name": "",
                "sampling_rate_hz": fs,
                "finite_fraction_pct": math.nan,
                "plausible_fraction_pct": math.nan,
                "mean_spo2_pct": math.nan,
                "median_spo2_pct": math.nan,
                "min_spo2_pct": math.nan,
                "p05_spo2_pct": math.nan,
                "baseline_spo2_pct": math.nan,
                "sleep_plausible_fraction_pct": math.nan,
                "sleep_baseline_spo2_pct": math.nan,
                "desaturation_scoring_rule": "pre_event_rolling_baseline",
                "desaturation_baseline_window_seconds": float(baseline_window_seconds),
                "desaturation_min_duration_seconds": float(min_desaturation_seconds),
                "sleep_hours": sleep_hours,
                "oxygen_status": "no_spo2_channel",
            }
            for threshold in low_spo2_thresholds_pct:
                key = int(threshold)
                row[f"time_below_{key}pct_pct_recording"] = math.nan
                row[f"time_below_{key}pct_pct_sleep"] = math.nan
            for drop in drop_thresholds_pct:
                key = int(drop)
                row[f"recording_desaturation_{key}pct_event_count_proxy"] = math.nan
                row[f"recording_desaturation_{key}pct_minutes_proxy"] = math.nan
                row[f"sleep_desaturation_{key}pct_event_count_proxy"] = math.nan
                row[f"sleep_desaturation_{key}pct_events_per_sleep_hour_proxy"] = math.nan
                row[f"sleep_desaturation_{key}pct_minutes_proxy"] = math.nan
                row[f"recording_desaturation_{key}pct_event_count"] = math.nan
                row[f"recording_desaturation_{key}pct_minutes"] = math.nan
                row[f"sleep_desaturation_{key}pct_event_count"] = math.nan
                row[f"sleep_odi_{key}pct_events_per_hour"] = math.nan
                row[f"sleep_desaturation_{key}pct_minutes"] = math.nan
                row[f"desaturation_{key}pct_event_count_proxy"] = math.nan
                row[f"desaturation_{key}pct_events_per_sleep_hour_proxy"] = math.nan
                row[f"desaturation_{key}pct_minutes_proxy"] = math.nan
            rows.append(row)
            continue

        channel_index = int(spo2_indices[0])
        record = wfdb.rdrecord(base, channels=[channel_index], physical=True)
        signal = _scaled_plausible_spo2(np.asarray(record.p_signal[:, 0], dtype=np.float64))
        finite = np.isfinite(signal)
        plausible = finite & (signal >= 40.0) & (signal <= 100.0)
        plausible_signal = signal[plausible]
        record_epochs = epochs_by_record.get(record_id, pd.DataFrame())
        sleep_mask = _sleep_sample_mask(record_epochs, sample_count=signal.size, fs=fs)
        sleep_plausible = plausible & sleep_mask
        sleep_plausible_signal = signal[sleep_plausible]
        pre_event_baseline = _pre_event_rolling_baseline(
            signal,
            plausible,
            fs=fs,
            baseline_window_seconds=baseline_window_seconds,
        )
        finite_fraction = float(finite.sum()) / float(signal.size) if signal.size else 0.0
        plausible_fraction = (
            float(plausible.sum()) / float(signal.size) if signal.size else 0.0
        )
        sleep_sample_count = int(sleep_mask.sum())
        sleep_plausible_fraction = (
            float(sleep_plausible.sum()) / float(sleep_sample_count)
            if sleep_sample_count > 0
            else math.nan
        )
        row = {
            "record_id": record_id,
            "spo2_channel_name": str(header.sig_name[channel_index]),
            "sampling_rate_hz": fs,
            "finite_fraction_pct": finite_fraction * 100.0,
            "plausible_fraction_pct": plausible_fraction * 100.0,
            "mean_spo2_pct": (
                float(np.mean(plausible_signal, dtype=np.float64))
                if plausible_signal.size
                else math.nan
            ),
            "median_spo2_pct": (
                float(np.median(plausible_signal)) if plausible_signal.size else math.nan
            ),
            "min_spo2_pct": (
                float(np.min(plausible_signal)) if plausible_signal.size else math.nan
            ),
            "p05_spo2_pct": (
                float(np.percentile(plausible_signal, 5)) if plausible_signal.size else math.nan
            ),
            "baseline_spo2_pct": (
                float(np.percentile(plausible_signal, 95)) if plausible_signal.size else math.nan
            ),
            "sleep_plausible_fraction_pct": (
                sleep_plausible_fraction * 100.0
                if math.isfinite(float(sleep_plausible_fraction))
                else math.nan
            ),
            "sleep_baseline_spo2_pct": (
                float(np.percentile(sleep_plausible_signal, 95))
                if sleep_plausible_signal.size
                else math.nan
            ),
            "desaturation_scoring_rule": "pre_event_rolling_baseline",
            "desaturation_baseline_window_seconds": float(baseline_window_seconds),
            "desaturation_min_duration_seconds": float(min_desaturation_seconds),
            "sleep_hours": sleep_hours,
            "oxygen_status": (
                "available"
                if sleep_plausible_signal.size
                else ("available_recording_only" if plausible_signal.size else "no_plausible_spo2")
            ),
        }
        for threshold in low_spo2_thresholds_pct:
            key = int(threshold)
            if plausible_signal.size:
                row[f"time_below_{key}pct_pct_recording"] = (
                    float((plausible_signal < float(threshold)).sum())
                    / float(plausible_signal.size)
                    * 100.0
                )
            else:
                row[f"time_below_{key}pct_pct_recording"] = math.nan
            if sleep_plausible_signal.size:
                row[f"time_below_{key}pct_pct_sleep"] = (
                    float((sleep_plausible_signal < float(threshold)).sum())
                    / float(sleep_plausible_signal.size)
                    * 100.0
                )
            else:
                row[f"time_below_{key}pct_pct_sleep"] = math.nan
        recording_baseline = float(row["baseline_spo2_pct"])
        sleep_baseline = float(row["sleep_baseline_spo2_pct"])
        for drop in drop_thresholds_pct:
            key = int(drop)
            if math.isfinite(recording_baseline) and plausible.any():
                recording_threshold = recording_baseline - float(drop)
                recording_count, recording_seconds = _count_threshold_segments(
                    plausible & (signal <= recording_threshold),
                    fs=fs,
                    min_duration_seconds=min_desaturation_seconds,
                )
                row[f"recording_desaturation_{key}pct_event_count_proxy"] = int(recording_count)
                row[f"recording_desaturation_{key}pct_minutes_proxy"] = recording_seconds / 60.0
            else:
                row[f"recording_desaturation_{key}pct_event_count_proxy"] = math.nan
                row[f"recording_desaturation_{key}pct_minutes_proxy"] = math.nan
            if math.isfinite(sleep_baseline) and sleep_plausible.any():
                sleep_threshold = sleep_baseline - float(drop)
                sleep_count, sleep_seconds = _count_threshold_segments(
                    sleep_plausible & (signal <= sleep_threshold),
                    fs=fs,
                    min_duration_seconds=min_desaturation_seconds,
                )
                row[f"sleep_desaturation_{key}pct_event_count_proxy"] = int(sleep_count)
                row[f"sleep_desaturation_{key}pct_events_per_sleep_hour_proxy"] = (
                    _safe_per_sleep_hour(sleep_count, sleep_hours)
                )
                row[f"sleep_desaturation_{key}pct_minutes_proxy"] = sleep_seconds / 60.0
                row[f"desaturation_{key}pct_event_count_proxy"] = int(sleep_count)
                row[f"desaturation_{key}pct_events_per_sleep_hour_proxy"] = (
                    _safe_per_sleep_hour(sleep_count, sleep_hours)
                )
                row[f"desaturation_{key}pct_minutes_proxy"] = sleep_seconds / 60.0
            else:
                row[f"sleep_desaturation_{key}pct_event_count_proxy"] = math.nan
                row[f"sleep_desaturation_{key}pct_events_per_sleep_hour_proxy"] = math.nan
                row[f"sleep_desaturation_{key}pct_minutes_proxy"] = math.nan
                row[f"desaturation_{key}pct_event_count_proxy"] = math.nan
                row[f"desaturation_{key}pct_events_per_sleep_hour_proxy"] = math.nan
                row[f"desaturation_{key}pct_minutes_proxy"] = math.nan
            if plausible.any():
                scored_recording_count, scored_recording_seconds = _count_desaturation_events(
                    signal,
                    baseline=pre_event_baseline,
                    plausible=plausible,
                    scope=np.ones(signal.shape, dtype=bool),
                    fs=fs,
                    drop_pct=float(drop),
                    min_duration_seconds=min_desaturation_seconds,
                )
                row[f"recording_desaturation_{key}pct_event_count"] = int(
                    scored_recording_count
                )
                row[f"recording_desaturation_{key}pct_minutes"] = (
                    scored_recording_seconds / 60.0
                )
            else:
                row[f"recording_desaturation_{key}pct_event_count"] = math.nan
                row[f"recording_desaturation_{key}pct_minutes"] = math.nan
            if sleep_plausible.any():
                scored_sleep_count, scored_sleep_seconds = _count_desaturation_events(
                    signal,
                    baseline=pre_event_baseline,
                    plausible=plausible,
                    scope=sleep_mask,
                    fs=fs,
                    drop_pct=float(drop),
                    min_duration_seconds=min_desaturation_seconds,
                )
                row[f"sleep_desaturation_{key}pct_event_count"] = int(scored_sleep_count)
                row[f"sleep_odi_{key}pct_events_per_hour"] = _safe_per_sleep_hour(
                    scored_sleep_count,
                    sleep_hours,
                )
                row[f"sleep_desaturation_{key}pct_minutes"] = scored_sleep_seconds / 60.0
            else:
                row[f"sleep_desaturation_{key}pct_event_count"] = math.nan
                row[f"sleep_odi_{key}pct_events_per_hour"] = math.nan
                row[f"sleep_desaturation_{key}pct_minutes"] = math.nan
        rows.append(row)
    return pd.DataFrame(rows)


def oxygen_artifact_review(oxygen: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if oxygen.empty:
        return pd.DataFrame(rows)
    for _, row in oxygen.iterrows():
        record_id = str(row["record_id"])
        oxygen_status = str(row.get("oxygen_status", ""))
        if oxygen_status != "available":
            rows.append(
                {
                    "record_id": record_id,
                    "oxygen_review_status": "not_available",
                    "review_priority": "none",
                    "review_flags": "",
                    "sleep_plausible_fraction_pct": math.nan,
                    "min_spo2_pct": math.nan,
                    "sleep_time_below_90pct_pct": math.nan,
                    "sleep_odi_3pct_events_per_hour": math.nan,
                    "sleep_odi_4pct_events_per_hour": math.nan,
                    "sleep_odi_3pct_minus_legacy_proxy": math.nan,
                    "review_focus": "No sleep-aligned plausible SO2 signal was available.",
                }
            )
            continue
        sleep_plausible_fraction = _finite_or_nan(
            row.get("sleep_plausible_fraction_pct", math.nan)
        )
        min_spo2 = _finite_or_nan(row.get("min_spo2_pct", math.nan))
        below90 = _finite_or_nan(row.get("time_below_90pct_pct_sleep", math.nan))
        odi3 = _finite_or_nan(row.get("sleep_odi_3pct_events_per_hour", math.nan))
        odi4 = _finite_or_nan(row.get("sleep_odi_4pct_events_per_hour", math.nan))
        proxy_odi3 = _finite_or_nan(
            row.get("sleep_desaturation_3pct_events_per_sleep_hour_proxy", math.nan)
        )
        odi3_minus_proxy = (
            odi3 - proxy_odi3
            if math.isfinite(odi3) and math.isfinite(proxy_odi3)
            else math.nan
        )
        flags: list[str] = []
        if math.isfinite(sleep_plausible_fraction) and sleep_plausible_fraction < 95.0:
            flags.append("low_sleep_plausible_fraction")
        if math.isfinite(min_spo2) and min_spo2 < 50.0:
            flags.append("very_low_spo2_value")
        if math.isfinite(odi3_minus_proxy) and abs(odi3_minus_proxy) > 15.0:
            flags.append("odi_proxy_disagreement")
        if math.isfinite(odi3) and math.isfinite(odi4) and odi3 > 0 and (odi4 / odi3) < 0.35:
            flags.append("many_shallow_desaturations")
        if math.isfinite(below90) and below90 > 30.0:
            flags.append("high_sleep_time_below_90")
        review_status = "artifact_review_recommended" if flags else "oxygen_review_ready"
        review_priority = "high" if len(flags) >= 2 else ("medium" if flags else "low")
        rows.append(
            {
                "record_id": record_id,
                "oxygen_review_status": review_status,
                "review_priority": review_priority,
                "review_flags": ";".join(flags),
                "sleep_plausible_fraction_pct": sleep_plausible_fraction,
                "min_spo2_pct": min_spo2,
                "sleep_time_below_90pct_pct": below90,
                "sleep_odi_3pct_events_per_hour": odi3,
                "sleep_odi_4pct_events_per_hour": odi4,
                "sleep_odi_3pct_minus_legacy_proxy": odi3_minus_proxy,
                "review_focus": (
                    "Inspect SO2 waveform windows and raw channel for dropout, motion artifact, "
                    "baseline drift, and whether desaturations align with respiratory events."
                    if flags
                    else "ODI output has no automatic artifact flags; spot-check event windows."
                ),
            }
        )
    return pd.DataFrame(rows)


def event_window_summaries(
    *,
    records: list[str],
    raw_dir: str | Path,
    epochs: pd.DataFrame,
    pre_seconds: float,
    post_seconds: float,
    max_events_per_record: int,
) -> pd.DataFrame:
    if pre_seconds < 0 or post_seconds <= 0:
        raise ValueError("event window seconds must be non-negative pre and positive post")
    if max_events_per_record <= 0:
        raise ValueError("max_events_per_record must be positive")
    try:
        import wfdb
    except ImportError as exc:
        raise RuntimeError("wfdb is required for MIT-BIH PSG WFDB files") from exc

    rows: list[dict[str, Any]] = []
    for record_id in records:
        base = _base_path(raw_dir, record_id).as_posix()
        header = wfdb.rdheader(base)
        fs = float(header.fs)
        if fs <= 0:
            raise ValueError(f"Invalid sampling rate for {record_id}: {header.fs}")
        selected_channels = [
            index
            for index, name in enumerate(header.sig_name)
            if _is_respiration_channel(str(name)) or _is_spo2_channel(str(name))
        ]
        if not selected_channels:
            continue
        record_events = epochs[
            (epochs["record_id"] == record_id)
            & (epochs["included_sleep"])
            & (epochs["respiratory_event_count"] > 0)
        ].head(max_events_per_record)
        for event_rank, (_, event) in enumerate(record_events.iterrows(), start=1):
            onset_seconds = float(event["onset_seconds"])
            start_sample = max(0, int(math.floor((onset_seconds - pre_seconds) * fs)))
            stop_sample = min(
                int(header.sig_len),
                int(math.ceil((onset_seconds + post_seconds) * fs)),
            )
            if stop_sample <= start_sample:
                continue
            record = wfdb.rdrecord(
                base,
                sampfrom=start_sample,
                sampto=stop_sample,
                channels=selected_channels,
                physical=True,
            )
            signals = np.asarray(record.p_signal, dtype=np.float64)
            for index, channel_name in enumerate(record.sig_name):
                signal = signals[:, index]
                if _is_spo2_channel(str(channel_name)):
                    signal = _scaled_plausible_spo2(signal)
                    finite = np.isfinite(signal) & (signal >= 40.0) & (signal <= 100.0)
                else:
                    finite = np.isfinite(signal)
                finite_signal = signal[finite]
                rows.append(
                    {
                        "record_id": record_id,
                        "event_rank": int(event_rank),
                        "epoch_index": int(event["epoch_index"]),
                        "onset_seconds": onset_seconds,
                        "event_tokens": str(event["event_tokens"]),
                        "mapped_stage": str(event["mapped_stage"]),
                        "window_start_seconds": float(start_sample) / fs,
                        "window_stop_seconds": float(stop_sample) / fs,
                        "channel_name": str(channel_name),
                        "is_respiration_channel": _is_respiration_channel(str(channel_name)),
                        "is_spo2_channel": _is_spo2_channel(str(channel_name)),
                        "finite_fraction_pct": (
                            float(finite.sum()) / float(signal.size) * 100.0
                            if signal.size
                            else 0.0
                        ),
                        "min_value": (
                            float(np.min(finite_signal)) if finite_signal.size else math.nan
                        ),
                        "mean_value": (
                            float(np.mean(finite_signal, dtype=np.float64))
                            if finite_signal.size
                            else math.nan
                        ),
                        "max_value": (
                            float(np.max(finite_signal)) if finite_signal.size else math.nan
                        ),
                        "std_value": (
                            float(np.std(finite_signal, dtype=np.float64))
                            if finite_signal.size
                            else math.nan
                        ),
                    }
                )
    return pd.DataFrame(rows)


def plot_event_windows(
    *,
    records: list[str],
    raw_dir: str | Path,
    epochs: pd.DataFrame,
    output_dir: Path,
    pre_seconds: float,
    post_seconds: float,
    plot_events_per_record: int,
) -> list[Path]:
    if plot_events_per_record <= 0:
        return []
    try:
        import wfdb
    except ImportError as exc:
        raise RuntimeError("wfdb is required for MIT-BIH PSG WFDB files") from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for record_id in records:
        base = _base_path(raw_dir, record_id).as_posix()
        header = wfdb.rdheader(base)
        fs = float(header.fs)
        if fs <= 0:
            raise ValueError(f"Invalid sampling rate for {record_id}: {header.fs}")
        selected_channels = [
            index
            for index, name in enumerate(header.sig_name)
            if _is_respiration_channel(str(name)) or _is_spo2_channel(str(name))
        ]
        if not selected_channels:
            continue
        record_events = epochs[
            (epochs["record_id"] == record_id)
            & (epochs["included_sleep"])
            & (epochs["respiratory_event_count"] > 0)
        ].head(plot_events_per_record)
        for _, event in record_events.iterrows():
            onset_seconds = float(event["onset_seconds"])
            start_sample = max(0, int(math.floor((onset_seconds - pre_seconds) * fs)))
            stop_sample = min(
                int(header.sig_len),
                int(math.ceil((onset_seconds + post_seconds) * fs)),
            )
            if stop_sample <= start_sample:
                continue
            record = wfdb.rdrecord(
                base,
                sampfrom=start_sample,
                sampto=stop_sample,
                channels=selected_channels,
                physical=True,
            )
            signals = np.asarray(record.p_signal, dtype=np.float64)
            x_seconds = np.arange(signals.shape[0], dtype=np.float64) / fs
            x_seconds = x_seconds + float(start_sample) / fs
            fig, axes = plt.subplots(
                len(record.sig_name),
                1,
                figsize=(10, max(2.4, 2.0 * len(record.sig_name))),
                sharex=True,
            )
            if len(record.sig_name) == 1:
                axes = [axes]
            for axis, channel_index in zip(axes, range(len(record.sig_name))):
                channel_name = str(record.sig_name[channel_index])
                signal = signals[:, channel_index]
                if _is_spo2_channel(channel_name):
                    signal = _scaled_plausible_spo2(signal)
                axis.plot(x_seconds, signal, linewidth=0.8, color="#2f5d7c")
                axis.axvspan(
                    onset_seconds,
                    onset_seconds + float(event["epoch_seconds"]),
                    color="#d95f02",
                    alpha=0.18,
                )
                axis.set_ylabel(channel_name)
                axis.grid(alpha=0.25)
            axes[-1].set_xlabel("recording time (s)")
            fig.suptitle(
                f"{record_id} epoch {int(event['epoch_index'])} {event['event_tokens']}",
                fontsize=10,
            )
            fig.tight_layout()
            out = output_dir / f"{record_id}_epoch_{int(event['epoch_index']):04d}.png"
            fig.savefig(out, dpi=150)
            plt.close(fig)
            paths.append(out)
    return paths


def clinical_indicators(
    metrics: pd.DataFrame,
    quality: pd.DataFrame,
    oxygen: pd.DataFrame | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    quality_by_record = {
        str(record_id): group.copy() for record_id, group in quality.groupby("record_id", sort=True)
    }
    oxygen_by_record = {}
    if oxygen is not None and not oxygen.empty:
        oxygen_by_record = {
            str(row["record_id"]): row for _, row in oxygen.iterrows()
        }
    for _, metric in metrics.iterrows():
        record_id = str(metric["record_id"])
        burden = float(metric["ahi_style_events_per_sleep_hour"])
        severity = str(metric["ahi_style_learning_severity"])
        record_quality = quality_by_record.get(record_id, pd.DataFrame())
        has_respiration = bool(
            (record_quality.get("is_respiration_channel", pd.Series(dtype=bool)))
            .astype(bool)
            .any()
        )
        has_dynamic_respiration = bool(
            (
                record_quality.get("is_respiration_channel", pd.Series(dtype=bool)).astype(bool)
                & record_quality.get("has_dynamic_signal", pd.Series(dtype=bool)).astype(bool)
            ).any()
        )
        has_spo2 = bool(
            (record_quality.get("is_spo2_channel", pd.Series(dtype=bool))).astype(bool).any()
        )
        oxygen_row = oxygen_by_record.get(record_id)
        oxygen_status = str(oxygen_row["oxygen_status"]) if oxygen_row is not None else ""
        desat3 = (
            float(
                oxygen_row.get(
                    "sleep_odi_3pct_events_per_hour",
                    oxygen_row.get(
                        "sleep_desaturation_3pct_events_per_sleep_hour_proxy",
                        oxygen_row.get(
                            "desaturation_3pct_events_per_sleep_hour_proxy",
                            math.nan,
                        ),
                    ),
                )
            )
            if oxygen_row is not None
            else math.nan
        )
        desat4 = (
            float(
                oxygen_row.get(
                    "sleep_odi_4pct_events_per_hour",
                    oxygen_row.get(
                        "sleep_desaturation_4pct_events_per_sleep_hour_proxy",
                        oxygen_row.get(
                            "desaturation_4pct_events_per_sleep_hour_proxy",
                            math.nan,
                        ),
                    ),
                )
            )
            if oxygen_row is not None
            else math.nan
        )
        below90 = (
            float(
                oxygen_row.get(
                    "time_below_90pct_pct_sleep",
                    oxygen_row.get("time_below_90pct_pct_recording", math.nan),
                )
            )
            if oxygen_row is not None
            else math.nan
        )
        if severity in {"moderate_range", "severe_range"}:
            status = "screen_positive_learning_signal"
        elif severity == "mild_range":
            status = "mild_learning_signal"
        elif severity == "minimal_range":
            status = "below_osa_learning_threshold"
        else:
            status = "cannot_compute"
        rows.append(
            {
                "record_id": record_id,
                "domain": "sleep_disordered_breathing",
                "indicator": "apnea_hypopnea_annotation_burden",
                "status": status,
                "evidence": (
                    f"Annotation burden {burden:.1f} respiratory events per sleep hour "
                    f"({severity.replace('_', ' ')})."
                ),
                "clinical_learning": (
                    "This is an AHI-style learning calculation from MIT-BIH .st labels, "
                    "not a standalone diagnosis."
                ),
                "next_data_needed": (
                    "Clinical symptoms, scoring rules, waveform review, oxygen desaturation, "
                    "arousals, comorbidities, and clinician interpretation."
                ),
            }
        )
        source_delta = float(metric["ahi_style_minus_source_reported_ahi"])
        source_note = str(metric.get("source_ahi_note", ""))
        rows.append(
            {
                "record_id": record_id,
                "domain": "source_consistency",
                "indicator": "annotation_burden_vs_source_ahi",
                "status": str(metric["source_ahi_alignment_status"]),
                "evidence": (
                    f"Annotation burden minus source AHI is {_fmt(source_delta)} events/h."
                    + (f" Source note: {source_note}." if source_note else "")
                ),
                "clinical_learning": (
                    "Simple token counts are an educational proxy and may differ from the "
                    "source AHI table because of scoring rules, wake exclusion, and event definitions."
                ),
                "next_data_needed": "Manual review of source annotations and scoring assumptions.",
            }
        )
        rows.append(
            {
                "record_id": record_id,
                "domain": "signal_quality",
                "indicator": "respiration_channel_available",
                "status": "available" if has_respiration and has_dynamic_respiration else "review_needed",
                "evidence": (
                    "Respiration channel is present with dynamic sampled signal."
                    if has_respiration and has_dynamic_respiration
                    else "Respiration channel was absent or not dynamic in the sampled segment."
                ),
                "clinical_learning": (
                    "Respiratory annotations are stronger when the airflow/effort waveform is present "
                    "and quality-checked."
                ),
                "next_data_needed": "Longer signal-quality review and event-by-event waveform inspection.",
            }
        )
        rows.append(
            {
                "record_id": record_id,
                "domain": "oxygenation",
                "indicator": "spo2_desaturation_burden",
                "status": (
                    "oxygen_desaturation_available"
                    if oxygen_status == "available"
                    else ("available_for_later_analysis" if has_spo2 else "not_available_in_record")
                ),
                "evidence": (
                    f"ODI 3% {_fmt(desat3)} events per sleep hour; "
                    f"ODI 4% {_fmt(desat4)} events per sleep hour; "
                    f"time below 90% SpO2 {_fmt(below90)}% of plausible sleep samples."
                    if oxygen_status == "available"
                    else (
                        "SpO2-like channel detected, but oxygen proxy metrics were not computed."
                        if has_spo2
                        else "No SpO2/oximetry channel detected in this record."
                    )
                ),
                "clinical_learning": (
                    "Oxygen desaturation burden can change OSA severity and treatment reasoning, "
                    "but it is not a standalone diagnosis and does not score airflow or arousals."
                ),
                "next_data_needed": (
                    "Validate desaturation scoring against airflow, arousals, and artifact review."
                    if oxygen_status == "available"
                    else "Choose MIT-BIH records with SO2 channels or another PSG dataset with oximetry."
                ),
            }
        )
        rows.append(
            {
                "record_id": record_id,
                "domain": "treatment_reasoning",
                "indicator": "osa_treatment_path",
                "status": "educational_question_only",
                "evidence": (
                    "Respiratory-event burden can motivate PAP/oral-appliance/referral questions, "
                    "but treatment selection is not made from this pilot output."
                ),
                "clinical_learning": (
                    "Confirmed OSA severity, symptoms, anatomy, preferences, contraindications, "
                    "and clinician review guide treatment."
                ),
                "next_data_needed": "Full PSG report, symptoms, exam, cardiometabolic risk, and specialist review.",
            }
        )
    return pd.DataFrame(rows)


def _fmt(value: Any, digits: int = 1) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(numeric):
        return "NA"
    return f"{numeric:.{digits}f}"


def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = [
        "| " + " | ".join(str(row.get(column, "")) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, sep, *body])


def build_report(
    *,
    records: list[str],
    metrics: pd.DataFrame,
    source_alignment: pd.DataFrame,
    quality: pd.DataFrame,
    oxygen: pd.DataFrame,
    oxygen_review: pd.DataFrame,
    event_windows: pd.DataFrame,
    event_plot_paths: list[Path],
    indicators: pd.DataFrame,
) -> str:
    metric_rows = []
    for _, row in metrics.iterrows():
        metric_rows.append(
            {
                "record": row["record_id"],
                "sleep h": _fmt(row["sleep_hours"], 2),
                "events": int(row["sleep_respiratory_event_count"]),
                "burden/h": _fmt(row["ahi_style_events_per_sleep_hour"]),
                "range": str(row["ahi_style_learning_severity"]).replace("_", " "),
                "source AHI": _fmt(row["source_reported_ahi"]),
                "source note": str(row.get("source_ahi_note", "")),
                "delta": _fmt(row["ahi_style_minus_source_reported_ahi"]),
                "obstructive/h": _fmt(row["obstructive_apnea_events_per_sleep_hour"]),
                "central/h": _fmt(row["central_apnea_events_per_sleep_hour"]),
                "hypopnea/h": _fmt(row["hypopnea_events_per_sleep_hour"]),
            }
        )

    source_alignment_rows = []
    if not source_alignment.empty:
        for _, row in source_alignment.iterrows():
            source_alignment_rows.append(
                {
                    "record": row["record_id"],
                    "annotation/h": _fmt(row["annotation_ahi_style_events_per_sleep_hour"]),
                    "source AHI": _fmt(row["source_reported_ahi"]),
                    "delta": _fmt(row["delta_events_per_sleep_hour"]),
                    "status": row["alignment_status"],
                    "priority": row["review_priority"],
                    "dominant event": row["dominant_respiratory_event_type"],
                    "review focus": row["review_focus"],
                }
            )

    channel_rows = []
    for _, row in quality.iterrows():
        if bool(row["is_respiration_channel"]) or bool(row["is_spo2_channel"]):
            channel_rows.append(
                {
                    "record": row["record_id"],
                    "channel": row["channel_name"],
                    "unit": row["unit"],
                    "finite %": _fmt(row["finite_fraction_pct"], 2),
                    "std": _fmt(row["standard_deviation"], 4),
                    "dynamic": bool(row["has_dynamic_signal"]),
                }
            )

    has_any_spo2 = bool(quality["is_spo2_channel"].astype(bool).any()) if not quality.empty else False
    records_with_spo2 = sorted(
        {
            str(row["record_id"])
            for _, row in quality.iterrows()
            if bool(row["is_spo2_channel"])
        }
    )
    channel_note = (
        "The selected records include SO2/oximetry channels, so oxygen saturation "
        "ODI metrics are computed below."
        if has_any_spo2
        else (
            "The selected records include respiration channels, but no SpO2/oximetry "
            "channels. Oxygen desaturation burden cannot be interpreted from this subset."
        )
    )
    if has_any_spo2 and len(records_with_spo2) != len(records):
        channel_note = (
            "Some selected records include SO2/oximetry channels "
            f"({', '.join(records_with_spo2)}); records without SO2 keep oxygen metrics unavailable."
        )

    oxygen_rows = []
    for _, row in oxygen.iterrows():
        oxygen_rows.append(
            {
                "record": row["record_id"],
                "SO2 channel": row["spo2_channel_name"],
                "status": row["oxygen_status"],
                "median %": _fmt(row["median_spo2_pct"]),
                "min %": _fmt(row["min_spo2_pct"]),
                "below 90 %": _fmt(row.get("time_below_90pct_pct_recording", math.nan)),
                "below 90 % sleep": _fmt(row.get("time_below_90pct_pct_sleep", math.nan)),
                "ODI 3%": _fmt(row.get("sleep_odi_3pct_events_per_hour", math.nan)),
                "ODI 4%": _fmt(row.get("sleep_odi_4pct_events_per_hour", math.nan)),
                "rule": row.get("desaturation_scoring_rule", ""),
            }
        )

    oxygen_review_rows = []
    if not oxygen_review.empty:
        for _, row in oxygen_review.iterrows():
            oxygen_review_rows.append(
                {
                    "record": row["record_id"],
                    "status": row["oxygen_review_status"],
                    "priority": row["review_priority"],
                    "flags": row.get("review_flags", ""),
                    "ODI3-proxy": _fmt(row.get("sleep_odi_3pct_minus_legacy_proxy", math.nan)),
                    "focus": row["review_focus"],
                }
            )

    event_rows = []
    if not event_windows.empty:
        for _, row in event_windows[event_windows["is_respiration_channel"]].iterrows():
            event_rows.append(
                {
                    "record": row["record_id"],
                    "epoch": int(row["epoch_index"]),
                    "tokens": row["event_tokens"],
                    "stage": row["mapped_stage"],
                    "window s": f"{_fmt(row['window_start_seconds'])}-{_fmt(row['window_stop_seconds'])}",
                    "resp mean": _fmt(row["mean_value"], 3),
                    "resp std": _fmt(row["std_value"], 3),
                }
            )

    indicator_rows = []
    for _, row in indicators.iterrows():
        indicator_rows.append(
            {
                "record": row["record_id"],
                "domain": row["domain"],
                "indicator": row["indicator"],
                "status": row["status"],
                "evidence": row["evidence"],
            }
        )

    lines = [
        "# MIT-BIH PSG Respiratory Pilot",
        "",
        "## Purpose",
        "",
        (
            "This report starts the respiratory and OSA-style evidence phase. It turns "
            "MIT-BIH `.st` sleep/apnea annotations into an annotation burden per sleep "
            "hour, checks whether respiration or SpO2 channels are present, and maps "
            "the results to clinical learning questions."
        ),
        "",
        "It is an educational analysis, not a diagnosis, prescription, or triage tool.",
        "",
        "## Records",
        "",
        f"- Records: {', '.join(records)}.",
        "- Epoch size: 30 s; each `.st` annotation is interpreted as applying to the following epoch.",
        (
            "- Record IDs are PhysioNet WFDB record IDs; segmented records such as "
            "`slp01a` and `slp02a` keep their suffixes."
        ),
        "",
        "## Respiratory Event Burden",
        "",
        _markdown_table(
            metric_rows,
            [
                "record",
                "sleep h",
                "events",
                "burden/h",
                "range",
                "source AHI",
                "source note",
                "delta",
                "obstructive/h",
                "central/h",
                "hypopnea/h",
            ],
        ),
        "",
        "## Source AHI Alignment Review",
        "",
        (
            "This table compares the simple annotation-token burden against the source "
            "reported AHI table. It is an audit view for educational alignment, not a "
            "replacement for scorer rules or clinical adjudication."
        ),
        "",
        _markdown_table(
            source_alignment_rows[:20],
            [
                "record",
                "annotation/h",
                "source AHI",
                "delta",
                "status",
                "priority",
                "dominant event",
                "review focus",
            ],
        )
        if source_alignment_rows
        else "No source AHI alignment rows were generated.",
        "",
        "## Channel Quality",
        "",
        channel_note,
        "",
        _markdown_table(
            channel_rows,
            ["record", "channel", "unit", "finite %", "std", "dynamic"],
        ),
        "",
        "## Oxygen Saturation",
        "",
        (
            "SO2 metrics are computed only when an oximetry channel is present. "
            "The report table uses sleep-only ODI values from a documented "
            "pre-event rolling-baseline desaturation rule; recording-wide and legacy "
            "percentile-proxy oxygen summaries remain in the CSV for audit. "
            "This is oxygen-only evidence, not full hypopnea scoring because airflow "
            "reduction and arousal rules are not adjudicated here."
        ),
        "",
        _markdown_table(
            oxygen_rows,
            [
                "record",
                "SO2 channel",
                "status",
                "median %",
                "min %",
                "below 90 %",
                "below 90 % sleep",
                "ODI 3%",
                "ODI 4%",
                "rule",
            ],
        ),
        "",
        "## Oxygen Artifact Review",
        "",
        (
            "This table flags records where the ODI scorer should be reviewed against "
            "the generated waveform windows or raw SO2 channel before using the oxygen "
            "signal as clinical-learning evidence."
        ),
        "",
        _markdown_table(
            oxygen_review_rows,
            ["record", "status", "priority", "flags", "ODI3-proxy", "focus"],
        )
        if oxygen_review_rows
        else "No oxygen artifact review rows were generated.",
        "",
        "## Event-Level Waveform Review",
        "",
        (
            "The event window table summarizes respiration channel windows around the "
            "first scored respiratory-event epochs per record. Generated figures overlay "
            "the scored 30 s event epoch on respiration and SO2 channels when available."
        ),
        "",
        _markdown_table(
            event_rows[:20],
            ["record", "epoch", "tokens", "stage", "window s", "resp mean", "resp std"],
        )
        if event_rows
        else "No event windows were generated.",
        "",
        "Generated event plots:",
        "",
        "\n".join(f"- `{path.as_posix()}`" for path in event_plot_paths[:20])
        if event_plot_paths
        else "- No event plots generated.",
        "",
        "## Clinical Learning Indicators",
        "",
        _markdown_table(
            indicator_rows,
            ["record", "domain", "indicator", "status", "evidence"],
        ),
        "",
        "## How To Read This",
        "",
        (
            "- The core disease-style output is `ahi_style_events_per_sleep_hour`: "
            "respiratory event annotations divided by sleep hours."
        ),
        (
            "- Adult AHI learning bands used here are: <5 minimal, 5-14 mild, 15-29 "
            "moderate, and >=30 severe events per sleep hour."
        ),
        (
            "- A real clinical conclusion still needs scoring-rule context, symptoms, "
            "waveform review, oxygen desaturation, arousals, comorbidities, and clinician review."
        ),
        (
            "- SO2-derived desaturation metrics add oxygenation evidence, but artifact "
            "review, airflow reduction, arousal scoring, and clinician interpretation "
            "are still required before diagnostic use."
        ),
        (
            "- Treatment reasoning should be framed as questions: whether OSA evidence "
            "supports PAP evaluation, oral-appliance discussion, weight/lifestyle work, "
            "positional therapy, surgery referral, or another diagnosis."
        ),
        "",
        "## Next Data Step",
        "",
        (
            "Next, manually adjudicate the high-priority source AHI alignment rows, "
            "review the pre-event-baseline ODI scorer against artifacts and event "
            "windows, and then decide whether a richer PSG dataset is needed for "
            "clinical-style examples."
        ),
        "",
        "## Source Notes",
        "",
        (
            "- PhysioNet MIT-BIH PSG: https://physionet.org/content/slpdb/ "
            "and signal/annotation notes at "
            "https://archive.physionet.org/physiobank/database/slpdb/slpdb.shtml"
        ),
        (
            "- AHI bands cross-check: Cleveland Clinic AHI ranges, "
            "https://my.clevelandclinic.org/health/articles/apnea-hypopnea-index-ahi"
        ),
        (
            "- Hypopnea scoring context: AASM-recommended adult hypopnea criteria "
            "use airflow reduction plus 3% oxygen desaturation or arousal, while "
            "CMS-style scoring uses 4% oxygen desaturation; this report computes "
            "oxygen-only ODI signals, not full hypopnea events. "
            "https://doi.org/10.5664/jcsm.9952"
        ),
        "",
    ]
    return "\n".join(lines)


def run_mit_bih_psg_respiratory_pilot(
    config: dict[str, Any],
    *,
    records: list[str] | None = None,
    output_prefix: str | None = None,
) -> MitBihPsgPilotOutputs:
    selected_records = mit_bih_psg_records(config, records)
    outputs = config["outputs"]
    validation = validate_mit_bih_psg_manifest(outputs["manifest_csv"], records=selected_records)
    if not bool(validation["checksum_ok"].all()) or not bool(
        validation["required_file_set_complete"].all()
    ):
        raise ValueError("MIT-BIH PSG files are missing or checksum validation failed")

    annotation_config = config["annotations"]
    epoch_seconds = float(annotation_config["epoch_seconds"])
    stage_mapping = {
        str(key): str(value)
        for key, value in annotation_config["sleep_stage_mapping"].items()
    }
    excluded_stage_tokens = {
        str(value) for value in annotation_config.get("excluded_stage_tokens", [])
    }
    raw_dir = config["dataset"]["raw_dir"]
    annotation_parts = [
        read_annotation_epochs(
            record_id=record_id,
            raw_dir=raw_dir,
            epoch_seconds=epoch_seconds,
            stage_mapping=stage_mapping,
            excluded_stage_tokens=excluded_stage_tokens,
        )
        for record_id in selected_records
    ]
    epochs = pd.concat(annotation_parts, ignore_index=True)
    source_reported_ahi = {
        str(key): float(value)
        for key, value in config["selection"].get("source_reported_ahi", {}).items()
    }
    source_ahi_notes = {
        str(key): str(value)
        for key, value in config["selection"].get("source_ahi_notes", {}).items()
    }
    metrics = respiratory_metrics(
        epochs,
        source_reported_ahi=source_reported_ahi,
        source_ahi_notes=source_ahi_notes,
        epoch_seconds=epoch_seconds,
    )
    alignment = source_ahi_alignment(metrics)
    quality = channel_quality(
        records=selected_records,
        raw_dir=raw_dir,
        sample_seconds=float(config["quality"]["sample_seconds"]),
    )
    oxygen_config = config.get("oxygen", {})
    oxygen = oxygen_saturation_metrics(
        records=selected_records,
        raw_dir=raw_dir,
        respiratory=metrics,
        epochs=epochs,
        drop_thresholds_pct=[
            float(value) for value in oxygen_config.get("desaturation_drop_pct", [3, 4])
        ],
        low_spo2_thresholds_pct=[
            float(value) for value in oxygen_config.get("low_spo2_thresholds_pct", [90, 88])
        ],
        min_desaturation_seconds=float(
            oxygen_config.get("min_desaturation_seconds", 10.0)
        ),
        baseline_window_seconds=float(
            oxygen_config.get("desaturation_baseline_window_seconds", 120.0)
        ),
    )
    oxygen_review = oxygen_artifact_review(oxygen)
    event_config = config.get("event_review", {})
    output_paths = _output_paths(outputs, output_prefix)
    event_windows = event_window_summaries(
        records=selected_records,
        raw_dir=raw_dir,
        epochs=epochs,
        pre_seconds=float(event_config.get("pre_seconds", 30.0)),
        post_seconds=float(event_config.get("post_seconds", 60.0)),
        max_events_per_record=int(event_config.get("max_events_per_record", 5)),
    )
    event_plot_paths = plot_event_windows(
        records=selected_records,
        raw_dir=raw_dir,
        epochs=epochs,
        output_dir=output_paths["event_plot_dir"],
        pre_seconds=float(event_config.get("pre_seconds", 30.0)),
        post_seconds=float(event_config.get("post_seconds", 60.0)),
        plot_events_per_record=int(event_config.get("plot_events_per_record", 2)),
    )
    indicators = clinical_indicators(metrics, quality, oxygen)

    epochs_out = output_paths["annotation_epochs_csv"]
    metrics_out = output_paths["respiratory_metrics_csv"]
    alignment_out = output_paths["source_alignment_csv"]
    oxygen_out = output_paths["oxygen_metrics_csv"]
    oxygen_review_out = output_paths["oxygen_artifact_review_csv"]
    event_windows_out = output_paths["event_windows_csv"]
    quality_out = output_paths["channel_quality_csv"]
    indicators_out = output_paths["clinical_indicators_csv"]
    report_out = output_paths["report_md"]
    for out in (
        epochs_out,
        metrics_out,
        alignment_out,
        oxygen_out,
        oxygen_review_out,
        event_windows_out,
        quality_out,
        indicators_out,
        report_out,
    ):
        out.parent.mkdir(parents=True, exist_ok=True)
    epochs.to_csv(epochs_out, index=False)
    metrics.to_csv(metrics_out, index=False)
    alignment.to_csv(alignment_out, index=False)
    oxygen.to_csv(oxygen_out, index=False)
    oxygen_review.to_csv(oxygen_review_out, index=False)
    event_windows.to_csv(event_windows_out, index=False)
    quality.to_csv(quality_out, index=False)
    indicators.to_csv(indicators_out, index=False)
    report_out.write_text(
        build_report(
            records=selected_records,
            metrics=metrics,
            source_alignment=alignment,
            quality=quality,
            oxygen=oxygen,
            oxygen_review=oxygen_review,
            event_windows=event_windows,
            event_plot_paths=event_plot_paths,
            indicators=indicators,
        ),
        encoding="utf-8",
    )
    return MitBihPsgPilotOutputs(
        annotation_epochs_csv=epochs_out,
        respiratory_metrics_csv=metrics_out,
        source_alignment_csv=alignment_out,
        oxygen_metrics_csv=oxygen_out,
        oxygen_artifact_review_csv=oxygen_review_out,
        event_windows_csv=event_windows_out,
        channel_quality_csv=quality_out,
        clinical_indicators_csv=indicators_out,
        report_md=report_out,
    )
