from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class TimeDomainHrv:
    n_intervals: int
    mean_nn_ms: float
    sdnn_ms: float
    rmssd_ms: float
    pnn50: float


def finite_1d(values: np.ndarray, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    return array[np.isfinite(array)]


def time_domain_hrv(interval_ms: np.ndarray) -> TimeDomainHrv:
    nn = finite_1d(interval_ms, name="interval_ms")
    n = int(nn.size)
    if n == 0:
        return TimeDomainHrv(n, np.nan, np.nan, np.nan, np.nan)

    mean_nn = float(np.mean(nn))
    sdnn = float(np.std(nn, ddof=1)) if n >= 2 else np.nan
    diff = np.diff(nn)
    if diff.size:
        rmssd = float(np.sqrt(np.mean(diff * diff)))
        pnn50 = float(np.mean(np.abs(diff) > 50.0))
    else:
        rmssd = np.nan
        pnn50 = np.nan
    return TimeDomainHrv(n, mean_nn, sdnn, rmssd, pnn50)


def hrv_to_dict(metrics: TimeDomainHrv, *, prefix: str = "") -> dict[str, float | int]:
    return {
        f"{prefix}n_intervals": metrics.n_intervals,
        f"{prefix}mean_nn_ms": metrics.mean_nn_ms,
        f"{prefix}sdnn_ms": metrics.sdnn_ms,
        f"{prefix}rmssd_ms": metrics.rmssd_ms,
        f"{prefix}pnn50": metrics.pnn50,
    }


def flagged_interpolate(interval_ms: np.ndarray, invalid_mask: np.ndarray) -> np.ndarray:
    intervals = finite_1d(interval_ms, name="interval_ms")
    mask = np.asarray(invalid_mask, dtype=bool)
    if intervals.shape != mask.shape:
        raise ValueError("interval_ms and invalid_mask must have the same shape")
    if not mask.any():
        return intervals.copy()
    if mask.all():
        return np.array([], dtype=np.float64)

    repaired = intervals.copy()
    x = np.arange(intervals.size, dtype=np.float64)
    repaired[mask] = np.interp(x[mask], x[~mask], intervals[~mask])
    return repaired
