# Sleep-EDF Pilot Benchmark Report

## Scope

This pilot benchmark verifies EDF reading, 30 s hypnogram expansion, R&K-to-five-class mapping, and a majority-stage baseline on the downloaded Sleep Cassette pilot records.

This report does not evaluate sleep quality, diagnose sleep disorders, or make event-detector accuracy claims.

## Records

- Records: SC4001, SC4011.
- MNE status: available.
- scikit-learn status: available.
- YASA status: available.

YASA staging was run with the frozen channel settings and aligned to the same included epoch table.

- YASA overall accuracy: 0.744.
- YASA balanced accuracy: 0.667.
- YASA macro-F1: 0.595.
- YASA Cohen's kappa: 0.544.


## Stage Distribution

| record | included | excluded | WAKE | N1 | N2 | N3 | REM |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SC4001 | 2650 | 0 | 1997 | 58 | 250 | 220 | 125 |
| SC4011 | 2802 | 0 | 1856 | 109 | 562 | 105 | 170 |

## Model Metrics

| model | record | epochs | majority ref | accuracy | balanced accuracy | macro-F1 | kappa |
| --- | --- | --- | --- | --- | --- | --- | --- |
| majority_stage_baseline | SC4001 | 2650 | WAKE | 0.754 | 0.200 | 0.172 | 0.000 |
| majority_stage_baseline | SC4011 | 2802 | WAKE | 0.662 | 0.200 | 0.159 | 0.000 |
| majority_stage_baseline | all | 5452 | WAKE | 0.707 | 0.200 | 0.166 | 0.000 |
| yasa_sleepstaging | SC4001 | 2650 | WAKE | 0.777 | 0.572 | 0.535 | 0.524 |
| yasa_sleepstaging | SC4011 | 2802 | WAKE | 0.713 | 0.748 | 0.619 | 0.547 |
| yasa_sleepstaging | all | 5452 | WAKE | 0.744 | 0.667 | 0.595 | 0.544 |

- Overall included epochs: 5452.
- Overall majority-stage accuracy: 0.707.
- Overall balanced accuracy: 0.200.
- Overall macro-F1: 0.166.
- Overall Cohen's kappa: 0.000.

## Reproduce

```bash
uv sync --extra sleep --extra dev
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4001,SC4011
uv run python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf.yaml --records SC4001,SC4011
uv sync --python 3.12 --extra sleep --extra dev
uv run --python 3.12 --extra sleep python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf.yaml --records SC4001,SC4011 --include-yasa
```

## Next Step

Use the completed runtime profile and pilot YASA benchmark as the gate for downloading and evaluating the next frozen Sleep-EDF records.
