# Sleep-EDF Benchmark Report

## Scope

This benchmark verifies EDF reading, 30 s hypnogram expansion, R&K-to-five-class mapping, and a majority-stage baseline on the downloaded Sleep Cassette records.

This report does not evaluate sleep quality, diagnose sleep disorders, or make event-detector accuracy claims.

## Records

- Output scope: twenty record.
- Records: SC4001, SC4011, SC4021, SC4031, SC4041, SC4051, SC4061, SC4071, SC4081, SC4091, SC4101, SC4111, SC4121, SC4131, SC4141, SC4151, SC4161, SC4171, SC4181, SC4191.
- MNE status: available.
- scikit-learn status: available.
- YASA status: available.

YASA staging was run with the frozen channel settings and aligned to the same included epoch table.

- YASA overall accuracy: 0.823.
- YASA balanced accuracy: 0.722.
- YASA macro-F1: 0.658.
- YASA Cohen's kappa: 0.676.


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
| SC4081 | 2796 | 0 | 1985 | 68 | 262 | 350 | 131 |
| SC4091 | 2721 | 11 | 1739 | 19 | 561 | 170 | 232 |
| SC4101 | 2719 | 1 | 1770 | 65 | 671 | 6 | 207 |
| SC4111 | 2641 | 1 | 1839 | 13 | 502 | 129 | 158 |
| SC4121 | 2685 | 101 | 1809 | 48 | 463 | 107 | 258 |
| SC4131 | 2814 | 0 | 1941 | 57 | 497 | 147 | 172 |
| SC4141 | 2756 | 0 | 1939 | 29 | 404 | 151 | 233 |
| SC4151 | 2616 | 4 | 1836 | 41 | 354 | 177 | 208 |
| SC4161 | 2621 | 5 | 1693 | 55 | 448 | 165 | 260 |
| SC4171 | 2741 | 1 | 1915 | 21 | 328 | 215 | 262 |
| SC4181 | 2756 | 0 | 1930 | 29 | 388 | 291 | 118 |
| SC4191 | 2774 | 0 | 1427 | 118 | 833 | 110 | 286 |

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
| majority_stage_baseline | SC4081 | 2796 | WAKE | 0.710 | 0.200 | 0.166 | 0.000 |
| majority_stage_baseline | SC4091 | 2721 | WAKE | 0.639 | 0.200 | 0.156 | 0.000 |
| majority_stage_baseline | SC4101 | 2719 | WAKE | 0.651 | 0.200 | 0.158 | 0.000 |
| majority_stage_baseline | SC4111 | 2641 | WAKE | 0.696 | 0.200 | 0.164 | 0.000 |
| majority_stage_baseline | SC4121 | 2685 | WAKE | 0.674 | 0.200 | 0.161 | 0.000 |
| majority_stage_baseline | SC4131 | 2814 | WAKE | 0.690 | 0.200 | 0.163 | 0.000 |
| majority_stage_baseline | SC4141 | 2756 | WAKE | 0.704 | 0.200 | 0.165 | 0.000 |
| majority_stage_baseline | SC4151 | 2616 | WAKE | 0.702 | 0.200 | 0.165 | 0.000 |
| majority_stage_baseline | SC4161 | 2621 | WAKE | 0.646 | 0.200 | 0.157 | 0.000 |
| majority_stage_baseline | SC4171 | 2741 | WAKE | 0.699 | 0.200 | 0.165 | 0.000 |
| majority_stage_baseline | SC4181 | 2756 | WAKE | 0.700 | 0.200 | 0.165 | 0.000 |
| majority_stage_baseline | SC4191 | 2774 | WAKE | 0.514 | 0.200 | 0.136 | 0.000 |
| majority_stage_baseline | all | 54587 | WAKE | 0.685 | 0.200 | 0.163 | 0.000 |
| yasa_sleepstaging | SC4001 | 2650 | WAKE | 0.777 | 0.572 | 0.535 | 0.524 |
| yasa_sleepstaging | SC4011 | 2802 | WAKE | 0.713 | 0.748 | 0.619 | 0.547 |
| yasa_sleepstaging | SC4021 | 2804 | WAKE | 0.804 | 0.687 | 0.591 | 0.639 |
| yasa_sleepstaging | SC4031 | 2820 | WAKE | 0.859 | 0.787 | 0.667 | 0.718 |
| yasa_sleepstaging | SC4041 | 2569 | WAKE | 0.815 | 0.770 | 0.690 | 0.696 |
| yasa_sleepstaging | SC4051 | 2722 | WAKE | 0.715 | 0.561 | 0.480 | 0.376 |
| yasa_sleepstaging | SC4061 | 2770 | WAKE | 0.913 | 0.716 | 0.703 | 0.789 |
| yasa_sleepstaging | SC4071 | 2810 | WAKE | 0.853 | 0.755 | 0.708 | 0.721 |
| yasa_sleepstaging | SC4081 | 2796 | WAKE | 0.785 | 0.657 | 0.606 | 0.597 |
| yasa_sleepstaging | SC4091 | 2721 | WAKE | 0.880 | 0.762 | 0.701 | 0.781 |
| yasa_sleepstaging | SC4101 | 2719 | WAKE | 0.713 | 0.725 | 0.477 | 0.525 |
| yasa_sleepstaging | SC4111 | 2641 | WAKE | 0.837 | 0.690 | 0.606 | 0.686 |
| yasa_sleepstaging | SC4121 | 2685 | WAKE | 0.853 | 0.717 | 0.663 | 0.731 |
| yasa_sleepstaging | SC4131 | 2814 | WAKE | 0.914 | 0.826 | 0.774 | 0.825 |
| yasa_sleepstaging | SC4141 | 2756 | WAKE | 0.923 | 0.796 | 0.758 | 0.841 |
| yasa_sleepstaging | SC4151 | 2616 | WAKE | 0.897 | 0.818 | 0.748 | 0.800 |
| yasa_sleepstaging | SC4161 | 2621 | WAKE | 0.881 | 0.773 | 0.749 | 0.787 |
| yasa_sleepstaging | SC4171 | 2741 | WAKE | 0.594 | 0.530 | 0.434 | 0.384 |
| yasa_sleepstaging | SC4181 | 2756 | WAKE | 0.856 | 0.722 | 0.645 | 0.724 |
| yasa_sleepstaging | SC4191 | 2774 | WAKE | 0.886 | 0.804 | 0.769 | 0.823 |
| yasa_sleepstaging | all | 54587 | WAKE | 0.823 | 0.722 | 0.658 | 0.676 |

- Overall included epochs: 54587.
- Overall majority-stage accuracy: 0.685.
- Overall balanced accuracy: 0.200.
- Overall macro-F1: 0.163.
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

Use the completed runtime profile and pilot YASA benchmark as the gate for downloading and evaluating the next frozen Sleep-EDF records.
