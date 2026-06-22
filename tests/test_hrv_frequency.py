import math

import numpy as np

from physio_signal_lab.features.hrv_frequency import frequency_domain_hrv


def _grid():
    return np.linspace(1 / 300, 0.5, 1024)


def test_frequency_domain_detects_lf_dominant_signal():
    time_s = np.arange(0, 300, 1.0)
    rr_ms = 1000.0 + 50.0 * np.sin(2 * np.pi * 0.10 * time_s)
    metrics = frequency_domain_hrv(
        time_s,
        rr_ms,
        interpolation_hz=4.0,
        nperseg_seconds=64.0,
        lf_band=(0.04, 0.15),
        hf_band=(0.15, 0.40),
        lomb_frequency_grid_hz=_grid(),
        min_nn_intervals=30,
    )
    assert metrics.welch_lf_power_ms2 > metrics.welch_hf_power_ms2
    assert metrics.lomb_lf_power_norm > metrics.lomb_hf_power_norm
    assert metrics.welch_lf_hf_ratio > 1


def test_frequency_domain_detects_hf_dominant_signal():
    time_s = np.arange(0, 300, 1.0)
    rr_ms = 1000.0 + 50.0 * np.sin(2 * np.pi * 0.25 * time_s)
    metrics = frequency_domain_hrv(
        time_s,
        rr_ms,
        interpolation_hz=4.0,
        nperseg_seconds=64.0,
        lf_band=(0.04, 0.15),
        hf_band=(0.15, 0.40),
        lomb_frequency_grid_hz=_grid(),
        min_nn_intervals=30,
    )
    assert metrics.welch_hf_power_ms2 > metrics.welch_lf_power_ms2
    assert metrics.lomb_hf_power_norm > metrics.lomb_lf_power_norm
    assert metrics.welch_lf_hf_ratio < 1


def test_frequency_domain_short_window_returns_nan_metrics():
    metrics = frequency_domain_hrv(
        np.array([0.0, 1.0, 2.0]),
        np.array([1000.0, 1005.0, 995.0]),
        interpolation_hz=4.0,
        nperseg_seconds=64.0,
        lf_band=(0.04, 0.15),
        hf_band=(0.15, 0.40),
        lomb_frequency_grid_hz=_grid(),
        min_nn_intervals=30,
    )
    assert metrics.n_intervals == 3
    assert math.isnan(metrics.welch_lf_power_ms2)
    assert math.isnan(metrics.lomb_lf_hf_ratio)
