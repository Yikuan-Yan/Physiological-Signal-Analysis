from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.optimize import linear_sum_assignment


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

    points = sorted(
        [(int(value), "reference", int(index)) for index, value in enumerate(reference)]
        + [(int(value), "detected", int(index)) for index, value in enumerate(detected)]
    )
    components: list[list[tuple[int, str, int]]] = []
    current: list[tuple[int, str, int]] = []
    current_end: int | None = None
    for point in points:
        value = point[0]
        if current_end is None or value > current_end:
            if current:
                components.append(current)
            current = [point]
            current_end = value + tolerance_samples
        else:
            current.append(point)
            current_end = max(current_end, value + tolerance_samples)
    if current:
        components.append(current)

    for component in components:
        ref_indices = [index for _, kind, index in component if kind == "reference"]
        det_indices = [index for _, kind, index in component if kind == "detected"]
        if not ref_indices or not det_indices:
            continue
        r = len(ref_indices)
        d = len(det_indices)
        if r == 1 and d == 1:
            ref_index = ref_indices[0]
            det_index = det_indices[0]
            if abs(int(detected[det_index] - reference[ref_index])) <= tolerance_samples:
                matched_reference.append(ref_index)
                matched_detected.append(det_index)
            continue
        if r == 1:
            ref_index = ref_indices[0]
            best_det = min(
                det_indices,
                key=lambda det_index: abs(int(detected[det_index] - reference[ref_index])),
            )
            if abs(int(detected[best_det] - reference[ref_index])) <= tolerance_samples:
                matched_reference.append(ref_index)
                matched_detected.append(best_det)
            continue
        if d == 1:
            det_index = det_indices[0]
            best_ref = min(
                ref_indices,
                key=lambda ref_index: abs(int(detected[det_index] - reference[ref_index])),
            )
            if abs(int(detected[det_index] - reference[best_ref])) <= tolerance_samples:
                matched_reference.append(best_ref)
                matched_detected.append(det_index)
            continue
        size = r + d
        match_priority = float((tolerance_samples + 1) * (size + 1))
        blocked = match_priority * 4.0
        cost = np.zeros((size, size), dtype=np.float64)
        cost[:r, :d] = blocked
        cost[:r, d:] = match_priority
        cost[r:, :d] = match_priority
        for local_r, ref_index in enumerate(ref_indices):
            for local_d, det_index in enumerate(det_indices):
                error = abs(int(detected[det_index] - reference[ref_index]))
                if error <= tolerance_samples:
                    cost[local_r, local_d] = float(error)
        row_ind, col_ind = linear_sum_assignment(cost)
        for row, col in zip(row_ind, col_ind):
            if row < r and col < d and cost[row, col] <= tolerance_samples:
                matched_reference.append(ref_indices[row])
                matched_detected.append(det_indices[col])

    matched_pairs = sorted(zip(matched_reference, matched_detected))
    matched_reference = [ref_index for ref_index, _ in matched_pairs]
    matched_detected = [det_index for _, det_index in matched_pairs]
    matched_reference_set = set(matched_reference)
    matched_detected_set = set(matched_detected)
    false_negative = [
        index for index in range(reference.size) if index not in matched_reference_set
    ]
    false_positive = [
        index for index in range(detected.size) if index not in matched_detected_set
    ]
    timing_errors = [
        int(detected[det_index] - reference[ref_index])
        for ref_index, det_index in matched_pairs
    ]

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
