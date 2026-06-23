# MIT-BIH PSG Respiratory Pilot

## Purpose

This report starts the respiratory and OSA-style evidence phase. It turns MIT-BIH `.st` sleep/apnea annotations into an annotation burden per sleep hour, checks whether respiration or SpO2 channels are present, and maps the results to clinical learning questions.

It is an educational analysis, not a diagnosis, prescription, or triage tool.

## Records

- Records: slp59, slp60, slp61, slp66, slp67x.
- Epoch size: 30 s; each `.st` annotation is interpreted as applying to the following epoch.
- Record IDs are PhysioNet WFDB record IDs; segmented records such as `slp01a` and `slp02a` keep their suffixes.

## Respiratory Event Burden

| record | sleep h | events | burden/h | range | source AHI | source note | delta | obstructive/h | central/h | hypopnea/h |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| slp59 | 2.65 | 184 | 69.4 | severe range | 55.3 |  | 14.1 | 29.1 | 17.4 | 23.0 |
| slp60 | 3.53 | 291 | 82.4 | severe range | 59.2 |  | 23.2 | 57.7 | 14.2 | 10.5 |
| slp61 | 4.97 | 244 | 49.1 | severe range | 41.2 |  | 7.9 | 40.9 | 1.4 | 6.8 |
| slp66 | 2.20 | 219 | 99.5 | severe range | 65.5 |  | 34.0 | 5.9 | 0.0 | 93.6 |
| slp67x | 0.68 | 54 | 79.0 | severe range | 0.7 |  | 78.3 | 17.6 | 55.6 | 5.9 |

## Source AHI Alignment Review

This table compares the simple annotation-token burden against the source reported AHI table. It is an audit view for educational alignment, not a replacement for scorer rules or clinical adjudication.

| record | annotation/h | source AHI | delta | status | priority | dominant event | review focus |
| --- | --- | --- | --- | --- | --- | --- | --- |
| slp67x | 79.0 | 0.7 | 78.3 | needs_manual_review | manual_review_high | central_apnea | Inspect event tokens, sleep/wake exclusion, and source scoring assumptions. |
| slp66 | 99.5 | 65.5 | 34.0 | needs_manual_review | manual_review_high | hypopnea | Inspect event tokens, sleep/wake exclusion, and source scoring assumptions. |
| slp60 | 82.4 | 59.2 | 23.2 | needs_manual_review | manual_review_high | obstructive_apnea | Inspect event tokens, sleep/wake exclusion, and source scoring assumptions. |
| slp59 | 69.4 | 55.3 | 14.1 | needs_manual_review | manual_review_high | obstructive_apnea | Inspect event tokens, sleep/wake exclusion, and source scoring assumptions. |
| slp61 | 49.1 | 41.2 | 7.9 | roughly_aligned | manual_review_medium | obstructive_apnea | Review scoring assumptions if this record is used as an example. |

## Channel Quality

The selected records include SO2/oximetry channels, so oxygen saturation ODI metrics are computed below.

| record | channel | unit | finite % | std | dynamic |
| --- | --- | --- | --- | --- | --- |
| slp59 | Resp (nasal) | l | 100.00 | 0.0005 | True |
| slp59 | Resp (abdominal) | l | 100.00 | 0.0023 | True |
| slp59 | SO2 | % | 100.00 | 0.0309 | True |
| slp60 | Resp (abdominal) | l | 100.00 | 0.1668 | True |
| slp60 | Resp (nasal) | l | 100.00 | 0.1644 | True |
| slp60 | SO2 | % | 100.00 | 0.0757 | True |
| slp61 | Resp (abdominal) | l | 100.00 | 0.1686 | True |
| slp61 | SO2 | % | 100.00 | 0.1481 | True |
| slp66 | Resp (nasal) | l | 100.00 | 0.1086 | True |
| slp66 | Resp (abdomen) | l | 100.00 | 0.0658 | True |
| slp66 | SO2 | % | 100.00 | 1.6566 | True |
| slp67x | Resp (nasal) | l | 100.00 | 0.0490 | True |
| slp67x | Resp (chest) | l | 100.00 | 0.0315 | True |
| slp67x | SO2 | % | 100.00 | 0.6684 | True |

## Oxygen Saturation

SO2 metrics are computed only when an oximetry channel is present. The report table uses sleep-only ODI values from a documented pre-event rolling-baseline desaturation rule; recording-wide and legacy percentile-proxy oxygen summaries remain in the CSV for audit. This is oxygen-only evidence, not full hypopnea scoring because airflow reduction and arousal rules are not adjudicated here.

