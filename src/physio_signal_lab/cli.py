from __future__ import annotations

from pathlib import Path
import argparse
import sys

import numpy as np

from physio_signal_lab.config import load_config
from physio_signal_lab.evaluation.artifacts import (
    artifact_experiment,
    summarize_artifact_experiment,
)
from physio_signal_lab.evaluation.peak_benchmark import benchmark_records
from physio_signal_lab.features.rr_nn import build_reference_intervals, window_metrics
from physio_signal_lab.features.rr_nn import frequency_window_metrics
from physio_signal_lab.features.uncertainty import (
    bootstrap_uncertainty,
    record_summary,
)
from physio_signal_lab.io.fantasia import build_inventory, record_ids_from_manifest
from physio_signal_lab.io.mit_bih_psg import (
    download_mit_bih_psg_selection,
    update_mit_bih_psg_manifest_checksums,
    validate_mit_bih_psg_manifest,
    write_mit_bih_psg_manifest,
)
from physio_signal_lab.io.sleep_edf import (
    download_sleep_edf_selection,
    update_manifest_checksums,
    validate_sleep_edf_manifest,
)
from physio_signal_lab.manifest import validate_manifest
from physio_signal_lab.release import build_release_bundle
from physio_signal_lab.reporting import write_hrv_core_report
from physio_signal_lab.mit_bih_psg import run_mit_bih_psg_respiratory_pilot
from physio_signal_lab.sleep_edf_benchmark import run_sleep_edf_pilot_benchmark
from physio_signal_lab.sleep_edf_preflight import run_sleep_edf_preflight
from physio_signal_lab.sleep_quality import run_sleep_edf_clinical_education
from physio_signal_lab.yasa_profile import run_yasa_profile


def _csv_record_override(value: str | None) -> list[str] | None:
    if value is None:
        return None
    records = [item.strip() for item in value.split(",") if item.strip()]
    return records or None


def _record_ids(config: dict, records_override: str | None = None) -> list[str]:
    override = _csv_record_override(records_override)
    if override is not None:
        return override

    manifest = config["dataset"]["manifest"]
    all_records = record_ids_from_manifest(manifest)
    mode = config.get("records", {}).get("mode", "all")
    if mode == "all":
        return all_records
    if mode == "pilot":
        return list(config.get("records", {}).get("pilot", []))
    raise ValueError(f"Unsupported records.mode: {mode}")


