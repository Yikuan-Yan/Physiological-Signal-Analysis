import math

import numpy as np
import pandas as pd

from physio_signal_lab.evaluation.artifacts import (
    apply_strategy,
    artifact_experiment,
    inject_ectopic_short_long,
    inject_missed_beat,
    inject_spurious_extra_beat,
    inject_timestamp_jitter,
    summarize_artifact_experiment,
)


def test_inject_missed_beat_merges_intervals_and_flags():
    intervals = np.array([1000.0, 1000.0, 1000.0, 1000.0])
    corrupted = inject_missed_beat(
        intervals,
        rate=0.25,
        rng=np.random.default_rng(1),
    )
    assert corrupted.injected_events == 1
    assert corrupted.intervals_ms.size == 3
    assert corrupted.invalid_mask.sum() == 1
    assert math.isclose(corrupted.intervals_ms[corrupted.invalid_mask][0], 2000.0)
    assert math.isclose(corrupted.intervals_ms.sum(), intervals.sum())
    assert math.isclose(corrupted.beat_times_ms[-1], intervals.sum())


def test_inject_spurious_extra_beat_splits_interval_and_flags():
    intervals = np.array([1000.0, 1000.0, 1000.0, 1000.0])
    corrupted = inject_spurious_extra_beat(
        intervals,
        rate=0.25,
        rng=np.random.default_rng(1),
    )
    assert corrupted.injected_events == 1
    assert corrupted.intervals_ms.size == 5
    assert corrupted.invalid_mask.sum() == 2
    assert set(corrupted.intervals_ms[corrupted.invalid_mask]) == {500.0}
    assert math.isclose(corrupted.intervals_ms.sum(), intervals.sum())
    assert math.isclose(corrupted.beat_times_ms[-1], intervals.sum())


def test_delete_and_interpolate_strategies():
    corrupted = inject_timestamp_jitter(
        np.array([1000.0, 1000.0, 1000.0]),
        rate=0.34,
        jitter_ms=50,
        rng=np.random.default_rng(3),
    )
    deleted = apply_strategy(corrupted, strategy="delete_flagged_intervals")
    interpolated = apply_strategy(corrupted, strategy="interpolate_flagged_intervals")
    assert deleted.size < corrupted.intervals_ms.size
    assert interpolated.size == corrupted.intervals_ms.size
    assert np.isfinite(interpolated).all()
    assert math.isclose(interpolated.sum(), corrupted.reference_span_ms)


def test_artifact_injections_preserve_recording_span():
    intervals = np.array([1000.0, 1010.0, 990.0, 1000.0, 1005.0])
    for injector, kwargs in [
        (inject_missed_beat, {}),
        (inject_spurious_extra_beat, {}),
        (inject_timestamp_jitter, {"jitter_ms": 50.0}),
        (inject_ectopic_short_long, {"shift_fraction": 0.3}),
    ]:
        corrupted = injector(
            intervals,
            rate=0.4,
            rng=np.random.default_rng(7),
            **kwargs,
        )
        assert np.all(corrupted.intervals_ms > 0)
        assert math.isclose(corrupted.intervals_ms.sum(), intervals.sum())
        repaired = apply_strategy(corrupted, strategy="interpolate_flagged_intervals")
        assert np.all(repaired > 0)
        assert math.isclose(repaired.sum(), intervals.sum())


def test_artifact_experiment_outputs_expected_rows():
    intervals = pd.DataFrame(
        {
            "record_id": ["r1"] * 5,
            "cohort": ["young"] * 5,
            "age": [25] * 5,
            "sex": ["F"] * 5,
            "rr_ms": [1000.0, 1010.0, 990.0, 1000.0, 1005.0],
            "is_nn": [True] * 5,
        }
    )
    results = artifact_experiment(
        intervals,
        artifact_types=["missed_beat", "timestamp_jitter"],
        rates=[0.2],
        repeats=2,
        strategies=["no_correction", "delete_flagged_intervals"],
        seed=42,
        jitter_ms=50,
        ectopic_shift_fraction=0.3,
    )
    assert len(results) == 8
    assert {"ref_rmssd_ms", "test_rmssd_ms", "rel_error_rmssd_ms"} <= set(
        results.columns
    )
    summary = summarize_artifact_experiment(results)
    assert len(summary) == 4
