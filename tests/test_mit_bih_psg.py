import math

import numpy as np
import pandas as pd
import pytest

from physio_signal_lab.io.mit_bih_psg import (
    build_mit_bih_psg_manifest,
    update_mit_bih_psg_manifest_checksums,
    validate_mit_bih_psg_manifest,
)
from physio_signal_lab.mit_bih_psg import (
    _count_threshold_segments,
    _count_desaturation_events,
    _pre_event_rolling_baseline,
    _sleep_sample_mask,
    build_dataset_decision_report,
    clinical_indicators,
    dataset_readiness,
    oxygen_artifact_review,
    parse_aux_note,
    respiratory_metrics,
    source_ahi_alignment,
)


STAGE_MAPPING = {
    "W": "WAKE",
    "1": "N1",
    "2": "N2",
    "3": "N3",
    "4": "N3",
    "R": "REM",
}


def test_mit_bih_checksum_update_ignores_skipped_existing_files(tmp_path):
    local = tmp_path / "slp01a.hea"
    local.write_text("corrupted", encoding="utf-8")
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(
        "\n".join(
            [
                "dataset,version,doi,license,access_date,source_url,record_id,local_path,sha256,included,exclusion_reason",
                f"MIT-BIH PSG,1.0.0,doi,license,2026-06-23,file://source,slp01a,{local.as_posix()},,true,",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    summary = pd.DataFrame(
        [
            {
                "record_id": "slp01a",
                "file_extension": "hea",
                "local_path": local.as_posix(),
                "status": "skipped_existing",
                "local_observed_sha256": "observed",
            }
        ]
    )

    update_mit_bih_psg_manifest_checksums(manifest, download_results=summary)
    validation = validate_mit_bih_psg_manifest(manifest)

    assert validation["checksum_ok"].tolist() == [False]
    assert "observed" not in manifest.read_text(encoding="utf-8")


def test_parse_aux_note_maps_stage_and_event_tokens():
    parsed = parse_aux_note(
        "4 LA LA",
        stage_mapping=STAGE_MAPPING,
        excluded_stage_tokens={"MT"},
    )

    assert parsed.sleep_stage_raw == "4"
    assert parsed.mapped_stage == "N3"
    assert parsed.included
    assert parsed.included_sleep
    assert parsed.event_tokens == ("LA", "LA")


def test_parse_aux_note_excludes_movement_time_with_respiratory_event():
    parsed = parse_aux_note(
        "MT X",
        stage_mapping=STAGE_MAPPING,
        excluded_stage_tokens={"MT"},
    )

    assert parsed.sleep_stage_raw == "MT"
    assert parsed.mapped_stage == ""
    assert not parsed.included
    assert not parsed.included_sleep
    assert parsed.event_tokens == ("X",)


def test_respiratory_metrics_count_sleep_events_per_sleep_hour():
    epochs = pd.DataFrame(
        [
            {
                "record_id": "slp01a",
                "mapped_stage": "WAKE",
                "included": True,
                "included_sleep": False,
                "respiratory_event_count": 1,
                "respiratory_event_epoch": True,
                "hypopnea_count": 1,
                "obstructive_apnea_count": 0,
                "central_apnea_count": 0,
                "arousal_associated_respiratory_count": 0,
            },
            {
                "record_id": "slp01a",
                "mapped_stage": "N2",
                "included": True,
                "included_sleep": True,
                "respiratory_event_count": 1,
                "respiratory_event_epoch": True,
                "hypopnea_count": 0,
                "obstructive_apnea_count": 1,
                "central_apnea_count": 0,
                "arousal_associated_respiratory_count": 0,
            },
            {
                "record_id": "slp01a",
                "mapped_stage": "REM",
                "included": True,
                "included_sleep": True,
                "respiratory_event_count": 1,
                "respiratory_event_epoch": True,
                "hypopnea_count": 1,
                "obstructive_apnea_count": 0,
                "central_apnea_count": 0,
                "arousal_associated_respiratory_count": 1,
            },
        ]
    )

    metrics = respiratory_metrics(
        epochs,
        source_reported_ahi={"slp01a": 17.0},
        epoch_seconds=30.0,
    )
    row = metrics.iloc[0]

    assert row["sleep_minutes"] == pytest.approx(1.0)
    assert row["sleep_respiratory_event_count"] == 2
    assert row["all_epoch_respiratory_event_count"] == 3
    assert row["ahi_style_events_per_sleep_hour"] == pytest.approx(120.0)
    assert row["obstructive_apnea_events_per_sleep_hour"] == pytest.approx(60.0)
    assert row["hypopnea_events_per_sleep_hour"] == pytest.approx(60.0)
    assert row["ahi_style_learning_severity"] == "severe_range"
    assert row["source_ahi_alignment_status"] == "needs_manual_review"


def test_respiratory_metrics_return_nan_when_no_sleep_epochs():
    epochs = pd.DataFrame(
        [
            {
                "record_id": "slp00",
                "mapped_stage": "WAKE",
                "included": True,
                "included_sleep": False,
                "respiratory_event_count": 0,
                "respiratory_event_epoch": False,
                "hypopnea_count": 0,
                "obstructive_apnea_count": 0,
                "central_apnea_count": 0,
                "arousal_associated_respiratory_count": 0,
            }
        ]
    )

    metrics = respiratory_metrics(epochs, source_reported_ahi={}, epoch_seconds=30.0)

    assert math.isnan(float(metrics.iloc[0]["ahi_style_events_per_sleep_hour"]))
    assert metrics.iloc[0]["ahi_style_learning_severity"] == "unavailable"


def test_source_ahi_alignment_separates_estimated_source_records():
    metrics = pd.DataFrame(
        [
            {
                "record_id": "slp67x",
                "ahi_style_events_per_sleep_hour": 79.0,
                "source_reported_ahi": 0.7,
                "ahi_style_minus_source_reported_ahi": 78.3,
                "source_ahi_alignment_status": "needs_manual_review",
                "source_ahi_note": "",
                "sleep_respiratory_event_count": 54,
                "sleep_hours": 0.6833333333333333,
                "hypopnea_events_per_sleep_hour": 60.0,
                "obstructive_apnea_events_per_sleep_hour": 19.0,
                "central_apnea_events_per_sleep_hour": 0.0,
            },
            {
                "record_id": "slp41",
                "ahi_style_events_per_sleep_hour": 0.0,
                "source_reported_ahi": 60.0,
                "ahi_style_minus_source_reported_ahi": -60.0,
                "source_ahi_alignment_status": "source_ahi_estimated_annotation_unavailable",
                "source_ahi_note": "estimated_from_visual_review_apnea_annotations_unavailable",
                "sleep_respiratory_event_count": 0,
                "sleep_hours": 2.0,
                "hypopnea_events_per_sleep_hour": 0.0,
                "obstructive_apnea_events_per_sleep_hour": 0.0,
                "central_apnea_events_per_sleep_hour": 0.0,
            },
        ]
    )

    alignment = source_ahi_alignment(metrics)
    by_record = alignment.set_index("record_id")

    assert by_record.loc["slp67x", "review_priority"] == "manual_review_high"
    assert by_record.loc["slp67x", "dominant_respiratory_event_type"] == "hypopnea"
    assert by_record.loc["slp41", "review_priority"] == "separate_source_review"
    assert "do not interpret annotation burden" in by_record.loc["slp41", "review_focus"]


def test_clinical_indicators_mark_missing_spo2_boundary():
    metrics = pd.DataFrame(
        [
            {
                "record_id": "slp01a",
                "ahi_style_events_per_sleep_hour": 17.0,
                "ahi_style_learning_severity": "moderate_range",
                "ahi_style_minus_source_reported_ahi": 2.0,
                "source_ahi_alignment_status": "roughly_aligned",
            }
        ]
    )
    quality = pd.DataFrame(
        [
            {
                "record_id": "slp01a",
                "is_respiration_channel": True,
                "is_spo2_channel": False,
                "has_dynamic_signal": True,
            }
        ]
    )

    indicators = clinical_indicators(metrics, quality)

    statuses = set(indicators["status"])
    assert "screen_positive_learning_signal" in statuses
    assert "not_available_in_record" in statuses
    assert "educational_question_only" in statuses


def test_count_threshold_segments_enforces_minimum_duration():
    mask = [False, True, True, False, True, True, True, True, False]

    count, seconds = _count_threshold_segments(
        mask,
        fs=1.0,
        min_duration_seconds=3.0,
    )

    assert count == 1
    assert seconds == pytest.approx(4.0)


def test_sleep_sample_mask_keeps_wake_samples_out_and_clips_epochs():
    epochs = pd.DataFrame(
        [
            {"included_sleep": False, "onset_seconds": 0.0, "epoch_seconds": 2.0},
            {"included_sleep": True, "onset_seconds": 2.0, "epoch_seconds": 3.0},
            {"included_sleep": True, "onset_seconds": 6.0, "epoch_seconds": 10.0},
        ]
    )

    mask = _sleep_sample_mask(epochs, sample_count=10, fs=1.0)

    np.testing.assert_array_equal(
        mask,
        np.array([False, False, True, True, True, False, True, True, True, True]),
    )


def test_pre_event_desaturation_scorer_uses_local_baseline_and_sleep_scope():
    signal = np.array([96, 96, 96, 92, 92, 92, 96, 96], dtype=float)
    plausible = np.ones(signal.shape, dtype=bool)
    sleep_scope = np.array([False, False, True, True, True, True, True, True])

    baseline = _pre_event_rolling_baseline(
        signal,
        plausible,
        fs=1.0,
        baseline_window_seconds=3.0,
    )
    count, seconds = _count_desaturation_events(
        signal,
        baseline=baseline,
        plausible=plausible,
        scope=sleep_scope,
        fs=1.0,
        drop_pct=3.0,
        min_duration_seconds=2.0,
    )

    assert count == 1
    assert seconds == pytest.approx(3.0)


def test_clinical_indicators_include_oxygen_desaturation_when_available():
    metrics = pd.DataFrame(
        [
            {
                "record_id": "slp59",
                "ahi_style_events_per_sleep_hour": 55.3,
                "ahi_style_learning_severity": "severe_range",
                "ahi_style_minus_source_reported_ahi": 0.0,
                "source_ahi_alignment_status": "roughly_aligned",
            }
        ]
    )
    quality = pd.DataFrame(
        [
            {
                "record_id": "slp59",
                "is_respiration_channel": True,
                "is_spo2_channel": True,
                "has_dynamic_signal": True,
            }
        ]
    )
    oxygen = pd.DataFrame(
        [
            {
                "record_id": "slp59",
                "oxygen_status": "available",
                "sleep_odi_3pct_events_per_hour": 12.5,
                "sleep_odi_4pct_events_per_hour": 7.5,
                "sleep_desaturation_3pct_events_per_sleep_hour_proxy": 14.5,
                "desaturation_3pct_events_per_sleep_hour_proxy": 99.9,
                "time_below_90pct_pct_sleep": 2.5,
                "time_below_90pct_pct_recording": 88.8,
            }
        ]
    )

    indicators = clinical_indicators(metrics, quality, oxygen)
    oxygen_row = indicators[indicators["indicator"] == "spo2_desaturation_burden"].iloc[0]

    assert oxygen_row["status"] == "oxygen_desaturation_available"
    assert "12.5" in oxygen_row["evidence"]
    assert "7.5" in oxygen_row["evidence"]
    assert "2.5" in oxygen_row["evidence"]
    assert "14.5" not in oxygen_row["evidence"]
    assert "99.9" not in oxygen_row["evidence"]
    assert "88.8" not in oxygen_row["evidence"]


def test_oxygen_artifact_review_flags_implausible_or_disagreeing_odi():
    oxygen = pd.DataFrame(
        [
            {
                "record_id": "slp66",
                "oxygen_status": "available",
                "sleep_plausible_fraction_pct": 91.0,
                "min_spo2_pct": 48.0,
                "time_below_90pct_pct_sleep": 42.0,
                "sleep_odi_3pct_events_per_hour": 53.2,
                "sleep_odi_4pct_events_per_hour": 24.1,
                "sleep_desaturation_3pct_events_per_sleep_hour_proxy": 10.0,
            },
            {
                "record_id": "slp01a",
                "oxygen_status": "no_spo2_channel",
            },
        ]
    )

    review = oxygen_artifact_review(oxygen).set_index("record_id")

    assert review.loc["slp66", "oxygen_review_status"] == "artifact_review_recommended"
    assert review.loc["slp66", "review_priority"] == "high"
    assert "very_low_spo2_value" in review.loc["slp66", "review_flags"]
    assert review.loc["slp01a", "oxygen_review_status"] == "not_available"


def test_dataset_readiness_separates_ready_and_manual_review_records():
    metrics = pd.DataFrame(
        [
            {"record_id": "slp60", "ahi_style_learning_severity": "severe_range"},
            {"record_id": "slp66", "ahi_style_learning_severity": "severe_range"},
            {"record_id": "slp41", "ahi_style_learning_severity": "minimal_range"},
        ]
    )
    source_alignment = pd.DataFrame(
        [
            {
                "record_id": "slp60",
                "alignment_status": "roughly_aligned",
                "review_priority": "low",
                "delta_events_per_sleep_hour": 2.0,
            },
            {
                "record_id": "slp66",
                "alignment_status": "needs_manual_review",
                "review_priority": "manual_review_high",
                "delta_events_per_sleep_hour": 34.0,
            },
            {
                "record_id": "slp41",
                "alignment_status": "source_ahi_estimated_annotation_unavailable",
                "review_priority": "separate_source_review",
                "delta_events_per_sleep_hour": math.nan,
            },
        ]
    )
    oxygen = pd.DataFrame(
        [
            {"record_id": "slp60", "oxygen_status": "available"},
            {"record_id": "slp66", "oxygen_status": "available"},
            {"record_id": "slp41", "oxygen_status": "no_spo2_channel"},
        ]
    )
    oxygen_review = pd.DataFrame(
        [
            {
                "record_id": "slp60",
                "oxygen_review_status": "oxygen_review_ready",
                "review_priority": "low",
            },
            {
                "record_id": "slp66",
                "oxygen_review_status": "artifact_review_recommended",
                "review_priority": "medium",
            },
            {
                "record_id": "slp41",
                "oxygen_review_status": "not_available",
                "review_priority": "none",
            },
        ]
    )
    quality = pd.DataFrame(
        [
            {
                "record_id": record_id,
                "is_respiration_channel": True,
                "has_dynamic_signal": True,
            }
            for record_id in ["slp60", "slp66", "slp41"]
        ]
    )

    readiness = dataset_readiness(
        metrics=metrics,
        source_alignment=source_alignment,
        oxygen=oxygen,
        oxygen_review=oxygen_review,
        quality=quality,
    ).set_index("record_id")

    assert (
        readiness.loc["slp60", "clinical_style_example_tier"]
        == "respiratory_plus_oxygen_learning_ready"
    )
    assert readiness.loc["slp60", "oxygen_learning_ready"]
    assert (
        readiness.loc["slp66", "clinical_style_example_tier"]
        == "manual_source_alignment_needed"
    )
    assert "source_ahi_alignment_needs_manual_review" in readiness.loc[
        "slp66",
        "main_limitations",
    ]
    assert readiness.loc["slp41", "clinical_style_example_tier"] == "source_context_only"

    decision = build_dataset_decision_report(
        records=["slp60", "slp66", "slp41"],
        readiness=readiness.reset_index(),
        source_alignment=source_alignment,
        oxygen_review=oxygen_review,
    )

    assert "Do not automatically add a richer PSG dataset" in decision
    assert "slp66" in decision


def test_build_mit_bih_psg_manifest_uses_physionet_record_files():
    config = {
        "dataset": {
            "name": "MIT-BIH Polysomnographic Database",
            "version": "1.0.0",
            "doi": "https://doi.org/10.13026/C23K5S",
            "license": "Open Data Commons Attribution License v1.0",
            "access_date": "2026-06-23",
            "source_base_url": "https://physionet.org/files/slpdb/1.0.0",
            "raw_dir": "data/raw/mit-bih-psg/1.0.0",
        },
        "selection": {
            "pilot_records": ["slp01a"],
            "files": ["hea", "dat", "st", "ecg"],
        },
    }

    manifest = build_mit_bih_psg_manifest(config)

    assert manifest["record_id"].tolist() == ["slp01a", "slp01a", "slp01a", "slp01a"]
    assert manifest["source_url"].tolist() == [
        "https://physionet.org/files/slpdb/1.0.0/slp01a.hea",
        "https://physionet.org/files/slpdb/1.0.0/slp01a.dat",
        "https://physionet.org/files/slpdb/1.0.0/slp01a.st",
        "https://physionet.org/files/slpdb/1.0.0/slp01a.ecg",
    ]
