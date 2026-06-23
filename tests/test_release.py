from __future__ import annotations

from pathlib import Path
import csv
import json

import pytest

from physio_signal_lab.release import CORE_RESULT_OUTPUT_KEYS, build_release_bundle


def _write(path: Path, text: str = "x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_build_release_bundle_copies_core_files_and_excludes_raw_data(tmp_path):
    config_path = _write(tmp_path / "configs" / "hrv" / "core.yaml", "dataset: {}\n")
    manifest_path = _write(tmp_path / "data/manifests/fantasia.csv", "local_path\nraw.dat\n")
    report_path = _write(tmp_path / "reports" / "hrv" / "core_report.md", "# HRV Core Report\n")

    outputs = {
        "hrv_core_report_md": str(report_path),
        "failure_plot_dir": str(tmp_path / "figures" / "hrv" / "peak_failures"),
    }
    for key in CORE_RESULT_OUTPUT_KEYS:
        outputs[key] = str(_write(tmp_path / "results" / f"{key}.csv", "metric,value\nx,1\n"))

    config = {
        "dataset": {
            "name": "Fantasia Database",
            "version": "1.0.0",
            "manifest": str(manifest_path),
        },
        "outputs": outputs,
    }

    release_dir = build_release_bundle(
        config,
        config_path=config_path,
        release_name="hrv-core-test",
        output_root=tmp_path / "releases",
    )

    assert (release_dir / "config" / "core.yaml").exists()
    assert (release_dir / "manifest" / "fantasia.csv").exists()
    assert (release_dir / "report" / "core_report.md").exists()
    assert (release_dir / "environment.txt").exists()
    assert (release_dir / "artifact_checksums.csv").exists()

    manifest = json.loads((release_dir / "release_manifest.json").read_text(encoding="utf-8"))
    assert manifest["release_name"] == "hrv-core-test"
    assert "Raw waveform files" in manifest["raw_data_policy"]

    with (release_dir / "artifact_checksums.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert {row["role"] for row in rows} >= {"config", "manifest", "report", "environment"}
    bundled_paths = {row["bundled_path"] for row in rows if row["bundled_path"]}
    assert bundled_paths >= {
        "config/core.yaml",
        "manifest/fantasia.csv",
        "report/core_report.md",
        "environment.txt",
    }
    assert not list(release_dir.rglob("*.dat"))


@pytest.mark.parametrize("release_name", ["../x", "x/y", "", ".", ".."])
def test_build_release_bundle_rejects_path_like_release_names(tmp_path, release_name):
    config = {"dataset": {"manifest": "missing.csv"}, "outputs": {}}
    with pytest.raises(ValueError):
        build_release_bundle(
            config,
            config_path="missing.yaml",
            release_name=release_name,
            output_root=tmp_path,
        )
