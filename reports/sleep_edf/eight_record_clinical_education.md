# Sleep-EDF Clinical Learning Report

## Purpose

This report shows how real sleep-stage data can be transformed into sleep quality metrics, clinical hypotheses, and treatment questions. It is an educational analysis, not a diagnosis, prescription, or triage tool.

## Records

- Records: SC4001, SC4011, SC4021, SC4031, SC4041, SC4051, SC4061, SC4071.
- Epoch size: 30 s.
- Main sleep period is inferred from first sleep epoch to last sleep epoch because this project does not yet use a clean lights-out/lights-on marker.
- Reference hypnogram rows are the primary view for learning from real labels; YASA rows show how a model-derived staging view can change downstream clinical-style metrics.

## Sleep Quality Metrics

| record | source | TST min | period SE % | WASO min | SOL proxy min | REM latency min | N3 % TST | REM % TST | awakenings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SC4001 | reference_hypnogram | 326.5 | 90.6 | 34.0 | 510.5 | 89.0 | 33.7 | 19.1 | 10 |
| SC4011 | reference_hypnogram | 473.0 | 96.2 | 18.5 | 359.0 | 119.5 | 11.1 | 18.0 | 13 |
| SC4021 | reference_hypnogram | 448.5 | 99.1 | 4.0 | 364.5 | 79.5 | 10.6 | 18.2 | 7 |
| SC4031 | reference_hypnogram | 406.0 | 97.6 | 10.0 | 435.5 | 105.5 | 7.0 | 25.7 | 12 |
| SC4041 | reference_hypnogram | 517.5 | 92.7 | 40.0 | 406.0 | 72.0 | 5.1 | 18.9 | 28 |
| SC4051 | reference_hypnogram | 232.0 | 84.1 | 44.0 | 644.5 | 82.0 | 29.1 | 14.7 | 10 |
| SC4061 | reference_hypnogram | 350.5 | 97.0 | 11.0 | 467.5 | 94.5 | 19.4 | 14.6 | 11 |
| SC4071 | reference_hypnogram | 426.0 | 99.5 | 2.0 | 466.5 | 58.5 | 19.0 | 23.2 | 3 |
| SC4001 | yasa_sleepstaging | 431.0 | 39.7 | 653.5 | 84.5 | 0.0 | 23.0 | 25.5 | 172 |
| SC4011 | yasa_sleepstaging | 761.0 | 56.0 | 597.5 | 37.5 | 83.0 | 12.9 | 35.7 | 203 |
| SC4021 | yasa_sleepstaging | 546.0 | 45.0 | 668.5 | 170.0 | 69.0 | 20.0 | 32.2 | 127 |
| SC4031 | yasa_sleepstaging | 490.0 | 36.9 | 838.0 | 61.5 | 0.0 | 17.9 | 37.4 | 124 |
| SC4041 | yasa_sleepstaging | 581.5 | 54.2 | 491.5 | 196.0 | 0.0 | 7.7 | 34.0 | 133 |
| SC4051 | yasa_sleepstaging | 497.5 | 39.0 | 778.5 | 45.5 | 0.0 | 18.7 | 45.0 | 199 |
| SC4061 | yasa_sleepstaging | 340.0 | 25.6 | 986.0 | 56.0 | 0.0 | 11.8 | 25.3 | 66 |
| SC4071 | yasa_sleepstaging | 528.0 | 41.6 | 740.5 | 86.0 | 99.0 | 19.7 | 22.3 | 105 |

## Figures

- Hypnogram timeline: `figures/sleep_edf/eight_record_hypnogram_timeline.png`
- Sleep architecture: `figures/sleep_edf/eight_record_sleep_architecture.png`

## Clinical Learning Indicators

