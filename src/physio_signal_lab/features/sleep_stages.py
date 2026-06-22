from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


R_AND_K_TO_STAGE = {
    "W": "WAKE",
    "1": "N1",
    "2": "N2",
    "3": "N3",
    "4": "N3",
    "R": "REM",
}

EXCLUDED_R_AND_K_LABELS = {"M", "?"}


@dataclass(frozen=True)
class AlignmentSummary:
    signal_duration_seconds: float
    hypnogram_duration_seconds: float
    duration_delta_seconds: float
    aligned: bool


def map_rk_label(label: str) -> str | None:
    normalized = label.strip()
    if normalized in EXCLUDED_R_AND_K_LABELS:
        return None
    if normalized not in R_AND_K_TO_STAGE:
        raise ValueError(f"Unsupported R&K sleep stage label: {label!r}")
    return R_AND_K_TO_STAGE[normalized]


def map_rk_labels(labels: Iterable[str]) -> list[str | None]:
    return [map_rk_label(label) for label in labels]


def count_mapped_stages(labels: Iterable[str]) -> dict[str, int]:
    counts = {stage: 0 for stage in ("WAKE", "N1", "N2", "N3", "REM")}
    counts["excluded"] = 0
    for mapped in map_rk_labels(labels):
        if mapped is None:
            counts["excluded"] += 1
        else:
            counts[mapped] += 1
    return counts


def validate_epoch_alignment(
    *,
    signal_duration_seconds: float,
    epoch_count: int,
    epoch_seconds: float = 30.0,
    tolerance_seconds: float = 30.0,
) -> AlignmentSummary:
    if signal_duration_seconds <= 0:
        raise ValueError("signal_duration_seconds must be positive")
    if epoch_count <= 0:
        raise ValueError("epoch_count must be positive")
    if epoch_seconds <= 0:
        raise ValueError("epoch_seconds must be positive")
    if tolerance_seconds < 0:
        raise ValueError("tolerance_seconds must be non-negative")

    hypnogram_duration_seconds = float(epoch_count) * float(epoch_seconds)
    duration_delta_seconds = abs(float(signal_duration_seconds) - hypnogram_duration_seconds)
    return AlignmentSummary(
        signal_duration_seconds=float(signal_duration_seconds),
        hypnogram_duration_seconds=hypnogram_duration_seconds,
        duration_delta_seconds=duration_delta_seconds,
        aligned=duration_delta_seconds <= float(tolerance_seconds),
    )
