# Sleep-EDF Clinical Learning Report

## Purpose

This report shows how real sleep-stage data can be transformed into sleep quality metrics, clinical hypotheses, and treatment questions. It is an educational analysis, not a diagnosis, prescription, or triage tool.

## Records

- Records: SC4001, SC4011, SC4021, SC4031, SC4041, SC4051, SC4061, SC4071, SC4081, SC4091, SC4101, SC4111, SC4121, SC4131, SC4141, SC4151, SC4161, SC4171, SC4181, SC4191.
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
| SC4041 | reference_hypnogram | 517.5 | 92.8 | 40.0 | 406.0 | 72.0 | 5.1 | 18.9 | 28 |
| SC4051 | reference_hypnogram | 232.0 | 84.1 | 44.0 | 644.5 | 82.0 | 29.1 | 14.7 | 10 |
| SC4061 | reference_hypnogram | 350.5 | 97.0 | 11.0 | 467.5 | 94.5 | 19.4 | 14.6 | 11 |
| SC4071 | reference_hypnogram | 426.0 | 99.5 | 2.0 | 466.5 | 58.5 | 19.0 | 23.2 | 3 |
| SC4081 | reference_hypnogram | 405.5 | 80.0 | 101.5 | 401.5 | 225.5 | 43.2 | 16.2 | 7 |
| SC4091 | reference_hypnogram | 491.0 | 97.0 | 15.0 | 402.5 | 54.0 | 17.3 | 23.6 | 6 |
| SC4101 | reference_hypnogram | 474.5 | 96.4 | 17.5 | 381.0 | 83.5 | 0.6 | 21.8 | 12 |
| SC4111 | reference_hypnogram | 401.0 | 99.3 | 3.0 | 467.5 | 101.5 | 16.1 | 19.7 | 4 |
| SC4121 | reference_hypnogram | 438.0 | 94.0 | 28.0 | 481.0 | 62.0 | 12.2 | 29.5 | 17 |
| SC4131 | reference_hypnogram | 436.5 | 96.1 | 17.5 | 481.0 | 157.0 | 16.8 | 19.7 | 17 |
| SC4141 | reference_hypnogram | 408.5 | 92.4 | 33.5 | 419.0 | 64.0 | 18.5 | 28.5 | 18 |
| SC4151 | reference_hypnogram | 390.0 | 93.8 | 26.0 | 447.0 | 52.5 | 22.7 | 26.7 | 6 |
| SC4161 | reference_hypnogram | 464.0 | 90.6 | 48.0 | 371.5 | 62.5 | 17.8 | 28.0 | 13 |
| SC4171 | reference_hypnogram | 413.0 | 93.7 | 28.0 | 483.5 | 160.5 | 26.0 | 31.7 | 20 |
| SC4181 | reference_hypnogram | 413.0 | 97.9 | 9.0 | 448.0 | 151.0 | 35.2 | 14.3 | 8 |
| SC4191 | reference_hypnogram | 673.5 | 95.2 | 34.0 | 587.0 | 62.0 | 8.2 | 21.2 | 19 |
| SC4001 | yasa_sleepstaging | 431.0 | 39.7 | 653.5 | 84.5 | 0.0 | 23.0 | 25.5 | 172 |
| SC4011 | yasa_sleepstaging | 761.0 | 56.0 | 597.5 | 37.5 | 83.0 | 12.9 | 35.7 | 203 |
| SC4021 | yasa_sleepstaging | 546.0 | 45.0 | 668.5 | 170.0 | 69.0 | 20.0 | 32.2 | 127 |
| SC4031 | yasa_sleepstaging | 490.0 | 36.9 | 838.0 | 61.5 | 0.0 | 17.9 | 37.4 | 124 |
| SC4041 | yasa_sleepstaging | 581.5 | 54.2 | 491.5 | 196.0 | 0.0 | 7.7 | 34.0 | 133 |
| SC4051 | yasa_sleepstaging | 497.5 | 39.0 | 778.5 | 45.5 | 0.0 | 18.7 | 45.0 | 199 |
| SC4061 | yasa_sleepstaging | 340.0 | 25.6 | 986.0 | 56.0 | 0.0 | 11.8 | 25.3 | 66 |
| SC4071 | yasa_sleepstaging | 528.0 | 41.6 | 740.5 | 86.0 | 99.0 | 19.7 | 22.3 | 105 |
| SC4081 | yasa_sleepstaging | 547.0 | 39.9 | 823.0 | 25.5 | 0.0 | 34.1 | 38.1 | 176 |
| SC4091 | yasa_sleepstaging | 513.5 | 41.1 | 735.0 | 96.0 | 85.0 | 18.5 | 22.6 | 73 |
| SC4101 | yasa_sleepstaging | 699.0 | 53.8 | 600.5 | 49.5 | 78.0 | 7.4 | 35.3 | 171 |
| SC4111 | yasa_sleepstaging | 490.5 | 39.5 | 752.0 | 55.5 | 197.5 | 12.6 | 34.7 | 101 |
| SC4121 | yasa_sleepstaging | 533.5 | 43.9 | 680.5 | 82.5 | 24.5 | 14.2 | 24.4 | 96 |
| SC4131 | yasa_sleepstaging | 438.5 | 38.9 | 687.5 | 219.0 | 0.0 | 23.5 | 24.2 | 66 |
| SC4141 | yasa_sleepstaging | 432.0 | 38.1 | 701.0 | 153.5 | 0.0 | 19.1 | 26.6 | 69 |
| SC4151 | yasa_sleepstaging | 459.0 | 38.1 | 745.5 | 82.5 | 0.0 | 26.6 | 34.0 | 55 |
| SC4161 | yasa_sleepstaging | 520.5 | 41.8 | 724.0 | 66.0 | 0.0 | 19.1 | 27.3 | 98 |
| SC4171 | yasa_sleepstaging | 813.0 | 64.2 | 452.5 | 95.5 | 40.0 | 23.0 | 45.6 | 144 |
| SC4181 | yasa_sleepstaging | 502.0 | 43.5 | 652.0 | 1.0 | 130.0 | 22.8 | 30.0 | 77 |
| SC4191 | yasa_sleepstaging | 724.5 | 58.2 | 520.0 | 134.0 | 307.0 | 10.1 | 27.0 | 89 |

