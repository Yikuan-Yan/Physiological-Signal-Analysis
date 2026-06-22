from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b

import numpy as np
import pandas as pd

from physio_signal_lab.features.hrv_time import (
    flagged_interpolate,
    hrv_to_dict,
    time_domain_hrv,
)


METRIC_NAMES = ("mean_nn_ms", "sdnn_ms", "rmssd_ms", "pnn50")


@dataclass(frozen=True)
class CorruptedIntervals:
    intervals_ms: np.ndarray
    invalid_mask: np.ndarray
    injected_events: int


def stable_seed(base_seed: int, *parts: object) -> int:
    h = blake2b(digest_size=8)
    h.update(str(base_seed).encode("utf-8"))
    for part in parts:
        h.update(b"|")
        h.update(str(part).encode("utf-8"))
    return int.from_bytes(h.digest(), byteorder="little", signed=False) % (2**32)


def _event_count(n_intervals: int, rate: float) -> int:
    if n_intervals <= 0:
        return 0
    if rate <= 0:
        return 0
    return max(1, int(round(n_intervals * rate)))


def _non_overlapping_starts(
    rng: np.random.Generator,
    *,
    max_start: int,
    count: int,
) -> list[int]:
    candidates = rng.permutation(np.arange(max_start + 1, dtype=np.int64))
    selected: list[int] = []
    blocked: set[int] = set()
    for candidate in candidates:
        c = int(candidate)
        if c in blocked:
            continue
        selected.append(c)
        blocked.update({c - 1, c, c + 1})
        if len(selected) >= count:
            break
    return sorted(selected)


def inject_missed_beat(
    intervals_ms: np.ndarray,
    *,
    rate: float,
    rng: np.random.Generator,
) -> CorruptedIntervals:
    intervals = np.asarray(intervals_ms, dtype=np.float64)
    count = min(_event_count(intervals.size, rate), max(0, intervals.size - 1))
    starts = _non_overlapping_starts(rng, max_start=intervals.size - 2, count=count)
    start_set = set(starts)
    corrupted: list[float] = []
    invalid: list[bool] = []
    i = 0
    while i < intervals.size:
        if i in start_set:
            corrupted.append(float(intervals[i] + intervals[i + 1]))
            invalid.append(True)
            i += 2
        else:
            corrupted.append(float(intervals[i]))
            invalid.append(False)
            i += 1
    return CorruptedIntervals(
        np.asarray(corrupted, dtype=np.float64),
        np.asarray(invalid, dtype=bool),
        len(starts),
    )


def inject_spurious_extra_beat(
    intervals_ms: np.ndarray,
    *,
    rate: float,
    rng: np.random.Generator,
) -> CorruptedIntervals:
    intervals = np.asarray(intervals_ms, dtype=np.float64)
    count = min(_event_count(intervals.size, rate), intervals.size)
    selected = set(rng.choice(intervals.size, size=count, replace=False).tolist())
    corrupted: list[float] = []
    invalid: list[bool] = []
    for i, interval in enumerate(intervals):
        if i in selected:
            corrupted.extend([float(interval / 2.0), float(interval / 2.0)])
            invalid.extend([True, True])
        else:
            corrupted.append(float(interval))
            invalid.append(False)
    return CorruptedIntervals(
        np.asarray(corrupted, dtype=np.float64),
        np.asarray(invalid, dtype=bool),
        len(selected),
    )


def inject_timestamp_jitter(
    intervals_ms: np.ndarray,
    *,
    rate: float,
    jitter_ms: float,
    rng: np.random.Generator,
) -> CorruptedIntervals:
    intervals = np.asarray(intervals_ms, dtype=np.float64).copy()
    if intervals.size < 2:
        return CorruptedIntervals(intervals, np.zeros(intervals.size, dtype=bool), 0)
    count = min(_event_count(intervals.size, rate), intervals.size - 1)
    boundaries = rng.choice(np.arange(1, intervals.size), size=count, replace=False)
    invalid = np.zeros(intervals.size, dtype=bool)
    for boundary in boundaries:
        delta = float(rng.uniform(-jitter_ms, jitter_ms))
        left = boundary - 1
        right = boundary
        limit = 0.45 * min(intervals[left], intervals[right])
        delta = float(np.clip(delta, -limit, limit))
        intervals[left] += delta
        intervals[right] -= delta
        invalid[[left, right]] = True
    return CorruptedIntervals(intervals, invalid, int(boundaries.size))


def inject_ectopic_short_long(
    intervals_ms: np.ndarray,
    *,
    rate: float,
    shift_fraction: float,
    rng: np.random.Generator,
) -> CorruptedIntervals:
    intervals = np.asarray(intervals_ms, dtype=np.float64).copy()
    if intervals.size < 2:
        return CorruptedIntervals(intervals, np.zeros(intervals.size, dtype=bool), 0)
    count = min(_event_count(intervals.size, rate), intervals.size - 1)
    boundaries = rng.choice(np.arange(1, intervals.size), size=count, replace=False)
    invalid = np.zeros(intervals.size, dtype=bool)
    for boundary in boundaries:
        left = boundary - 1
        right = boundary
        shift = shift_fraction * min(intervals[left], intervals[right])
        intervals[left] -= shift
        intervals[right] += shift
        invalid[[left, right]] = True
    return CorruptedIntervals(intervals, invalid, int(boundaries.size))


