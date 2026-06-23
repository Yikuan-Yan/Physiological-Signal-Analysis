from pathlib import Path

import pandas as pd
import pytest

from physio_signal_lab.config import load_config
from physio_signal_lab.features.sleep_stages import (
    count_mapped_stages,
    map_rk_label,
    validate_epoch_alignment,
)
from physio_signal_lab.io.sleep_edf import (
    build_sleep_cassette_selection,
    download_file,
    extract_edf_filenames,
    parse_sleep_edf_filename,
    update_manifest_checksums,
    validate_sleep_edf_manifest,
)
from physio_signal_lab.evaluation.sleep_staging import (
    align_model_predictions,
    expand_stage_annotations,
    majority_stage_predictions,
    map_yasa_stage,
    parse_sleep_stage_description,
    sleep_stage_metrics,
)
from physio_signal_lab.sleep_edf_preflight import run_sleep_edf_preflight
from physio_signal_lab.sleep_outputs import (
    clean_output_prefix,
    scoped_sleep_edf_output_path,
)
from physio_signal_lab.sleep_quality import (
    build_clinical_question_ranking,
    build_yasa_discrepancy_table,
    build_clinical_indicators,
    sleep_quality_metrics,
)
from physio_signal_lab.yasa_profile import build_yasa_profile_report


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


def test_expand_stage_annotations_maps_and_crops_to_signal_duration():
    annotations = [
        {"onset": 0.0, "duration": 60.0, "description": "Sleep stage W"},
        {"onset": 60.0, "duration": 30.0, "description": "Sleep stage 3"},
        {"onset": 90.0, "duration": 60.0, "description": "Sleep stage ?"},
        {"onset": 150.0, "duration": 60.0, "description": "Sleep stage R"},
    ]

    labels = expand_stage_annotations(
        pd.DataFrame(annotations),
        record_id="SC4001",
        signal_duration_seconds=180.0,
        epoch_seconds=30.0,
    )

    assert len(labels) == 6
    assert labels["epoch_index"].tolist() == list(range(6))
    assert labels["mapped_stage"].tolist() == ["WAKE", "WAKE", "N3", "", "", "REM"]
    assert labels["included"].tolist() == [True, True, True, False, False, True]


def test_parse_sleep_stage_description_rejects_non_stage_annotations():
    assert parse_sleep_stage_description("Sleep stage R") == "R"
    assert parse_sleep_stage_description("Movement time") == "M"
    with pytest.raises(ValueError):
        parse_sleep_stage_description("Lights off")


def test_majority_baseline_metrics_are_record_and_all_level():
    labels = pd.DataFrame(
        [
            {"record_id": "SC4001", "mapped_stage": "WAKE", "included": True},
            {"record_id": "SC4001", "mapped_stage": "WAKE", "included": True},
            {"record_id": "SC4001", "mapped_stage": "N2", "included": True},
            {"record_id": "SC4011", "mapped_stage": "N2", "included": True},
            {"record_id": "SC4011", "mapped_stage": "REM", "included": True},
            {"record_id": "SC4011", "mapped_stage": "", "included": False},
        ]
    )

    predictions = majority_stage_predictions(labels)
    metrics = sleep_stage_metrics(predictions, model_name="majority")

    assert predictions[predictions["record_id"] == "SC4001"]["predicted_stage"].unique().tolist() == [
        "WAKE"
    ]
    assert set(metrics["record_id"]) == {"SC4001", "SC4011", "all"}
    overall = metrics[metrics["record_id"] == "all"].iloc[0]
    assert overall["epoch_count"] == 5
    assert 0.0 <= overall["macro_f1"] <= 1.0


def test_yasa_stage_mapping_and_alignment():
    assert [map_yasa_stage(stage) for stage in ["W", "WAKE", "N1", "N2", "N3", "R"]] == [
        "WAKE",
        "WAKE",
        "N1",
        "N2",
        "N3",
        "REM",
    ]
    labels = pd.DataFrame(
        [
            {"record_id": "SC4001", "epoch_index": 0, "mapped_stage": "WAKE", "included": True},
            {"record_id": "SC4001", "epoch_index": 1, "mapped_stage": "N1", "included": True},
            {"record_id": "SC4001", "epoch_index": 2, "mapped_stage": "", "included": False},
        ]
    )
    predictions = pd.DataFrame(
        [
            {"record_id": "SC4001", "epoch_index": 0, "predicted_stage": "WAKE"},
            {"record_id": "SC4001", "epoch_index": 1, "predicted_stage": "N2"},
            {"record_id": "SC4001", "epoch_index": 2, "predicted_stage": "N3"},
        ]
    )

    aligned = align_model_predictions(labels, predictions, model_name="yasa")
    assert aligned["predicted_stage"].tolist() == ["WAKE", "N2"]
    assert aligned["model"].tolist() == ["yasa", "yasa"]