| record | source | domain | indicator | status | evidence |
| --- | --- | --- | --- | --- | --- |
| SC4001 | reference_hypnogram | sleep_quality | short_total_sleep_time | screen_positive | TST 326.5 min is below the adult 7 h learning reference. |
| SC4001 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 510.5 min after recording start. |
| SC4001 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4001 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4001 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4011 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 359.0 min after recording start. |
| SC4011 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4011 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4011 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4021 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 364.5 min after recording start. |
| SC4021 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4021 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4021 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4031 | reference_hypnogram | sleep_quality | short_total_sleep_time | screen_positive | TST 406.0 min is below the adult 7 h learning reference. |
| SC4031 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 435.5 min after recording start. |
| SC4031 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4031 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4031 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4041 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 406.0 min after recording start. |
| SC4041 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4041 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4041 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4051 | reference_hypnogram | sleep_quality | short_total_sleep_time | screen_positive | TST 232.0 min is below the adult 7 h learning reference. |
| SC4051 | reference_hypnogram | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 84.1%, WASO 44.0 min. |
| SC4051 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 644.5 min after recording start. |
| SC4051 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4051 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4051 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4061 | reference_hypnogram | sleep_quality | short_total_sleep_time | screen_positive | TST 350.5 min is below the adult 7 h learning reference. |
| SC4061 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 467.5 min after recording start. |
| SC4061 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4061 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4061 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4071 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 466.5 min after recording start. |
| SC4071 | reference_hypnogram | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 58.5 min from first sleep. |
| SC4071 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4071 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4071 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4001 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 39.7%, WASO 653.5 min. |
| SC4001 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 84.5 min after recording start. |
| SC4001 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 0.0 min from first sleep. |
| SC4001 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4001 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4001 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4011 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 56.0%, WASO 597.5 min. |
| SC4011 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 37.5 min after recording start. |
| SC4011 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4011 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4011 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4021 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 45.0%, WASO 668.5 min. |
| SC4021 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 170.0 min after recording start. |
| SC4021 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4021 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4021 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4031 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 36.9%, WASO 838.0 min. |
| SC4031 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 61.5 min after recording start. |
| SC4031 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 0.0 min from first sleep. |
| SC4031 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4031 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4031 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4041 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 54.2%, WASO 491.5 min. |
| SC4041 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 196.0 min after recording start. |
| SC4041 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 0.0 min from first sleep. |
| SC4041 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4041 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4041 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4051 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 39.0%, WASO 778.5 min. |
| SC4051 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 45.5 min after recording start. |
| SC4051 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 0.0 min from first sleep. |
| SC4051 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4051 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4051 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4061 | yasa_sleepstaging | sleep_quality | short_total_sleep_time | screen_positive | TST 340.0 min is below the adult 7 h learning reference. |
| SC4061 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 25.6%, WASO 986.0 min. |
| SC4061 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 56.0 min after recording start. |
| SC4061 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 0.0 min from first sleep. |
| SC4061 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4061 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4061 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4071 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 41.6%, WASO 740.5 min. |
| SC4071 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 86.0 min after recording start. |
| SC4071 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4071 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4071 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |

## Clinical Question Ranking

