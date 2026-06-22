from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class PeakMatchResult:
    tolerance_samples: int
    matched_reference_indices: np.ndarray
    matched_detected_indices: np.ndarray
    false_negative_reference_indices: np.ndarray
    false_positive_detected_indices: np.ndarray
    timing_error_samples: np.ndarray


@dataclass(frozen=True)
class PeakMetrics:
    tolerance_ms: float
    tolerance_samples: int
    n_reference: int
    n_detected: int
    true_positives: int
    false_positives: int
    false_negatives: int
    sensitivity: float
    positive_predictive_value: float
    f1: float
    median_timing_error_ms: float
    median_abs_timing_error_ms: float
    iqr_abs_timing_error_ms: float
    p95_abs_timing_error_ms: float


def tolerance_to_samples(tolerance_ms: float, sampling_rate_hz: float) -> int:
    if tolerance_ms < 0:
        raise ValueError("tolerance_ms must be non-negative")
    if sampling_rate_hz <= 0:
        raise ValueError("sampling_rate_hz must be positive")
    return int(math.ceil((tolerance_ms / 1000.0) * sampling_rate_hz))


def _sorted_int_array(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=np.int64)
    if array.ndim != 1:
        raise ValueError("Peak sample arrays must be one-dimensional")
    if array.size > 1 and np.any(np.diff(array) < 0):
        array = np.sort(array)
    return array


def match_peaks(
    reference_samples: np.ndarray,
    detected_samples: np.ndarray,
    *,
    tolerance_samples: int,
) -> PeakMatchResult:
    if tolerance_samples < 0:
        raise ValueError("tolerance_samples must be non-negative")
    reference = _sorted_int_array(reference_samples)
    detected = _sorted_int_array(detected_samples)

    matched_reference: list[int] = []
    matched_detected: list[int] = []
    false_negative: list[int] = []
    false_positive: list[int] = []
    timing_errors: list[int] = []

    i = 0
    j = 0
    while i < reference.size and j < detected.size:
        diff = int(detected[j] - reference[i])
        if abs(diff) <= tolerance_samples:
            matched_reference.append(i)
            matched_detected.append(j)
            timing_errors.append(diff)
            i += 1
            j += 1
        elif detected[j] < reference[i] - tolerance_samples:
            false_positive.append(j)
            j += 1
        else:
            false_negative.append(i)
            i += 1

    if i < reference.size:
        false_negative.extend(range(i, reference.size))
    if j < detected.size:
        false_positive.extend(range(j, detected.size))

    return PeakMatchResult(
        tolerance_samples=tolerance_samples,
        matched_reference_indices=np.asarray(matched_reference, dtype=np.int64),
        matched_detected_indices=np.asarray(matched_detected, dtype=np.int64),
        false_negative_reference_indices=np.asarray(false_negative, dtype=np.int64),
        false_positive_detected_indices=np.asarray(false_positive, dtype=np.int64),
        timing_error_samples=np.asarray(timing_errors, dtype=np.int64),
    )


def _safe_divide(numerator: int, denominator: int) -> float:
    return float(numerator / denominator) if denominator else float("nan")


def peak_metrics(
    reference_samples: np.ndarray,
    detected_samples: np.ndarray,
    *,
    sampling_rate_hz: float,
    tolerance_ms: float,
) -> tuple[PeakMetrics, PeakMatchResult]:
    tolerance_samples = tolerance_to_samples(tolerance_ms, sampling_rate_hz)
    match = match_peaks(
        reference_samples,
        detected_samples,
        tolerance_samples=tolerance_samples,
    )

    tp = int(match.matched_reference_indices.size)
    fp = int(match.false_positive_detected_indices.size)
    fn = int(match.false_negative_reference_indices.size)
    sensitivity = _safe_divide(tp, tp + fn)
    ppv = _safe_divide(tp, tp + fp)
    f1 = (
        2.0 * sensitivity * ppv / (sensitivity + ppv)
        if np.isfinite(sensitivity + ppv) and (sensitivity + ppv) > 0
        else float("nan")
    )

    timing_ms = match.timing_error_samples.astype(np.float64) * 1000.0 / sampling_rate_hz
    abs_timing_ms = np.abs(timing_ms)
    if timing_ms.size:
        median_timing_error_ms = float(np.median(timing_ms))
        median_abs_timing_error_ms = float(np.median(abs_timing_ms))
        q25, q75 = np.percentile(abs_timing_ms, [25, 75])
        iqr_abs_timing_error_ms = float(q75 - q25)
        p95_abs_timing_error_ms = float(np.percentile(abs_timing_ms, 95))
    else:
        median_timing_error_ms = float("nan")
        median_abs_timing_error_ms = float("nan")
        iqr_abs_timing_error_ms = float("nan")
        p95_abs_timing_error_ms = float("nan")

    return (
        PeakMetrics(
            tolerance_ms=float(tolerance_ms),
            tolerance_samples=tolerance_samples,
            n_reference=int(np.asarray(reference_samples).size),
            n_detected=int(np.asarray(detected_samples).size),
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            sensitivity=sensitivity,
            positive_predictive_value=ppv,
            f1=f1,
            median_timing_error_ms=median_timing_error_ms,
            median_abs_timing_error_ms=median_abs_timing_error_ms,
            iqr_abs_timing_error_ms=iqr_abs_timing_error_ms,
            p95_abs_timing_error_ms=p95_abs_timing_error_ms,
        ),
        match,
    )
