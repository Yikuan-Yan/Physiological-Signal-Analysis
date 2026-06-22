# Sleep-EDF Next Work Plan

## Current State

The Fantasia ECG/HRV core is complete and frozen at `hrv-core-v0.1.0`. Sleep-EDF has passed protocol preflight, pilot data access, epoch-label alignment, majority-stage baseline benchmarking, and opt-in YASA pilot benchmarking for `SC4001` and `SC4011`.

The YASA runtime gate is now passed for the two-record pilot in a Python 3.12 sleep-extra environment. The implementation runs YASA in a child process with a hard timeout, writes a runtime profile, and commits YASA metrics only after aligned predictions are produced for all included pilot epochs.

The next frozen download batch is also complete: `SC4021`, `SC4031`, and `SC4041` were downloaded and checksum-validated. Raw EDF files remain ignored under `data/raw/`.

No sleep-quality, diagnostic, clinical, or event-detector accuracy claims are in scope.

## Completed In This Stage

- Added `profile-yasa-runtime` for bounded YASA profiling.
- Added a YASA worker subprocess to isolate imports, EDF read, `SleepStaging`, prediction, probability extraction, and CSV writes.
- Replaced in-process `--include-yasa` benchmark execution with the bounded worker path.
- Added support for YASA 0.7 `Hypnogram` outputs and `WAKE` labels.
- Generated pilot YASA outputs:
  - `results/sleep_edf/pilot_yasa_predictions.csv`
  - `results/sleep_edf/pilot_yasa_probabilities.csv`
  - `results/sleep_edf/pilot_yasa_metrics.csv`
  - `reports/sleep_edf_yasa_profile.md`
  - `reports/sleep_edf_yasa_runtime_gate.md`
- Downloaded and validated:
  - `SC4021`
  - `SC4031`
  - `SC4041`

## Current Pilot Results

Pilot YASA metrics for `SC4001` and `SC4011`:

| records | epochs | accuracy | balanced accuracy | macro-F1 | Cohen's kappa |
| --- | --- | --- | --- | --- | --- |
| SC4001, SC4011 | 5452 | 0.744 | 0.667 | 0.595 | 0.544 |

The majority-stage baseline remains the comparison floor:

| records | epochs | accuracy | balanced accuracy | macro-F1 | Cohen's kappa |
| --- | --- | --- | --- | --- | --- |
| SC4001, SC4011 | 5452 | 0.707 | 0.200 | 0.166 | 0.000 |

## Compatibility Caveat

YASA 0.7.0 emits a scikit-learn `InconsistentVersionWarning` because its bundled estimator was pickled with scikit-learn 0.24.2 and is currently loaded with scikit-learn 1.9.0. Treat YASA metrics as a local benchmark result with a reproducibility caveat until the model/runtime version pairing is pinned or cross-checked.

## Next Workstreams

### Track A: Expand Data Downloads

Continue downloading the frozen Sleep Cassette benchmark records in small batches and validate each batch immediately:

```bash
uv run python -m physio_signal_lab.cli download-sleep-edf --config configs/sleep_edf.yaml --records SC4051,SC4061,SC4071
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4051,SC4061,SC4071

uv run python -m physio_signal_lab.cli download-sleep-edf --config configs/sleep_edf.yaml --records SC4081,SC4091,SC4101
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4081,SC4091,SC4101

uv run python -m physio_signal_lab.cli download-sleep-edf --config configs/sleep_edf.yaml --records SC4111,SC4121,SC4131
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4111,SC4121,SC4131

uv run python -m physio_signal_lab.cli download-sleep-edf --config configs/sleep_edf.yaml --records SC4141,SC4151,SC4161
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4141,SC4151,SC4161

uv run python -m physio_signal_lab.cli download-sleep-edf --config configs/sleep_edf.yaml --records SC4171,SC4181,SC4191
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4171,SC4181,SC4191
```

Acceptance gate:

- all selected EDF files exist locally;
- `data_manifest_sleep_edf.csv` has SHA256 entries for all selected rows;
- validation reports `missing_files=0` and `checksum_mismatches=0`;
- raw EDF files remain ignored under `data/raw/`.

### Track B: Generalize Benchmark Outputs

The current command can run arbitrary record overrides, but the output names are still pilot-oriented. Before evaluating more records, split the benchmark outputs by scope so expanded runs do not overwrite the pilot artifacts.

Recommended implementation:

- keep current `pilot_*` outputs for `SC4001,SC4011`;
- add an expanded benchmark command or `--output-prefix`;
- write per-scope labels, predictions, probabilities, metrics, and reports;
- keep the YASA child-process timeout gate for every expanded run.

### Track C: Expanded Baseline And YASA Evaluation

After output names are generalized, run an expanded benchmark in two layers:

```bash
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041
uv run python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041
uv run python -m physio_signal_lab.cli profile-yasa-runtime --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041 --full-night --timeout-seconds 180
uv run python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041 --include-yasa
```

Use scope-specific output paths before committing those expanded metrics.

## Claim Review Checklist

Before publishing any Sleep-EDF report:

- use "reference label" rather than "ground truth";
- state that Sleep-EDF labels are R&K-derived manual annotations;
- state that R&K stage 3 and 4 are mapped to N3;
- report channel mismatch for YASA because Sleep-EDF uses Fpz-Cz/Pz-Oz rather than preferred central derivations;
- compare against majority-stage baseline;
- include macro-F1, balanced accuracy, Cohen's kappa, and per-stage metrics;
- avoid sleep-quality, disease, clinical, or treatment claims;
- avoid event-detector accuracy claims for spindles or slow waves.

## Immediate Next Actions

1. Commit the completed YASA runtime gate, pilot YASA outputs, and validated `SC4021`/`SC4031`/`SC4041` manifest updates.
2. Add scope-specific benchmark output paths before running 5-record or 20-record metrics.
3. Continue the next download batch: `SC4051,SC4061,SC4071`.
