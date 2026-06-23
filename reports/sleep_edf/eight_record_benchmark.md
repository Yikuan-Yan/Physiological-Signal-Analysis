# Sleep-EDF Benchmark Report

## Scope

This benchmark verifies EDF reading, 30 s hypnogram expansion, R&K-to-five-class mapping, and a global majority-stage baseline on the downloaded Sleep Cassette records.

This report does not evaluate sleep quality, diagnose sleep disorders, or make event-detector accuracy claims.

## Records

- Output scope: eight record.
- Records: SC4001, SC4011, SC4021, SC4031, SC4041, SC4051, SC4061, SC4071.
- MNE status: available.
- scikit-learn status: available.
- YASA status: available.

YASA staging was not requested in this run. Use `--include-yasa` in a Python 3.12 sleep-extra environment to generate YASA predictions. Use `profile-yasa-runtime` first when changing records, channels, or timeout budgets.


## Stage Distribution

| record | included | excluded | WAKE | N1 | N2 | N3 | REM |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SC4001 | 2650 | 0 | 1997 | 58 | 250 | 220 | 125 |
| SC4011 | 2802 | 0 | 1856 | 109 | 562 | 105 | 170 |
| SC4021 | 2804 | 0 | 1907 | 94 | 545 | 95 | 163 |
| SC4031 | 2820 | 0 | 2008 | 61 | 485 | 57 | 209 |
| SC4041 | 2569 | 1 | 1534 | 166 | 620 | 53 | 196 |
| SC4051 | 2722 | 0 | 2258 | 44 | 217 | 135 | 68 |
| SC4061 | 2770 | 0 | 2069 | 56 | 407 | 136 | 102 |
| SC4071 | 2810 | 0 | 1958 | 89 | 403 | 162 | 198 |

## Model Metrics

| model | record | epochs | majority ref | accuracy | balanced accuracy | macro-F1 | kappa |
| --- | --- | --- | --- | --- | --- | --- | --- |
| global_majority_stage_baseline | SC4001 | 2650 | WAKE | 0.754 | 0.200 | 0.172 | 0.000 |
| global_majority_stage_baseline | SC4011 | 2802 | WAKE | 0.662 | 0.200 | 0.159 | 0.000 |
| global_majority_stage_baseline | SC4021 | 2804 | WAKE | 0.680 | 0.200 | 0.162 | 0.000 |
| global_majority_stage_baseline | SC4031 | 2820 | WAKE | 0.712 | 0.200 | 0.166 | 0.000 |
| global_majority_stage_baseline | SC4041 | 2569 | WAKE | 0.597 | 0.200 | 0.150 | 0.000 |
| global_majority_stage_baseline | SC4051 | 2722 | WAKE | 0.830 | 0.200 | 0.181 | 0.000 |
| global_majority_stage_baseline | SC4061 | 2770 | WAKE | 0.747 | 0.200 | 0.171 | 0.000 |
| global_majority_stage_baseline | SC4071 | 2810 | WAKE | 0.697 | 0.200 | 0.164 | 0.000 |
| global_majority_stage_baseline | all | 21947 | WAKE | 0.710 | 0.200 | 0.166 | 0.000 |

- Overall included epochs: 21947.
- Overall global-majority accuracy: 0.710.
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
