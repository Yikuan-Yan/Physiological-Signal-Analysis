from __future__ import annotations

from pathlib import Path
import argparse
import sys

from physio_signal_lab.config import load_config
from physio_signal_lab.evaluation.peak_benchmark import benchmark_records
from physio_signal_lab.io.fantasia import build_inventory, record_ids_from_manifest
from physio_signal_lab.manifest import validate_manifest


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
    inventory_fantasia(inventory_args)
    benchmark_peaks(benchmark_args)
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
