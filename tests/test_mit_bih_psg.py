import math

import numpy as np
import pandas as pd
import pytest

from physio_signal_lab.io.mit_bih_psg import build_mit_bih_psg_manifest
from physio_signal_lab.mit_bih_psg import (
    _count_threshold_segments,
    _sleep_sample_mask,
    clinical_indicators,
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


def test_clinical_indicators_include_oxygen_proxy_when_available():
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
                "sleep_desaturation_3pct_events_per_sleep_hour_proxy": 14.5,
                "desaturation_3pct_events_per_sleep_hour_proxy": 99.9,
                "time_below_90pct_pct_sleep": 2.5,
                "time_below_90pct_pct_recording": 88.8,
            }
        ]
    )

    indicators = clinical_indicators(metrics, quality, oxygen)
    oxygen_row = indicators[indicators["indicator"] == "spo2_desaturation_burden"].iloc[0]

    assert oxygen_row["status"] == "oxygen_proxy_available"
    assert "14.5" in oxygen_row["evidence"]
    assert "2.5" in oxygen_row["evidence"]
    assert "99.9" not in oxygen_row["evidence"]
    assert "88.8" not in oxygen_row["evidence"]


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
