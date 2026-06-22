import pandas as pd

from physio_signal_lab.features.uncertainty import (
    bootstrap_uncertainty,
    record_summary,
)


def test_record_summary_and_bootstrap_uncertainty_are_deterministic():
    windows = pd.DataFrame(
        {
            "record_id": ["a", "a", "b", "b"],
            "cohort": ["young", "young", "old", "old"],
            "age": [25, 25, 75, 75],
            "sex": ["F", "F", "M", "M"],
            "window_index": [0, 1, 0, 1],
            "mean_nn_ms": [1000.0, 1020.0, 900.0, 920.0],
            "sdnn_ms": [20.0, 22.0, 30.0, 32.0],
            "rmssd_ms": [10.0, 12.0, 40.0, 42.0],
            "pnn50": [0.0, 0.1, 0.2, 0.3],
        }
    )
    frequency = pd.DataFrame(
        {
            "record_id": ["a", "a", "b", "b"],
            "cohort": ["young", "young", "old", "old"],
            "age": [25, 25, 75, 75],
            "sex": ["F", "F", "M", "M"],
            "window_index": [0, 1, 0, 1],
            "welch_lf_power_ms2": [1.0, 1.2, 2.0, 2.2],
            "welch_hf_power_ms2": [0.5, 0.6, 1.0, 1.1],
            "welch_lf_hf_ratio": [2.0, 2.0, 2.0, 2.0],
            "lomb_lf_hf_ratio": [1.8, 1.9, 2.1, 2.2],
            "lf_hf_ratio_delta": [-0.2, -0.1, 0.1, 0.2],
        }
    )
    summary = record_summary(windows, frequency)
    assert len(summary) == 2
    assert set(summary["record_id"]) == {"a", "b"}
    first = bootstrap_uncertainty(summary, seed=7, iterations=100, ci=0.95)
    second = bootstrap_uncertainty(summary, seed=7, iterations=100, ci=0.95)
    assert first.equals(second)
    assert set(first["group"]) == {"all", "old", "young"}
