# Sleep-EDF Benchmark Report

## Scope

This benchmark verifies EDF reading, 30 s hypnogram expansion, R&K-to-five-class mapping, and a global majority-stage baseline on the downloaded Sleep Cassette records.

This report does not evaluate sleep quality, diagnose sleep disorders, or make event-detector accuracy claims.

## Records

- Output scope: pilot.
- Records: SC4001, SC4011.
- MNE status: available.
- scikit-learn status: available.
- YASA status: available.

YASA staging was not requested in this run. Use `--include-yasa` in a Python 3.12 sleep-extra environment to generate YASA predictions. Use `profile-yasa-runtime` first when changing records, channels, or timeout budgets.


## Stage Distribution

| record | included | excluded | WAKE | N1 | N2 | N3 | REM |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SC4001 | 2650 | 0 | 1997 | 58 | 250 | 220 | 125 |
| SC4011 | 2802 | 0 | 1856 | 109 | 562 | 105 | 170 |

## Model Metrics

| model | record | epochs | majority ref | accuracy | balanced accuracy | macro-F1 | kappa |
| --- | --- | --- | --- | --- | --- | --- | --- |
| global_majority_stage_baseline | SC4001 | 2650 | WAKE | 0.754 | 0.200 | 0.172 | 0.000 |
| global_majority_stage_baseline | SC4011 | 2802 | WAKE | 0.662 | 0.200 | 0.159 | 0.000 |
| global_majority_stage_baseline | all | 5452 | WAKE | 0.707 | 0.200 | 0.166 | 0.000 |

- Overall included epochs: 5452.
- Overall global-majority accuracy: 0.707.
- Overall balanced accuracy: 0.200.
- Overall macro-F1: 0.166.
- Overall Cohen's kappa: 0.000.

## Reproduce

```bash
uv sync --extra sleep --extra dev
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf/default.yaml --records SC4001,SC4011
uv run python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf/default.yaml --records SC4001,SC4011
uv sync --python 3.12 --extra sleep --extra dev
uv run --python 3.12 --extra sleep python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf/default.yaml --records SC4001,SC4011 --include-yasa
```

## Next Step

Run `profile-yasa-runtime` and then `--include-yasa` before expanding beyond the pilot records.