def test_yasa_stage_mapping_rejects_unknown_label():
    with pytest.raises(ValueError):
        map_yasa_stage("UNKNOWN")


def test_yasa_profile_report_summarizes_runtime_gate_rows():
    profile = pd.DataFrame(
        [
            {
                "record_id": "SC4001",
                "status": "completed",
                "crop_seconds": 120,
                "timeout_seconds": 60,
                "wall_seconds": 12.5,
                "predicted_epochs": 4,
                "total_seconds": 12.0,
            },
            {
                "record_id": "SC4011",
                "status": "timeout",
                "crop_seconds": 120,
                "timeout_seconds": 60,
                "wall_seconds": 60.1,
            },
            {
                "record_id": "SC4021",
                "status": "error",
                "crop_seconds": 120,
                "timeout_seconds": 60,
                "wall_seconds": 1.0,
            },
        ]
    )

    report = build_yasa_profile_report(profile)
    assert "completed: 1" in report
    assert "timed out: 1" in report
    assert "errored: 1" in report
    assert "runtime gate, not a sleep-stage benchmark" in report


def test_sleep_quality_metrics_compute_continuity_from_stage_epochs():
    epochs = pd.DataFrame(
        [
            {"record_id": "SC4001", "epoch_index": 0, "mapped_stage": "WAKE", "included": True},
            {"record_id": "SC4001", "epoch_index": 1, "mapped_stage": "WAKE", "included": True},
            {"record_id": "SC4001", "epoch_index": 2, "mapped_stage": "N1", "included": True},
            {"record_id": "SC4001", "epoch_index": 3, "mapped_stage": "N2", "included": True},
            {"record_id": "SC4001", "epoch_index": 4, "mapped_stage": "WAKE", "included": True},
            {"record_id": "SC4001", "epoch_index": 5, "mapped_stage": "N3", "included": True},
            {"record_id": "SC4001", "epoch_index": 6, "mapped_stage": "REM", "included": True},
            {"record_id": "SC4001", "epoch_index": 7, "mapped_stage": "WAKE", "included": True},
            {"record_id": "SC4001", "epoch_index": 8, "mapped_stage": "WAKE", "included": True},
            {"record_id": "SC4001", "epoch_index": 9, "mapped_stage": "WAKE", "included": True},
            {"record_id": "SC4001", "epoch_index": 10, "mapped_stage": "", "included": False},
        ]
    )

    metrics = sleep_quality_metrics(
        epochs,
        stage_column="mapped_stage",
        source="reference",
        epoch_seconds=30.0,
    )
    row = metrics.iloc[0]
    assert row["included_minutes"] == pytest.approx(5.0)
    assert row["total_sleep_time_minutes"] == pytest.approx(2.0)
    assert row["recording_sleep_efficiency_pct"] == pytest.approx(40.0)
    assert row["sleep_onset_latency_proxy_minutes"] == pytest.approx(1.0)
    assert row["sleep_period_minutes"] == pytest.approx(2.5)
    assert row["sleep_period_efficiency_pct"] == pytest.approx(80.0)
    assert row["waso_minutes"] == pytest.approx(0.5)
    assert row["terminal_wake_minutes"] == pytest.approx(1.5)
    assert row["rem_latency_minutes"] == pytest.approx(2.0)
    assert row["awakening_count"] == 1
    assert row["longest_wake_bout_after_sleep_onset_minutes"] == pytest.approx(0.5)
    assert row["stage_transition_count"] == 4
    assert row["n3_pct_tst"] == pytest.approx(25.0)
    assert row["rem_pct_tst"] == pytest.approx(25.0)


def test_clinical_indicators_mark_disease_domains_as_not_diagnosed():
    metrics = pd.DataFrame(
        [
            {
                "record_id": "SC4001",
                "source": "reference",
                "total_sleep_time_minutes": 320.0,
                "sleep_period_efficiency_pct": 80.0,
                "waso_minutes": 70.0,
                "sleep_onset_latency_proxy_minutes": 35.0,
                "rem_latency_minutes": 45.0,
            }
        ]
    )

    indicators = build_clinical_indicators(metrics)
    statuses = set(indicators["status"])
    assert "screen_positive" in statuses
    assert "cannot_assess_from_stage_metrics" in statuses
    assert "cannot_diagnose_from_psg_alone" in statuses
    assert "not_recommended_from_this_dataset" in statuses


