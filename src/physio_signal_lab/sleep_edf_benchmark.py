from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import importlib.util

import pandas as pd

from physio_signal_lab.evaluation.sleep_staging import (
    majority_stage_predictions,
    paths_from_selection,
    read_sleep_edf_epoch_labels,
    sleep_stage_metrics,
    stage_summary,
)
from physio_signal_lab.io.sleep_edf import validate_sleep_edf_manifest


@dataclass(frozen=True)
class SleepEdfBenchmarkOutputs:
    epoch_labels_csv: Path
    baseline_metrics_csv: Path
    stage_summary_csv: Path
    report_md: Path


def _fmt(value: float, digits: int = 3) -> str:
    return f"{float(value):.{digits}f}"


def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = [
        "| " + " | ".join(str(row.get(column, "")) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, sep, *body])


def _dependency_status() -> dict[str, str]:
    status = {}
    for package in ("mne", "yasa", "sklearn"):
        status[package] = "available" if importlib.util.find_spec(package) else "missing"
    return status


def build_sleep_edf_pilot_report(
    *,
    records: list[str],
    stage_summary_df: pd.DataFrame,
    metrics: pd.DataFrame,
    dependency_status: dict[str, str],
) -> str:
    overall = metrics[metrics["record_id"] == "all"].iloc[0]
    rows = []
    for _, row in metrics.iterrows():
        rows.append(
            {
                "record": row["record_id"],
                "epochs": int(row["epoch_count"]),
                "majority ref": row["majority_reference_stage"],
                "accuracy": _fmt(row["accuracy"]),
                "balanced accuracy": _fmt(row["balanced_accuracy"]),
                "macro-F1": _fmt(row["macro_f1"]),
                "kappa": _fmt(row["cohen_kappa"]),
            }
        )

    stage_rows = []
    for _, row in stage_summary_df.iterrows():
        stage_rows.append(
            {
                "record": row["record_id"],
                "included": int(row["included_epochs"]),
                "excluded": int(row["excluded_epochs"]),
                "WAKE": int(row["wake_epochs"]),
                "N1": int(row["n1_epochs"]),
                "N2": int(row["n2_epochs"]),
                "N3": int(row["n3_epochs"]),
                "REM": int(row["rem_epochs"]),
            }
        )

    lines = [
        "# Sleep-EDF Pilot Benchmark Report",
        "",
        "## Scope",
        "",
        (
            "This pilot benchmark verifies EDF reading, 30 s hypnogram expansion, "
            "R&K-to-five-class mapping, and a majority-stage baseline on the downloaded "
            "Sleep Cassette pilot records."
        ),
        "",
        "This report does not evaluate sleep quality, diagnose sleep disorders, or make event-detector accuracy claims.",
        "",
        "## Records",
        "",
        f"- Records: {', '.join(records)}.",
        f"- MNE status: {dependency_status.get('mne', 'unknown')}.",
        f"- scikit-learn status: {dependency_status.get('sklearn', 'unknown')}.",
        f"- YASA status: {dependency_status.get('yasa', 'unknown')}.",
        "",
        (
            "YASA staging was not run in this stage because the current Python 3.13 "
            "environment could not resolve a compatible YASA dependency set. The benchmark "
            "therefore reports only the frozen majority-stage baseline."
        ),
        "",
        "## Stage Distribution",
        "",
        _markdown_table(
            stage_rows,
            ["record", "included", "excluded", "WAKE", "N1", "N2", "N3", "REM"],
        ),
        "",
        "## Majority-Stage Baseline",
        "",
        _markdown_table(
            rows,
            ["record", "epochs", "majority ref", "accuracy", "balanced accuracy", "macro-F1", "kappa"],
        ),
        "",
        f"- Overall included epochs: {int(overall['epoch_count'])}.",
        f"- Overall majority-stage accuracy: {_fmt(overall['accuracy'])}.",
        f"- Overall balanced accuracy: {_fmt(overall['balanced_accuracy'])}.",
        f"- Overall macro-F1: {_fmt(overall['macro_f1'])}.",
        f"- Overall Cohen's kappa: {_fmt(overall['cohen_kappa'])}.",
        "",
        "## Reproduce",
        "",
        "```bash",
        "uv sync --extra sleep --extra dev",
        "uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4001,SC4011",
        "uv run python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf.yaml --records SC4001,SC4011",
        "```",
        "",
        "## Next Step",
        "",
        (
            "Resolve the YASA dependency blocker or run the sleep benchmark in a compatible "
            "Python environment, then add YASA predictions and probability outputs using the "
            "same aligned epoch table."
        ),
        "",
    ]
    return "\n".join(lines)


def run_sleep_edf_pilot_benchmark(
    config: dict[str, Any],
    *,
    records: list[str],
) -> SleepEdfBenchmarkOutputs:
    outputs = config["outputs"]
    validation = validate_sleep_edf_manifest(outputs["manifest_csv"], records=records)
    if not bool(validation["checksum_ok"].all()):
        raise ValueError("Sleep-EDF pilot files are missing or checksum validation failed")

    selection = pd.read_csv(outputs["selection_csv"])
    paths = paths_from_selection(selection, records)
    labels_parts = []
    metadata_rows = []
    epoch_seconds = float(config["sleep_stages"]["epoch_seconds"])
    for path_set in paths:
        labels, metadata = read_sleep_edf_epoch_labels(
            path_set,
            epoch_seconds=epoch_seconds,
        )
        labels_parts.append(labels)
        metadata_rows.append(metadata)

    labels_df = pd.concat(labels_parts, ignore_index=True)
    metadata_df = pd.DataFrame(metadata_rows)
    predictions = majority_stage_predictions(labels_df)
    metrics = sleep_stage_metrics(predictions, model_name="majority_stage_baseline")
    summary = stage_summary(labels_df, metadata_df)

    epoch_labels_out = Path(outputs["epoch_labels_csv"])
    epoch_labels_out.parent.mkdir(parents=True, exist_ok=True)
    labels_df.to_csv(epoch_labels_out, index=False)

    baseline_metrics_out = Path(outputs["baseline_metrics_csv"])
    baseline_metrics_out.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(baseline_metrics_out, index=False)

    stage_summary_out = Path(outputs["baseline_stage_summary_csv"])
    stage_summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(stage_summary_out, index=False)

    report_out = Path(outputs["pilot_benchmark_report_md"])
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(
        build_sleep_edf_pilot_report(
            records=records,
            stage_summary_df=summary,
            metrics=metrics,
            dependency_status=_dependency_status(),
        ),
        encoding="utf-8",
    )

    return SleepEdfBenchmarkOutputs(
        epoch_labels_csv=epoch_labels_out,
        baseline_metrics_csv=baseline_metrics_out,
        stage_summary_csv=stage_summary_out,
        report_md=report_out,
    )
