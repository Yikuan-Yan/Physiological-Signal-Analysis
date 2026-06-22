from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def choose_failure_window(
    reference_samples: np.ndarray,
    detected_samples: np.ndarray,
    false_negative_indices: np.ndarray,
    false_positive_indices: np.ndarray,
    *,
    signal_length: int,
    sampling_rate_hz: float,
    window_seconds: float,
) -> tuple[int, int]:
    window_samples = max(1, int(round(window_seconds * sampling_rate_hz)))
    error_samples: list[int] = []
    if false_negative_indices.size:
        error_samples.extend(reference_samples[false_negative_indices].tolist())
    if false_positive_indices.size:
        error_samples.extend(detected_samples[false_positive_indices].tolist())
    center = int(np.median(error_samples)) if error_samples else signal_length // 2
    start = max(0, center - window_samples // 2)
    stop = min(signal_length, start + window_samples)
    start = max(0, stop - window_samples)
    return start, stop


def plot_peak_overlay(
    *,
    record_id: str,
    ecg: np.ndarray,
    sampling_rate_hz: float,
    reference_samples: np.ndarray,
    detected_samples: np.ndarray,
    false_negative_indices: np.ndarray,
    false_positive_indices: np.ndarray,
    output_path: str | Path,
    window_seconds: float,
) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    start, stop = choose_failure_window(
        reference_samples,
        detected_samples,
        false_negative_indices,
        false_positive_indices,
        signal_length=int(ecg.shape[0]),
        sampling_rate_hz=sampling_rate_hz,
        window_seconds=window_seconds,
    )

    segment = ecg[start:stop]
    time_s = np.arange(start, stop, dtype=np.float64) / sampling_rate_hz
    ref_in_window = reference_samples[
        (reference_samples >= start) & (reference_samples < stop)
    ]
    det_in_window = detected_samples[
        (detected_samples >= start) & (detected_samples < stop)
    ]

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(time_s, segment, color="black", linewidth=0.8, label="ECG")
    if ref_in_window.size:
        ax.scatter(
            ref_in_window / sampling_rate_hz,
            ecg[ref_in_window],
            s=24,
            color="#0072B2",
            marker="o",
            label="reference",
        )
    if det_in_window.size:
        ax.scatter(
            det_in_window / sampling_rate_hz,
            ecg[det_in_window],
            s=20,
            color="#D55E00",
            marker="x",
            label="detected",
        )
    ax.set_title(f"{record_id}: ECG peak overlay")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("ECG")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