| record | SO2 channel | status | median % | min % | below 90 % | below 90 % sleep | ODI 3% | ODI 4% | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| slp59 | SO2 | available | 91.5 | 40.0 | 26.0 | 25.3 | 45.7 | 40.0 | pre_event_rolling_baseline |
| slp60 | SO2 | available | 93.0 | 70.7 | 15.2 | 20.1 | 45.6 | 37.1 | pre_event_rolling_baseline |
| slp61 | SO2 | available | 94.6 | 40.0 | 18.8 | 19.6 | 34.8 | 32.2 | pre_event_rolling_baseline |
| slp66 | SO2 | available | 90.8 | 81.9 | 30.9 | 42.1 | 53.2 | 24.1 | pre_event_rolling_baseline |
| slp67x | SO2 | available | 93.7 | 83.7 | 12.1 | 3.6 | 32.2 | 16.1 | pre_event_rolling_baseline |

## Oxygen Artifact Review

This table flags records where the ODI scorer should be reviewed against the generated waveform windows or raw SO2 channel before using the oxygen signal as clinical-learning evidence.

| record | status | priority | flags | ODI3 minus proxy | focus |
| --- | --- | --- | --- | --- | --- |
| slp59 | artifact_review_recommended | medium | very_low_spo2_value | 3.8 | Inspect SO2 waveform windows and raw channel for dropout, motion artifact, baseline drift, and whether desaturations align with respiratory events. |
| slp60 | oxygen_review_ready | low |  | 6.5 | ODI output has no automatic artifact flags; spot-check event windows. |
| slp61 | artifact_review_recommended | medium | very_low_spo2_value | 5.4 | Inspect SO2 waveform windows and raw channel for dropout, motion artifact, baseline drift, and whether desaturations align with respiratory events. |
| slp66 | artifact_review_recommended | medium | high_sleep_time_below_90 | 7.7 | Inspect SO2 waveform windows and raw channel for dropout, motion artifact, baseline drift, and whether desaturations align with respiratory events. |
| slp67x | oxygen_review_ready | low |  | -8.8 | ODI output has no automatic artifact flags; spot-check event windows. |

## Event-Level Waveform Review

The event window table summarizes respiration channel windows around the first scored respiratory-event epochs per record. Generated figures overlay the scored 30 s event epoch on respiration and SO2 channels when available.

| record | epoch | tokens | stage | window s | resp mean | resp std |
| --- | --- | --- | --- | --- | --- | --- |
| slp59 | 36 | HA X | N1 | 1710.0-1800.0 | 0.179 | 0.148 |
| slp59 | 36 | HA X | N1 | 1710.0-1800.0 | 0.150 | 0.136 |
| slp59 | 38 | X | N1 | 1770.0-1860.0 | 0.182 | 0.152 |
| slp59 | 38 | X | N1 | 1770.0-1860.0 | 0.152 | 0.132 |
| slp59 | 39 | X | N1 | 1800.0-1890.0 | 0.180 | 0.147 |
| slp59 | 39 | X | N1 | 1800.0-1890.0 | 0.151 | 0.131 |
| slp59 | 40 | X | N1 | 1830.0-1920.0 | 0.189 | 0.154 |
| slp59 | 40 | X | N1 | 1830.0-1920.0 | 0.152 | 0.115 |
| slp59 | 42 | HA CAA | N1 | 1890.0-1980.0 | 0.178 | 0.168 |
| slp59 | 42 | HA CAA | N1 | 1890.0-1980.0 | 0.150 | 0.111 |
| slp60 | 4 | HA | N1 | 90.0-180.0 | -0.020 | 0.217 |
| slp60 | 4 | HA | N1 | 90.0-180.0 | -0.270 | 0.155 |
| slp60 | 7 | CAA CAA | N1 | 180.0-270.0 | -0.009 | 0.208 |
| slp60 | 7 | CAA CAA | N1 | 180.0-270.0 | -0.270 | 0.158 |
| slp60 | 8 | CAA | N1 | 210.0-300.0 | -0.006 | 0.249 |
| slp60 | 8 | CAA | N1 | 210.0-300.0 | -0.272 | 0.158 |
| slp60 | 9 | X | N1 | 240.0-330.0 | -0.015 | 0.223 |
| slp60 | 9 | X | N1 | 240.0-330.0 | -0.271 | 0.137 |
| slp60 | 10 | CA | N1 | 270.0-360.0 | -0.013 | 0.263 |
| slp60 | 10 | CA | N1 | 270.0-360.0 | -0.269 | 0.140 |

Generated event plots:

