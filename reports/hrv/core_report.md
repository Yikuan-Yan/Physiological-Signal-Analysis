# HRV Core Report

## Question and Scope

This report evaluates a reproducible ECG to RR/NN to HRV workflow on the PhysioNet Fantasia Database v1.0.0. The scope is method validation: data access, reference annotation alignment, R-peak detector behavior, RR/NN interval construction, artifact sensitivity, frequency-domain method sensitivity, and record-level uncertainty.

This report does not make medical, diagnostic, risk-scoring, personal baseline, or treatment claims.

## Dataset and Protocol

- Dataset: Fantasia Database v1.0.0.
- License: Open Data Commons Attribution License v1.0, as recorded in `data/manifests/fantasia.csv`.
- Records analyzed: 40 total; 20 young and 20 old.
- Sex balance: {'F': 20, 'M': 20}.
- Age range: 21-85 years.
- Sampling rates: {250.0: 39, 333.0: 1}.
- Channels: {'RESP|ECG': 20, 'RESP|ECG|BP': 20}.
- ECG non-finite samples: 4217 across 8 records; detector input used explicit linear interpolation for those samples and retained counts in output tables.

## Reproducibility

From a fresh environment with the raw Fantasia files already present under `data/raw/fantasia/1.0.0`:

```bash
uv sync --frozen --extra dev
uv run python -m physio_signal_lab.cli validate-data --manifest data/manifests/fantasia.csv
uv run python -m physio_signal_lab.cli run-ecg-core --config configs/hrv/core.yaml
uv run pytest -q
```

The current manifest validation produced 0 missing files, 0 checksum mismatches, and 0 missing record files.

## R-Peak Detector Benchmark

The official `.ecg` annotations are treated as reference annotations, not absolute truth. NeuroKit2 was evaluated record-by-record at 50 ms and 100 ms tolerances.

- 50 ms total TP/FP/FN: 285032/1280/502.
- 50 ms median sensitivity: 0.99969.
- 50 ms median PPV: 0.99948.
- 50 ms median F1: 0.99936.
- 50 ms median absolute timing error: 8.0 ms.

| record | F1 | FP | FN | median abs error |
| --- | --- | --- | --- | --- |
| f1o09 | 0.9726 | 277 | 0 | 8.0 ms |
| f2o08 | 0.9784 | 247 | 64 | 20.0 ms |
| f2o06 | 0.9800 | 210 | 4 | 8.0 ms |
| f2y09 | 0.9859 | 65 | 182 | 4.0 ms |
| f2o09 | 0.9860 | 152 | 22 | 28.0 ms |

Worst-case overlay plots are stored in `figures/hrv/peak_failures/`.

## RR and NN Intervals

RR intervals use all adjacent reference annotations. NN intervals are the subset where both endpoint annotation symbols are `N` and interval duration is within 300-2000 ms.

- RR intervals: 285,494.
- NN intervals: 280,748.
- Excluded intervals: 4,746.
- Exclusion reasons: {'non_normal_endpoint': 4739, 'invalid_rr_duration': 7}.
- 5 min windows: 977; median valid fraction 1.0000.
- Window RMSSD median: 34.502 ms.

## Artifact Sensitivity

Artifact experiments injected missed beat, spurious extra beat, timestamp jitter, and ectopic-like short-long interval pairs at rates 0.1%, 0.5%, 1%, and 3%, with 20 repeats and fixed seeds.

- Scenario rows: 38,400.
- Strategies: ['delete_flagged_intervals', 'interpolate_flagged_intervals', 'no_correction'].

| artifact | strategy | median RMSSD rel error | median SDNN rel error | median pNN50 rel error |
| --- | --- | --- | --- | --- |
| ectopic_short_long | interpolate_flagged_intervals | -3.39% | -0.45% | -6.98% |
| ectopic_short_long | no_correction | 293.16% | 46.31% | 63.36% |
| missed_beat | interpolate_flagged_intervals | 1.72% | 2.84% | -2.34% |
| missed_beat | no_correction | 676.39% | 185.76% | 42.77% |
| spurious_extra_beat | interpolate_flagged_intervals | -6.31% | -3.30% | -7.51% |
| spurious_extra_beat | no_correction | 277.70% | 99.76% | 38.06% |
| timestamp_jitter | interpolate_flagged_intervals | -3.40% | -0.44% | -6.91% |
| timestamp_jitter | no_correction | 6.16% | 0.59% | 16.79% |

## Frequency-Domain HRV and Method Sensitivity

Primary frequency analysis interpolates the NN tachogram to 4 Hz and uses Welch PSD. Lomb-Scargle is reported as a normalized sensitivity analysis on the unevenly sampled series; its band powers are not treated as the same physical units as Welch `ms^2` powers.

- Frequency windows: 977; valid Welch windows 969; short/insufficient windows 8.
- Median Welch LF power: 644.612 ms^2.
- Median Welch HF power: 211.980 ms^2.
- Median Welch LF/HF ratio: 2.412.
- Median Lomb LF/HF ratio: 1.723.
- Median Lomb-Welch LF/HF ratio delta: -0.575.

LF/HF is reported only as a secondary descriptive metric and is not interpreted as autonomic balance.

## Record-Level Uncertainty

Uncertainty is estimated by bootstrapping record-level window medians, so records rather than beats or windows are the resampling unit.

- MeanNN: 1,026.165 ms (95% CI 989.893-1,051.099 ms).
- SDNN: 54.787 ms (95% CI 41.758-74.584 ms).
- RMSSD: 32.678 ms (95% CI 27.765-50.559 ms).
- pNN50: 0.113 (95% CI 0.048-0.255).
- Welch LF power: 738.748 ms^2 (95% CI 313.936-1,270.406 ms^2).
- Welch HF power: 196.713 ms^2 (95% CI 129.472-413.578 ms^2).
- Welch LF/HF ratio: 2.452 (95% CI 1.713-3.090).
- Lomb LF/HF ratio: 1.635 (95% CI 1.317-2.227).

## Core Gate Decision

| gate | status | evidence |
| --- | --- | --- |
| Fantasia 40 records readable and inventoried | pass | 40 inventory rows |
| Manifest and local files validated | pass | 0 missing files; 0 checksum mismatches; 0 missing record files |
| R-peak detector evaluated against reference annotation | pass | 40 records at 50 ms; median F1 0.9994 |
| RR and NN intervals separated with exclusion reasons | pass | 280748 NN, 4746 excluded |
| Four artifact classes quantified | pass | 38400 artifact scenarios |
| Frequency analysis compares Welch and Lomb-Scargle | pass | 969 valid frequency windows |
| Uncertainty reported at record level | pass | 27 bootstrap CI rows |
| No diagnostic or personal baseline claims | pass | Report wording restricted to method and reproducibility claims |

**Decision:** pass the current public-data HRV core implementation gate for method-development purposes.

## Limitations

- Fantasia is a single-session resting laboratory dataset, not longitudinal or ambulatory monitoring.
- Reference annotations may contain uncertainty and are not treated as error-free truth.
- RR/NN rules are explicit and conservative; alternative beat classification rules may change HRV values.
- Artifact experiments are controlled perturbations, not estimates of real device artifact prevalence.
- Frequency-domain results depend on interpolation, PSD settings, windowing, and band definitions.
- No personal baseline, disease detection, stress inference, sleep quality, or device-purchase conclusion follows from this analysis.

## Next Direction

The next defensible step is a report review pass: inspect the five worst peak overlays, review artifact sensitivity trade-offs, and decide whether to freeze a version tag before optional Sleep-EDF/YASA expansion.
