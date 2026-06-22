# Sleep-EDF Benchmark Report

## Scope

This benchmark verifies EDF reading, 30 s hypnogram expansion, R&K-to-five-class mapping, and a majority-stage baseline on the downloaded Sleep Cassette records.

This report does not evaluate sleep quality, diagnose sleep disorders, or make event-detector accuracy claims.

## Records

- Output scope: eight record.
- Records: SC4001, SC4011, SC4021, SC4031, SC4041, SC4051, SC4061, SC4071.
- MNE status: available.
- scikit-learn status: available.
- YASA status: available.

YASA staging was run with the frozen channel settings and aligned to the same included epoch table.

- YASA overall accuracy: 0.806.
- YASA balanced accuracy: 0.702.
- YASA macro-F1: 0.630.
- YASA Cohen's kappa: 0.630.


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
| majority_stage_baseline | SC4001 | 2650 | WAKE | 0.754 | 0.200 | 0.172 | 0.000 |
| majority_stage_baseline | SC4011 | 2802 | WAKE | 0.662 | 0.200 | 0.159 | 0.000 |
| majority_stage_baseline | SC4021 | 2804 | WAKE | 0.680 | 0.200 | 0.162 | 0.000 |
| majority_stage_baseline | SC4031 | 2820 | WAKE | 0.712 | 0.200 | 0.166 | 0.000 |
| majority_stage_baseline | SC4041 | 2569 | WAKE | 0.597 | 0.200 | 0.150 | 0.000 |
| majority_stage_baseline | SC4051 | 2722 | WAKE | 0.830 | 0.200 | 0.181 | 0.000 |
| majority_stage_baseline | SC4061 | 2770 | WAKE | 0.747 | 0.200 | 0.171 | 0.000 |
| majority_stage_baseline | SC4071 | 2810 | WAKE | 0.697 | 0.200 | 0.164 | 0.000 |
| majority_stage_baseline | all | 21947 | WAKE | 0.710 | 0.200 | 0.166 | 0.000 |
| yasa_sleepstaging | SC4001 | 2650 | WAKE | 0.777 | 0.572 | 0.535 | 0.524 |
| yasa_sleepstaging | SC4011 | 2802 | WAKE | 0.713 | 0.748 | 0.619 | 0.547 |
| yasa_sleepstaging | SC4021 | 2804 | WAKE | 0.804 | 0.687 | 0.591 | 0.639 |
| yasa_sleepstaging | SC4031 | 2820 | WAKE | 0.859 | 0.787 | 0.667 | 0.718 |
| yasa_sleepstaging | SC4041 | 2569 | WAKE | 0.815 | 0.770 | 0.690 | 0.696 |
| yasa_sleepstaging | SC4051 | 2722 | WAKE | 0.715 | 0.561 | 0.480 | 0.376 |
| yasa_sleepstaging | SC4061 | 2770 | WAKE | 0.913 | 0.716 | 0.703 | 0.789 |
| yasa_sleepstaging | SC4071 | 2810 | WAKE | 0.853 | 0.755 | 0.708 | 0.721 |
| yasa_sleepstaging | all | 21947 | WAKE | 0.806 | 0.702 | 0.630 | 0.630 |

- Overall included epochs: 21947.
- Overall majority-stage accuracy: 0.710.
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
