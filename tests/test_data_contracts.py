from pathlib import Path

import numpy as np
import pytest

from physio_signal_lab.io.fantasia import (
    build_inventory,
    load_record,
    record_ids_from_manifest,
)
from physio_signal_lab.manifest import validate_manifest


ROOT = Path("data/raw/fantasia/1.0.0")
MANIFEST = Path("data_manifest.csv")


pytestmark = pytest.mark.skipif(
    not ROOT.exists() or not MANIFEST.exists(),
    reason="Fantasia raw data is not available in this environment",
)


def test_manifest_validates_downloaded_fantasia_files():
    result = validate_manifest(MANIFEST)
    assert result.ok
    assert result.record_count == 40
    assert result.missing_files == ()
    assert result.checksum_mismatches == ()
    assert result.missing_record_files == ()


def test_pilot_records_have_expected_ecg_contract():
    for record_id in ("f1y01", "f1o01"):
        record = load_record(record_id, ROOT)
        assert record.sampling_rate_hz == 250
        assert record.ecg.ndim == 1
        assert record.ecg.size > 250 * 60 * 100
        assert record.reference_peak_samples.ndim == 1
        assert record.reference_peak_samples.size > 1000
        assert record.reference_peak_samples[0] >= 0
        assert record.reference_peak_samples[-1] < record.ecg.size
        assert record.ecg_nonfinite_count == 0


def test_f2o02_nonfinite_ecg_segment_is_repaired_and_reported():
    record = load_record("f2o02", ROOT)
    assert record.ecg_nonfinite_count == 39
    assert record.ecg.ndim == 1
    assert record.ecg.size == 1757482
    assert record.ecg_nonfinite_count > 0
    assert record.ecg_nonfinite_count / record.ecg.size < 0.001
    assert np.isfinite(record.ecg).all()


def test_inventory_covers_all_records():
    record_ids = record_ids_from_manifest(MANIFEST)
    inventory = build_inventory(record_ids, ROOT)
    assert len(inventory) == 40
    assert set(inventory["sampling_rate_hz"]) == {250.0, 333.0}
    assert inventory.loc[inventory["record_id"] == "f2y02", "sampling_rate_hz"].item() == 333
    assert set(inventory["cohort"]) == {"old", "young"}
    assert inventory["annotation_count"].min() > 1000
    assert inventory["duration_minutes"].between(100, 130).all()
    assert inventory["ecg_nonfinite_count"].sum() == 4217
    assert inventory["ecg_nonfinite_fraction"].max() < 0.002
