# Repository Structure

This repository is organized by analysis domain and artifact type. The root is kept for project-level engineering files only.

## Top-Level Layout

- `configs/`: runnable YAML configurations grouped by domain.
- `data/manifests/`: tracked provenance, checksum, and local-path manifests. Raw waveform data stays out of git under `data/raw/`.
- `docs/`: durable project documentation and long-range plans.
- `figures/`: tracked visual outputs grouped by domain.
- `reports/`: human-readable analysis reports grouped by domain.
- `results/`: tracked CSV outputs grouped by domain.
- `src/physio_signal_lab/`: Python package source.
- `tests/`: pytest coverage for data contracts, numerical logic, reports, and CLI-facing workflows.
- `releases/`: frozen release bundles. These may intentionally preserve older internal names for reproducibility.

## Domain Layout

- `configs/hrv/core.yaml`
- `configs/sleep_edf/default.yaml`
- `configs/mit_bih_psg/default.yaml`
- `reports/hrv/`
- `reports/sleep_edf/`
- `reports/mit_bih_psg/`
- `reports/project/`
- `results/hrv/`
- `results/sleep_edf/`
- `results/mit_bih_psg/`
- `figures/hrv/`
- `figures/sleep_edf/`
- `figures/mit_bih_psg/`

## Naming Rules

- Domain directories use stable dataset or analysis names: `hrv`, `sleep_edf`, `mit_bih_psg`.
- Default runnable configs are named `default.yaml`, except single-stage core workflows such as `hrv/core.yaml`.
- Reports use concise names inside domain folders instead of repeating the domain prefix.
- Result CSVs keep their workflow prefix when multiple batch sizes or record sets coexist.
- Release bundle internals are treated as frozen artifacts and are not used as current-path examples.

## Current Entry Points

```bash
uv run python -m physio_signal_lab.cli validate-data --manifest data/manifests/fantasia.csv
uv run python -m physio_signal_lab.cli run-ecg-core --config configs/hrv/core.yaml
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf/default.yaml
uv run python -m physio_signal_lab.cli validate-mit-bih-psg --config configs/mit_bih_psg/default.yaml
```
