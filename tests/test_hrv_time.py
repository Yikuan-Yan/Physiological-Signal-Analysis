import math

import numpy as np

from physio_signal_lab.features.hrv_time import flagged_interpolate, time_domain_hrv


def test_time_domain_hrv_known_sequence():
    intervals = np.array([1000.0, 1020.0, 980.0, 1000.0])
    metrics = time_domain_hrv(intervals)
    assert metrics.n_intervals == 4
    assert math.isclose(metrics.mean_nn_ms, 1000.0)
    assert math.isclose(metrics.sdnn_ms, 16.32993161855452)
    assert math.isclose(metrics.rmssd_ms, math.sqrt((20**2 + 40**2 + 20**2) / 3))
    assert math.isclose(metrics.pnn50, 0.0)


def test_flagged_interpolate_replaces_only_flagged_values():
    intervals = np.array([1000.0, 500.0, 1100.0, 900.0])
    repaired = flagged_interpolate(intervals, np.array([False, True, False, False]))
    assert repaired.tolist() == [1000.0, 1050.0, 1100.0, 900.0]


def test_flagged_interpolate_all_invalid_returns_empty():
    intervals = np.array([500.0, 500.0])
    repaired = flagged_interpolate(intervals, np.array([True, True]))
    assert repaired.size == 0


def test_flagged_interpolate_treats_nan_as_invalid_in_original_index_space():
    intervals = np.array([1000.0, np.nan, 1020.0])
    repaired = flagged_interpolate(intervals, np.array([False, True, False]))
    assert repaired.tolist() == [1000.0, 1010.0, 1020.0]
