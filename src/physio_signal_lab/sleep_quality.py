from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from physio_signal_lab.evaluation.sleep_staging import (
    align_model_predictions,
    paths_from_selection,
    read_sleep_edf_epoch_labels,
)
from physio_signal_lab.io.sleep_edf import validate_sleep_edf_manifest
from physio_signal_lab.sleep_outputs import (
    clean_output_prefix,
    scoped_sleep_edf_output_path,
    scoped_sleep_edf_report_path,
)


SLEEP_STAGES = ("N1", "N2", "N3", "REM")
QUALITY_STAGES = ("WAKE", *SLEEP_STAGES)
STAGE_TO_CODE = {"WAKE": 4, "REM": 3, "N1": 2, "N2": 1, "N3": 0}
STAGE_COLORS = {
    "WAKE": "#8a8f98",
    "N1": "#6baed6",
    "N2": "#3182bd",
    "N3": "#08519c",
    "REM": "#f28e2b",
}


@dataclass(frozen=True)
class SleepClinicalEducationOutputs:
    metrics_csv: Path
    indicators_csv: Path
    discrepancy_csv: Path | None
    question_ranking_csv: Path
    hypnogram_plot_png: Path
    architecture_plot_png: Path
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


def build_yasa_discrepancy_table(
    labels: pd.DataFrame,
    yasa_predictions: pd.DataFrame,
) -> pd.DataFrame:
    aligned = align_model_predictions(
        labels,
        yasa_predictions,
        model_name="yasa_sleepstaging",
    )
    rows: list[dict[str, Any]] = []
    for record_id, group in aligned.groupby("record_id", sort=True):
        total = len(group)
        pair_counts = (
            group.groupby(["mapped_stage", "predicted_stage"], sort=True)
            .size()
            .reset_index(name="epoch_count")
        )
        for _, pair in pair_counts.iterrows():
            reference_stage = str(pair["mapped_stage"])
            predicted_stage = str(pair["predicted_stage"])
            count = int(pair["epoch_count"])
            rows.append(
                {
                    "record_id": str(record_id),
                    "reference_stage": reference_stage,
                    "yasa_stage": predicted_stage,
                    "pair_type": (
                        "agreement" if reference_stage == predicted_stage else "discrepancy"
                    ),
                    "epoch_count": count,
                    "pct_record_epochs": _safe_pct(count, total),
                }
            )
    return pd.DataFrame(rows)


