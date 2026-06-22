from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import re

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from sklearn.metrics import precision_recall_fscore_support

from physio_signal_lab.features.sleep_stages import map_rk_label


SLEEP_STAGE_DESCRIPTION_RE = re.compile(r"^Sleep stage (?P<label>[W1234RM?])$")
STAGE_ORDER = ("WAKE", "N1", "N2", "N3", "REM")


@dataclass(frozen=True)
class SleepEdfPaths:
    record_id: str
    psg_path: Path
    hypnogram_path: Path


def parse_sleep_stage_description(description: str) -> str:
    match = SLEEP_STAGE_DESCRIPTION_RE.match(str(description))
    if match is None:
        raise ValueError(f"Unsupported Sleep-EDF annotation description: {description!r}")
    return match.group("label")


def expand_stage_annotations(
    annotations: pd.DataFrame,
    *,
    record_id: str,
    signal_duration_seconds: float,
    epoch_seconds: float,
) -> pd.DataFrame:
    if signal_duration_seconds <= 0:
        raise ValueError("signal_duration_seconds must be positive")
    if epoch_seconds <= 0:
        raise ValueError("epoch_seconds must be positive")

    rows: list[dict[str, Any]] = []
    epoch_index = 0
    for _, annotation in annotations.sort_values("onset").iterrows():
        onset = float(annotation["onset"])
        duration = float(annotation["duration"])
        if duration <= 0 or onset >= signal_duration_seconds:
            continue
        stop = min(onset + duration, signal_duration_seconds)
        n_epochs = int(np.floor((stop - onset) / epoch_seconds + 1e-9))
        if n_epochs <= 0:
            continue
        rk_label = parse_sleep_stage_description(str(annotation["description"]))
        mapped = map_rk_label(rk_label)
        for offset in range(n_epochs):
            epoch_onset = onset + offset * epoch_seconds
            rows.append(
                {
                    "record_id": record_id,
                    "epoch_index": epoch_index,
                    "onset_seconds": epoch_onset,
                    "rk_label": rk_label,
                    "mapped_stage": mapped if mapped is not None else "",
                    "included": mapped is not None,
                }
            )
            epoch_index += 1

    labels = pd.DataFrame(rows)
    if labels.empty:
        raise ValueError(f"No epoch labels expanded for {record_id}")
    expected = int(np.floor(signal_duration_seconds / epoch_seconds + 1e-9))
    if int(labels["epoch_index"].max()) + 1 > expected:
        raise ValueError(f"Expanded labels exceed signal duration for {record_id}")
    return labels


