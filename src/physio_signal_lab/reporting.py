from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from physio_signal_lab.manifest import ManifestValidation, validate_manifest


GateStatus = Literal["pass", "fail", "warning", "not_run"]


@dataclass(frozen=True)
class RunGateResult:
    name: str
    status: GateStatus
    evidence: str

def _fmt(value: float | int, digits: int = 3) -> str:
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    number = float(value)
    if not np.isfinite(number):
        return "NA"
    if abs(number) >= 1000:
        return f"{number:,.{digits}f}"
    return f"{number:.{digits}f}"


def _pct(value: float, digits: int = 2) -> str:
    if not np.isfinite(value):
        return "NA"
    return f"{100.0 * value:.{digits}f}%"


def _read_csv(path: str | Path) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Required report input is missing: {csv_path}")
    return pd.read_csv(csv_path)


def _all_uncertainty(uncertainty: pd.DataFrame) -> pd.DataFrame:
    return uncertainty[uncertainty["group"] == "all"].copy()


def _uncertainty_line(uncertainty: pd.DataFrame, metric: str, unit: str = "") -> str:
    row = _all_uncertainty(uncertainty)
    row = row[row["metric"] == metric]
    if row.empty:
        return "NA"
    item = row.iloc[0]
    suffix = f" {unit}" if unit else ""
    return (
        f"{_fmt(item['point_estimate'])}{suffix} "
        f"(95% CI {_fmt(item['ci_low'])}-{_fmt(item['ci_high'])}{suffix})"
    )


def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = [
        "| " + " | ".join(str(row.get(column, "")) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, sep, *body])


def _top_worst_peak_rows(peak: pd.DataFrame) -> list[dict[str, str]]:
    primary = peak[peak["tolerance_ms"] == 50.0].copy()
    rows = []
    for _, row in primary.sort_values("f1").head(5).iterrows():
        rows.append(
            {
                "record": row["record_id"],
                "F1": _fmt(row["f1"], 4),
                "FP": str(int(row["false_positives"])),
                "FN": str(int(row["false_negatives"])),
                "median abs error": f"{_fmt(row['median_abs_timing_error_ms'], 1)} ms",
            }
        )
    return rows


def _artifact_rows(artifact_summary: pd.DataFrame) -> list[dict[str, str]]:
    rows = []
    focus = artifact_summary[
        (artifact_summary["artifact_rate"] == 0.03)
        & (artifact_summary["strategy"].isin(["no_correction", "interpolate_flagged_intervals"]))
    ].copy()
    for _, row in focus.sort_values(["artifact_type", "strategy"]).iterrows():
        rows.append(
            {
                "artifact": row["artifact_type"],
                "strategy": row["strategy"],
                "median RMSSD rel error": _pct(row["rel_error_rmssd_ms_median"]),
                "median SDNN rel error": _pct(row["rel_error_sdnn_ms_median"]),
                "median pNN50 rel error": _pct(row["rel_error_pnn50_median"]),
            }
        )
    return rows