## Figures

- Hypnogram timeline: `figures/sleep_edf/twenty_record_hypnogram_timeline.png`
- Sleep architecture: `figures/sleep_edf/twenty_record_sleep_architecture.png`

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
| SC4081 | reference_hypnogram | sleep_quality | short_total_sleep_time | screen_positive | TST 405.5 min is below the adult 7 h learning reference. |
| SC4081 | reference_hypnogram | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 80.0%, WASO 101.5 min. |
| SC4081 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 401.5 min after recording start. |
| SC4081 | reference_hypnogram | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 225.5 min from first sleep. |
| SC4081 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4081 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4081 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4091 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 402.5 min after recording start. |
| SC4091 | reference_hypnogram | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 54.0 min from first sleep. |
| SC4091 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4091 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4091 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4101 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 381.0 min after recording start. |
| SC4101 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4101 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4101 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4111 | reference_hypnogram | sleep_quality | short_total_sleep_time | screen_positive | TST 401.0 min is below the adult 7 h learning reference. |
| SC4111 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 467.5 min after recording start. |
| SC4111 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4111 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4111 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4121 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 481.0 min after recording start. |
| SC4121 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4121 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4121 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4131 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 481.0 min after recording start. |
| SC4131 | reference_hypnogram | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 157.0 min from first sleep. |
| SC4131 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4131 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4131 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4141 | reference_hypnogram | sleep_quality | short_total_sleep_time | screen_positive | TST 408.5 min is below the adult 7 h learning reference. |
| SC4141 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 419.0 min after recording start. |
| SC4141 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4141 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4141 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4151 | reference_hypnogram | sleep_quality | short_total_sleep_time | screen_positive | TST 390.0 min is below the adult 7 h learning reference. |
| SC4151 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 447.0 min after recording start. |
| SC4151 | reference_hypnogram | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 52.5 min from first sleep. |
| SC4151 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4151 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4151 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4161 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 371.5 min after recording start. |
| SC4161 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4161 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4161 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4171 | reference_hypnogram | sleep_quality | short_total_sleep_time | screen_positive | TST 413.0 min is below the adult 7 h learning reference. |
| SC4171 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 483.5 min after recording start. |
| SC4171 | reference_hypnogram | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 160.5 min from first sleep. |
| SC4171 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4171 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4171 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4181 | reference_hypnogram | sleep_quality | short_total_sleep_time | screen_positive | TST 413.0 min is below the adult 7 h learning reference. |
| SC4181 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 448.0 min after recording start. |
| SC4181 | reference_hypnogram | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 151.0 min from first sleep. |
| SC4181 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4181 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4181 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4191 | reference_hypnogram | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 587.0 min after recording start. |
| SC4191 | reference_hypnogram | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4191 | reference_hypnogram | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4191 | reference_hypnogram | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
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
| SC4081 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 39.9%, WASO 823.0 min. |
| SC4081 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 0.0 min from first sleep. |
| SC4081 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4081 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4081 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4091 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 41.1%, WASO 735.0 min. |
| SC4091 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 96.0 min after recording start. |
| SC4091 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4091 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4091 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4101 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 53.8%, WASO 600.5 min. |
| SC4101 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 49.5 min after recording start. |
| SC4101 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4101 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4101 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4111 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 39.5%, WASO 752.0 min. |
| SC4111 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 55.5 min after recording start. |
| SC4111 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 197.5 min from first sleep. |
| SC4111 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4111 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4111 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4121 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 43.9%, WASO 680.5 min. |
| SC4121 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 82.5 min after recording start. |
| SC4121 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 24.5 min from first sleep. |
| SC4121 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4121 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4121 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4131 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 38.9%, WASO 687.5 min. |
| SC4131 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 219.0 min after recording start. |
| SC4131 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 0.0 min from first sleep. |
| SC4131 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4131 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4131 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4141 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 38.1%, WASO 701.0 min. |
| SC4141 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 153.5 min after recording start. |
| SC4141 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 0.0 min from first sleep. |
| SC4141 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4141 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4141 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4151 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 38.1%, WASO 745.5 min. |
| SC4151 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 82.5 min after recording start. |
| SC4151 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 0.0 min from first sleep. |
| SC4151 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4151 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4151 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4161 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 41.8%, WASO 724.0 min. |
| SC4161 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 66.0 min after recording start. |
| SC4161 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 0.0 min from first sleep. |
| SC4161 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4161 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4161 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4171 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 64.2%, WASO 452.5 min. |
| SC4171 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 95.5 min after recording start. |
| SC4171 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 40.0 min from first sleep. |
| SC4171 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4171 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4171 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4181 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 43.5%, WASO 652.0 min. |
| SC4181 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 130.0 min from first sleep. |
| SC4181 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4181 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4181 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |
| SC4191 | yasa_sleepstaging | sleep_quality | low_sleep_continuity | screen_positive | Inferred sleep-period efficiency 58.2%, WASO 520.0 min. |
| SC4191 | yasa_sleepstaging | sleep_quality | long_sleep_onset_latency_proxy | context_required | First sleep begins 134.0 min after recording start. |
| SC4191 | yasa_sleepstaging | sleep_architecture | rem_latency_outside_learning_band | architecture_note | REM latency 307.0 min from first sleep. |
| SC4191 | yasa_sleepstaging | sleep_disordered_breathing | osa_or_hypoventilation | cannot_assess_from_stage_metrics | Stage labels do not provide scored apneas, hypopneas, oxygen desaturations, or AHI. |
| SC4191 | yasa_sleepstaging | insomnia | insomnia_disorder | cannot_diagnose_from_psg_alone | The dataset has objective stages but no complaint duration, daytime impairment, or sleep opportunity history. |
| SC4191 | yasa_sleepstaging | treatment_reasoning | treatment_decision | not_recommended_from_this_dataset | This analysis can generate hypotheses and referral questions, not prescribe treatment. |

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
| SC4081 | reference_hypnogram | 1 | Is REM or stage architecture unusual? | 1.76 | REM latency 225.5 min, N3 43.2% TST, REM 16.2% TST. |
| SC4081 | reference_hypnogram | 2 | Is sleep continuity poor? | 1.19 | Sleep-period efficiency 80.0%, WASO 101.5 min. |
| SC4081 | reference_hypnogram | 3 | Is lights-out context needed? | 1.00 | First sleep begins 401.5 min after recording start. |
| SC4091 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 402.5 min after recording start. |
| SC4091 | reference_hypnogram | 2 | Is REM or stage architecture unusual? | 0.20 | REM latency 54.0 min, N3 17.3% TST, REM 23.6% TST. |
| SC4091 | reference_hypnogram | 3 | Is sleep duration insufficient? | 0.00 | TST 491.0 min. |
| SC4101 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 381.0 min after recording start. |
| SC4101 | reference_hypnogram | 2 | Is REM or stage architecture unusual? | 0.94 | REM latency 83.5 min, N3 0.6% TST, REM 21.8% TST. |
| SC4101 | reference_hypnogram | 3 | Is sleep duration insufficient? | 0.00 | TST 474.5 min. |
| SC4111 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 467.5 min after recording start. |
| SC4111 | reference_hypnogram | 2 | Is sleep duration insufficient? | 0.32 | TST 401.0 min. |
| SC4111 | reference_hypnogram | 3 | Is sleep continuity poor? | 0.00 | Sleep-period efficiency 99.3%, WASO 3.0 min. |
| SC4121 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 481.0 min after recording start. |
| SC4121 | reference_hypnogram | 2 | Is respiratory-event evidence needed? | 0.13 | Fragmentation proxy: 17 awakenings, WASO 28.0 min. |
| SC4121 | reference_hypnogram | 3 | Is sleep duration insufficient? | 0.00 | TST 438.0 min. |
| SC4131 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 481.0 min after recording start. |
| SC4131 | reference_hypnogram | 2 | Is REM or stage architecture unusual? | 0.62 | REM latency 157.0 min, N3 16.8% TST, REM 19.7% TST. |
| SC4131 | reference_hypnogram | 3 | Is respiratory-event evidence needed? | 0.13 | Fragmentation proxy: 17 awakenings, WASO 17.5 min. |
| SC4141 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 419.0 min after recording start. |
| SC4141 | reference_hypnogram | 2 | Is respiratory-event evidence needed? | 0.20 | Fragmentation proxy: 18 awakenings, WASO 33.5 min. |
| SC4141 | reference_hypnogram | 3 | Is sleep duration insufficient? | 0.19 | TST 408.5 min. |
| SC4151 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 447.0 min after recording start. |
| SC4151 | reference_hypnogram | 2 | Is sleep duration insufficient? | 0.50 | TST 390.0 min. |
| SC4151 | reference_hypnogram | 3 | Is REM or stage architecture unusual? | 0.25 | REM latency 52.5 min, N3 22.7% TST, REM 26.7% TST. |
| SC4161 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 371.5 min after recording start. |
| SC4161 | reference_hypnogram | 2 | Is sleep duration insufficient? | 0.00 | TST 464.0 min. |
| SC4161 | reference_hypnogram | 3 | Is sleep continuity poor? | 0.00 | Sleep-period efficiency 90.6%, WASO 48.0 min. |
| SC4171 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 483.5 min after recording start. |
| SC4171 | reference_hypnogram | 2 | Is REM or stage architecture unusual? | 0.68 | REM latency 160.5 min, N3 26.0% TST, REM 31.7% TST. |
| SC4171 | reference_hypnogram | 3 | Is respiratory-event evidence needed? | 0.33 | Fragmentation proxy: 20 awakenings, WASO 28.0 min. |
| SC4181 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 448.0 min after recording start. |
| SC4181 | reference_hypnogram | 2 | Is REM or stage architecture unusual? | 0.59 | REM latency 151.0 min, N3 35.2% TST, REM 14.3% TST. |
| SC4181 | reference_hypnogram | 3 | Is sleep duration insufficient? | 0.12 | TST 413.0 min. |
| SC4191 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 587.0 min after recording start. |
| SC4191 | reference_hypnogram | 2 | Is respiratory-event evidence needed? | 0.27 | Fragmentation proxy: 19 awakenings, WASO 34.0 min. |
| SC4191 | reference_hypnogram | 3 | Is REM or stage architecture unusual? | 0.18 | REM latency 62.0 min, N3 8.2% TST, REM 21.2% TST. |
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
| SC4041 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 10.27 | Sleep-period efficiency 54.2%, WASO 491.5 min. |
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
| SC4081 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 26.96 | Fragmentation proxy: 176 awakenings, WASO 823.0 min. |
| SC4081 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 17.22 | Sleep-period efficiency 39.9%, WASO 823.0 min. |
| SC4081 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 2.00 | REM latency 0.0 min, N3 34.1% TST, REM 38.1% TST. |
| SC4091 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 18.50 | Fragmentation proxy: 73 awakenings, WASO 735.0 min. |
| SC4091 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 15.64 | Sleep-period efficiency 41.1%, WASO 735.0 min. |
| SC4091 | yasa_sleepstaging | 3 | Is lights-out context needed? | 1.00 | First sleep begins 96.0 min after recording start. |
| SC4101 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 21.53 | Fragmentation proxy: 171 awakenings, WASO 600.5 min. |
| SC4101 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 12.13 | Sleep-period efficiency 53.8%, WASO 600.5 min. |
| SC4101 | yasa_sleepstaging | 3 | Is lights-out context needed? | 0.33 | First sleep begins 49.5 min after recording start. |
| SC4111 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 20.82 | Fragmentation proxy: 101 awakenings, WASO 752.0 min. |
| SC4111 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 16.09 | Sleep-period efficiency 39.5%, WASO 752.0 min. |
| SC4111 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 1.29 | REM latency 197.5 min, N3 12.6% TST, REM 34.7% TST. |
| SC4121 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 18.85 | Fragmentation proxy: 96 awakenings, WASO 680.5 min. |
| SC4121 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 14.45 | Sleep-period efficiency 43.9%, WASO 680.5 min. |
| SC4121 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 1.18 | REM latency 24.5 min, N3 14.2% TST, REM 24.4% TST. |
| SC4131 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 17.46 | Fragmentation proxy: 66 awakenings, WASO 687.5 min. |
| SC4131 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 15.06 | Sleep-period efficiency 38.9%, WASO 687.5 min. |
| SC4131 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 2.00 | REM latency 0.0 min, N3 23.5% TST, REM 24.2% TST. |
| SC4141 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 17.97 | Fragmentation proxy: 69 awakenings, WASO 701.0 min. |
| SC4141 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 15.37 | Sleep-period efficiency 38.1%, WASO 701.0 min. |
| SC4141 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 2.00 | REM latency 0.0 min, N3 19.1% TST, REM 26.6% TST. |
| SC4151 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 17.78 | Fragmentation proxy: 55 awakenings, WASO 745.5 min. |
| SC4151 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 16.11 | Sleep-period efficiency 38.1%, WASO 745.5 min. |
| SC4151 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 2.00 | REM latency 0.0 min, N3 26.6% TST, REM 34.0% TST. |
| SC4161 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 19.92 | Fragmentation proxy: 98 awakenings, WASO 724.0 min. |
| SC4161 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 15.38 | Sleep-period efficiency 41.8%, WASO 724.0 min. |
| SC4161 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 2.00 | REM latency 0.0 min, N3 19.1% TST, REM 27.3% TST. |
| SC4171 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 16.22 | Fragmentation proxy: 144 awakenings, WASO 452.5 min. |
| SC4171 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 8.62 | Sleep-period efficiency 64.2%, WASO 452.5 min. |
| SC4171 | yasa_sleepstaging | 3 | Is lights-out context needed? | 1.00 | First sleep begins 95.5 min after recording start. |
| SC4181 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 17.15 | Fragmentation proxy: 77 awakenings, WASO 652.0 min. |
| SC4181 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 14.02 | Sleep-period efficiency 43.5%, WASO 652.0 min. |
| SC4181 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 0.17 | REM latency 130.0 min, N3 22.8% TST, REM 30.0% TST. |
| SC4191 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 14.28 | Fragmentation proxy: 89 awakenings, WASO 520.0 min. |
| SC4191 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 10.35 | Sleep-period efficiency 58.2%, WASO 520.0 min. |
| SC4191 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 3.12 | REM latency 307.0 min, N3 10.1% TST, REM 27.0% TST. |

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
| SC4081 | WAKE | REM | 317 | 11.3 |
| SC4081 | N2 | N3 | 69 | 2.5 |
| SC4081 | WAKE | N2 | 48 | 1.7 |
| SC4081 | N1 | WAKE | 40 | 1.4 |
| SC4091 | REM | N2 | 51 | 1.9 |
| SC4091 | WAKE | REM | 45 | 1.7 |
| SC4091 | N2 | REM | 38 | 1.4 |
| SC4091 | WAKE | N2 | 36 | 1.3 |
| SC4101 | WAKE | N2 | 253 | 9.3 |
| SC4101 | WAKE | REM | 248 | 9.1 |
| SC4101 | N2 | N3 | 91 | 3.3 |
| SC4101 | N2 | N1 | 66 | 2.4 |
| SC4111 | N2 | REM | 120 | 4.5 |
| SC4111 | WAKE | N2 | 103 | 3.9 |
| SC4111 | WAKE | REM | 60 | 2.3 |
| SC4111 | WAKE | N3 | 34 | 1.3 |
| SC4121 | WAKE | REM | 105 | 3.9 |
| SC4121 | REM | N2 | 71 | 2.6 |
| SC4121 | WAKE | N2 | 63 | 2.3 |
| SC4121 | N2 | N3 | 42 | 1.6 |
| SC4131 | N2 | N3 | 56 | 2.0 |
| SC4131 | N2 | N1 | 48 | 1.7 |
| SC4131 | WAKE | N2 | 35 | 1.2 |
| SC4131 | N2 | REM | 30 | 1.1 |
| SC4141 | WAKE | REM | 48 | 1.7 |
| SC4141 | REM | N2 | 29 | 1.1 |
| SC4141 | N2 | N3 | 27 | 1.0 |
| SC4141 | REM | N1 | 25 | 0.9 |
| SC4151 | WAKE | REM | 114 | 4.4 |
| SC4151 | N2 | N3 | 58 | 2.2 |
| SC4151 | WAKE | N1 | 21 | 0.8 |
| SC4151 | N2 | N1 | 16 | 0.6 |
| SC4161 | WAKE | N2 | 76 | 2.9 |
| SC4161 | WAKE | REM | 70 | 2.7 |
| SC4161 | N2 | N3 | 41 | 1.6 |
| SC4161 | REM | N2 | 26 | 1.0 |
| SC4171 | WAKE | REM | 588 | 21.5 |
| SC4171 | N2 | N3 | 161 | 5.9 |
| SC4171 | WAKE | N2 | 152 | 5.5 |
| SC4171 | REM | N2 | 110 | 4.0 |
| SC4181 | WAKE | REM | 146 | 5.3 |
| SC4181 | N3 | N2 | 63 | 2.3 |
| SC4181 | N2 | REM | 36 | 1.3 |
| SC4181 | N2 | N1 | 27 | 1.0 |
| SC4191 | WAKE | N2 | 73 | 2.6 |
| SC4191 | N2 | REM | 49 | 1.8 |
| SC4191 | N1 | REM | 43 | 1.6 |
| SC4191 | N2 | N3 | 36 | 1.3 |

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
