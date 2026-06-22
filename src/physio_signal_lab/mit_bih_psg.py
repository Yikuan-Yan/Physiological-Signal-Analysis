from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import math

import numpy as np
import pandas as pd

from physio_signal_lab.io.mit_bih_psg import (
    mit_bih_psg_records,
    validate_mit_bih_psg_manifest,
)


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


def respiratory_metrics(
    epochs: pd.DataFrame,
    *,
    source_reported_ahi: dict[str, float],
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
            "ahi_style_minus_source_reported_ahi": (
                ahi_style - float(reported) if math.isfinite(float(reported)) else math.nan
            ),
        }
        row["ahi_style_learning_severity"] = _severity_from_ahi_style_burden(ahi_style)
        rows.append(row)
    return pd.DataFrame(rows)


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


def clinical_indicators(metrics: pd.DataFrame, quality: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    quality_by_record = {
        str(record_id): group.copy() for record_id, group in quality.groupby("record_id", sort=True)
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
                "status": "available_for_later_analysis" if has_spo2 else "not_available_in_record",
                "evidence": (
                    "SpO2-like channel detected."
                    if has_spo2
                    else "No SpO2/oximetry channel detected in this pilot record."
                ),
                "clinical_learning": (
                    "Oxygen desaturation burden can change OSA severity and treatment reasoning, "
                    "but it cannot be inferred when oximetry is absent."
                ),
                "next_data_needed": "Choose MIT-BIH records with SO2 channels or another PSG dataset with oximetry.",
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
    quality: pd.DataFrame,
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
                "delta": _fmt(row["ahi_style_minus_source_reported_ahi"]),
                "obstructive/h": _fmt(row["obstructive_apnea_events_per_sleep_hour"]),
                "central/h": _fmt(row["central_apnea_events_per_sleep_hour"]),
                "hypopnea/h": _fmt(row["hypopnea_events_per_sleep_hour"]),
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
            "- Pilot records use actual PhysioNet record IDs `slp01a`, `slp02a`, and "
            "`slp03`; the `a` suffix matters for segmented records."
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
                "delta",
                "obstructive/h",
                "central/h",
                "hypopnea/h",
            ],
        ),
        "",
        "## Channel Quality",
        "",
        (
            "The pilot records include respiration channels, but these three records do "
            "not expose SpO2/oximetry channels. That means oxygen desaturation burden "
            "cannot be interpreted from this pilot subset."
        ),
        "",
        _markdown_table(
            channel_rows,
            ["record", "channel", "unit", "finite %", "std", "dynamic"],
        ),
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
            "- Treatment reasoning should be framed as questions: whether OSA evidence "
            "supports PAP evaluation, oral-appliance discussion, weight/lifestyle work, "
            "positional therapy, surgery referral, or another diagnosis."
        ),
        "",
        "## Next Data Step",
        "",
        (
            "Add MIT-BIH records with SO2 channels, such as `slp59`, `slp60`, `slp61`, "
            "`slp66`, or `slp67x`, or move to a PSG dataset with richer oximetry and "
            "respiratory-event scoring."
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
        "",
    ]
    return "\n".join(lines)


def run_mit_bih_psg_respiratory_pilot(
    config: dict[str, Any],
    *,
    records: list[str] | None = None,
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
    metrics = respiratory_metrics(
        epochs,
        source_reported_ahi=source_reported_ahi,
        epoch_seconds=epoch_seconds,
    )
    quality = channel_quality(
        records=selected_records,
        raw_dir=raw_dir,
        sample_seconds=float(config["quality"]["sample_seconds"]),
    )
    indicators = clinical_indicators(metrics, quality)

    epochs_out = Path(outputs["annotation_epochs_csv"])
    metrics_out = Path(outputs["respiratory_metrics_csv"])
    quality_out = Path(outputs["channel_quality_csv"])
    indicators_out = Path(outputs["clinical_indicators_csv"])
    report_out = Path(outputs["report_md"])
    for out in (epochs_out, metrics_out, quality_out, indicators_out, report_out):
        out.parent.mkdir(parents=True, exist_ok=True)
    epochs.to_csv(epochs_out, index=False)
    metrics.to_csv(metrics_out, index=False)
    quality.to_csv(quality_out, index=False)
    indicators.to_csv(indicators_out, index=False)
    report_out.write_text(
        build_report(
            records=selected_records,
            metrics=metrics,
            quality=quality,
            indicators=indicators,
        ),
        encoding="utf-8",
    )
    return MitBihPsgPilotOutputs(
        annotation_epochs_csv=epochs_out,
        respiratory_metrics_csv=metrics_out,
        channel_quality_csv=quality_out,
        clinical_indicators_csv=indicators_out,
        report_md=report_out,
    )