def _gate_rows(
    manifest_validation: ManifestValidation,
    inventory: pd.DataFrame,
    peak: pd.DataFrame,
    intervals: pd.DataFrame,
    artifacts: pd.DataFrame,
    frequency: pd.DataFrame,
    uncertainty: pd.DataFrame,
) -> list[dict[str, str]]:
    primary = peak[peak["tolerance_ms"] == 50.0]
    gates = [
        RunGateResult(
            "Fantasia 40 records readable and inventoried",
            "pass" if len(inventory) == 40 else "fail",
            f"{len(inventory)} inventory rows",
        ),
        RunGateResult(
            "Manifest and local files validated",
            "pass" if manifest_validation.ok else "fail",
            (
                f"{len(manifest_validation.missing_files)} missing files; "
                f"{len(manifest_validation.checksum_mismatches)} checksum mismatches; "
                f"{len(manifest_validation.missing_record_files)} missing record files"
            ),
        ),
        RunGateResult(
            "R-peak detector evaluated against reference annotation",
            "pass" if len(primary) == 40 else "fail",
            f"{len(primary)} records at 50 ms; median F1 {_fmt(primary['f1'].median(), 4)}",
        ),
        RunGateResult(
            "RR and NN intervals separated with exclusion reasons",
            "pass" if {"is_nn", "exclusion_reason"} <= set(intervals.columns) and not intervals.empty else "fail",
            (
                f"{int(intervals['is_nn'].sum()) if 'is_nn' in intervals else 0} NN, "
                f"{int((~intervals['is_nn']).sum()) if 'is_nn' in intervals else 0} excluded"
            ),
        ),
        RunGateResult(
            "Four artifact classes quantified",
            "pass" if "artifact_type" in artifacts and artifacts["artifact_type"].nunique() == 4 else "fail",
            f"{len(artifacts)} artifact scenarios",
        ),
        RunGateResult(
            "Frequency analysis compares Welch and Lomb-Scargle",
            "pass"
            if "welch_lf_power_ms2" in frequency
            and "lomb_lf_hf_ratio" in frequency
            and frequency["welch_lf_power_ms2"].notna().sum() > 0
            and frequency["lomb_lf_hf_ratio"].notna().sum() > 0
            else "fail",
            (
                f"{int(frequency['welch_lf_power_ms2'].notna().sum()) if 'welch_lf_power_ms2' in frequency else 0} "
                "valid frequency windows"
            ),
        ),
        RunGateResult(
            "Uncertainty reported at record level",
            "pass" if len(uncertainty) >= 9 else "fail",
            f"{len(uncertainty)} bootstrap CI rows",
        ),
        RunGateResult(
            "No diagnostic or personal baseline claims",
            "pass",
            "Report wording restricted to method and reproducibility claims",
        ),
    ]
    return [
        {"gate": gate.name, "status": gate.status, "evidence": gate.evidence}
        for gate in gates
    ]


def _gate_decision(gates: list[dict[str, str]]) -> str:
    statuses = {str(row["status"]) for row in gates}
    if "fail" in statuses:
        return "fail"
    if {"warning", "not_run"} & statuses:
        return "warning"
    return "pass"


