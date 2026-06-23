import math

import numpy as np

from physio_signal_lab.evaluation.peak_matching import (
    match_peaks,
    peak_metrics,
    tolerance_to_samples,
)


def test_tolerance_to_samples_ceil_boundary():
    assert tolerance_to_samples(50, 250) == 13
    assert tolerance_to_samples(100, 250) == 25
    assert tolerance_to_samples(50, 333) == 17


def test_match_peaks_perfect_match():
    reference = np.array([100, 250, 400])
    detected = np.array([100, 250, 400])
    result = match_peaks(reference, detected, tolerance_samples=0)
    assert result.matched_reference_indices.tolist() == [0, 1, 2]
    assert result.matched_detected_indices.tolist() == [0, 1, 2]
    assert result.false_negative_reference_indices.size == 0
    assert result.false_positive_detected_indices.size == 0
    assert result.timing_error_samples.tolist() == [0, 0, 0]


def test_match_peaks_extra_and_missing_beats():
    reference = np.array([100, 250, 400, 550])
    detected = np.array([100, 252, 300, 552])
    result = match_peaks(reference, detected, tolerance_samples=5)
    assert result.matched_reference_indices.tolist() == [0, 1, 3]
    assert result.matched_detected_indices.tolist() == [0, 1, 3]
    assert result.false_negative_reference_indices.tolist() == [2]
    assert result.false_positive_detected_indices.tolist() == [2]
    assert result.timing_error_samples.tolist() == [0, 2, 2]


def test_match_peaks_minimizes_timing_error_after_maximizing_matches():
    reference = np.array([0, 8])
    detected = np.array([5])
    result = match_peaks(reference, detected, tolerance_samples=5)

    assert result.matched_reference_indices.tolist() == [1]
    assert result.matched_detected_indices.tolist() == [0]
    assert result.false_negative_reference_indices.tolist() == [0]
    assert result.timing_error_samples.tolist() == [-3]


def test_peak_metrics_values():
    reference = np.array([100, 250, 400, 550])
    detected = np.array([100, 252, 300, 552])
    metrics, _ = peak_metrics(
        reference,
        detected,
        sampling_rate_hz=250,
        tolerance_ms=20,
    )
    assert metrics.true_positives == 3
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 1
    assert math.isclose(metrics.sensitivity, 0.75)
    assert math.isclose(metrics.positive_predictive_value, 0.75)
    assert math.isclose(metrics.f1, 0.75)
    assert math.isclose(metrics.median_abs_timing_error_ms, 8.0)