def _ensure_parent(path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def validate_data(args: argparse.Namespace) -> int:
    result = validate_manifest(args.manifest)
    print(f"rows={result.row_count}")
    print(f"records={result.record_count}")
    print(f"checked_files={result.checked_file_count}")
    print(f"missing_files={len(result.missing_files)}")
    print(f"checksum_mismatches={len(result.checksum_mismatches)}")
    print(f"missing_record_files={len(result.missing_record_files)}")
    if not result.ok:
        return 1
    return 0


def inventory_fantasia(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    records = _record_ids(config, args.records)
    raw_dir = config["dataset"]["raw_dir"]
    channel = config["ecg"]["channel_name"]
    out = _ensure_parent(args.out or config["outputs"]["inventory_csv"])
    inventory = build_inventory(records, raw_dir, ecg_channel=channel)
    inventory.to_csv(out, index=False)
    print(f"wrote {out} rows={len(inventory)}")
    return 0


def benchmark_peaks(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    records = _record_ids(config, args.records)
    raw_dir = config["dataset"]["raw_dir"]
    ecg_config = config["ecg"]
    benchmark_config = config["benchmark"]
    outputs = config["outputs"]
    out = _ensure_parent(args.out or outputs["peak_benchmark_csv"])
    plot_count = args.failure_plot_count
    if plot_count is None:
        plot_count = int(benchmark_config.get("failure_plot_count", 0))

    metrics = benchmark_records(
        records,
        raw_dir,
        tolerances_ms=[float(x) for x in benchmark_config["tolerances_ms"]],
        ecg_channel=ecg_config["channel_name"],
        clean_method=ecg_config["detector"]["clean_method"],
        peak_method=ecg_config["detector"]["peak_method"],
        failure_plot_count=plot_count,
        failure_window_seconds=float(benchmark_config["failure_window_seconds"]),
        failure_plot_dir=outputs["failure_plot_dir"],
    )
    metrics.to_csv(out, index=False)
    print(f"wrote {out} rows={len(metrics)}")
    return 0


def run_rr_artifacts(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    records = _record_ids(config, args.records)
    raw_dir = config["dataset"]["raw_dir"]
    rr_config = config["rr_nn"]
    artifact_config = config["artifact_experiment"]
    outputs = config["outputs"]

    intervals = build_reference_intervals(
        records,
        raw_dir,
        normal_symbols=set(rr_config["normal_symbols"]),
        valid_rr_min_ms=float(rr_config["valid_rr_ms"]["min"]),
        valid_rr_max_ms=float(rr_config["valid_rr_ms"]["max"]),
    )
    intervals_out = _ensure_parent(outputs["reference_intervals_csv"])
    intervals.to_csv(intervals_out, index=False)
    print(f"wrote {intervals_out} rows={len(intervals)}")

    windows = window_metrics(
        intervals,
        window_seconds=float(rr_config["window_seconds"]),
    )
    windows_out = _ensure_parent(outputs["window_metrics_csv"])
    windows.to_csv(windows_out, index=False)
    print(f"wrote {windows_out} rows={len(windows)}")

    sensitivity = artifact_experiment(
        intervals,
        artifact_types=list(artifact_config["types"]),
        rates=[float(rate) for rate in artifact_config["rates"]],
        repeats=int(artifact_config["repeats"]),
        strategies=list(artifact_config["strategies"]),
        seed=int(artifact_config["seed"]),
        jitter_ms=float(artifact_config["jitter_ms"]),
        ectopic_shift_fraction=float(artifact_config["ectopic_shift_fraction"]),
    )
    sensitivity_out = _ensure_parent(outputs["artifact_sensitivity_csv"])
    sensitivity.to_csv(sensitivity_out, index=False)
    print(f"wrote {sensitivity_out} rows={len(sensitivity)}")

    summary = summarize_artifact_experiment(sensitivity)
    summary_out = _ensure_parent(outputs["artifact_summary_csv"])
    summary.to_csv(summary_out, index=False)
    print(f"wrote {summary_out} rows={len(summary)}")
    return 0


def run_frequency_hrv(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    records = _record_ids(config, args.records)
    raw_dir = config["dataset"]["raw_dir"]
    rr_config = config["rr_nn"]
    freq_config = config["hrv_frequency"]
    uncertainty_config = config["uncertainty"]
    outputs = config["outputs"]

    intervals = build_reference_intervals(
        records,
        raw_dir,
        normal_symbols=set(rr_config["normal_symbols"]),
        valid_rr_min_ms=float(rr_config["valid_rr_ms"]["min"]),
        valid_rr_max_ms=float(rr_config["valid_rr_ms"]["max"]),
    )
    windows = window_metrics(
        intervals,
        window_seconds=float(rr_config["window_seconds"]),
    )
    bands = freq_config["bands_hz"]
    grid_config = freq_config["lomb_frequency_grid_hz"]
    frequency_grid = np.linspace(
        float(grid_config["min"]),
        float(grid_config["max"]),
        int(grid_config["count"]),
    )
    frequency = frequency_window_metrics(
        intervals,
        window_seconds=float(rr_config["window_seconds"]),
        interpolation_hz=float(freq_config["interpolation_hz"]),
        nperseg_seconds=float(freq_config["welch_nperseg_seconds"]),
        lf_band=(float(bands["lf"][0]), float(bands["lf"][1])),
        hf_band=(float(bands["hf"][0]), float(bands["hf"][1])),
        lomb_frequency_grid_hz=frequency_grid,
        min_nn_intervals=int(freq_config["min_nn_intervals"]),
    )
    frequency_out = _ensure_parent(outputs["frequency_window_metrics_csv"])
    frequency.to_csv(frequency_out, index=False)
    print(f"wrote {frequency_out} rows={len(frequency)}")

    records_summary = record_summary(windows, frequency)
    summary_out = _ensure_parent(outputs["hrv_record_summary_csv"])
    records_summary.to_csv(summary_out, index=False)
    print(f"wrote {summary_out} rows={len(records_summary)}")

    uncertainty = bootstrap_uncertainty(
        records_summary,
        seed=int(uncertainty_config["seed"]),
        iterations=int(uncertainty_config["bootstrap_iterations"]),
        ci=float(uncertainty_config["ci"]),
    )
    uncertainty_out = _ensure_parent(outputs["hrv_uncertainty_csv"])
    uncertainty.to_csv(uncertainty_out, index=False)
    print(f"wrote {uncertainty_out} rows={len(uncertainty)}")
    return 0


def build_report(args: argparse.Namespace) -> int:
    if args.report != "hrv-core":
        raise ValueError(f"Unsupported report: {args.report}")
    config = load_config(args.config)
    out = write_hrv_core_report(config, args.out)
    print(f"wrote {out}")
    return 0


def freeze_release(args: argparse.Namespace) -> int:
    if args.release != "hrv-core":
        raise ValueError(f"Unsupported release: {args.release}")
    config = load_config(args.config)
    release_dir = build_release_bundle(
        config,
        config_path=args.config,
        release_name=args.release_name,
        output_root=args.output_root,
    )
    print(f"wrote {release_dir}")
    return 0


def sleep_edf_preflight(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    outputs = run_sleep_edf_preflight(config)
    print(f"wrote {outputs.selection_csv}")
    print(f"wrote {outputs.manifest_csv}")
    print(f"wrote {outputs.report_md}")
    return 0


def download_sleep_edf(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    outputs = config["outputs"]
    records = _csv_record_override(args.records)
    summary = download_sleep_edf_selection(
        outputs["selection_csv"],
        records=records,
        overwrite=args.overwrite,
    )
    summary_out = _ensure_parent(outputs["download_summary_csv"])
    summary.to_csv(summary_out, index=False)
    manifest_out = update_manifest_checksums(outputs["manifest_csv"], records=records)
    print(f"wrote {summary_out} rows={len(summary)}")
    print(f"updated {manifest_out}")
    print(f"bytes={int(summary['bytes'].sum())}")
    print(f"downloaded={(summary['status'].str.startswith('downloaded')).sum()}")
    print(f"skipped_existing={(summary['status'] == 'skipped_existing').sum()}")
    return 0


def validate_sleep_edf(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    outputs = config["outputs"]
    records = _csv_record_override(args.records)
    validation = validate_sleep_edf_manifest(outputs["manifest_csv"], records=records)
    validation_out = _ensure_parent(outputs["validation_csv"])
    validation.to_csv(validation_out, index=False)
    missing = int((~validation["exists"]).sum())
    checksum_mismatches = int((~validation["checksum_ok"]).sum())
    print(f"wrote {validation_out} rows={len(validation)}")
    print(f"missing_files={missing}")
    print(f"checksum_mismatches={checksum_mismatches}")
    print(f"bytes={int(validation['bytes'].sum())}")
    return 0 if missing == 0 and checksum_mismatches == 0 else 1


def sleep_edf_pilot_benchmark(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    records = _csv_record_override(args.records)
    if records is None:
        records = [f"SC{int(subject):03d}1" for subject in config["selection"]["pilot_subjects"]]
    outputs = run_sleep_edf_pilot_benchmark(
        config,
        records=records,
        include_yasa=args.include_yasa,
        output_prefix=args.output_prefix,
    )
    print(f"wrote {outputs.epoch_labels_csv}")
    print(f"wrote {outputs.baseline_metrics_csv}")
    print(f"wrote {outputs.stage_summary_csv}")
    if outputs.yasa_predictions_csv is not None:
        print(f"wrote {outputs.yasa_predictions_csv}")
    if outputs.yasa_probabilities_csv is not None:
        print(f"wrote {outputs.yasa_probabilities_csv}")
    if outputs.yasa_metrics_csv is not None:
        print(f"wrote {outputs.yasa_metrics_csv}")
    print(f"wrote {outputs.report_md}")
    return 0


def profile_yasa_runtime(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    records = _csv_record_override(args.records)
    if records is None:
        records = [f"SC{int(subject):03d}1" for subject in config["selection"]["pilot_subjects"]]
    crop_seconds = None if args.full_night else args.crop_seconds
    outputs = run_yasa_profile(
        config,
        records=records,
        crop_seconds=crop_seconds,
        timeout_seconds=args.timeout_seconds,
        output_prefix=args.output_prefix,
    )
    print(f"wrote {outputs.profile_csv}")
    print(f"wrote {outputs.report_md}")
    return 0


def sleep_edf_clinical_education(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    records = _csv_record_override(args.records)
    if records is None:
        records = [f"SC{int(subject):03d}1" for subject in config["selection"]["pilot_subjects"]]
    outputs = run_sleep_edf_clinical_education(
        config,
        records=records,
        output_prefix=args.output_prefix,
        include_yasa=args.include_yasa,
    )
    print(f"wrote {outputs.metrics_csv}")
    print(f"wrote {outputs.indicators_csv}")
    if outputs.discrepancy_csv is not None:
        print(f"wrote {outputs.discrepancy_csv}")
    print(f"wrote {outputs.question_ranking_csv}")
    print(f"wrote {outputs.hypnogram_plot_png}")
    print(f"wrote {outputs.architecture_plot_png}")
    print(f"wrote {outputs.report_md}")
    print("wrote reports\\sleep_edf_clinical_learning_plan.md")
    return 0


def download_mit_bih_psg(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    records = _csv_record_override(args.records)
    manifest_out = write_mit_bih_psg_manifest(config)
    summary = download_mit_bih_psg_selection(
        config,
        records=records,
        overwrite=args.overwrite,
    )
    summary_out = _ensure_parent(config["outputs"]["download_summary_csv"])
    summary.to_csv(summary_out, index=False)
    update_mit_bih_psg_manifest_checksums(manifest_out)
    print(f"wrote {summary_out} rows={len(summary)}")
    print(f"updated {manifest_out}")
    print(f"bytes={int(summary['bytes'].sum())}")
    print(f"downloaded={(summary['status'].str.startswith('downloaded')).sum()}")
    print(f"skipped_existing={(summary['status'] == 'skipped_existing').sum()}")
    return 0


def validate_mit_bih_psg(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    records = _csv_record_override(args.records)
    validation = validate_mit_bih_psg_manifest(
        config["outputs"]["manifest_csv"],
        records=records,
    )
    validation_out = _ensure_parent(config["outputs"]["validation_csv"])
    validation.to_csv(validation_out, index=False)
    missing = int((~validation["exists"]).sum())
    checksum_mismatches = int((~validation["checksum_ok"]).sum())
    incomplete_records = int((~validation["required_file_set_complete"]).sum())
    print(f"wrote {validation_out} rows={len(validation)}")
    print(f"missing_files={missing}")
    print(f"checksum_mismatches={checksum_mismatches}")
    print(f"incomplete_required_file_rows={incomplete_records}")
    print(f"bytes={int(validation['bytes'].sum())}")
    return 0 if missing == 0 and checksum_mismatches == 0 and incomplete_records == 0 else 1


def mit_bih_psg_respiratory_pilot(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    records = _csv_record_override(args.records)
    outputs = run_mit_bih_psg_respiratory_pilot(
        config,
        records=records,
        output_prefix=args.output_prefix,
    )
    print(f"wrote {outputs.annotation_epochs_csv}")
    print(f"wrote {outputs.respiratory_metrics_csv}")
    print(f"wrote {outputs.source_alignment_csv}")
    print(f"wrote {outputs.oxygen_metrics_csv}")
    print(f"wrote {outputs.oxygen_artifact_review_csv}")
    print(f"wrote {outputs.event_windows_csv}")
    print(f"wrote {outputs.channel_quality_csv}")
    print(f"wrote {outputs.clinical_indicators_csv}")
    print(f"wrote {outputs.report_md}")
    return 0


def run_ecg_core(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    manifest = config["dataset"]["manifest"]
    result = validate_manifest(manifest)
    if not result.ok:
        print("manifest validation failed", file=sys.stderr)
        return 1

    records_arg = args.records
    inventory_args = argparse.Namespace(
        config=args.config,
        records=records_arg,
        out=config["outputs"]["inventory_csv"],
    )
    benchmark_args = argparse.Namespace(
        config=args.config,
        records=records_arg,
        out=config["outputs"]["peak_benchmark_csv"],
        failure_plot_count=None,
    )
    rr_artifact_args = argparse.Namespace(
        config=args.config,
        records=records_arg,
    )
    frequency_args = argparse.Namespace(
        config=args.config,
        records=records_arg,
    )
    inventory_fantasia(inventory_args)
    benchmark_peaks(benchmark_args)
    run_rr_artifacts(rr_artifact_args)
    run_frequency_hrv(frequency_args)
    report_args = argparse.Namespace(
        config=args.config,
        report="hrv-core",
        out=config["outputs"]["hrv_core_report_md"],
    )
    build_report(report_args)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="physio-signal-lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate-data")
    validate_parser.add_argument("--manifest", default="data_manifest.csv")
    validate_parser.set_defaults(func=validate_data)

    inventory_parser = subparsers.add_parser("inventory-fantasia")
    inventory_parser.add_argument("--config", default="configs/hrv_core.yaml")
    inventory_parser.add_argument("--records", default=None)
    inventory_parser.add_argument("--out", default=None)
    inventory_parser.set_defaults(func=inventory_fantasia)

    benchmark_parser = subparsers.add_parser("benchmark-peaks")
    benchmark_parser.add_argument("--config", default="configs/hrv_core.yaml")
    benchmark_parser.add_argument("--records", default=None)
    benchmark_parser.add_argument("--out", default=None)
    benchmark_parser.add_argument("--failure-plot-count", type=int, default=None)
    benchmark_parser.set_defaults(func=benchmark_peaks)

    rr_artifacts_parser = subparsers.add_parser("run-rr-artifacts")
    rr_artifacts_parser.add_argument("--config", default="configs/hrv_core.yaml")
    rr_artifacts_parser.add_argument("--records", default=None)
    rr_artifacts_parser.set_defaults(func=run_rr_artifacts)

    frequency_parser = subparsers.add_parser("run-frequency-hrv")
    frequency_parser.add_argument("--config", default="configs/hrv_core.yaml")
    frequency_parser.add_argument("--records", default=None)
    frequency_parser.set_defaults(func=run_frequency_hrv)

    report_parser = subparsers.add_parser("build-report")
    report_parser.add_argument("report", choices=["hrv-core"])
    report_parser.add_argument("--config", default="configs/hrv_core.yaml")
    report_parser.add_argument("--out", default=None)
    report_parser.set_defaults(func=build_report)

    release_parser = subparsers.add_parser("freeze-release")
    release_parser.add_argument("release", choices=["hrv-core"])
    release_parser.add_argument("--config", default="configs/hrv_core.yaml")
    release_parser.add_argument("--release-name", default="hrv-core-v0.1.0")
    release_parser.add_argument("--output-root", default="releases")
    release_parser.set_defaults(func=freeze_release)

    sleep_edf_parser = subparsers.add_parser("run-sleep-edf-preflight")
    sleep_edf_parser.add_argument("--config", default="configs/sleep_edf.yaml")
    sleep_edf_parser.set_defaults(func=sleep_edf_preflight)

    sleep_edf_download_parser = subparsers.add_parser("download-sleep-edf")
    sleep_edf_download_parser.add_argument("--config", default="configs/sleep_edf.yaml")
    sleep_edf_download_parser.add_argument("--records", default=None)
    sleep_edf_download_parser.add_argument("--overwrite", action="store_true")
    sleep_edf_download_parser.set_defaults(func=download_sleep_edf)

    sleep_edf_validate_parser = subparsers.add_parser("validate-sleep-edf")
    sleep_edf_validate_parser.add_argument("--config", default="configs/sleep_edf.yaml")
    sleep_edf_validate_parser.add_argument("--records", default=None)
    sleep_edf_validate_parser.set_defaults(func=validate_sleep_edf)

    sleep_edf_benchmark_parser = subparsers.add_parser("run-sleep-edf-pilot-benchmark")
    sleep_edf_benchmark_parser.add_argument("--config", default="configs/sleep_edf.yaml")
    sleep_edf_benchmark_parser.add_argument("--records", default=None)
    sleep_edf_benchmark_parser.add_argument("--output-prefix", default="pilot")
    sleep_edf_benchmark_parser.add_argument("--include-yasa", action="store_true")
    sleep_edf_benchmark_parser.set_defaults(func=sleep_edf_pilot_benchmark)

    yasa_profile_parser = subparsers.add_parser("profile-yasa-runtime")
    yasa_profile_parser.add_argument("--config", default="configs/sleep_edf.yaml")
    yasa_profile_parser.add_argument("--records", default=None)
    yasa_profile_parser.add_argument("--crop-seconds", type=float, default=120.0)
    yasa_profile_parser.add_argument("--full-night", action="store_true")
    yasa_profile_parser.add_argument("--timeout-seconds", type=float, default=120.0)
    yasa_profile_parser.add_argument("--output-prefix", default=None)
    yasa_profile_parser.set_defaults(func=profile_yasa_runtime)

    clinical_parser = subparsers.add_parser("run-sleep-edf-clinical-education")
    clinical_parser.add_argument("--config", default="configs/sleep_edf.yaml")
    clinical_parser.add_argument("--records", default=None)
    clinical_parser.add_argument("--output-prefix", default="pilot")
    clinical_parser.add_argument("--include-yasa", action="store_true")
    clinical_parser.set_defaults(func=sleep_edf_clinical_education)

    mit_download_parser = subparsers.add_parser("download-mit-bih-psg")
    mit_download_parser.add_argument("--config", default="configs/mit_bih_psg.yaml")
    mit_download_parser.add_argument("--records", default=None)
    mit_download_parser.add_argument("--overwrite", action="store_true")
    mit_download_parser.set_defaults(func=download_mit_bih_psg)

    mit_validate_parser = subparsers.add_parser("validate-mit-bih-psg")
    mit_validate_parser.add_argument("--config", default="configs/mit_bih_psg.yaml")
    mit_validate_parser.add_argument("--records", default=None)
    mit_validate_parser.set_defaults(func=validate_mit_bih_psg)

    mit_pilot_parser = subparsers.add_parser("run-mit-bih-psg-respiratory-pilot")
    mit_pilot_parser.add_argument("--config", default="configs/mit_bih_psg.yaml")
    mit_pilot_parser.add_argument("--records", default=None)
    mit_pilot_parser.add_argument("--output-prefix", default=None)
    mit_pilot_parser.set_defaults(func=mit_bih_psg_respiratory_pilot)

    run_parser = subparsers.add_parser("run-ecg-core")
    run_parser.add_argument("--config", default="configs/hrv_core.yaml")
    run_parser.add_argument("--records", default=None)
    run_parser.set_defaults(func=run_ecg_core)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
