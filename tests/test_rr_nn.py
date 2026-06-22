from pathlib import Path

import pytest

from physio_signal_lab.features.rr_nn import (
    build_reference_intervals,
    reference_intervals_for_record,
    window_metrics,
)


ROOT = Path("data/raw/fantasia/1.0.0")


pytestmark = pytest.mark.skipif(
    not ROOT.exists(),
    reason="Fantasia raw data is not available in this environment",
)


def test_reference_intervals_mark_non_normal_symbols():
    intervals = reference_intervals_for_record(
        "f1y01",
        ROOT,
        normal_symbols={"N"},
        valid_rr_min_ms=300,
        valid_rr_max_ms=2000,
    )
    assert len(intervals) == 8709
    assert intervals["is_nn"].sum() < len(intervals)
    excluded = intervals[~intervals["is_nn"]]
    assert set(excluded["exclusion_reason"]) == {"non_normal_endpoint"}


def test_window_metrics_for_pilot_records():
    intervals = build_reference_intervals(
        ["f1y01", "f1o01"],
        ROOT,
        normal_symbols={"N"},
        valid_rr_min_ms=300,
        valid_rr_max_ms=2000,
    )
    metrics = window_metrics(intervals, window_seconds=300)
    assert set(metrics["record_id"]) == {"f1y01", "f1o01"}
    complete = metrics[(metrics["window_end_s"] <= 7200)]
    assert complete["nn_intervals"].min() > 100
    assert metrics["valid_fraction"].between(0, 1).all()
    assert metrics["rmssd_ms"].notna().all()
