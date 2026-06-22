from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import math

import pandas as pd

from physio_signal_lab.evaluation.sleep_staging import (
    align_model_predictions,
    paths_from_selection,
    read_sleep_edf_epoch_labels,
)
from physio_signal_lab.io.sleep_edf import validate_sleep_edf_manifest


SLEEP_STAGES = ("N1", "N2", "N3", "REM")
QUALITY_STAGES = ("WAKE", *SLEEP_STAGES)


@dataclass(frozen=True)
class SleepClinicalEducationOutputs:
    metrics_csv: Path
    indicators_csv: Path
    report_md: Path


def _safe_pct(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return math.nan
    return float(numerator) / float(denominator) * 100.0


def _safe_rate(count: int, minutes: float) -> float:
    if minutes <= 0:
        return math.nan
    return float(count) / (float(minutes) / 60.0)


def _max_consecutive(values: list[bool], target: bool = True) -> int:
    longest = 0
    current = 0
    for value in values:
        if value == target:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def _stage_counts(stages: pd.Series) -> dict[str, int]:
    counts = stages.value_counts().to_dict()
    return {stage: int(counts.get(stage, 0)) for stage in QUALITY_STAGES}


def sleep_quality_metrics(
    epochs: pd.DataFrame,
    *,
    stage_column: str,
    source: str,
    epoch_seconds: float,
) -> pd.DataFrame:
    if epoch_seconds <= 0:
        raise ValueError("epoch_seconds must be positive")
    if stage_column not in epochs:
        raise ValueError(f"Missing stage column: {stage_column}")
    if "record_id" not in epochs or "epoch_index" not in epochs:
        raise ValueError("epochs must include record_id and epoch_index columns")

    frame = epochs.copy()
    if "included" in frame:
        frame = frame[frame["included"]].copy()
    frame[stage_column] = frame[stage_column].astype(str)
    unexpected = sorted(set(frame[stage_column]) - set(QUALITY_STAGES))
    if unexpected:
        raise ValueError(f"Unsupported sleep quality stage labels: {unexpected}")

    epoch_minutes = float(epoch_seconds) / 60.0
    rows: list[dict[str, Any]] = []
    for record_id, group in frame.sort_values(["record_id", "epoch_index"]).groupby(
        "record_id", sort=True
    ):
        stages = group[stage_column].astype(str).tolist()
        total_epochs = len(stages)
        total_minutes = float(total_epochs) * epoch_minutes
        is_sleep = [stage != "WAKE" for stage in stages]
        sleep_epochs = int(sum(is_sleep))
        sleep_minutes = float(sleep_epochs) * epoch_minutes
        counts = _stage_counts(pd.Series(stages))

        row: dict[str, Any] = {
            "record_id": str(record_id),
            "source": source,
            "epoch_seconds": float(epoch_seconds),
            "included_epochs": total_epochs,
            "included_minutes": total_minutes,
            "total_sleep_time_minutes": sleep_minutes,
            "recording_sleep_efficiency_pct": _safe_pct(sleep_minutes, total_minutes),
            "wake_minutes": float(counts["WAKE"]) * epoch_minutes,
        }
        for stage in SLEEP_STAGES:
            minutes = float(counts[stage]) * epoch_minutes
            row[f"{stage.lower()}_minutes"] = minutes
            row[f"{stage.lower()}_pct_tst"] = _safe_pct(minutes, sleep_minutes)

        if sleep_epochs == 0:
            row.update(
                {
                    "sleep_onset_latency_proxy_minutes": math.nan,
                    "last_sleep_epoch_index": math.nan,
                    "sleep_period_minutes": math.nan,
                    "sleep_period_efficiency_pct": math.nan,
                    "waso_minutes": math.nan,
                    "terminal_wake_minutes": math.nan,
                    "rem_latency_minutes": math.nan,
                    "awakening_count": 0,
                    "longest_wake_bout_after_sleep_onset_minutes": math.nan,
                    "stage_transition_count": 0,
                    "awakenings_per_sleep_hour": math.nan,
                }
            )
            rows.append(row)
            continue

        first_sleep = next(index for index, value in enumerate(is_sleep) if value)
        last_sleep = len(is_sleep) - 1 - next(
            index for index, value in enumerate(reversed(is_sleep)) if value
        )
        period_stages = stages[first_sleep : last_sleep + 1]
        period_is_wake = [stage == "WAKE" for stage in period_stages]
        sleep_period_minutes = float(len(period_stages)) * epoch_minutes
        wake_after_sleep_onset_epochs = int(sum(period_is_wake))
        awakenings = 0
        for previous, current in zip(period_stages, period_stages[1:]):
            if previous != "WAKE" and current == "WAKE":
                awakenings += 1
        transitions = sum(
            1
            for previous, current in zip(period_stages, period_stages[1:])
            if previous != current
        )
        first_rem = next(
            (index for index, stage in enumerate(stages) if stage == "REM"),
            None,
        )
        row.update(
            {
                "sleep_onset_latency_proxy_minutes": float(first_sleep) * epoch_minutes,
                "last_sleep_epoch_index": int(group.iloc[last_sleep]["epoch_index"]),
                "sleep_period_minutes": sleep_period_minutes,
                "sleep_period_efficiency_pct": _safe_pct(
                    sleep_minutes,
                    sleep_period_minutes,
                ),
                "waso_minutes": float(wake_after_sleep_onset_epochs) * epoch_minutes,
                "terminal_wake_minutes": float(total_epochs - last_sleep - 1)
                * epoch_minutes,
                "rem_latency_minutes": (
                    float(first_rem - first_sleep) * epoch_minutes
                    if first_rem is not None and first_rem >= first_sleep
                    else math.nan
                ),
                "awakening_count": awakenings,
                "longest_wake_bout_after_sleep_onset_minutes": float(
                    _max_consecutive(period_is_wake)
                )
                * epoch_minutes,
                "stage_transition_count": transitions,
                "awakenings_per_sleep_hour": _safe_rate(awakenings, sleep_minutes),
            }
        )
        rows.append(row)

    return pd.DataFrame(rows)


def build_clinical_indicators(metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for _, row in metrics.iterrows():
        record_id = str(row["record_id"])
        source = str(row["source"])
        tst = float(row["total_sleep_time_minutes"])
        period_efficiency = float(row["sleep_period_efficiency_pct"])
        waso = float(row["waso_minutes"])
        latency = float(row["sleep_onset_latency_proxy_minutes"])
        rem_latency = float(row["rem_latency_minutes"])

        if tst < 420.0:
            rows.append(
                {
                    "record_id": record_id,
                    "source": source,
                    "domain": "sleep_quality",
                    "indicator": "short_total_sleep_time",
                    "status": "screen_positive",
                    "evidence": f"TST {tst:.1f} min is below the adult 7 h learning reference.",
                    "clinical_learning": "Short objective sleep can contribute to poor sleep quality, but adequacy also depends on age, sleep need, and daytime symptoms.",
                    "next_data_needed": "Sleep diary, habitual schedule, daytime sleepiness, medications, and clinical history.",
                }
            )
        else:
            rows.append(
                {
                    "record_id": record_id,
                    "source": source,
                    "domain": "sleep_quality",
                    "indicator": "total_sleep_time",
                    "status": "within_learning_reference",
                    "evidence": f"TST {tst:.1f} min is at or above 7 h.",
                    "clinical_learning": "Duration alone does not prove restorative sleep; continuity, symptoms, and comorbidities still matter.",
                    "next_data_needed": "Daytime function and repeated-night stability.",
                }
            )

        if period_efficiency < 85.0 or waso > 60.0:
            rows.append(
                {
                    "record_id": record_id,
                    "source": source,
                    "domain": "sleep_quality",
                    "indicator": "low_sleep_continuity",
                    "status": "screen_positive",
                    "evidence": f"Inferred sleep-period efficiency {period_efficiency:.1f}%, WASO {waso:.1f} min.",
                    "clinical_learning": "Low continuity can match insomnia-like fragmentation, pain, medications, respiratory events, or other causes.",
                    "next_data_needed": "Symptoms, arousal/event scoring, respiratory channels, medications, and repeated nights.",
                }
            )

        if latency > 30.0:
            rows.append(
                {
                    "record_id": record_id,
                    "source": source,
                    "domain": "sleep_quality",
                    "indicator": "long_sleep_onset_latency_proxy",
                    "status": "context_required",
                    "evidence": f"First sleep begins {latency:.1f} min after recording start.",
                    "clinical_learning": "This is only a proxy because Sleep-EDF does not expose a clean lights-out marker in this analysis.",
                    "next_data_needed": "Lights-out time, patient-reported bedtime, sleep diary, and lab notes.",
                }
            )

        if math.isfinite(rem_latency) and (rem_latency < 60.0 or rem_latency > 120.0):
            rows.append(
                {
                    "record_id": record_id,
                    "source": source,
                    "domain": "sleep_architecture",
                    "indicator": "rem_latency_outside_learning_band",
                    "status": "architecture_note",
                    "evidence": f"REM latency {rem_latency:.1f} min from first sleep.",
                    "clinical_learning": "REM timing is biologically meaningful but non-specific; it is not a diagnosis by itself.",
                    "next_data_needed": "Medication, mood history, sleep deprivation context, MSLT if hypersomnolence is suspected.",
                }
            )

        rows.extend(
            [
                {
                    "record_id": record_id,
                    "source": source,
                    "domain": "sleep_disordered_breathing",
                    "indicator": "osa_or_hypoventilation",
                    "status": "cannot_assess_from_stage_metrics",
                    "evidence": "Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI.",
                    "clinical_learning": "OSA diagnosis needs PSG/HSAT-style respiratory evidence, not sleep architecture alone.",
                    "next_data_needed": "Airflow, respiratory effort, SpO2, arousals, scored events, symptoms, and clinician review.",
                },
                {
                    "record_id": record_id,
                    "source": source,
                    "domain": "insomnia",
                    "indicator": "insomnia_disorder",
                    "status": "cannot_diagnose_from_psg_alone",
                    "evidence": "The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history.",
                    "clinical_learning": "PSG can support a sleep-continuity discussion, but insomnia is primarily a clinical diagnosis.",
                    "next_data_needed": "Sleep history, diary, ISI/PSQI-like questionnaire, duration >=3 months, daytime impairment.",
                },
                {
                    "record_id": record_id,
                    "source": source,
                    "domain": "treatment_reasoning",
                    "indicator": "treatment_decision",
                    "status": "not_recommended_from_this_dataset",
                    "evidence": "This analysis can generate hypotheses and referral questions, not prescribe treatment.",
                    "clinical_learning": "Treatment follows a confirmed diagnosis, patient goals, risks, contraindications, and clinician judgment.",
                    "next_data_needed": "Full clinical evaluation and disorder-specific diagnostic evidence.",
                },
            ]
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


def build_sleep_clinical_education_report(
    *,
    records: list[str],
    metrics: pd.DataFrame,
    indicators: pd.DataFrame,
) -> str:
    metric_rows = []
    for _, row in metrics.iterrows():
        metric_rows.append(
            {
                "record": row["record_id"],
                "source": row["source"],
                "TST min": _fmt(row["total_sleep_time_minutes"]),
                "period SE %": _fmt(row["sleep_period_efficiency_pct"]),
                "WASO min": _fmt(row["waso_minutes"]),
                "SOL proxy min": _fmt(row["sleep_onset_latency_proxy_minutes"]),
                "REM latency min": _fmt(row["rem_latency_minutes"]),
                "N3 % TST": _fmt(row["n3_pct_tst"]),
                "REM % TST": _fmt(row["rem_pct_tst"]),
                "awakenings": int(row["awakening_count"]),
            }
        )

    indicator_rows = []
    for _, row in indicators.iterrows():
        if row["status"] in {
            "screen_positive",
            "context_required",
            "architecture_note",
            "cannot_assess_from_stage_metrics",
            "cannot_diagnose_from_psg_alone",
            "not_recommended_from_this_dataset",
        }:
            indicator_rows.append(
                {
                    "record": row["record_id"],
                    "source": row["source"],
                    "domain": row["domain"],
                    "indicator": row["indicator"],
                    "status": row["status"],
                    "evidence": row["evidence"],
                }
            )

    lines = [
        "# Sleep-EDF Clinical Learning Report",
        "",
        "## Purpose",
        "",
        (
            "This report shows how real sleep-stage data can be transformed into sleep "
            "quality metrics, clinical hypotheses, and treatment questions. It is an "
            "educational analysis, not a diagnosis, prescription, or triage tool."
        ),
        "",
        "## Records",
        "",
        f"- Records: {', '.join(records)}.",
        "- Epoch size: 30 s.",
        (
            "- Main sleep period is inferred from first sleep epoch to last sleep epoch "
            "because this project does not yet use a clean lights-out/lights-on marker."
        ),
        (
            "- Reference hypnogram rows are the primary view for learning from real labels; "
            "YASA rows show how a model-derived staging view can change downstream clinical-style metrics."
        ),
        "",
        "## Sleep Quality Metrics",
        "",
        _markdown_table(
            metric_rows,
            [
                "record",
                "source",
                "TST min",
                "period SE %",
                "WASO min",
                "SOL proxy min",
                "REM latency min",
                "N3 % TST",
                "REM % TST",
                "awakenings",
            ],
        ),
        "",
        "## Clinical Learning Indicators",
        "",
        _markdown_table(
            indicator_rows,
            ["record", "source", "domain", "indicator", "status", "evidence"],
        ),
        "",
        "## How To Read This",
        "",
        (
            "- Sleep quality is represented here by duration, continuity, fragmentation, "
            "REM timing, and stage percentages."
        ),
        (
            "- Disease reasoning starts from these patterns but needs disorder-specific "
            "data before it becomes diagnosis."
        ),
        (
            "- Treatment reasoning is intentionally framed as next clinical questions. "
            "For example, low continuity can lead to an insomnia history, medication "
            "review, pain review, or respiratory-event evaluation; it does not by itself "
            "select CBT-I, PAP, medication, or any other treatment."
        ),
        (
            "- Large differences between reference and YASA rows should be treated as model "
            "behavior to investigate before using model-derived metrics for any clinical workflow."
        ),
        "",
        "## Treatment Learning Map",
        "",
        _markdown_table(
            [
                {
                    "possible question": "Poor sleep duration or continuity",
                    "data trigger": "Low TST, high WASO, low sleep-period efficiency, high fragmentation",
                    "missing evidence": "Symptoms, sleep opportunity, diary, medications, pain, mental health, repeated nights",
                    "clinical path": "Insomnia history, behavior review, CBT-I discussion, or search for another sleep disorder",
                },
                {
                    "possible question": "Sleep-disordered breathing",
                    "data trigger": "Fragmented sleep, reduced REM/N3, symptoms, snoring, witnessed apneas, cardiometabolic risk",
                    "missing evidence": "Airflow, effort, SpO2, arousals, apnea/hypopnea scoring, AHI",
                    "clinical path": "PSG or HSAT, then clinician decides PAP, oral appliance, surgery, weight/lifestyle path, or other care",
                },
                {
                    "possible question": "Central hypersomnolence or narcolepsy",
                    "data trigger": "Very short REM latency or abnormal REM timing plus daytime sleepiness",
                    "missing evidence": "MSLT, sleep diary/actigraphy, medication washout context, cataplexy history",
                    "clinical path": "Sleep specialist evaluation before any medication or safety recommendation",
                },
                {
                    "possible question": "Movement or REM behavior disorder",
                    "data trigger": "Fragmentation, abnormal movements, REM-without-atonia suspicion",
                    "missing evidence": "Leg EMG, chin EMG review, video PSG, event scoring, injury history",
                    "clinical path": "Disorder-specific PSG review before safety or medication decisions",
                },
            ],
            ["possible question", "data trigger", "missing evidence", "clinical path"],
        ),
        "",
        "## What This Dataset Can And Cannot Support",
        "",
        (
            "- Can support: sleep architecture, total sleep time, inferred WASO, inferred "
            "sleep-period efficiency, REM latency, stage balance, and fragmentation."
        ),
        (
            "- Cannot diagnose from these outputs alone: obstructive sleep apnea, central "
            "sleep apnea, insomnia disorder, narcolepsy, REM sleep behavior disorder, "
            "periodic limb movement disorder, depression, or circadian rhythm disorder."
        ),
        (
            "- Needed for those diagnoses: symptoms, sleep history, questionnaires, "
            "lights-out/lights-on times, airflow, respiratory effort, SpO2, arousals, "
            "leg EMG, MSLT when indicated, and clinician review."
        ),
        "",
        "## References Used For Learning Boundaries",
        "",
        (
            "- NCBI Bookshelf StatPearls, Physiology, Sleep Stages: sleep stage biology, "
            "typical REM timing, and PSG channels used for sleep-disorder testing. "
            "https://www.ncbi.nlm.nih.gov/books/NBK526132/"
        ),
        (
            "- AASM Sleep Education FAQ: adults should generally sleep 7 or more hours "
            "per night for optimal health. https://sleepeducation.org/sleep-faqs/"
        ),
        (
            "- AAST insomnia overview: insomnia diagnosis depends on clinical sleep "
            "history, daytime impact, duration, and self-report/questionnaires. "
            "https://aastweb.org/insomnia-types-diagnosis-and-treatment/"
        ),
        (
            "- AASM/JCSM OSA guidance context: PSG/HSAT respiratory evidence guides OSA "
            "diagnosis and longitudinal management. "
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC8314660/"
        ),
        "",
    ]
    return "\n".join(lines)


def write_clinical_learning_plan(path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "\n".join(
            [
                "# Sleep-EDF Clinical Learning Implementation Plan",
                "",
                "## Goal",
                "",
                (
                    "Turn real Sleep-EDF hypnogram data into an educational bridge from "
                    "raw physiological recording to sleep quality metrics, disease "
                    "hypotheses, diagnostic evidence requirements, and treatment questions."
                ),
                "",
                "This is not a publication claim-review plan. The goal is to understand what the data can teach and where clinical evidence is still missing.",
                "",
                "## Implementation Tasks",
                "",
                "1. Compute sleep quality metrics from 30 s stage epochs.",
                "2. Separate full recording metrics from inferred main sleep-period metrics.",
                "3. Generate clinical learning indicators for sleep duration, continuity, latency, REM timing, and fragmentation.",
                "4. Mark disorder areas that cannot be diagnosed from stage metrics alone.",
                "5. Add a treatment learning map that shows how confirmed evidence would guide clinical questions.",
                "6. Write an educational report that maps data patterns to next clinical questions and missing data.",
                "7. Keep raw EDF files out of git while committing compact metrics and reports.",
                "",
                "## Diagnostic Reasoning Boundaries",
                "",
                "- Sleep quality can be estimated from stages and continuity metrics.",
                "- Insomnia requires subjective complaint, sleep opportunity, duration, and daytime impairment.",
                "- OSA requires respiratory event evidence such as airflow, effort, SpO2, arousals, and AHI.",
                "- Narcolepsy requires symptoms and usually MSLT; overnight REM latency alone is not enough.",
                "- Treatment decisions require clinician review and disorder-specific evidence, but the report should show the reasoning path.",
                "",
                "## Immediate Command",
                "",
                "```bash",
                "uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf.yaml --records SC4001,SC4011 --output-prefix pilot --include-yasa",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return out


def run_sleep_edf_clinical_education(
    config: dict[str, Any],
    *,
    records: list[str],
    output_prefix: str,
    include_yasa: bool,
) -> SleepClinicalEducationOutputs:
    outputs = config["outputs"]
    validation = validate_sleep_edf_manifest(outputs["manifest_csv"], records=records)
    if not bool(validation["checksum_ok"].all()):
        raise ValueError("Sleep-EDF files are missing or checksum validation failed")

    selection = pd.read_csv(outputs["selection_csv"])
    paths = paths_from_selection(selection, records)
    epoch_seconds = float(config["sleep_stages"]["epoch_seconds"])
    labels_parts = []
    for path_set in paths:
        labels, _metadata = read_sleep_edf_epoch_labels(
            path_set,
            epoch_seconds=epoch_seconds,
        )
        labels_parts.append(labels)
    labels_df = pd.concat(labels_parts, ignore_index=True)

    metric_parts = [
        sleep_quality_metrics(
            labels_df,
            stage_column="mapped_stage",
            source="reference_hypnogram",
            epoch_seconds=epoch_seconds,
        )
    ]
    if include_yasa:
        yasa_predictions = pd.read_csv(outputs["yasa_predictions_csv"])
        aligned = align_model_predictions(
            labels_df,
            yasa_predictions,
            model_name="yasa_sleepstaging",
        )
        metric_parts.append(
            sleep_quality_metrics(
                aligned,
                stage_column="predicted_stage",
                source="yasa_sleepstaging",
                epoch_seconds=epoch_seconds,
            )
        )
    metrics = pd.concat(metric_parts, ignore_index=True)
    indicators = build_clinical_indicators(metrics)

    metrics_out = Path("results") / "sleep_edf" / f"{output_prefix}_sleep_quality_metrics.csv"
    indicators_out = Path("results") / "sleep_edf" / f"{output_prefix}_clinical_indicators.csv"
    report_out = Path("reports") / f"sleep_edf_{output_prefix}_clinical_education.md"
    for out in (metrics_out, indicators_out, report_out):
        out.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(metrics_out, index=False)
    indicators.to_csv(indicators_out, index=False)
    report_out.write_text(
        build_sleep_clinical_education_report(
            records=records,
            metrics=metrics,
            indicators=indicators,
        ),
        encoding="utf-8",
    )
    write_clinical_learning_plan("reports/sleep_edf_clinical_learning_plan.md")
    return SleepClinicalEducationOutputs(
        metrics_csv=metrics_out,
        indicators_csv=indicators_out,
        report_md=report_out,
    )