def build_clinical_question_ranking(metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in metrics.iterrows():
        record_id = str(row["record_id"])
        source = str(row["source"])
        tst = float(row["total_sleep_time_minutes"])
        period_efficiency = float(row["sleep_period_efficiency_pct"])
        waso = float(row["waso_minutes"])
        latency = float(row["sleep_onset_latency_proxy_minutes"])
        rem_latency = float(row["rem_latency_minutes"])
        awakenings = float(row["awakening_count"])
        rem_pct = float(row["rem_pct_tst"])
        n3_pct = float(row["n3_pct_tst"])

        duration_score = max(0.0, (420.0 - tst) / 60.0)
        continuity_score = max(0.0, (85.0 - period_efficiency) / 10.0) + max(
            0.0,
            (waso - 60.0) / 60.0,
        )
        latency_score = min(1.0, max(0.0, (latency - 30.0) / 60.0))
        rem_score = 0.0
        if math.isfinite(rem_latency):
            rem_score += max(0.0, (60.0 - rem_latency) / 30.0)
            rem_score += max(0.0, (rem_latency - 120.0) / 60.0)
        architecture_score = rem_score + max(0.0, (10.0 - n3_pct) / 10.0) + max(
            0.0,
            (15.0 - rem_pct) / 10.0,
        )
        respiratory_evidence_score = max(0.0, continuity_score - 1.0) + max(
            0.0,
            (awakenings - 15.0) / 15.0,
        )

        candidates = [
            {
                "clinical_question": "Is sleep duration insufficient?",
                "priority_score": duration_score,
                "evidence": f"TST {tst:.1f} min.",
                "next_data_needed": "Habitual sleep schedule, sleep diary, daytime symptoms.",
            },
            {
                "clinical_question": "Is sleep continuity poor?",
                "priority_score": continuity_score,
                "evidence": f"Sleep-period efficiency {period_efficiency:.1f}%, WASO {waso:.1f} min.",
                "next_data_needed": "Arousal scoring, symptoms, pain/medication review, repeated nights.",
            },
            {
                "clinical_question": "Is lights-out context needed?",
                "priority_score": latency_score,
                "evidence": f"First sleep begins {latency:.1f} min after recording start.",
                "next_data_needed": "Lights-out marker and patient-reported bedtime.",
            },
            {
                "clinical_question": "Is REM or stage architecture unusual?",
                "priority_score": architecture_score,
                "evidence": f"REM latency {_fmt(rem_latency)} min, N3 {_fmt(n3_pct)}% TST, REM {_fmt(rem_pct)}% TST.",
                "next_data_needed": "Medication, mood, sleep deprivation, repeated nights, MSLT if indicated.",
            },
            {
                "clinical_question": "Is respiratory-event evidence needed?",
                "priority_score": respiratory_evidence_score,
                "evidence": f"Fragmentation proxy: {awakenings:.0f} awakenings, WASO {waso:.1f} min.",
                "next_data_needed": "Airflow, effort, SpO2, arousals, scored apneas/hypopneas, AHI.",
            },
        ]
        ranked = sorted(candidates, key=lambda item: item["priority_score"], reverse=True)
        for rank, candidate in enumerate(ranked, start=1):
            rows.append(
                {
                    "record_id": record_id,
                    "source": source,
                    "rank": rank,
                    "clinical_question": candidate["clinical_question"],
                    "priority_score": round(float(candidate["priority_score"]), 3),
                    "evidence": candidate["evidence"],
                    "next_data_needed": candidate["next_data_needed"],
                }
            )
    return pd.DataFrame(rows)


def _stage_epoch_view(
    labels: pd.DataFrame,
    yasa_predictions: pd.DataFrame | None,
) -> pd.DataFrame:
    reference = labels[labels["included"]].copy()
    reference["source"] = "reference_hypnogram"
    reference["stage"] = reference["mapped_stage"]
    parts = [reference[["record_id", "epoch_index", "source", "stage"]]]
    if yasa_predictions is not None:
        aligned = align_model_predictions(
            labels,
            yasa_predictions,
            model_name="yasa_sleepstaging",
        )
        aligned["source"] = "yasa_sleepstaging"
        aligned["stage"] = aligned["predicted_stage"]
        parts.append(aligned[["record_id", "epoch_index", "source", "stage"]])
    return pd.concat(parts, ignore_index=True)


def plot_hypnogram_timeline(
    stage_epochs: pd.DataFrame,
    *,
    output_path: Path,
    epoch_seconds: float,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    groups = list(stage_epochs.groupby(["record_id", "source"], sort=True))
    height = max(2.4, 1.6 * len(groups))
    fig, axes = plt.subplots(len(groups), 1, figsize=(11, height), sharex=False)
    if len(groups) == 1:
        axes = [axes]
    for axis, ((record_id, source), group) in zip(axes, groups):
        ordered = group.sort_values("epoch_index")
        x_hours = ordered["epoch_index"].astype(float) * float(epoch_seconds) / 3600.0
        y = ordered["stage"].map(STAGE_TO_CODE)
        axis.step(x_hours, y, where="post", color="#234b6d", linewidth=0.8)
        axis.set_yticks([0, 1, 2, 3, 4])
        axis.set_yticklabels(["N3", "N2", "N1", "REM", "Wake"])
        axis.set_ylim(-0.4, 4.4)
        axis.set_ylabel(f"{record_id}\n{source}", rotation=0, ha="right", va="center")
        axis.grid(axis="y", alpha=0.25)
    axes[-1].set_xlabel("Recording time (hours)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def plot_sleep_architecture(
    metrics: pd.DataFrame,
    *,
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    labels = [f"{row.record_id}\n{row.source}" for row in metrics.itertuples()]
    bottoms = [0.0] * len(metrics)
    fig, axis = plt.subplots(figsize=(max(8.0, len(metrics) * 1.15), 4.8))
    for stage in SLEEP_STAGES:
        values = metrics[f"{stage.lower()}_pct_tst"].fillna(0.0).astype(float).tolist()
        axis.bar(
            labels,
            values,
            bottom=bottoms,
            label=stage,
            color=STAGE_COLORS[stage],
        )
        bottoms = [bottom + value for bottom, value in zip(bottoms, values)]
    axis.set_ylabel("% of total sleep time")
    axis.set_ylim(0, 100)
    axis.legend(ncols=4, loc="upper center", bbox_to_anchor=(0.5, 1.16))
    axis.grid(axis="y", alpha=0.25)
    axis.tick_params(axis="x", labelrotation=35)
    for label in axis.get_xticklabels():
        label.set_horizontalalignment("right")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


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
    question_ranking: pd.DataFrame,
    discrepancy: pd.DataFrame | None,
    hypnogram_plot: Path,
    architecture_plot: Path,
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

    ranking_rows = []
    for _, row in question_ranking[question_ranking["rank"] <= 3].iterrows():
        ranking_rows.append(
            {
                "record": row["record_id"],
                "source": row["source"],
                "rank": int(row["rank"]),
                "question": row["clinical_question"],
                "score": _fmt(row["priority_score"], digits=2),
                "evidence": row["evidence"],
            }
        )

    discrepancy_rows = []
    if discrepancy is not None and not discrepancy.empty:
        top_discrepancies = discrepancy[discrepancy["pair_type"] == "discrepancy"].sort_values(
            ["record_id", "epoch_count"],
            ascending=[True, False],
        )
        for _, row in top_discrepancies.groupby("record_id", sort=True).head(4).iterrows():
            discrepancy_rows.append(
                {
                    "record": row["record_id"],
                    "reference": row["reference_stage"],
                    "yasa": row["yasa_stage"],
                    "epochs": int(row["epoch_count"]),
                    "% epochs": _fmt(row["pct_record_epochs"]),
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
        "## Figures",
        "",
        f"- Hypnogram timeline: `{hypnogram_plot.as_posix()}`",
        f"- Sleep architecture: `{architecture_plot.as_posix()}`",
        "",
        "## Clinical Learning Indicators",
        "",
        _markdown_table(
            indicator_rows,
            ["record", "source", "domain", "indicator", "status", "evidence"],
        ),
        "",
        "## Clinical Question Ranking",
        "",
        _markdown_table(
            ranking_rows,
            ["record", "source", "rank", "question", "score", "evidence"],
        ),
        "",
        "## Reference vs YASA Discrepancy",
        "",
        (
            "This table highlights where model-derived staging would change downstream "
            "sleep-quality reasoning. Large discrepancies should be investigated before "
            "using model-derived metrics clinically."
        ),
        "",
        _markdown_table(
            discrepancy_rows,
            ["record", "reference", "yasa", "epochs", "% epochs"],
        )
        if discrepancy_rows
        else "YASA discrepancy table was not generated for this run.",
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
                "1. Done: compute sleep quality metrics from 30 s stage epochs.",
                "2. Done: separate full recording metrics from inferred main sleep-period metrics.",
                "3. Done: generate clinical learning indicators for sleep duration, continuity, latency, REM timing, and fragmentation.",
                "4. Done: mark disorder areas that cannot be diagnosed from stage metrics alone.",
                "5. Done: add a treatment learning map that shows how confirmed evidence would guide clinical questions.",
                "6. Done: add hypnogram timelines, sleep architecture plots, model discrepancy tables, and clinical question rankings.",
                "7. Done: write pilot, five-record, eight-record, eleven-record, and twenty-record educational reports that map data patterns to next clinical questions and missing data.",
                "8. Done: keep raw EDF files out of git while committing compact metrics, reports, and figures.",
                "9. Done: add MIT-BIH PSG respiratory pilot so OSA-style reasoning can use respiration signals and apnea/hypopnea annotations.",
                "10. Done: add SO2-channel MIT-BIH records so oxygen desaturation burden can be learned from real data.",
                "11. Done: add event-level waveform windows and plots around scored respiratory-event epochs.",
                "12. Done: run the complete 18-record MIT-BIH PSG report.",
                "13. Done: align SO2 oxygen metrics to sleep epochs while retaining recording-wide audit columns.",
                "14. Done: add source AHI alignment audit outputs for high-priority manual review.",
                "15. Done: replace the main sleep-only oxygen proxy with a documented pre-event rolling-baseline ODI scorer.",
                "16. Done: add oxygen artifact review outputs for SO2 waveform/raw-channel prioritization.",
                "17. Done: add dataset-readiness outputs and a richer-PSG gate decision.",
                "18. Next: manually adjudicate high-priority alignment rows against source AHI scoring rules.",
                "19. Next: inspect SO2 artifact-review records before using oxygen evidence as clinical-learning examples.",
                "",
                "## Diagnostic Reasoning Boundaries",
                "",
                "- Sleep quality can be estimated from stages and continuity metrics.",
                "- Insomnia requires subjective complaint, sleep opportunity, duration, and daytime impairment.",
                "- OSA requires respiratory event evidence such as airflow, effort, SpO2, arousals, and AHI.",
                "- Narcolepsy requires symptoms and usually MSLT; overnight REM latency alone is not enough.",
                "- Treatment decisions require clinician review and disorder-specific evidence, but the report should show the reasoning path.",
                "",
                "## Current Commands",
                "",
                "```bash",
                "uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf/default.yaml --records SC4001,SC4011 --output-prefix pilot --include-yasa",
                "uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf/default.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041 --output-prefix five_record --include-yasa",
                "uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf/default.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041,SC4051,SC4061,SC4071 --output-prefix eight_record --include-yasa",
                "uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf/default.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041,SC4051,SC4061,SC4071,SC4081,SC4091,SC4101 --output-prefix eleven_record --include-yasa",
                "uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf/default.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041,SC4051,SC4061,SC4071,SC4081,SC4091,SC4101,SC4111,SC4121,SC4131,SC4141,SC4151,SC4161,SC4171,SC4181,SC4191 --output-prefix twenty_record --include-yasa",
                "uv run python -m physio_signal_lab.cli run-mit-bih-psg-respiratory-pilot --config configs/mit_bih_psg/default.yaml --records slp01a,slp02a,slp03",
                "uv run python -m physio_signal_lab.cli run-mit-bih-psg-respiratory-pilot --config configs/mit_bih_psg/default.yaml --records slp59,slp60,slp61,slp66,slp67x --output-prefix oxygen_record",
                "uv run python -m physio_signal_lab.cli run-mit-bih-psg-respiratory-pilot --config configs/mit_bih_psg/default.yaml --output-prefix all_record",
                "uv run python -m physio_signal_lab.cli run-mit-bih-psg-respiratory-pilot --config configs/mit_bih_psg/default.yaml --output-prefix complete_record",
                "```",
                "",
                "## Next Dataset Direction",
                "",
                "MIT-BIH PSG is now integrated for respiratory-event and sleep-aligned SO2 oxygenation learning across all 18 records. Use `reports/mit_bih_psg/complete_record_dataset_decision.md` and `reports/project/respiratory_dataset_candidates.md` to drive source AHI alignment, SO2 artifact review, and any later richer-PSG dataset decision.",
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
    output_prefix = clean_output_prefix(output_prefix)
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
    yasa_predictions = None
    discrepancy = None
    if include_yasa:
        yasa_predictions_path = scoped_sleep_edf_output_path(output_prefix, "yasa_predictions.csv")
        if not yasa_predictions_path.exists():
            yasa_predictions_path = Path(outputs["yasa_predictions_csv"])
        yasa_predictions = pd.read_csv(yasa_predictions_path)
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
        discrepancy = build_yasa_discrepancy_table(labels_df, yasa_predictions)
    metrics = pd.concat(metric_parts, ignore_index=True)
    indicators = build_clinical_indicators(metrics)
    question_ranking = build_clinical_question_ranking(metrics)
    stage_epochs = _stage_epoch_view(labels_df, yasa_predictions)

    metrics_out = scoped_sleep_edf_output_path(output_prefix, "sleep_quality_metrics.csv")
    indicators_out = scoped_sleep_edf_output_path(output_prefix, "clinical_indicators.csv")
    question_ranking_out = scoped_sleep_edf_output_path(
        output_prefix,
        "clinical_question_ranking.csv",
    )
    discrepancy_out = (
        scoped_sleep_edf_output_path(output_prefix, "yasa_discrepancy.csv")
        if discrepancy is not None
        else None
    )
    report_out = scoped_sleep_edf_report_path(output_prefix, "clinical_education.md")
    hypnogram_plot = Path("figures") / "sleep_edf" / f"{output_prefix}_hypnogram_timeline.png"
    architecture_plot = Path("figures") / "sleep_edf" / f"{output_prefix}_sleep_architecture.png"
    for out in (
        metrics_out,
        indicators_out,
        question_ranking_out,
        report_out,
        hypnogram_plot,
        architecture_plot,
    ):
        out.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(metrics_out, index=False)
    indicators.to_csv(indicators_out, index=False)
    question_ranking.to_csv(question_ranking_out, index=False)
    if discrepancy is not None and discrepancy_out is not None:
        discrepancy.to_csv(discrepancy_out, index=False)
    plot_hypnogram_timeline(
        stage_epochs,
        output_path=hypnogram_plot,
        epoch_seconds=epoch_seconds,
    )
    plot_sleep_architecture(metrics, output_path=architecture_plot)
    report_out.write_text(
        build_sleep_clinical_education_report(
            records=records,
            metrics=metrics,
            indicators=indicators,
            question_ranking=question_ranking,
            discrepancy=discrepancy,
            hypnogram_plot=hypnogram_plot,
            architecture_plot=architecture_plot,
        ),
        encoding="utf-8",
    )
    write_clinical_learning_plan("reports/sleep_edf/clinical_learning_plan.md")
    return SleepClinicalEducationOutputs(
        metrics_csv=metrics_out,
        indicators_csv=indicators_out,
        discrepancy_csv=discrepancy_out,
        question_ranking_csv=question_ranking_out,
        hypnogram_plot_png=hypnogram_plot,
        architecture_plot_png=architecture_plot,
        report_md=report_out,
    )
