from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from physio_signal_lab.features.hrv_time import hrv_to_dict, time_domain_hrv
from physio_signal_lab.io.fantasia import load_record


def reference_intervals_for_record(
    record_id: str,
    raw_dir: str | Path,
    *,
    normal_symbols: set[str],
    valid_rr_min_ms: float,
    valid_rr_max_ms: float,
) -> pd.DataFrame:
    record = load_record(record_id, raw_dir)
    samples = record.reference_peak_samples
    symbols = np.asarray(record.annotation_symbols, dtype=object)
    if samples.size != symbols.size:
        raise ValueError(f"Annotation sample/symbol length mismatch: {record_id}")
    if samples.size < 2:
        raise ValueError(f"Record has fewer than two annotations: {record_id}")

    start_samples = samples[:-1]
    end_samples = samples[1:]
    start_symbols = symbols[:-1]
    end_symbols = symbols[1:]
    rr_ms = (end_samples - start_samples).astype(np.float64) * 1000.0
    rr_ms /= record.sampling_rate_hz
    normal_endpoint = np.isin(start_symbols, list(normal_symbols)) & np.isin(
        end_symbols, list(normal_symbols)
    )
    valid_duration = (rr_ms >= valid_rr_min_ms) & (rr_ms <= valid_rr_max_ms)
    is_nn = normal_endpoint & valid_duration

    exclusion_reason = np.full(samples.size - 1, "", dtype=object)
    exclusion_reason[~normal_endpoint] = "non_normal_endpoint"
    exclusion_reason[normal_endpoint & ~valid_duration] = "invalid_rr_duration"

    return pd.DataFrame(
        {
            "record_id": record.record_id,
            "cohort": record.cohort,
            "age": record.age,
            "sex": record.sex,
            "interval_index": np.arange(samples.size - 1, dtype=np.int64),
            "start_sample": start_samples,
            "end_sample": end_samples,
            "start_time_s": start_samples / record.sampling_rate_hz,
            "end_time_s": end_samples / record.sampling_rate_hz,
            "rr_ms": rr_ms,
            "start_symbol": start_symbols,
            "end_symbol": end_symbols,
            "is_nn": is_nn,
            "exclusion_reason": exclusion_reason,
            "correction_flag": "none",
            "provenance": "fantasia_ecg_reference_annotation",
        }
    )


def build_reference_intervals(
    record_ids: list[str],
    raw_dir: str | Path,
    *,
    normal_symbols: set[str],
    valid_rr_min_ms: float,
    valid_rr_max_ms: float,
) -> pd.DataFrame:
    frames = [
        reference_intervals_for_record(
            record_id,
            raw_dir,
            normal_symbols=normal_symbols,
            valid_rr_min_ms=valid_rr_min_ms,
            valid_rr_max_ms=valid_rr_max_ms,
        )
        for record_id in record_ids
    ]
    return pd.concat(frames, ignore_index=True)


def window_metrics(intervals: pd.DataFrame, *, window_seconds: float) -> pd.DataFrame:
    rows = []
    for record_id, group in intervals.groupby("record_id", sort=True):
        window_index = np.floor(group["end_time_s"].to_numpy() / window_seconds).astype(int)
        group = group.assign(window_index=window_index)
        for idx, window in group.groupby("window_index", sort=True):
            total = int(len(window))
            nn = window[window["is_nn"]]
            metrics = time_domain_hrv(nn["rr_ms"].to_numpy(dtype=np.float64))
            start_s = float(idx * window_seconds)
            row = {
                "record_id": record_id,
                "cohort": window["cohort"].iloc[0],
                "age": int(window["age"].iloc[0]),
                "sex": window["sex"].iloc[0],
                "window_index": int(idx),
                "window_start_s": start_s,
                "window_end_s": start_s + window_seconds,
                "total_intervals": total,
                "nn_intervals": int(len(nn)),
                "excluded_intervals": total - int(len(nn)),
                "valid_fraction": int(len(nn)) / total if total else np.nan,
            }
            row.update(hrv_to_dict(metrics))
            rows.append(row)
    return pd.DataFrame(rows)