| record | source | rank | question | score | evidence |
| --- | --- | --- | --- | --- | --- |
| SC4001 | reference_hypnogram | 1 | Is sleep duration insufficient? | 1.56 | TST 326.5 min. |
| SC4001 | reference_hypnogram | 2 | Is lights-out context needed? | 1.00 | First sleep begins 510.5 min after recording start. |
| SC4001 | reference_hypnogram | 3 | Is sleep continuity poor? | 0.00 | Sleep-period efficiency 90.6%, WASO 34.0 min. |
| SC4011 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 359.0 min after recording start. |
| SC4011 | reference_hypnogram | 2 | Is sleep duration insufficient? | 0.00 | TST 473.0 min. |
| SC4011 | reference_hypnogram | 3 | Is sleep continuity poor? | 0.00 | Sleep-period efficiency 96.2%, WASO 18.5 min. |
| SC4021 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 364.5 min after recording start. |
| SC4021 | reference_hypnogram | 2 | Is sleep duration insufficient? | 0.00 | TST 448.5 min. |
| SC4021 | reference_hypnogram | 3 | Is sleep continuity poor? | 0.00 | Sleep-period efficiency 99.1%, WASO 4.0 min. |
| SC4031 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 435.5 min after recording start. |
| SC4031 | reference_hypnogram | 2 | Is REM or stage architecture unusual? | 0.30 | REM latency 105.5 min, N3 7.0% TST, REM 25.7% TST. |
| SC4031 | reference_hypnogram | 3 | Is sleep duration insufficient? | 0.23 | TST 406.0 min. |
| SC4041 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 406.0 min after recording start. |
| SC4041 | reference_hypnogram | 2 | Is respiratory-event evidence needed? | 0.87 | Fragmentation proxy: 28 awakenings, WASO 40.0 min. |
| SC4041 | reference_hypnogram | 3 | Is REM or stage architecture unusual? | 0.49 | REM latency 72.0 min, N3 5.1% TST, REM 18.9% TST. |
| SC4051 | reference_hypnogram | 1 | Is sleep duration insufficient? | 3.13 | TST 232.0 min. |
| SC4051 | reference_hypnogram | 2 | Is lights-out context needed? | 1.00 | First sleep begins 644.5 min after recording start. |
| SC4051 | reference_hypnogram | 3 | Is sleep continuity poor? | 0.09 | Sleep-period efficiency 84.1%, WASO 44.0 min. |
| SC4061 | reference_hypnogram | 1 | Is sleep duration insufficient? | 1.16 | TST 350.5 min. |
| SC4061 | reference_hypnogram | 2 | Is lights-out context needed? | 1.00 | First sleep begins 467.5 min after recording start. |
| SC4061 | reference_hypnogram | 3 | Is REM or stage architecture unusual? | 0.04 | REM latency 94.5 min, N3 19.4% TST, REM 14.6% TST. |
| SC4071 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 466.5 min after recording start. |
| SC4071 | reference_hypnogram | 2 | Is REM or stage architecture unusual? | 0.05 | REM latency 58.5 min, N3 19.0% TST, REM 23.2% TST. |
| SC4071 | reference_hypnogram | 3 | Is sleep duration insufficient? | 0.00 | TST 426.0 min. |
| SC4001 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 23.88 | Fragmentation proxy: 172 awakenings, WASO 653.5 min. |
| SC4001 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 14.42 | Sleep-period efficiency 39.7%, WASO 653.5 min. |
| SC4001 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 2.00 | REM latency 0.0 min, N3 23.0% TST, REM 25.5% TST. |
| SC4011 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 23.39 | Fragmentation proxy: 203 awakenings, WASO 597.5 min. |
| SC4011 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 11.86 | Sleep-period efficiency 56.0%, WASO 597.5 min. |
| SC4011 | yasa_sleepstaging | 3 | Is lights-out context needed? | 0.12 | First sleep begins 37.5 min after recording start. |
| SC4021 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 20.61 | Fragmentation proxy: 127 awakenings, WASO 668.5 min. |
| SC4021 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 14.15 | Sleep-period efficiency 45.0%, WASO 668.5 min. |
| SC4021 | yasa_sleepstaging | 3 | Is lights-out context needed? | 1.00 | First sleep begins 170.0 min after recording start. |
| SC4031 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 24.04 | Fragmentation proxy: 124 awakenings, WASO 838.0 min. |
| SC4031 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 17.78 | Sleep-period efficiency 36.9%, WASO 838.0 min. |
| SC4031 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 2.00 | REM latency 0.0 min, N3 17.9% TST, REM 37.4% TST. |
| SC4041 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 17.14 | Fragmentation proxy: 133 awakenings, WASO 491.5 min. |
| SC4041 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 10.28 | Sleep-period efficiency 54.2%, WASO 491.5 min. |
| SC4041 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 2.23 | REM latency 0.0 min, N3 7.7% TST, REM 34.0% TST. |
| SC4051 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 27.84 | Fragmentation proxy: 199 awakenings, WASO 778.5 min. |
| SC4051 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 16.58 | Sleep-period efficiency 39.0%, WASO 778.5 min. |
| SC4051 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 2.00 | REM latency 0.0 min, N3 18.7% TST, REM 45.0% TST. |
| SC4061 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 23.77 | Fragmentation proxy: 66 awakenings, WASO 986.0 min. |
| SC4061 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 21.37 | Sleep-period efficiency 25.6%, WASO 986.0 min. |
| SC4061 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 2.00 | REM latency 0.0 min, N3 11.8% TST, REM 25.3% TST. |
| SC4071 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 20.68 | Fragmentation proxy: 105 awakenings, WASO 740.5 min. |
| SC4071 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 15.68 | Sleep-period efficiency 41.6%, WASO 740.5 min. |
| SC4071 | yasa_sleepstaging | 3 | Is lights-out context needed? | 0.93 | First sleep begins 86.0 min after recording start. |

## Reference vs YASA Discrepancy

This table highlights where model-derived staging would change downstream sleep-quality reasoning. Large discrepancies should be investigated before using model-derived metrics clinically.

