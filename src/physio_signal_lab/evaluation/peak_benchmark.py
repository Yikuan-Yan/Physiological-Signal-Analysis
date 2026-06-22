from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import neurokit2 as nk
import numpy as np
import pandas as pd

from physio_signal_lab.evaluation.peak_matching import (
    PeakMatchResult,
    peak_metrics,
)
from physio_signal_lab.io.fantasia import FantasiaRecordData, load_record
from physio_signal_lab.plots import plot_peak_overlay


@dataclass(frozen=True)
class RecordBenchmark:
    record: FantasiaRecordData
    detected_peak_samples: np.ndarray
    metrics: pd.DataFrame
    primary_match: PeakMatchResult


def detect_r_peaks(
    ecg: np.ndarray,
    *,
    sampling_rate_hz: float,
    clean_method: str = "neurokit",
    peak_method: str = "neurokit",
) -> np.ndarray:
    cleaned = nk.ecg_clean(
        ecg,
        sampling_rate=int(round(sampling_rate_hz)),
        method=clean_method,
    )
    _, info = nk.ecg_peaks(
        cleaned,
        sampling_rate=int(round(sampling_rate_hz)),
        method=peak_method,
    )
    peaks = np.asarray(info["ECG_R_Peaks"], dtype=np.int64)
    return np.sort(peaks)


def benchmark_record(
    record_id: str,
    raw_dir: str | Path,
    *,
    tolerances_ms: list[float],
    ecg_channel: str = "ECG",
    clean_method: str = "neurokit",
    peak_method: str = "neurokit",
) -> RecordBenchmark:
    record = load_record(record_id, raw_dir, ecg_channel=ecg_channel)
    detected = detect_r_peaks(
        record.ecg,
        sampling_rate_hz=record.sampling_rate_hz,
        clean_method=clean_method,
        peak_method=peak_method,
    )

    rows = []
    primary_match: PeakMatchResult | None = None
    for tolerance_ms in tolerances_ms:
        metrics, match = peak_metrics(
            record.reference_peak_samples,
            detected,
            sampling_rate_hz=record.sampling_rate_hz,
            tolerance_ms=tolerance_ms,
        )
        if primary_match is None:
            primary_match = match
        rows.append(
            {
                "record_id": record.record_id,
                "cohort": record.cohort,
                "age": record.age,
                "sex": record.sex,
                "sampling_rate_hz": record.sampling_rate_hz,
                "duration_seconds": record.ecg.shape[0] / record.sampling_rate_hz,
                "ecg_nonfinite_count": record.ecg_nonfinite_count,
                "ecg_nonfinite_fraction": record.ecg_nonfinite_count
                / record.ecg.shape[0],
                "ecg_repair_method": (
                    "linear_interpolation" if record.ecg_nonfinite_count else "none"
                ),
                "detector": peak_method,
                "tolerance_ms": metrics.tolerance_ms,
                "tolerance_samples": metrics.tolerance_samples,
                "n_reference": metrics.n_reference,
                "n_detected": metrics.n_detected,
                "true_positives": metrics.true_positives,
                "false_positives": metrics.false_positives,
                "false_negatives": metrics.false_negatives,
                "sensitivity": metrics.sensitivity,
                "positive_predictive_value": metrics.positive_predictive_value,
                "f1": metrics.f1,
                "median_timing_error_ms": metrics.median_timing_error_ms,
                "median_abs_timing_error_ms": metrics.median_abs_timing_error_ms,
                "iqr_abs_timing_error_ms": metrics.iqr_abs_timing_error_ms,
                "p95_abs_timing_error_ms": metrics.p95_abs_timing_error_ms,
            }
        )

    if primary_match is None:
        raise ValueError("At least one tolerance is required")
    return RecordBenchmark(
        record=record,
        detected_peak_samples=detected,
        metrics=pd.DataFrame(rows),
        primary_match=primary_match,
    )


def benchmark_records(
    record_ids: list[str],
    raw_dir: str | Path,
    *,
    tolerances_ms: list[float],
    ecg_channel: str = "ECG",
    clean_method: str = "neurokit",
    peak_method: str = "neurokit",
    failure_plot_count: int = 0,
    failure_window_seconds: float = 30.0,
    failure_plot_dir: str | Path | None = None,
) -> pd.DataFrame:
    benchmarks: list[RecordBenchmark] = []
    for record_id in record_ids:
        benchmarks.append(
            benchmark_record(
                record_id,
                raw_dir,
                tolerances_ms=tolerances_ms,
                ecg_channel=ecg_channel,
                clean_method=clean_method,
                peak_method=peak_method,
            )
        )

    all_metrics = pd.concat([item.metrics for item in benchmarks], ignore_index=True)

    if failure_plot_count > 0 and failure_plot_dir is not None:
        primary_tolerance = float(tolerances_ms[0])
        primary = all_metrics[all_metrics["tolerance_ms"] == primary_tolerance]
        worst_ids = (
            primary.sort_values(["f1", "record_id"], ascending=[True, True])[
                "record_id"
            ]
            .head(failure_plot_count)
            .tolist()
        )
        by_id = {item.record.record_id: item for item in benchmarks}
        for record_id in worst_ids:
            item = by_id[record_id]
            plot_peak_overlay(
                record_id=record_id,
                ecg=item.record.ecg,
                sampling_rate_hz=item.record.sampling_rate_hz,
                reference_samples=item.record.reference_peak_samples,
                detected_samples=item.detected_peak_samples,
                false_negative_indices=item.primary_match.false_negative_reference_indices,
                false_positive_indices=item.primary_match.false_positive_detected_indices,
                output_path=Path(failure_plot_dir) / f"{record_id}_peak_overlay.png",
                window_seconds=failure_window_seconds,
            )

    return all_metrics
