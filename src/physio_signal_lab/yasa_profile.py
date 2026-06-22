from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import os
import subprocess
import sys
import time

import pandas as pd

from physio_signal_lab.evaluation.sleep_staging import paths_from_selection
from physio_signal_lab.io.sleep_edf import validate_sleep_edf_manifest
from physio_signal_lab.sleep_outputs import (
    clean_output_prefix,
    scoped_sleep_edf_output_path,
    scoped_sleep_edf_report_path,
)


@dataclass(frozen=True)
class YasaProfileOutputs:
    profile_csv: Path
    report_md: Path


def _worker_command(
    *,
    record_id: str,
    psg_path: Path,
    eeg_name: str,
    eog_name: str | None,
    emg_name: str | None,
    crop_seconds: float | None,
    predictions_out: Path | None = None,
    probabilities_out: Path | None = None,
) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "physio_signal_lab.yasa_profile_worker",
        "--record-id",
        record_id,
        "--psg-path",
        str(psg_path),
        "--eeg-name",
        eeg_name,
    ]
    if eog_name:
        command.extend(["--eog-name", eog_name])
    if emg_name:
        command.extend(["--emg-name", emg_name])
    if crop_seconds is not None:
        command.extend(["--crop-seconds", str(crop_seconds)])
    if predictions_out is not None:
        command.extend(["--predictions-out", str(predictions_out)])
    if probabilities_out is not None:
        command.extend(["--probabilities-out", str(probabilities_out)])
    return command


def _process_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip()
    return value.strip()


def run_yasa_worker_subprocess(
    *,
    record_id: str,
    psg_path: Path,
    eeg_name: str,
    eog_name: str | None,
    emg_name: str | None,
    crop_seconds: float | None,
    timeout_seconds: float,
    predictions_out: Path | None = None,
    probabilities_out: Path | None = None,
) -> dict[str, Any]:
    command = _worker_command(
        record_id=record_id,
        psg_path=psg_path,
        eeg_name=eeg_name,
        eog_name=eog_name,
        emg_name=emg_name,
        crop_seconds=crop_seconds,
        predictions_out=predictions_out,
        probabilities_out=probabilities_out,
    )
    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("MKL_NUM_THREADS", "1")
    env.setdefault("NUMEXPR_NUM_THREADS", "1")
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "record_id": record_id,
            "status": "timeout",
            "crop_seconds": crop_seconds,
            "timeout_seconds": timeout_seconds,
            "wall_seconds": round(time.perf_counter() - started, 6),
            "error": f"worker timed out after {timeout_seconds} s",
            "stdout": _process_text(exc.stdout),
            "stderr": _process_text(exc.stderr),
        }

    stdout = _process_text(completed.stdout)
    row: dict[str, Any]
    try:
        row = json.loads(stdout.splitlines()[-1]) if stdout else {}
    except json.JSONDecodeError:
        row = {
            "record_id": record_id,
            "status": "error",
            "error": "worker did not emit JSON",
        }
    row.setdefault("record_id", record_id)
    row.setdefault("status", "completed" if completed.returncode == 0 else "error")
    row["crop_seconds"] = crop_seconds
    row["timeout_seconds"] = timeout_seconds
    row["wall_seconds"] = round(time.perf_counter() - started, 6)
    row["returncode"] = completed.returncode
    row["stdout"] = stdout
    row["stderr"] = _process_text(completed.stderr)
    return row


def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = [
        "| " + " | ".join(str(row.get(column, "")) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, sep, *body])


def build_yasa_profile_report(profile: pd.DataFrame) -> str:
    rows = []
    for _, row in profile.iterrows():
        rows.append(
            {
                "record": row.get("record_id", ""),
                "status": row.get("status", ""),
                "crop_s": row.get("crop_seconds", ""),
                "timeout_s": row.get("timeout_seconds", ""),
                "wall_s": f"{float(row.get('wall_seconds', 0.0)):.3f}",
                "epochs": row.get("predicted_epochs", ""),
                "total_s": row.get("total_seconds", ""),
            }
        )

    completed = int((profile["status"] == "completed").sum()) if "status" in profile else 0
    timed_out = int((profile["status"] == "timeout").sum()) if "status" in profile else 0
    errored = int((profile["status"] == "error").sum()) if "status" in profile else 0
    lines = [
        "# Sleep-EDF YASA Runtime Profile",
        "",
        "## Scope",
        "",
        (
            "This report profiles YASA runtime in a child process with a hard timeout. "
            "It is a runtime gate, not a sleep-stage benchmark."
        ),
        "",
        "No sleep-quality, clinical, diagnostic, or YASA performance claims are made here.",
        "",
        "## Summary",
        "",
        f"- completed: {completed}",
        f"- timed out: {timed_out}",
        f"- errored: {errored}",
        "",
        _markdown_table(
            rows,
            ["record", "status", "crop_s", "timeout_s", "wall_s", "epochs", "total_s"],
        ),
        "",
        "## Decision Rule",
        "",
        (
            "YASA metrics may be committed only after a profiling run completes and the "
            "subsequent `--include-yasa` benchmark writes aligned predictions for all included pilot epochs."
        ),
        "",
    ]
    return "\n".join(lines)


def run_yasa_profile(
    config: dict[str, Any],
    *,
    records: list[str],
    crop_seconds: float | None,
    timeout_seconds: float,
    output_prefix: str | None = None,
) -> YasaProfileOutputs:
    outputs = config["outputs"]
    validation = validate_sleep_edf_manifest(outputs["manifest_csv"], records=records)
    if not bool(validation["checksum_ok"].all()):
        raise ValueError("Sleep-EDF raw files are missing or checksum validation failed")

    selection = pd.read_csv(outputs["selection_csv"])
    paths = paths_from_selection(selection, records)
    channel_config = config["channels"]["staging"]
    rows = [
        run_yasa_worker_subprocess(
            record_id=path_set.record_id,
            psg_path=path_set.psg_path,
            eeg_name=channel_config["eeg_name"],
            eog_name=channel_config.get("eog_name"),
            emg_name=channel_config.get("emg_name"),
            crop_seconds=crop_seconds,
            timeout_seconds=timeout_seconds,
        )
        for path_set in paths
    ]

    profile = pd.DataFrame(rows)
    if output_prefix is None:
        profile_out = Path(outputs["yasa_profile_csv"])
        report_out = Path(outputs["yasa_profile_report_md"])
    else:
        output_prefix = clean_output_prefix(output_prefix)
        profile_out = scoped_sleep_edf_output_path(output_prefix, "yasa_runtime_profile.csv")
        report_out = scoped_sleep_edf_report_path(output_prefix, "yasa_profile.md")
    profile_out.parent.mkdir(parents=True, exist_ok=True)
    profile.to_csv(profile_out, index=False)

    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(build_yasa_profile_report(profile), encoding="utf-8")
    return YasaProfileOutputs(profile_csv=profile_out, report_md=report_out)
