from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from physio_signal_lab.io.sleep_edf import (
    build_sleep_cassette_selection,
    fetch_edf_filenames,
    write_sleep_edf_manifest,
)


@dataclass(frozen=True)
class SleepEdfPreflightOutputs:
    selection_csv: Path
    manifest_csv: Path
    report_md: Path


def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = [
        "| " + " | ".join(str(row.get(column, "")) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, sep, *body])


def build_sleep_edf_preflight_report(
    config: dict[str, Any],
    selection: pd.DataFrame,
    *,
    access_date: str,
) -> str:
    label_mapping = config["sleep_stages"]["label_mapping"]
    excluded = config["sleep_stages"]["excluded_labels"]
    pilot = selection[selection["role"] == "pilot"]
    benchmark = selection[selection["role"] == "benchmark"]
    subject_list = ", ".join(str(subject) for subject in selection["subject_id"].tolist())
    rows = [
        {
            "R&K label": label,
            "mapped class": mapped,
            "status": "included",
        }
        for label, mapped in label_mapping.items()
    ]
    rows.extend(
        {
            "R&K label": label,
            "mapped class": "excluded",
            "status": "excluded",
        }
        for label in excluded
    )

    lines = [
        "# Sleep-EDF Preflight Report",
        "",
        "## Scope",
        "",
        (
            "This preflight freezes the Sleep-EDF/YASA expansion protocol after the "
            "Fantasia HRV core gate. It selects the benchmark records and records the "
            "label mapping before any model results are inspected."
        ),
        "",
        "This report does not evaluate sleep quality, diagnose sleep disorders, or make event-detector accuracy claims.",
        "",
        "## Dataset",
        "",
        f"- Dataset: {config['dataset']['name']} v{config['dataset']['version']}.",
        f"- DOI: {config['dataset']['doi']}.",
        f"- License: {config['dataset']['license']}.",
        f"- Access date: {access_date}.",
        f"- Source index: {config['dataset']['cassette_index_url']}.",
        "- Cohort included: Sleep Cassette only.",
        "- Cohorts excluded: Sleep Telemetry, to avoid mixing home healthy recordings with hospital/temazepam protocol recordings.",
        "",
        "## Frozen Selection",
        "",
        f"- Selection rule: {config['selection']['rule']}.",
        f"- Participants: {len(selection)} total; {len(pilot)} pilot and {len(benchmark)} benchmark-only.",
        f"- Subject IDs: {subject_list}.",
        "- Recording per participant: first available paired PSG/Hypnogram night.",
        "",
        _markdown_table(
            selection[
                [
                    "subject_id",
                    "night",
                    "role",
                    "recording_id",
                    "psg_filename",
                    "hypnogram_filename",
                ]
            ].to_dict("records"),
            ["subject_id", "night", "role", "recording_id", "psg_filename", "hypnogram_filename"],
        ),
        "",
        "## Label Mapping",
        "",
        _markdown_table(rows, ["R&K label", "mapped class", "status"]),
        "",
        "Movement and unscored epochs are excluded from the primary five-class benchmark.",
        "",
        "## YASA Branch Rules",
        "",
        "- Staging branch: pass raw MNE object into YASA SleepStaging without project-side z-score or filter.",
        f"- Staging channels: EEG `{config['channels']['staging']['eeg_name']}`, "
        f"EOG `{config['channels']['staging']['eog_name']}`, "
        f"EMG `{config['channels']['staging']['emg_name']}`.",
        "- Spectral branch and event branch must be implemented separately from staging preprocessing.",
        f"- Channel limitation: {config['channels']['limitation']}",
        "",
        "## Acceptance Checks",
        "",
        "- 20 Sleep Cassette participants are frozen before model execution.",
        "- Each selected participant has one PSG file and one matching Hypnogram file.",
        "- R&K label mapping is explicit and unit-tested.",
        "- Baseline/model benchmark must report majority-stage baseline, macro-F1, balanced accuracy, Cohen's kappa, per-stage metrics, and participant-level uncertainty.",
        "- Spindle and slow-wave detections remain exploratory summaries because Sleep-EDF has no event-level expert annotation.",
        "",
        "## Next Implementation Step",
        "",
        (
            "Download the selected PSG/Hypnogram pairs into `data/raw/sleep-edfx/1.0.0`, "
            "then implement a benchmark command that reads EDF files, aligns 30 s hypnogram "
            "epochs, runs the majority baseline and YASA model, and writes participant-level metrics."
        ),
        "",
    ]
    return "\n".join(lines)


def run_sleep_edf_preflight(
    config: dict[str, Any],
    *,
    filenames: list[str] | None = None,
) -> SleepEdfPreflightOutputs:
    dataset = config["dataset"]
    outputs = config["outputs"]
    access_date = datetime.now(timezone.utc).date().isoformat()
    if filenames is None:
        filenames = fetch_edf_filenames(dataset["cassette_index_url"])

    selection = build_sleep_cassette_selection(
        filenames,
        benchmark_subjects=[int(subject) for subject in config["selection"]["benchmark_subjects"]],
        pilot_subjects=[int(subject) for subject in config["selection"]["pilot_subjects"]],
        source_base_url=dataset["source_base_url"],
        raw_dir=dataset["raw_dir"],
    )

    selection_csv = Path(outputs["selection_csv"])
    selection_csv.parent.mkdir(parents=True, exist_ok=True)
    selection.to_csv(selection_csv, index=False)

    manifest_csv = write_sleep_edf_manifest(
        selection,
        output_path=outputs["manifest_csv"],
        dataset=dataset["name"],
        version=dataset["version"],
        doi=dataset["doi"],
        license_name=dataset["license"],
        access_date=access_date,
    )

    report_md = Path(outputs["preflight_report_md"])
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text(
        build_sleep_edf_preflight_report(config, selection, access_date=access_date),
        encoding="utf-8",
    )
    return SleepEdfPreflightOutputs(
        selection_csv=selection_csv,
        manifest_csv=manifest_csv,
        report_md=report_md,
    )
