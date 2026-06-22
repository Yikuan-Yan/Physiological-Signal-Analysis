from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import signal


@dataclass(frozen=True)
class FrequencyHrv:
    n_intervals: int
    duration_seconds: float
    welch_lf_power_ms2: float
    welch_hf_power_ms2: float
    welch_lf_hf_ratio: float
    lomb_lf_power_norm: float
    lomb_hf_power_norm: float
    lomb_lf_hf_ratio: float
    lf_hf_ratio_delta: float


def _finite_sorted_series(
    time_s: np.ndarray,
    interval_ms: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    t = np.asarray(time_s, dtype=np.float64)
    y = np.asarray(interval_ms, dtype=np.float64)
    if t.ndim != 1 or y.ndim != 1:
        raise ValueError("time_s and interval_ms must be one-dimensional")
    if t.shape != y.shape:
        raise ValueError("time_s and interval_ms must have the same shape")
    mask = np.isfinite(t) & np.isfinite(y)
    t = t[mask]
    y = y[mask]
    if t.size > 1:
        order = np.argsort(t)
        t = t[order]
        y = y[order]
        keep = np.concatenate([[True], np.diff(t) > 0])
        t = t[keep]
        y = y[keep]
    return t, y


def _nan_frequency_hrv(n_intervals: int, duration_seconds: float) -> FrequencyHrv:
    return FrequencyHrv(
        n_intervals=n_intervals,
        duration_seconds=duration_seconds,
        welch_lf_power_ms2=np.nan,
        welch_hf_power_ms2=np.nan,
        welch_lf_hf_ratio=np.nan,
        lomb_lf_power_norm=np.nan,
        lomb_hf_power_norm=np.nan,
        lomb_lf_hf_ratio=np.nan,
        lf_hf_ratio_delta=np.nan,
    )


def band_power(frequency_hz: np.ndarray, power: np.ndarray, band: tuple[float, float]) -> float:
    lo, hi = band
    mask = (frequency_hz >= lo) & (frequency_hz < hi)
    if int(mask.sum()) < 2:
        return float("nan")
    return float(np.trapezoid(power[mask], frequency_hz[mask]))


def _ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if np.isfinite(denominator) and denominator > 0 else np.nan


def welch_band_powers(
    time_s: np.ndarray,
    interval_ms: np.ndarray,
    *,
    interpolation_hz: float,
    nperseg_seconds: float,
    lf_band: tuple[float, float],
    hf_band: tuple[float, float],
) -> tuple[float, float, float]:
    t, y = _finite_sorted_series(time_s, interval_ms)
    if t.size < 3 or interpolation_hz <= 0:
        return np.nan, np.nan, np.nan

    dt = 1.0 / interpolation_hz
    uniform_t = np.arange(t[0], t[-1] + dt / 2.0, dt, dtype=np.float64)
    if uniform_t.size < 4:
        return np.nan, np.nan, np.nan
    uniform_y = np.interp(uniform_t, t, y)
    nperseg = max(4, int(round(nperseg_seconds * interpolation_hz)))
    nperseg = min(nperseg, uniform_y.size)
    noverlap = min(nperseg // 2, max(0, nperseg - 1))
    frequency, psd = signal.welch(
        uniform_y,
        fs=interpolation_hz,
        nperseg=nperseg,
        noverlap=noverlap,
        detrend="constant",
        scaling="density",
    )
    lf_power = band_power(frequency, psd, lf_band)
    hf_power = band_power(frequency, psd, hf_band)
    return lf_power, hf_power, _ratio(lf_power, hf_power)


def lomb_band_powers(
    time_s: np.ndarray,
    interval_ms: np.ndarray,
    *,
    frequency_grid_hz: np.ndarray,
    lf_band: tuple[float, float],
    hf_band: tuple[float, float],
) -> tuple[float, float, float]:
    t, y = _finite_sorted_series(time_s, interval_ms)
    grid = np.asarray(frequency_grid_hz, dtype=np.float64)
    if t.size < 3 or grid.ndim != 1 or grid.size < 3:
        return np.nan, np.nan, np.nan
    t = t - t[0]
    y = y - np.mean(y)
    angular = 2.0 * np.pi * grid
    power = signal.lombscargle(
        t,
        y,
        angular,
        normalize=True,
        floating_mean=True,
    )
    lf_power = band_power(grid, power, lf_band)
    hf_power = band_power(grid, power, hf_band)
    return lf_power, hf_power, _ratio(lf_power, hf_power)


def frequency_domain_hrv(
    time_s: np.ndarray,
    interval_ms: np.ndarray,
    *,
    interpolation_hz: float,
    nperseg_seconds: float,
    lf_band: tuple[float, float],
    hf_band: tuple[float, float],
    lomb_frequency_grid_hz: np.ndarray,
    min_nn_intervals: int,
) -> FrequencyHrv:
    t, y = _finite_sorted_series(time_s, interval_ms)
    duration = float(t[-1] - t[0]) if t.size >= 2 else 0.0
    if y.size < min_nn_intervals:
        return _nan_frequency_hrv(int(y.size), duration)

    welch_lf, welch_hf, welch_ratio = welch_band_powers(
        t,
        y,
        interpolation_hz=interpolation_hz,
        nperseg_seconds=nperseg_seconds,
        lf_band=lf_band,
        hf_band=hf_band,
    )
    lomb_lf, lomb_hf, lomb_ratio = lomb_band_powers(
        t,
        y,
        frequency_grid_hz=lomb_frequency_grid_hz,
        lf_band=lf_band,
        hf_band=hf_band,
    )
    return FrequencyHrv(
        n_intervals=int(y.size),
        duration_seconds=duration,
        welch_lf_power_ms2=welch_lf,
        welch_hf_power_ms2=welch_hf,
        welch_lf_hf_ratio=welch_ratio,
        lomb_lf_power_norm=lomb_lf,
        lomb_hf_power_norm=lomb_hf,
        lomb_lf_hf_ratio=lomb_ratio,
        lf_hf_ratio_delta=lomb_ratio - welch_ratio
        if np.isfinite(lomb_ratio) and np.isfinite(welch_ratio)
        else np.nan,
    )


def frequency_to_dict(metrics: FrequencyHrv) -> dict[str, float | int]:
    return {
        "freq_n_intervals": metrics.n_intervals,
        "freq_duration_seconds": metrics.duration_seconds,
        "welch_lf_power_ms2": metrics.welch_lf_power_ms2,
        "welch_hf_power_ms2": metrics.welch_hf_power_ms2,
        "welch_lf_hf_ratio": metrics.welch_lf_hf_ratio,
        "lomb_lf_power_norm": metrics.lomb_lf_power_norm,
        "lomb_hf_power_norm": metrics.lomb_hf_power_norm,
        "lomb_lf_hf_ratio": metrics.lomb_lf_hf_ratio,
        "lf_hf_ratio_delta": metrics.lf_hf_ratio_delta,
    }