- `figures/mit_bih_psg/oxygen_record/slp59_epoch_0036.png`
- `figures/mit_bih_psg/oxygen_record/slp59_epoch_0038.png`
- `figures/mit_bih_psg/oxygen_record/slp60_epoch_0004.png`
- `figures/mit_bih_psg/oxygen_record/slp60_epoch_0007.png`
- `figures/mit_bih_psg/oxygen_record/slp61_epoch_0019.png`
- `figures/mit_bih_psg/oxygen_record/slp61_epoch_0020.png`
- `figures/mit_bih_psg/oxygen_record/slp66_epoch_0004.png`
- `figures/mit_bih_psg/oxygen_record/slp66_epoch_0005.png`
- `figures/mit_bih_psg/oxygen_record/slp67x_epoch_0000.png`
- `figures/mit_bih_psg/oxygen_record/slp67x_epoch_0004.png`

## Clinical Learning Indicators

| record | domain | indicator | status | evidence |
| --- | --- | --- | --- | --- |
| slp59 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 69.4 respiratory events per sleep hour (severe range). |
| slp59 | source_consistency | annotation_burden_vs_source_ahi | needs_manual_review | Annotation burden minus source AHI is 14.1 events/h. |
| slp59 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp59 | oxygenation | spo2_desaturation_burden | oxygen_desaturation_available | ODI 3% 45.7 events per sleep hour; ODI 4% 40.0 events per sleep hour; time below 90% SpO2 25.3% of plausible sleep samples. |
| slp59 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp60 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 82.4 respiratory events per sleep hour (severe range). |
| slp60 | source_consistency | annotation_burden_vs_source_ahi | needs_manual_review | Annotation burden minus source AHI is 23.2 events/h. |
| slp60 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp60 | oxygenation | spo2_desaturation_burden | oxygen_desaturation_available | ODI 3% 45.6 events per sleep hour; ODI 4% 37.1 events per sleep hour; time below 90% SpO2 20.1% of plausible sleep samples. |
| slp60 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp61 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 49.1 respiratory events per sleep hour (severe range). |
| slp61 | source_consistency | annotation_burden_vs_source_ahi | roughly_aligned | Annotation burden minus source AHI is 7.9 events/h. |
| slp61 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp61 | oxygenation | spo2_desaturation_burden | oxygen_desaturation_available | ODI 3% 34.8 events per sleep hour; ODI 4% 32.2 events per sleep hour; time below 90% SpO2 19.6% of plausible sleep samples. |
| slp61 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp66 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 99.5 respiratory events per sleep hour (severe range). |
| slp66 | source_consistency | annotation_burden_vs_source_ahi | needs_manual_review | Annotation burden minus source AHI is 34.0 events/h. |
| slp66 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp66 | oxygenation | spo2_desaturation_burden | oxygen_desaturation_available | ODI 3% 53.2 events per sleep hour; ODI 4% 24.1 events per sleep hour; time below 90% SpO2 42.1% of plausible sleep samples. |
| slp66 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp67x | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 79.0 respiratory events per sleep hour (severe range). |
| slp67x | source_consistency | annotation_burden_vs_source_ahi | needs_manual_review | Annotation burden minus source AHI is 78.3 events/h. |
| slp67x | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp67x | oxygenation | spo2_desaturation_burden | oxygen_desaturation_available | ODI 3% 32.2 events per sleep hour; ODI 4% 16.1 events per sleep hour; time below 90% SpO2 3.6% of plausible sleep samples. |
| slp67x | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |

## How To Read This

- The core disease-style output is `ahi_style_events_per_sleep_hour`: respiratory event annotations divided by sleep hours.
- Adult AHI learning bands used here are: <5 minimal, 5-14 mild, 15-29 moderate, and >=30 severe events per sleep hour.
- A real clinical conclusion still needs scoring-rule context, symptoms, waveform review, oxygen desaturation, arousals, comorbidities, and clinician review.
- SO2-derived desaturation metrics add oxygenation evidence, but artifact review, airflow reduction, arousal scoring, and clinician interpretation are still required before diagnostic use.
- Treatment reasoning should be framed as questions: whether OSA evidence supports PAP evaluation, oral-appliance discussion, weight/lifestyle work, positional therapy, surgery referral, or another diagnosis.

## Next Data Step

Next, manually adjudicate the high-priority source AHI alignment rows, review the pre-event-baseline ODI scorer against artifacts and event windows, and then use the generated dataset-readiness decision report to decide whether a richer PSG dataset is needed for clinical-style examples.

## Source Notes

- PhysioNet MIT-BIH PSG: https://physionet.org/content/slpdb/ and signal/annotation notes at https://archive.physionet.org/physiobank/database/slpdb/slpdb.shtml
- AHI bands cross-check: Cleveland Clinic AHI ranges, https://my.clevelandclinic.org/health/articles/apnea-hypopnea-index-ahi
- Hypopnea scoring context: AASM-recommended adult hypopnea criteria use airflow reduction plus 3% oxygen desaturation or arousal, while CMS-style scoring uses 4% oxygen desaturation; this report computes oxygen-only ODI signals, not full hypopnea events. https://doi.org/10.5664/jcsm.9952
