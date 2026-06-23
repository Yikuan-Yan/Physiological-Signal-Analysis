from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any
import csv
import hashlib
import json
import platform
import shutil
import subprocess
import sys

from physio_signal_lab import __version__


CORE_RESULT_OUTPUT_KEYS = (
    "inventory_csv",
    "peak_benchmark_csv",
    "reference_intervals_csv",
    "window_metrics_csv",
    "artifact_sensitivity_csv",
    "artifact_summary_csv",
    "frequency_window_metrics_csv",
    "hrv_record_summary_csv",
    "hrv_uncertainty_csv",
)

ENVIRONMENT_PACKAGES = (
    "physio-signal-lab",
    "matplotlib",
    "neurokit2",
    "numpy",
    "pandas",
    "pyyaml",
    "scipy",
    "wfdb",
    "pytest",
)


@dataclass(frozen=True)
class ReleaseFile:
    role: str
    source_path: str
    sha256: str
    bytes: int
    bundled_path: str | None


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _project_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _file_record(path: Path, role: str, bundled_path: str | None = None) -> ReleaseFile:
    if not path.exists():
        raise FileNotFoundError(f"Release artifact is missing: {path}")
    return ReleaseFile(
        role=role,
        source_path=_project_relative(path),
        sha256=_sha256_file(path),
        bytes=path.stat().st_size,
        bundled_path=bundled_path,
    )


def _copy_artifact(source: Path, destination: Path, role: str) -> ReleaseFile:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return _file_record(
        source,
        role=role,
        bundled_path=destination.relative_to(destination.parent.parent).as_posix(),
    )


def _run_git(args: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip()


def _status_is_dirty(status: str | None, excluded_prefix: str | None = None) -> bool:
    if not status:
        return False
    for line in status.splitlines():
        if len(line) < 4:
            return True
        path = line[3:].replace("\\", "/").rstrip("/")
        if excluded_prefix and (
            path == excluded_prefix or path.startswith(f"{excluded_prefix}/")
            or excluded_prefix.startswith(f"{path}/")
        ):
            continue
        return True
    return False


def git_state(excluded_path: str | Path | None = None) -> dict[str, Any]:
    status = _run_git(["status", "--short"])
    excluded_prefix = None
    if excluded_path is not None:
        excluded_prefix = _project_relative(Path(excluded_path)).replace("\\", "/")
    return {
        "commit": _run_git(["rev-parse", "HEAD"]),
        "branch": _run_git(["branch", "--show-current"]),
        "dirty": _status_is_dirty(status, excluded_prefix),
    }


def environment_lines() -> list[str]:
    lines = [
        f"generated_at_utc={datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"python={sys.version.split()[0]}",
        f"platform={platform.platform()}",
        f"executable={sys.executable}",
    ]
    for package in ENVIRONMENT_PACKAGES:
        try:
            version = metadata.version(package)
        except metadata.PackageNotFoundError:
            version = "not-installed"
        lines.append(f"{package}={version}")
    return lines


def _result_artifacts(config: dict[str, Any]) -> list[tuple[str, Path]]:
    outputs = config["outputs"]
    artifacts = [(key, Path(outputs[key])) for key in CORE_RESULT_OUTPUT_KEYS]
    failure_plot_dir = Path(outputs["failure_plot_dir"])
    if failure_plot_dir.exists():
        artifacts.extend(
            ("failure_plot", path)
            for path in sorted(failure_plot_dir.glob("*.png"))
            if path.is_file()
        )
    return artifacts


def _write_checksum_csv(path: Path, rows: list[ReleaseFile]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["role", "source_path", "sha256", "bytes", "bundled_path"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def _write_release_readme(path: Path, release_name: str) -> None:
    path.write_text(
        "\n".join(
            [
                f"# {release_name}",
                "",
                "This bundle freezes the public-data ECG/HRV core stage.",
                "",
                "Bundled files:",
                "",
                "- `config/<config file>`: frozen analysis configuration.",
                "- `manifest/<manifest csv>`: raw-data manifest with source URLs and checksums.",
                "- `report/<report md>`: core Gate report generated from tracked outputs.",
                "- `environment.txt`: Python, platform, and package versions.",
                "- `artifact_checksums.csv`: checksums for tracked result tables and figures.",
                "- `release_manifest.json`: machine-readable release metadata.",
                "",
                "Raw waveform files are intentionally excluded. Rebuild them from the manifest and PhysioNet source if needed.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def build_release_bundle(
    config: dict[str, Any],
    *,
    config_path: str | Path,
    release_name: str,
    output_root: str | Path = "releases",
) -> Path:
    release_name_path = Path(release_name)
    if (
        release_name_path.is_absolute()
        or len(release_name_path.parts) != 1
        or release_name in {"", ".", ".."}
    ):
        raise ValueError(f"Release name must be a single directory name: {release_name!r}")

    release_dir = Path(output_root) / release_name
    release_dir.mkdir(parents=True, exist_ok=True)

    config_source = Path(config_path)
    manifest_source = Path(config["dataset"]["manifest"])
    report_source = Path(config["outputs"]["hrv_core_report_md"])

    bundled_records = [
        _copy_artifact(config_source, release_dir / "config" / config_source.name, "config"),
        _copy_artifact(manifest_source, release_dir / "manifest" / manifest_source.name, "manifest"),
        _copy_artifact(report_source, release_dir / "report" / report_source.name, "report"),
    ]

    checksum_records = [
        *bundled_records,
        _file_record(Path("pyproject.toml"), "environment_source"),
        _file_record(Path("uv.lock"), "environment_lock"),
    ]
    checksum_records.extend(
        _file_record(path, role=role)
        for role, path in _result_artifacts(config)
    )

    environment_path = release_dir / "environment.txt"
    environment_path.write_text("\n".join(environment_lines()) + "\n", encoding="utf-8")
    checksum_records.append(
        _file_record(environment_path, role="environment", bundled_path="environment.txt")
    )

    checksums_path = release_dir / "artifact_checksums.csv"
    _write_checksum_csv(checksums_path, checksum_records)

    readme_path = release_dir / "README.md"
    _write_release_readme(readme_path, release_name)

    manifest = {
        "release_name": release_name,
        "project_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dataset": {
            "name": config["dataset"]["name"],
            "version": config["dataset"]["version"],
            "manifest": _project_relative(manifest_source),
        },
        "raw_data_policy": "Raw waveform files under data/raw are intentionally excluded.",
        "git": git_state(excluded_path=release_dir),
        "bundled_files": [asdict(record) for record in bundled_records],
        "checksum_file": "artifact_checksums.csv",
    }
    (release_dir / "release_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return release_dir