def build_hrv_core_report(config: dict[str, Any]) -> str:
    outputs = config["outputs"]
    manifest_validation = validate_manifest(config["dataset"]["manifest"])
    inventory = _read_csv(outputs["inventory_csv"])
    peak = _read_csv(outputs["peak_benchmark_csv"])
    intervals = _read_csv(outputs["reference_intervals_csv"])
    windows = _read_csv(outputs["window_metrics_csv"])
    artifacts = _read_csv(outputs["artifact_sensitivity_csv"])
    artifact_summary = _read_csv(outputs["artifact_summary_csv"])
    frequency = _read_csv(outputs["frequency_window_metrics_csv"])
    record_summary = _read_csv(outputs["hrv_record_summary_csv"])
    uncertainty = _read_csv(outputs["hrv_uncertainty_csv"])

    primary_peak = peak[peak["tolerance_ms"] == 50.0]
    valid_frequency = frequency["welch_lf_power_ms2"].notna()
    excluded = intervals[~intervals["is_nn"]]
    nonfinite_records = inventory[inventory["ecg_nonfinite_count"] > 0]
    gate_rows = _gate_rows(
        manifest_validation,
        inventory,
        peak,
        intervals,
        artifacts,
        frequency,
        uncertainty,
    )
    decision = _gate_decision(gate_rows)
    decision_text = {
        "pass": "pass the current public-data HRV core implementation gate for method-development purposes.",
        "warning": "complete with warnings for the current public-data HRV core implementation gate.",
        "fail": "fail the current public-data HRV core implementation gate until required gates are fixed.",
    }[decision]

    lines: list[str] = [
        "# HRV Core Report",
        "",
        "## Question and Scope",
        "",
        (
            "This report evaluates a reproducible ECG to RR/NN to HRV workflow on "
            "the PhysioNet Fantasia Database v1.0.0. The scope is method validation: "
            "data access, reference annotation alignment, R-peak detector behavior, "
            "RR/NN interval construction, artifact sensitivity, frequency-domain "
            "method sensitivity, and record-level uncertainty."
        ),
        "",
        "This report does not make medical, diagnostic, risk-scoring, personal baseline, or treatment claims.",
        "",
        "## Dataset and Protocol",
        "",
        f"- Dataset: {config['dataset']['name']} v{config['dataset']['version']}.",
        "- License: Open Data Commons Attribution License v1.0, as recorded in `data/manifests/fantasia.csv`.",
        f"- Records analyzed: {len(inventory)} total; "
        f"{int((inventory['cohort'] == 'young').sum())} young and "
        f"{int((inventory['cohort'] == 'old').sum())} old.",
        f"- Sex balance: {inventory['sex'].value_counts().to_dict()}.",
        f"- Age range: {int(inventory['age'].min())}-{int(inventory['age'].max())} years.",
        f"- Sampling rates: {inventory['sampling_rate_hz'].value_counts().sort_index().to_dict()}.",
        f"- Channels: {inventory['channel_names'].value_counts().to_dict()}.",
        (
            f"- ECG non-finite samples: {int(inventory['ecg_nonfinite_count'].sum())} "
            f"across {len(nonfinite_records)} records; detector input used explicit linear interpolation "
            "for those samples and retained counts in output tables."
        ),
        "",
        "## Reproducibility",
        "",
        "From a fresh environment with the raw Fantasia files already present under `data/raw/fantasia/1.0.0`:",
        "",
        "```bash",
        "uv sync --frozen --extra dev",
        "uv run python -m physio_signal_lab.cli validate-data --manifest data/manifests/fantasia.csv",
        "uv run python -m physio_signal_lab.cli run-ecg-core --config configs/hrv/core.yaml",
        "uv run pytest -q",
        "```",
        "",
        (
            "The current manifest validation produced "
            f"{len(manifest_validation.missing_files)} missing files, "
            f"{len(manifest_validation.checksum_mismatches)} checksum mismatches, and "
            f"{len(manifest_validation.missing_record_files)} missing record files."
        ),
        "",
        "## R-Peak Detector Benchmark",
        "",
        (
            "The official `.ecg` annotations are treated as reference annotations, not absolute truth. "
            "NeuroKit2 was evaluated record-by-record at 50 ms and 100 ms tolerances."
        ),
        "",
        f"- 50 ms total TP/FP/FN: {int(primary_peak['true_positives'].sum())}/"
        f"{int(primary_peak['false_positives'].sum())}/"
        f"{int(primary_peak['false_negatives'].sum())}.",
        f"- 50 ms median sensitivity: {_fmt(primary_peak['sensitivity'].median(), 5)}.",
        f"- 50 ms median PPV: {_fmt(primary_peak['positive_predictive_value'].median(), 5)}.",
        f"- 50 ms median F1: {_fmt(primary_peak['f1'].median(), 5)}.",
        f"- 50 ms median absolute timing error: {_fmt(primary_peak['median_abs_timing_error_ms'].median(), 1)} ms.",
        "",
        _markdown_table(_top_worst_peak_rows(peak), ["record", "F1", "FP", "FN", "median abs error"]),
        "",
        "Worst-case overlay plots are stored in `figures/hrv/peak_failures/`.",
        "",
        "## RR and NN Intervals",
        "",
        (
            "RR intervals use all adjacent reference annotations. NN intervals are the subset where both "
            "endpoint annotation symbols are `N` and interval duration is within 300-2000 ms."
        ),
        "",
        f"- RR intervals: {len(intervals):,}.",
        f"- NN intervals: {int(intervals['is_nn'].sum()):,}.",
        f"- Excluded intervals: {int((~intervals['is_nn']).sum()):,}.",
        f"- Exclusion reasons: {excluded['exclusion_reason'].value_counts().to_dict()}.",
        f"- 5 min windows: {len(windows):,}; median valid fraction {_fmt(windows['valid_fraction'].median(), 4)}.",
        f"- Window RMSSD median: {_fmt(windows['rmssd_ms'].median())} ms.",
        "",
        "## Artifact Sensitivity",
        "",
        (
            "Artifact experiments injected missed beat, spurious extra beat, timestamp jitter, and ectopic-like "
            "short-long interval pairs at rates 0.1%, 0.5%, 1%, and 3%, with 20 repeats and fixed seeds."
        ),
        "",
        f"- Scenario rows: {len(artifacts):,}.",
        f"- Strategies: {sorted(artifacts['strategy'].unique().tolist())}.",
        "",
        _markdown_table(
            _artifact_rows(artifact_summary),
            ["artifact", "strategy", "median RMSSD rel error", "median SDNN rel error", "median pNN50 rel error"],
        ),
        "",
        "## Frequency-Domain HRV and Method Sensitivity",
        "",
        (
            "Primary frequency analysis interpolates the NN tachogram to 4 Hz and uses Welch PSD. "
            "Lomb-Scargle is reported as a normalized sensitivity analysis on the unevenly sampled series; "
            "its band powers are not treated as the same physical units as Welch `ms^2` powers."
        ),
        "",
        f"- Frequency windows: {len(frequency):,}; valid Welch windows {int(valid_frequency.sum()):,}; "
        f"short/insufficient windows {int((~valid_frequency).sum()):,}.",
        f"- Median Welch LF power: {_fmt(frequency['welch_lf_power_ms2'].median())} ms^2.",
        f"- Median Welch HF power: {_fmt(frequency['welch_hf_power_ms2'].median())} ms^2.",
        f"- Median Welch LF/HF ratio: {_fmt(frequency['welch_lf_hf_ratio'].median())}.",
        f"- Median Lomb LF/HF ratio: {_fmt(frequency['lomb_lf_hf_ratio'].median())}.",
        f"- Median Lomb-Welch LF/HF ratio delta: {_fmt(frequency['lf_hf_ratio_delta'].median())}.",
        "",
        "LF/HF is reported only as a secondary descriptive metric and is not interpreted as autonomic balance.",
        "",
        "## Record-Level Uncertainty",
        "",
        (
            "Uncertainty is estimated by bootstrapping record-level window medians, so records rather than beats "
            "or windows are the resampling unit."
        ),
        "",
        f"- MeanNN: {_uncertainty_line(uncertainty, 'mean_nn_ms', 'ms')}.",
        f"- SDNN: {_uncertainty_line(uncertainty, 'sdnn_ms', 'ms')}.",
        f"- RMSSD: {_uncertainty_line(uncertainty, 'rmssd_ms', 'ms')}.",
        f"- pNN50: {_uncertainty_line(uncertainty, 'pnn50')}.",
        f"- Welch LF power: {_uncertainty_line(uncertainty, 'welch_lf_power_ms2', 'ms^2')}.",
        f"- Welch HF power: {_uncertainty_line(uncertainty, 'welch_hf_power_ms2', 'ms^2')}.",
        f"- Welch LF/HF ratio: {_uncertainty_line(uncertainty, 'welch_lf_hf_ratio')}.",
        f"- Lomb LF/HF ratio: {_uncertainty_line(uncertainty, 'lomb_lf_hf_ratio')}.",
        "",
        "## Core Gate Decision",
        "",
        _markdown_table(
            gate_rows,
            ["gate", "status", "evidence"],
        ),
        "",
        f"**Decision:** {decision_text}",
        "",
        "## Limitations",
        "",
        "- Fantasia is a single-session resting laboratory dataset, not longitudinal or ambulatory monitoring.",
        "- Reference annotations may contain uncertainty and are not treated as error-free truth.",
        "- RR/NN rules are explicit and conservative; alternative beat classification rules may change HRV values.",
        "- Artifact experiments are controlled perturbations, not estimates of real device artifact prevalence.",
        "- Frequency-domain results depend on interpolation, PSD settings, windowing, and band definitions.",
        "- No personal baseline, disease detection, stress inference, sleep quality, or device-purchase conclusion follows from this analysis.",
        "",
        "## Next Direction",
        "",
        (
            "The next defensible step is a report review pass: inspect the five worst peak overlays, review "
            "artifact sensitivity trade-offs, and decide whether to freeze a version tag before optional "
            "Sleep-EDF/YASA expansion."
        ),
        "",
    ]
    return "\n".join(lines)


def write_hrv_core_report(config: dict[str, Any], output_path: str | Path | None = None) -> Path:
    out = Path(output_path or config["outputs"]["hrv_core_report_md"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_hrv_core_report(config), encoding="utf-8")
    return out