| record | reference | yasa | epochs | % epochs |
| --- | --- | --- | --- | --- |
| SC4001 | WAKE | REM | 188 | 7.1 |
| SC4001 | WAKE | N2 | 111 | 4.2 |
| SC4001 | N3 | WAKE | 51 | 1.9 |
| SC4001 | REM | WAKE | 50 | 1.9 |
| SC4011 | WAKE | REM | 381 | 13.6 |
| SC4011 | WAKE | N2 | 183 | 6.5 |
| SC4011 | WAKE | N3 | 38 | 1.4 |
| SC4011 | N2 | N1 | 34 | 1.2 |
| SC4021 | WAKE | REM | 223 | 8.0 |
| SC4021 | N2 | N3 | 127 | 4.5 |
| SC4021 | N1 | WAKE | 49 | 1.7 |
| SC4021 | REM | N1 | 34 | 1.2 |
| SC4031 | WAKE | REM | 185 | 6.6 |
| SC4031 | N2 | N3 | 109 | 3.9 |
| SC4031 | REM | N1 | 21 | 0.7 |
| SC4031 | N1 | WAKE | 15 | 0.5 |
| SC4041 | WAKE | REM | 177 | 6.9 |
| SC4041 | N2 | N1 | 66 | 2.6 |
| SC4041 | N1 | WAKE | 58 | 2.3 |
| SC4041 | N2 | N3 | 38 | 1.5 |
| SC4051 | WAKE | REM | 382 | 14.0 |
| SC4051 | WAKE | N2 | 137 | 5.0 |
| SC4051 | WAKE | N3 | 49 | 1.8 |
| SC4051 | N3 | WAKE | 46 | 1.7 |
| SC4061 | N3 | WAKE | 63 | 2.3 |
| SC4061 | WAKE | REM | 51 | 1.8 |
| SC4061 | N2 | N3 | 20 | 0.7 |
| SC4061 | N1 | WAKE | 17 | 0.6 |
| SC4071 | WAKE | N2 | 163 | 5.8 |
| SC4071 | WAKE | REM | 61 | 2.2 |
| SC4071 | N2 | N3 | 51 | 1.8 |
| SC4071 | N1 | WAKE | 34 | 1.2 |

## How To Read This

- Sleep quality is represented here by duration, continuity, fragmentation, REM timing, and stage percentages.
- Disease reasoning starts from these patterns but needs disorder-specific data before it becomes diagnosis.
- Treatment reasoning is intentionally framed as next clinical questions. For example, low continuity can lead to an insomnia history, medication review, pain review, or respiratory-event evaluation; it does not by itself select CBT-I, PAP, medication, or any other treatment.
- Large differences between reference and YASA rows should be treated as model behavior to investigate before using model-derived metrics for any clinical workflow.

## Treatment Learning Map

| possible question | data trigger | missing evidence | clinical path |
| --- | --- | --- | --- |
| Poor sleep duration or continuity | Low TST, high WASO, low sleep-period efficiency, high fragmentation | Symptoms, sleep opportunity, diary, medications, pain, mental health, repeated nights | Insomnia history, behavior review, CBT-I discussion, or search for another sleep disorder |
| Sleep-disordered breathing | Fragmented sleep, reduced REM/N3, symptoms, snoring, witnessed apneas, cardiometabolic risk | Airflow, effort, SpO2, arousals, apnea/hypopnea scoring, AHI | PSG or HSAT, then clinician decides PAP, oral appliance, surgery, weight/lifestyle path, or other care |
| Central hypersomnolence or narcolepsy | Very short REM latency or abnormal REM timing plus daytime sleepiness | MSLT, sleep diary/actigraphy, medication washout context, cataplexy history | Sleep specialist evaluation before any medication or safety recommendation |
| Movement or REM behavior disorder | Fragmentation, abnormal movements, REM-without-atonia suspicion | Leg EMG, chin EMG review, video PSG, event scoring, injury history | Disorder-specific PSG review before safety or medication decisions |

## What This Dataset Can And Cannot Support

- Can support: sleep architecture, total sleep time, inferred WASO, inferred sleep-period efficiency, REM latency, stage balance, and fragmentation.
- Cannot diagnose from these outputs alone: obstructive sleep apnea, central sleep apnea, insomnia disorder, narcolepsy, REM sleep behavior disorder, periodic limb movement disorder, depression, or circadian rhythm disorder.
- Needed for those diagnoses: symptoms, sleep history, questionnaires, lights-out/lights-on times, airflow, respiratory effort, SpO2, arousals, leg EMG, MSLT when indicated, and clinician review.

## References Used For Learning Boundaries

- NCBI Bookshelf StatPearls, Physiology, Sleep Stages: sleep stage biology, typical REM timing, and PSG channels used for sleep-disorder testing. https://www.ncbi.nlm.nih.gov/books/NBK526132/
- AASM Sleep Education FAQ: adults should generally sleep 7 or more hours per night for optimal health. https://sleepeducation.org/sleep-faqs/
- AAST insomnia overview: insomnia diagnosis depends on clinical sleep history, daytime impact, duration, and self-report/questionnaires. https://aastweb.org/insomnia-types-diagnosis-and-treatment/
- AASM/JCSM OSA guidance context: PSG/HSAT respiratory evidence guides OSA diagnosis and longitudinal management. https://pmc.ncbi.nlm.nih.gov/articles/PMC8314660/