def read_sleep_edf_epoch_labels(
    paths: SleepEdfPaths,
    *,
    epoch_seconds: float,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    try:
        import mne
    except ImportError as exc:
        raise RuntimeError(
            "MNE is required for Sleep-EDF EDF/hypnogram reading. "
            "Install with `uv sync --extra sleep --extra dev`."
        ) from exc

    raw = mne.io.read_raw_edf(paths.psg_path, preload=False, verbose="ERROR")
    annotations = mne.read_annotations(paths.hypnogram_path)
    annotation_frame = pd.DataFrame(
        {
            "onset": annotations.onset,
            "duration": annotations.duration,
            "description": annotations.description.astype(str),
        }
    )
    duration_seconds = float(raw.n_times / raw.info["sfreq"])
    labels = expand_stage_annotations(
        annotation_frame,
        record_id=paths.record_id,
        signal_duration_seconds=duration_seconds,
        epoch_seconds=epoch_seconds,
    )
    metadata = {
        "record_id": paths.record_id,
        "sampling_rate_hz": float(raw.info["sfreq"]),
        "duration_seconds": duration_seconds,
        "raw_epoch_count": int(np.floor(duration_seconds / epoch_seconds + 1e-9)),
        "expanded_epoch_count": int(len(labels)),
        "included_epoch_count": int(labels["included"].sum()),
        "excluded_epoch_count": int((~labels["included"]).sum()),
        "channel_names": ";".join(raw.ch_names),
    }
    return labels, metadata


def paths_from_selection(selection: pd.DataFrame, records: list[str]) -> list[SleepEdfPaths]:
    wanted = set(records)
    selected = selection[selection["recording_id"].isin(wanted)].copy()
    if selected.empty:
        raise ValueError("No selected Sleep-EDF records found")
    return [
        SleepEdfPaths(
            record_id=str(row["recording_id"]),
            psg_path=Path(str(row["psg_local_path"])),
            hypnogram_path=Path(str(row["hypnogram_local_path"])),
        )
        for _, row in selected.iterrows()
    ]


def majority_stage_predictions(labels: pd.DataFrame) -> pd.DataFrame:
    included = labels[labels["included"]].copy()
    if included.empty:
        raise ValueError("No included sleep-stage epochs available")
    rows: list[pd.DataFrame] = []
    for record_id, group in included.groupby("record_id", sort=True):
        counts = group["mapped_stage"].value_counts()
        majority_stage = str(counts.sort_values(ascending=False).index[0])
        predicted = group.copy()
        predicted["predicted_stage"] = majority_stage
        rows.append(predicted)
    return pd.concat(rows, ignore_index=True)


def _metrics_row(
    *,
    record_id: str,
    y_true: list[str],
    y_pred: list[str],
    model_name: str,
) -> dict[str, Any]:
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=list(STAGE_ORDER),
        zero_division=0,
    )
    present = support > 0
    balanced_accuracy = float(np.mean(recall[present])) if np.any(present) else float("nan")
    row: dict[str, Any] = {
        "record_id": record_id,
        "model": model_name,
        "epoch_count": len(y_true),
        "majority_reference_stage": pd.Series(y_true).mode().sort_values().iloc[0],
        "predicted_majority_stage": pd.Series(y_pred).mode().sort_values().iloc[0],
        "accuracy": float(np.mean(np.asarray(y_true) == np.asarray(y_pred))),
        "balanced_accuracy": balanced_accuracy,
        "cohen_kappa": float(cohen_kappa_score(y_true, y_pred, labels=list(STAGE_ORDER))),
        "macro_f1": float(np.mean(f1)),
    }
    for stage, p, r, f, n in zip(STAGE_ORDER, precision, recall, f1, support):
        key = stage.lower()
        row[f"{key}_precision"] = float(p)
        row[f"{key}_recall"] = float(r)
        row[f"{key}_f1"] = float(f)
        row[f"{key}_support"] = int(n)
    return row


def sleep_stage_metrics(predictions: pd.DataFrame, *, model_name: str) -> pd.DataFrame:
    rows = []
    for record_id, group in predictions.groupby("record_id", sort=True):
        rows.append(
            _metrics_row(
                record_id=str(record_id),
                y_true=group["mapped_stage"].astype(str).tolist(),
                y_pred=group["predicted_stage"].astype(str).tolist(),
                model_name=model_name,
            )
        )
    rows.append(
        _metrics_row(
            record_id="all",
            y_true=predictions["mapped_stage"].astype(str).tolist(),
            y_pred=predictions["predicted_stage"].astype(str).tolist(),
            model_name=model_name,
        )
    )
    return pd.DataFrame(rows)


def stage_summary(labels: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for record_id, group in labels.groupby("record_id", sort=True):
        included = group[group["included"]]
        counts = included["mapped_stage"].value_counts().to_dict()
        row = {
            "record_id": record_id,
            "total_epochs": int(len(group)),
            "included_epochs": int(len(included)),
            "excluded_epochs": int((~group["included"]).sum()),
        }
        for stage in STAGE_ORDER:
            row[f"{stage.lower()}_epochs"] = int(counts.get(stage, 0))
        rows.append(row)
    summary = pd.DataFrame(rows)
    return summary.merge(metadata, on="record_id", how="left")
