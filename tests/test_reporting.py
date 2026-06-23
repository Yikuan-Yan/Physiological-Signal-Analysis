from pathlib import Path

import pytest

from physio_signal_lab.config import load_config
from physio_signal_lab.reporting import build_hrv_core_report, write_hrv_core_report


REQUIRED_RESULTS = [
    Path("results/hrv/data_quality/fantasia_inventory.csv"),
    Path("results/hrv/peak_benchmark/peak_benchmark_by_record.csv"),
    Path("results/hrv/rr_nn/reference_intervals.csv"),
    Path("results/hrv/rr_nn/window_metrics.csv"),
    Path("results/hrv/artifacts/artifact_sensitivity.csv"),
    Path("results/hrv/artifacts/artifact_summary.csv"),
    Path("results/hrv/frequency/frequency_window_metrics.csv"),
    Path("results/hrv/frequency/hrv_record_summary.csv"),
    Path("results/hrv/frequency/hrv_uncertainty.csv"),
]


pytestmark = pytest.mark.skipif(
    not all(path.exists() for path in REQUIRED_RESULTS),
    reason="Generated result CSVs are not available in this environment",
)


def test_build_hrv_core_report_contains_gate_and_limitations():
    config = load_config("configs/hrv/core.yaml")
    report = build_hrv_core_report(config)
    assert "# HRV Core Report" in report
    assert "Core Gate Decision" in report
    assert "pass the current public-data HRV core implementation gate" in report
    assert "does not make medical, diagnostic" in report
    assert "LF/HF is reported only as a secondary descriptive metric" in report


def test_build_hrv_core_report_fails_gate_on_manifest_checksum_mismatch(tmp_path):
    config = load_config("configs/hrv/core.yaml")
    bad_file = tmp_path / "raw.dat"
    bad_file.write_text("not the expected content", encoding="utf-8")
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(
        "\n".join(
            [
                "dataset,version,doi,license,access_date,source_url,record_id,local_path,sha256,included,exclusion_reason",
                f"Fantasia,1.0.0,doi,license,2026-06-23,file://source,r1,{bad_file.as_posix()},0000,true,",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    config["dataset"]["manifest"] = str(manifest)

    report = build_hrv_core_report(config)

    assert "| Manifest and local files validated | fail |" in report
    assert "**Decision:** fail" in report


def test_write_hrv_core_report(tmp_path):
    config = load_config("configs/hrv/core.yaml")
    out = tmp_path / "hrv_core_report.md"
    written = write_hrv_core_report(config, out)
    assert written == out
    assert out.exists()
    assert out.read_text(encoding="utf-8").startswith("# HRV Core Report")
