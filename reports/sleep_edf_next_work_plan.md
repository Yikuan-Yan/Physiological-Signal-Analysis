# Sleep-EDF Next Work Plan

## Current State

The Fantasia ECG/HRV core is complete and frozen at `hrv-core-v0.1.0`. Sleep-EDF has passed protocol preflight, pilot data access, epoch-label alignment, and majority-stage baseline benchmarking for `SC4001` and `SC4011`.

YASA is available in a Python 3.12 sleep-extra environment, but local YASA execution is still runtime-gated. Full pilot YASA and a 10 min smoke crop both timed out, so no YASA metrics are treated as valid yet.

## Goal

Move from pilot baseline to a reproducible 20-participant Sleep-EDF benchmark with:

- frozen Sleep Cassette participant selection;
- checked PSG/Hypnogram files and SHA256 manifest entries;
- majority-stage baseline;
- YASA staging, if the runtime gate is resolved;
- per-subject metrics and participant-level uncertainty;
- explicit limitations around R&K labels, channel mismatch, and scorer uncertainty.

No sleep-quality, diagnostic, clinical, or event-detector accuracy claims are in scope.

## Parallel Workstreams

### Track A: YASA Runtime Profiling Gate

Purpose: determine whether YASA can run locally in a bounded, reproducible way before any YASA metrics are committed.

Recommended steps:

1. Create/sync the Python 3.12 sleep environment:

```bash
uv sync --python 3.12 --extra sleep --extra dev
```

2. Add a profiling script or command that times these stages separately:

- EDF read;
- channel picking;
- raw crop;
- `yasa.SleepStaging(...)` construction;
- feature extraction / `predict()`;
- `predict_proba()`;
- CSV write.

3. Start with a very small crop, then increase only if each gate passes:

- `SC4001`, first 2 min;
- `SC4001`, first 10 min;
- `SC4001`, first 30 min;
- `SC4001`, full night;
- `SC4001` + `SC4011`.

4. Record elapsed time, peak memory if available, package versions, and whether output epoch counts match the aligned epoch table.

Acceptance gate:

- a bounded pilot YASA run completes end-to-end;
- predictions cover all included pilot epochs;
- probabilities align one row per predicted epoch;
- no YASA metrics are committed unless the aligned outputs are complete.

Fallback if blocked:

- try a clean Python 3.12 environment outside the project `.venv`;
- limit thread counts with environment variables such as `OMP_NUM_THREADS=1`;
- test WSL/Linux if Windows execution remains stalled;
- keep the baseline benchmark as the only committed model result until YASA completes.

### Track B: Remaining Sleep-EDF Data Download

Purpose: download and validate the remaining frozen Sleep Cassette records while Track A investigates runtime.

This can run in parallel with Track A because it is mostly network and disk I/O, while YASA profiling is compute-bound. Avoid running large checksum updates at the exact same time as profiling if disk contention becomes visible.

Recommended batches:

```bash
uv run python -m physio_signal_lab.cli download-sleep-edf --config configs/sleep_edf.yaml --records SC4021,SC4031,SC4041
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4021,SC4031,SC4041

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

- all 40 selected EDF files exist locally;
- `data_manifest_sleep_edf.csv` has SHA256 for all selected rows;
- full validation reports `missing_files=0` and `checksum_mismatches=0`;
- raw EDF files remain ignored under `data/raw/`.

### Track C: Full Benchmark Integration

Purpose: merge Track A and Track B only after both are ready.

Baseline path:

```bash
uv run python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf.yaml --records SC4001,SC4011
```

Future full-selection path:

```bash
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml
uv run python -m physio_signal_lab.cli run-sleep-edf-benchmark --config configs/sleep_edf.yaml
```

YASA path, only after Track A passes:

```bash
uv run --python 3.12 --extra sleep python -m physio_signal_lab.cli run-sleep-edf-benchmark --config configs/sleep_edf.yaml --include-yasa
```

Expected outputs:

- per-epoch reference labels;
- majority baseline predictions;
- YASA predictions and probabilities, if available;
- per-subject metrics;
- overall metrics;
- participant-level bootstrap confidence intervals;
- failure/error-review candidate epochs.

## Order Of Execution

1. Start Track B downloads in small batches.
2. While downloads run, implement Track A profiling instrumentation.
3. Validate each downloaded batch immediately.
4. Do not run full 20-subject YASA until Track A passes on pilot.
5. Once all data validates, run full baseline benchmark.
6. Once YASA is runtime-stable, add YASA metrics.
7. Write the Sleep-EDF benchmark report.
8. Freeze a new release/tag only after the benchmark report passes claim review.

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

Recommended next action:

1. Add a bounded YASA profiling command.
2. In parallel, download the next batch: `SC4021,SC4031,SC4041`.
3. Validate that batch and update `data_manifest_sleep_edf.csv`.
4. Use the profiling result to decide whether YASA stays local, moves to WSL/Linux, or remains deferred.
