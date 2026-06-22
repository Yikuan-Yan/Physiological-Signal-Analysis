from __future__ import annotations

import numpy as np
import pandas as pd


DEFAULT_METRICS = [
    "mean_nn_ms",
    "sdnn_ms",
    "rmssd_ms",
    "pnn50",
    "welch_lf_power_ms2",
    "welch_hf_power_ms2",
    "welch_lf_hf_ratio",
    "lomb_lf_hf_ratio",
    "lf_hf_ratio_delta",
]


def record_summary(
    window_metrics: pd.DataFrame,
    frequency_metrics: pd.DataFrame,
    *,
    metrics: list[str] | None = None,
) -> pd.DataFrame:
    metrics = metrics or DEFAULT_METRICS
    merged = window_metrics.merge(
        frequency_metrics,
        on=["record_id", "cohort", "age", "sex", "window_index"],
        how="left",
    )
    rows = []
    for record_id, group in merged.groupby("record_id", sort=True):
        row = {
            "record_id": record_id,
            "cohort": group["cohort"].iloc[0],
            "age": int(group["age"].iloc[0]),
            "sex": group["sex"].iloc[0],
            "window_count": int(len(group)),
        }
        for metric in metrics:
            values = group[metric].to_numpy(dtype=np.float64)
            finite = values[np.isfinite(values)]
            row[f"median_{metric}"] = float(np.median(finite)) if finite.size else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def bootstrap_ci(
    values: np.ndarray,
    *,
    rng: np.random.Generator,
    iterations: int,
    ci: float,
) -> tuple[float, float, float, int]:
    data = np.asarray(values, dtype=np.float64)
    data = data[np.isfinite(data)]
    n = int(data.size)
    if n == 0:
        return np.nan, np.nan, np.nan, 0
    point = float(np.median(data))
    samples = rng.choice(data, size=(iterations, n), replace=True)
    estimates = np.median(samples, axis=1)
    alpha = 1.0 - ci
    low, high = np.quantile(estimates, [alpha / 2.0, 1.0 - alpha / 2.0])
    return point, float(low), float(high), n


def bootstrap_uncertainty(
    record_metrics: pd.DataFrame,
    *,
    seed: int,
    iterations: int,
    ci: float,
    metrics: list[str] | None = None,
) -> pd.DataFrame:
    metrics = metrics or DEFAULT_METRICS
    rows = []
    groups = [("all", record_metrics)]
    groups.extend(
        (str(cohort), group)
        for cohort, group in record_metrics.groupby("cohort", sort=True)
    )
    for group_name, group in groups:
        for metric in metrics:
            column = f"median_{metric}"
            rng = np.random.default_rng(
                seed + sum(ord(char) for char in f"{group_name}:{metric}")
            )
            point, low, high, n = bootstrap_ci(
                group[column].to_numpy(dtype=np.float64),
                rng=rng,
                iterations=iterations,
                ci=ci,
            )
            rows.append(
                {
                    "group": group_name,
                    "metric": metric,
                    "record_count": n,
                    "estimator": "median_of_record_window_medians",
                    "point_estimate": point,
                    "ci_low": low,
                    "ci_high": high,
                    "ci": ci,
                    "bootstrap_iterations": iterations,
                }
            )
    return pd.DataFrame(rows)