def test_scoped_sleep_edf_output_prefix_paths_are_validated():
    assert scoped_sleep_edf_output_path("five_record", "epoch_labels.csv").as_posix() == (
        "results/sleep_edf/five_record_epoch_labels.csv"
    )
    assert clean_output_prefix("pilot-1") == "pilot-1"
    with pytest.raises(ValueError):
        clean_output_prefix("../bad")


def test_yasa_discrepancy_table_counts_stage_pairs():
    labels = pd.DataFrame(
        [
            {"record_id": "SC4001", "epoch_index": 0, "mapped_stage": "WAKE", "included": True},
            {"record_id": "SC4001", "epoch_index": 1, "mapped_stage": "N2", "included": True},
            {"record_id": "SC4001", "epoch_index": 2, "mapped_stage": "REM", "included": True},
        ]
    )
    yasa = pd.DataFrame(
        [
            {"record_id": "SC4001", "epoch_index": 0, "predicted_stage": "WAKE"},
            {"record_id": "SC4001", "epoch_index": 1, "predicted_stage": "WAKE"},
            {"record_id": "SC4001", "epoch_index": 2, "predicted_stage": "REM"},
        ]
    )

    discrepancy = build_yasa_discrepancy_table(labels, yasa)
    assert set(discrepancy["pair_type"]) == {"agreement", "discrepancy"}
    n2_to_wake = discrepancy[
        (discrepancy["reference_stage"] == "N2") & (discrepancy["yasa_stage"] == "WAKE")
    ].iloc[0]
    assert n2_to_wake["epoch_count"] == 1
    assert n2_to_wake["pct_record_epochs"] == pytest.approx(100.0 / 3.0)


def test_clinical_question_ranking_prioritizes_low_continuity():
    metrics = pd.DataFrame(
        [
            {
                "record_id": "SC4001",
                "source": "reference",
                "total_sleep_time_minutes": 450.0,
                "sleep_period_efficiency_pct": 60.0,
                "waso_minutes": 180.0,
                "sleep_onset_latency_proxy_minutes": 20.0,
                "rem_latency_minutes": 90.0,
                "awakening_count": 30,
                "rem_pct_tst": 20.0,
                "n3_pct_tst": 15.0,
            }
        ]
    )

    ranking = build_clinical_question_ranking(metrics)
    top = ranking[ranking["rank"] == 1].iloc[0]
    assert top["clinical_question"] == "Is sleep continuity poor?"
    assert top["priority_score"] > 0


def test_run_sleep_edf_preflight_writes_selection_manifest_and_report(tmp_path):
    config = load_config("configs/sleep_edf/default.yaml")
    config["outputs"] = {
        "selection_csv": str(tmp_path / "results" / "sleep_edf_selection.csv"),
        "manifest_csv": str(tmp_path / "data/manifests/sleep_edf.csv"),
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


def test_download_updates_and_validates_manifest_checksums(tmp_path):
    source = tmp_path / "source.edf"
    source.write_bytes(b"edf bytes")
    local = tmp_path / "raw" / "SC4001E0-PSG.edf"

    result = download_file(source.resolve().as_uri(), local)
    assert result["status"] == "downloaded"
    assert local.read_bytes() == b"edf bytes"

    manifest = tmp_path / "manifest.csv"
    missing = tmp_path / "raw" / "SC4011E0-PSG.edf"
    manifest.write_text(
        "\n".join(
            [
                "dataset,version,doi,license,access_date,source_url,record_id,local_path,sha256,included,exclusion_reason",
                f"Sleep-EDF,1.0.0,doi,license,2026-06-22,{source.resolve().as_uri()},SC4001,{local.as_posix()},,true,",
                f"Sleep-EDF,1.0.0,doi,license,2026-06-22,{source.resolve().as_uri()},SC4011,{missing.as_posix()},,true,",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    update_manifest_checksums(manifest, records=["SC4001"])
    validation = validate_sleep_edf_manifest(manifest, records=["SC4001"])
    assert validation["exists"].tolist() == [True]
    assert validation["checksum_ok"].tolist() == [True]
    updated_manifest = manifest.read_text(encoding="utf-8")
    assert result["sha256"] in updated_manifest
