from pathlib import Path

import pytest

from physio_signal_lab.config import load_config
from physio_signal_lab.features.sleep_stages import (
    count_mapped_stages,
    map_rk_label,
    validate_epoch_alignment,
)
from physio_signal_lab.io.sleep_edf import (
    build_sleep_cassette_selection,
    extract_edf_filenames,
    parse_sleep_edf_filename,
)
from physio_signal_lab.sleep_edf_preflight import run_sleep_edf_preflight


FIXTURE_FILENAMES = [
    "SC4001E0-PSG.edf",
    "SC4001EC-Hypnogram.edf",
    "SC4002E0-PSG.edf",
    "SC4002EC-Hypnogram.edf",
    "SC4011E0-PSG.edf",
    "SC4011EH-Hypnogram.edf",
    "SC4021E0-PSG.edf",
    "SC4021EH-Hypnogram.edf",
    "SC4031E0-PSG.edf",
    "SC4031EC-Hypnogram.edf",
    "SC4041E0-PSG.edf",
    "SC4041EC-Hypnogram.edf",
    "SC4051E0-PSG.edf",
    "SC4051EC-Hypnogram.edf",
    "SC4061E0-PSG.edf",
    "SC4061EC-Hypnogram.edf",
    "SC4071E0-PSG.edf",
    "SC4071EC-Hypnogram.edf",
    "SC4081E0-PSG.edf",
    "SC4081EC-Hypnogram.edf",
    "SC4091E0-PSG.edf",
    "SC4091EC-Hypnogram.edf",
    "SC4101E0-PSG.edf",
    "SC4101EC-Hypnogram.edf",
    "SC4111E0-PSG.edf",
    "SC4111EC-Hypnogram.edf",
    "SC4121E0-PSG.edf",
    "SC4121EC-Hypnogram.edf",
    "SC4131E0-PSG.edf",
    "SC4131EC-Hypnogram.edf",
    "SC4141E0-PSG.edf",
    "SC4141EU-Hypnogram.edf",
    "SC4151E0-PSG.edf",
    "SC4151EC-Hypnogram.edf",
    "SC4161E0-PSG.edf",
    "SC4161EC-Hypnogram.edf",
    "SC4171E0-PSG.edf",
    "SC4171EU-Hypnogram.edf",
    "SC4181E0-PSG.edf",
    "SC4181EC-Hypnogram.edf",
    "SC4191E0-PSG.edf",
    "SC4191EP-Hypnogram.edf",
    "ST7011J0-PSG.edf",
    "ST7011JP-Hypnogram.edf",
]


def test_parse_sleep_edf_filename_for_psg_and_hypnogram():
    psg = parse_sleep_edf_filename("SC4001E0-PSG.edf")
    hypnogram = parse_sleep_edf_filename("SC4001EC-Hypnogram.edf")

    assert psg.cohort == "sleep-cassette"
    assert psg.subject_id == 400
    assert psg.night == 1
    assert psg.kind == "PSG"
    assert psg.recording_id == "SC4001"
    assert hypnogram.kind == "Hypnogram"
    assert hypnogram.code == "EC"


def test_extract_edf_filenames_from_physionet_style_index():
    html = '<a href="SC4001E0-PSG.edf">SC4001E0-PSG.edf</a>'
    html += '<a href="SC4001EC-Hypnogram.edf">SC4001EC-Hypnogram.edf</a>'
    assert extract_edf_filenames(html) == [
        "SC4001E0-PSG.edf",
        "SC4001EC-Hypnogram.edf",
    ]


def test_sleep_cassette_selection_uses_first_available_night_and_excludes_st():
    selection = build_sleep_cassette_selection(
        FIXTURE_FILENAMES,
        benchmark_subjects=[400, 401],
        pilot_subjects=[400],
        source_base_url="https://physionet.org/files/sleep-edfx/1.0.0",
        raw_dir="data/raw/sleep-edfx/1.0.0",
    )

    assert selection["subject_id"].tolist() == [400, 401]
    assert selection["night"].tolist() == [1, 1]
    assert selection["role"].tolist() == ["pilot", "benchmark"]
    assert selection["psg_filename"].tolist() == ["SC4001E0-PSG.edf", "SC4011E0-PSG.edf"]
    assert selection["hypnogram_filename"].tolist() == [
        "SC4001EC-Hypnogram.edf",
        "SC4011EH-Hypnogram.edf",
    ]
    assert "ST7011J0-PSG.edf" not in selection["psg_filename"].tolist()


def test_sleep_stage_mapping_and_epoch_alignment():
    assert map_rk_label("W") == "WAKE"
    assert map_rk_label("3") == "N3"
    assert map_rk_label("4") == "N3"
    assert map_rk_label("?") is None
    assert count_mapped_stages(["W", "1", "2", "3", "4", "R", "M", "?"]) == {
        "WAKE": 1,
        "N1": 1,
        "N2": 1,
        "N3": 2,
        "REM": 1,
        "excluded": 2,
    }
    summary = validate_epoch_alignment(signal_duration_seconds=300, epoch_count=10)
    assert summary.aligned
    assert summary.duration_delta_seconds == 0


def test_sleep_stage_mapping_rejects_unknown_label():
    with pytest.raises(ValueError):
        map_rk_label("N2")


def test_run_sleep_edf_preflight_writes_selection_manifest_and_report(tmp_path):
    config = load_config("configs/sleep_edf.yaml")
    config["outputs"] = {
        "selection_csv": str(tmp_path / "results" / "sleep_edf_selection.csv"),
        "manifest_csv": str(tmp_path / "data_manifest_sleep_edf.csv"),
        "preflight_report_md": str(tmp_path / "reports" / "sleep_edf_preflight.md"),
    }

    outputs = run_sleep_edf_preflight(config, filenames=FIXTURE_FILENAMES)

    assert outputs.selection_csv.exists()
    assert outputs.manifest_csv.exists()
    assert outputs.report_md.exists()
    selection_lines = outputs.selection_csv.read_text(encoding="utf-8").splitlines()
    manifest_lines = outputs.manifest_csv.read_text(encoding="utf-8").splitlines()
    report = outputs.report_md.read_text(encoding="utf-8")
    assert len(selection_lines) == 21
    assert len(manifest_lines) == 41
    assert "first_available_night_for_first_20_sorted_sleep_cassette_subjects" in report
    assert "event-detector accuracy claims" in report
    assert Path(config["dataset"]["raw_dir"]).as_posix() in outputs.manifest_csv.read_text(
        encoding="utf-8"
    )
