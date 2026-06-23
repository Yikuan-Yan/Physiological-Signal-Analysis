# Sleep-EDF Clinical Learning Report

## Purpose

This report shows how real sleep-stage data can be transformed into sleep quality metrics, clinical hypotheses, and treatment questions. It is an educational analysis, not a diagnosis, prescription, or triage tool.

## Records

- Records: SC4001, SC4011.
- Epoch size: 30 s.
- Main sleep period is inferred from first sleep epoch to last sleep epoch because this project does not yet use a clean lights-out/lights-on marker.
- Reference hypnogram rows are the primary view for learning from real labels; YASA rows show how a model-derived staging view can change downstream clinical-style metrics.

## Sleep Quality Metrics

| record | source | TST min | period SE % | WASO min | SOL proxy min | REM latency min | N3 % TST | REM % TST | awakenings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SC4001 | reference_hypnogram | 326.5 | 90.6 | 34.0 | 510.5 | 89.0 | 33.7 | 19.1 | 10 |
| SC4011 | reference_hypnogram | 473.0 | 96.2 | 18.5 | 359.0 | 119.5 | 11.1 | 18.0 | 13 |
| SC4001 | yasa_sleepstaging | 431.0 | 39.7 | 653.5 | 84.5 | 0.0 | 23.0 | 25.5 | 172 |
| SC4011 | yasa_sleepstaging | 761.0 | 56.0 | 597.5 | 37.5 | 83.0 | 12.9 | 35.7 | 203 |

## Figures

- Hypnogram timeline: `figures/sleep_edf/pilot_hypnogram_timeline.png`
- Sleep architecture: `figures/sleep_edf/pilot_sleep_architecture.png`

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

## Clinical Question Ranking

| record | source | rank | question | score | evidence |
| --- | --- | --- | --- | --- | --- |
| SC4001 | reference_hypnogram | 1 | Is sleep duration insufficient? | 1.56 | TST 326.5 min. |
| SC4001 | reference_hypnogram | 2 | Is lights-out context needed? | 1.00 | First sleep begins 510.5 min after recording start. |
| SC4001 | reference_hypnogram | 3 | Is sleep continuity poor? | 0.00 | Sleep-period efficiency 90.6%, WASO 34.0 min. |
| SC4011 | reference_hypnogram | 1 | Is lights-out context needed? | 1.00 | First sleep begins 359.0 min after recording start. |
| SC4011 | reference_hypnogram | 2 | Is sleep duration insufficient? | 0.00 | TST 473.0 min. |
| SC4011 | reference_hypnogram | 3 | Is sleep continuity poor? | 0.00 | Sleep-period efficiency 96.2%, WASO 18.5 min. |
| SC4001 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 23.88 | Fragmentation proxy: 172 awakenings, WASO 653.5 min. |
| SC4001 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 14.42 | Sleep-period efficiency 39.7%, WASO 653.5 min. |
| SC4001 | yasa_sleepstaging | 3 | Is REM or stage architecture unusual? | 2.00 | REM latency 0.0 min, N3 23.0% TST, REM 25.5% TST. |
| SC4011 | yasa_sleepstaging | 1 | Is respiratory-event evidence needed? | 23.39 | Fragmentation proxy: 203 awakenings, WASO 597.5 min. |
| SC4011 | yasa_sleepstaging | 2 | Is sleep continuity poor? | 11.86 | Sleep-period efficiency 56.0%, WASO 597.5 min. |
| SC4011 | yasa_sleepstaging | 3 | Is lights-out context needed? | 0.12 | First sleep begins 37.5 min after recording start. |

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
