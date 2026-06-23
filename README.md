# Physio Signal Lab

An auditable public-data physiological signal analysis toolkit covering ECG/HRV method validation, Sleep-EDF sleep staging evaluation, and MIT-BIH PSG respiratory/SpO2 educational analysis.

> **Scope boundary:** this repository is a research and education prototype, not clinical decision-support software. Raw waveform data are excluded from the repository. Tracked CSV files, figures, and reports are audit artifacts and should not be interpreted as a fresh raw-waveform rerun in every checkout.

## Project Goals

This repository organizes public physiological signal analysis into traceable workflows rather than isolated notebooks:

- YAML files define dataset selections, algorithm parameters, and output paths.
- Manifests record source URLs, local paths, SHA-256 values, and inclusion status.
- A CLI runs validation, benchmark, feature extraction, reporting, and release tasks.
- Machine-readable CSV files, explanatory figures, and Markdown reports are retained for audit.
- Tests cover core numerical logic, data contracts, report gates, and release behavior.

## Core Pipelines

| Pipeline | Dataset | Implemented workflow | Current scope |
| --- | --- | --- | --- |
| ECG / HRV | [Fantasia Database](https://physionet.org/content/fantasia/1.0.0/) | ECG inventory, NeuroKit2 R-peak benchmark, RR/NN filtering, time/frequency-domain HRV, artifact sensitivity, record-level bootstrap uncertainty, gated report | 40 records |
| Sleep staging | [Sleep-EDF Expanded](https://physionet.org/content/sleep-edfx/1.0.0/) | R&K to 5-stage mapping, global-majority baseline, YASA staging, per-stage metrics, sleep-quality proxies, discrepancy reports | First available Sleep Cassette night for subjects 400-419, 20 records |
| Respiratory / SpO2 | [MIT-BIH Polysomnographic Database](https://physionet.org/content/slpdb/1.0.0/) | `.st` annotation parsing, AHI-style burden, source-AHI alignment, SpO2/ODI proxy, event windows, dataset-readiness gate | All 18 records; 5 records include an oxygen channel |

## Method Boundaries

- HRV downstream metrics use reference annotations to construct RR/NN intervals. NeuroKit2 detected peaks are used for detector benchmarking; detector error is not yet propagated into HRV outputs.
- The per-record majority baseline is a descriptive target-aware oracle. The benchmark also includes a real global majority-stage baseline.
- MIT-BIH AHI-style burden and ODI proxy outputs are educational proxies. This repository does not implement a validated clinical hypopnea scoring workflow.
- Model-derived sleep staging, respiratory annotation burden, and oxygen proxies are not diagnoses or treatment recommendations.

## Tracked Result Snapshot

The following values are read from tracked artifacts in this repository. They are not a guarantee that a fresh clone without raw data can reproduce the full pipelines immediately.

| Track | Tracked snapshot | Evidence |
| --- | --- | --- |
| HRV | Median F1 at 50 ms tolerance `0.999361`; 285,494 reference intervals; 977 300-second windows; 38,400 artifact scenarios | `results/hrv/` |
| Sleep-EDF | 54,587 included epochs; YASA accuracy `0.823310`, balanced accuracy `0.721763`, macro-F1 `0.658405`, kappa `0.675571` | `results/sleep_edf/twenty_record_*` |
| MIT-BIH PSG | 10,197 annotation epochs; 3,162 sleep-only respiratory tokens; oxygen review statuses: 13 unavailable, 3 artifact review, 2 ready | `results/mit_bih_psg/all_record_*` |

Detailed usage notes and audit commentary are in [`WORK_GUIDE.md`](WORK_GUIDE.md). A concise project-state summary is in [`reports/project/project_state_summary.md`](reports/project/project_state_summary.md). Chinese-language source documents are archived under [`zh/`](zh/).

## Repository Layout

```text
configs/                         YAML configuration for the three pipelines
  hrv/core.yaml
  sleep_edf/default.yaml
  mit_bih_psg/default.yaml

data/manifests/                  Data source, local path, and SHA-256 contracts
docs/                            Public documentation, excluding ignored planning drafts
src/physio_signal_lab/           Python package and CLI
  cli.py                         CLI subcommands
  io/                            WFDB / EDF data access
  evaluation/                    Peak matching, artifacts, sleep staging
  features/                      RR/NN, HRV, sleep features, uncertainty
  reporting.py                   HRV report gate
  release.py                     HRV release metadata bundle
  sleep_*.py                     Sleep-EDF workflows
  mit_bih_psg.py                 Respiratory/SpO2 workflow

tests/                           Regression tests
results/                         Tracked CSV outputs
reports/                         Tracked Markdown reports
figures/                         Tracked figures
releases/hrv-core-v0.1.0/        Existing HRV provenance bundle
zh/                              Chinese-language archived source documents
```

## Environment

[`pyproject.toml`](pyproject.toml) declares:

- Python `>=3.11,<3.14`;
- core dependencies: NumPy, pandas, SciPy, Matplotlib, PyYAML, WFDB, NeuroKit2;
- sleep extra: MNE, scikit-learn, YASA;
- build backend: Hatchling;
- dependency lock: [`uv.lock`](uv.lock).

The complete Sleep/YASA workflow is best run with **Python 3.12**. `pyproject.toml` marks YASA for Python `<3.13`.

## Installation

Use [uv](https://docs.astral.sh/uv/concepts/projects/sync/) with the lockfile:

```bash
uv sync --frozen --python 3.12 --extra dev --extra sleep
```

For ECG/HRV-only work:

```bash
uv sync --frozen --extra dev
```

Basic smoke checks:

```bash
uv run python -m compileall -q src
uv run physio-signal-lab --help
uv run pytest -q
```

## Data Preparation

Raw data are excluded by `.gitignore` and are expected under `data/raw/`. Review the manifests before downloading or restoring files:

- `data/manifests/fantasia.csv`
- `data/manifests/sleep_edf.csv`
- `data/manifests/mit_bih_psg.csv`

### Fantasia

This repository does not include a Fantasia downloader. Restore files from [PhysioNet Fantasia](https://physionet.org/content/fantasia/1.0.0/) according to `source_url` and `local_path` in the manifest:

```text
data/raw/fantasia/1.0.0/
```

Then validate:

```bash
uv run physio-signal-lab validate-data \
  --manifest data/manifests/fantasia.csv
```

### Sleep-EDF

```bash
uv run physio-signal-lab run-sleep-edf-preflight \
  --config configs/sleep_edf/default.yaml

uv run physio-signal-lab download-sleep-edf \
  --config configs/sleep_edf/default.yaml

uv run physio-signal-lab validate-sleep-edf \
  --config configs/sleep_edf/default.yaml
```

### MIT-BIH PSG

```bash
uv run physio-signal-lab download-mit-bih-psg \
  --config configs/mit_bih_psg/default.yaml

uv run physio-signal-lab validate-mit-bih-psg \
  --config configs/mit_bih_psg/default.yaml
```

The downloaders compute local SHA-256 values. A first download is not yet cross-checked against an independent upstream checksum manifest.

## Minimal Examples

After the Fantasia `f1y01` files are available, run a single-record inventory first to avoid overwriting full-run outputs:

```bash
uv run physio-signal-lab inventory-fantasia \
  --config configs/hrv/core.yaml \
  --records f1y01 \
  --out results/hrv/data_quality/smoke_f1y01.csv
```

Full ECG/HRV pipeline:

```bash
uv run physio-signal-lab run-ecg-core \
  --config configs/hrv/core.yaml
```

Sleep-EDF two-record benchmark:

```bash
uv run physio-signal-lab run-sleep-edf-pilot-benchmark \
  --config configs/sleep_edf/default.yaml \
  --records SC4001,SC4011 \
  --output-prefix pilot \
  --include-yasa
```

MIT-BIH PSG 18-record analysis:

```bash
uv run physio-signal-lab run-mit-bih-psg-respiratory-pilot \
  --config configs/mit_bih_psg/default.yaml \
  --output-prefix all_record
```

## Current Status

The repository is a research/education prototype with implemented artifacts for three pipelines. It is not yet a clean-checkout reproducible release.

Known gaps:

- no CI workflow, coverage report, tiny integration fixtures, or root-level release procedure;
- full pipeline reruns require raw data that are intentionally not committed;
- output paths do not yet use a unified run ID, atomic output directory, schema version, or stale-output detection;
- `mit_bih_psg.py` and `sleep_quality.py` remain large mixed-responsibility modules;
- the HRV release bundle is mostly provenance metadata, not a complete offline source/lock/results snapshot;
- clinical-style metrics remain educational proxies and require external validation before clinical claims.

## References

- [Fantasia Database v1.0.0](https://physionet.org/content/fantasia/1.0.0/)
- [Sleep-EDF Database Expanded v1.0.0](https://physionet.org/content/sleep-edfx/1.0.0/)
- [MIT-BIH Polysomnographic Database v1.0.0](https://physionet.org/content/slpdb/1.0.0/)
- [WFDB Python documentation](https://wfdb-python.readthedocs.io/en/latest/)
- [NeuroKit2 ECG API](https://neuropsychology.github.io/NeuroKit/functions/ecg.html) and [paper](https://doi.org/10.3758/s13428-020-01516-y)
- [SciPy Welch PSD](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html) and [Lomb-Scargle](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lombscargle.html)
- [HRV Task Force standards](https://doi.org/10.1161/01.CIR.93.5.1043)
- [MNE `read_raw_edf`](https://mne.tools/stable/generated/mne.io.read_raw_edf.html)
- [YASA `SleepStaging`](https://yasa-sleep.org/generated/yasa.SleepStaging.html) and [paper](https://doi.org/10.7554/eLife.70092)
- [AASM hypopnea scoring rule discussion](https://doi.org/10.5664/jcsm.9952)
- Related tools: [pyHRV](https://github.com/PGomes92/pyhrv), [HeartPy](https://github.com/paulvangentcom/heartrate_analysis_python)

## Citation

Please cite this repository using [`CITATION.cff`](CITATION.cff), and cite the original public datasets and method libraries used in any derived analysis.

## License

Repository code and documentation are released under the [MIT License](LICENSE). Third-party datasets remain governed by their own PhysioNet terms and citations; raw data are not redistributed in this repository.
