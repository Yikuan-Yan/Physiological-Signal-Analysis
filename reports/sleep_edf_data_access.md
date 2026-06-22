# Sleep-EDF Data Access Report

## Scope

This data-access stage verifies the selected Sleep-EDF pilot subset after the preflight protocol freeze. It does not run YASA, score sleep, evaluate sleep quality, or make clinical claims.

## Completed Data

- Dataset: Sleep-EDF Database Expanded v1.0.0.
- Cohort: Sleep Cassette only.
- Pilot records downloaded: `SC4001`, `SC4011`.
- Files downloaded: 4 EDF files, 2 PSG and 2 Hypnogram files.
- Total local bytes validated: 99,457,092.
- Raw files are stored under `data/raw/sleep-edfx/1.0.0/sleep-cassette/` and remain ignored by git.

## Validation

```bash
uv run python -m physio_signal_lab.cli download-sleep-edf --config configs/sleep_edf.yaml --records SC4001,SC4011
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4001,SC4011
```

The pilot validation output reported:

- rows: 4
- missing files: 0
- checksum mismatches: 0
- bytes: 99,457,092

The pilot SHA256 values are recorded in `data_manifest_sleep_edf.csv`. The remaining frozen benchmark records keep blank SHA256 values until those raw files are downloaded.

## Current Boundary

The full frozen 20-participant benchmark selection remains unchanged in `results/sleep_edf/sleep_edf_selection.csv`. Downloading the remaining 18 participants should continue with the same resumable command, in small batches if the PhysioNet connection is slow.

Next implementation step: after all selected raw files validate, implement EDF reading, 30 s hypnogram alignment, majority-stage baseline, and YASA staging benchmark outputs.