def inject_artifact(
    intervals_ms: np.ndarray,
    *,
    artifact_type: str,
    rate: float,
    jitter_ms: float,
    ectopic_shift_fraction: float,
    rng: np.random.Generator,
) -> CorruptedIntervals:
    if artifact_type == "missed_beat":
        return inject_missed_beat(intervals_ms, rate=rate, rng=rng)
    if artifact_type == "spurious_extra_beat":
        return inject_spurious_extra_beat(intervals_ms, rate=rate, rng=rng)
    if artifact_type == "timestamp_jitter":
        return inject_timestamp_jitter(
            intervals_ms,
            rate=rate,
            jitter_ms=jitter_ms,
            rng=rng,
        )
    if artifact_type == "ectopic_short_long":
        return inject_ectopic_short_long(
            intervals_ms,
            rate=rate,
            shift_fraction=ectopic_shift_fraction,
            rng=rng,
        )
    raise ValueError(f"Unsupported artifact_type: {artifact_type}")


def apply_strategy(corrupted: CorruptedIntervals, *, strategy: str) -> np.ndarray:
    if strategy == "no_correction":
        return corrupted.intervals_ms
    if strategy == "delete_flagged_intervals":
        return corrupted.intervals_ms[~corrupted.invalid_mask]
    if strategy == "interpolate_flagged_intervals":
        return flagged_interpolate(corrupted.intervals_ms, corrupted.invalid_mask)
    raise ValueError(f"Unsupported strategy: {strategy}")


def _error_columns(
    reference: dict[str, float | int],
    observed: dict[str, float | int],
) -> dict[str, float]:
    out: dict[str, float] = {}
    for metric in METRIC_NAMES:
        ref = float(reference[f"ref_{metric}"])
        obs = float(observed[f"test_{metric}"])
        abs_error = obs - ref
        out[f"abs_error_{metric}"] = abs_error
        out[f"rel_error_{metric}"] = (
            abs_error / ref if np.isfinite(ref) and abs(ref) > 0 else np.nan
        )
    return out


def artifact_experiment(
    intervals: pd.DataFrame,
    *,
    artifact_types: list[str],
    rates: list[float],
    repeats: int,
    strategies: list[str],
    seed: int,
    jitter_ms: float,
    ectopic_shift_fraction: float,
) -> pd.DataFrame:
    rows = []
    for record_id, group in intervals.groupby("record_id", sort=True):
        nn = group[group["is_nn"]]["rr_ms"].to_numpy(dtype=np.float64)
        reference_metrics = hrv_to_dict(time_domain_hrv(nn), prefix="ref_")
        meta = group.iloc[0]
        for artifact_type in artifact_types:
            for rate in rates:
                for repeat in range(repeats):
                    scenario_seed = stable_seed(seed, record_id, artifact_type, rate, repeat)
                    rng = np.random.default_rng(scenario_seed)
                    corrupted = inject_artifact(
                        nn,
                        artifact_type=artifact_type,
                        rate=float(rate),
                        jitter_ms=jitter_ms,
                        ectopic_shift_fraction=ectopic_shift_fraction,
                        rng=rng,
                    )
                    for strategy in strategies:
                        test_intervals = apply_strategy(corrupted, strategy=strategy)
                        observed_metrics = hrv_to_dict(
                            time_domain_hrv(test_intervals),
                            prefix="test_",
                        )
                        row = {
                            "record_id": record_id,
                            "cohort": meta["cohort"],
                            "age": int(meta["age"]),
                            "sex": meta["sex"],
                            "artifact_type": artifact_type,
                            "artifact_rate": float(rate),
                            "repeat": repeat,
                            "strategy": strategy,
                            "seed": scenario_seed,
                            "injected_events": corrupted.injected_events,
                            "flagged_intervals": int(corrupted.invalid_mask.sum()),
                        }
                        row.update(reference_metrics)
                        row.update(observed_metrics)
                        row.update(_error_columns(reference_metrics, observed_metrics))
                        rows.append(row)
    return pd.DataFrame(rows)


def summarize_artifact_experiment(results: pd.DataFrame) -> pd.DataFrame:
    error_columns = [
        column for column in results.columns if column.startswith("rel_error_")
    ]
    grouped = results.groupby(
        ["artifact_type", "artifact_rate", "strategy"],
        sort=True,
    )
    summary = grouped[error_columns].agg(["median", "mean", "std"]).reset_index()
    summary.columns = [
        "_".join(part for part in column if part)
        if isinstance(column, tuple)
        else column
        for column in summary.columns
    ]
    return summary
