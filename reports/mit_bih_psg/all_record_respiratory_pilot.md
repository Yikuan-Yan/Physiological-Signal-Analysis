# MIT-BIH PSG Respiratory Pilot

## Purpose

This report starts the respiratory and OSA-style evidence phase. It turns MIT-BIH `.st` sleep/apnea annotations into an annotation burden per sleep hour, checks whether respiration or SpO2 channels are present, and maps the results to clinical learning questions.

It is an educational analysis, not a diagnosis, prescription, or triage tool.

## Records

- Records: slp01a, slp01b, slp02a, slp02b, slp03, slp04, slp14, slp16, slp32, slp37, slp41, slp45, slp48, slp59, slp60, slp61, slp66, slp67x.
- Epoch size: 30 s; each `.st` annotation is interpreted as applying to the following epoch.
- Record IDs are PhysioNet WFDB record IDs; segmented records such as `slp01a` and `slp02a` keep their suffixes.

## Respiratory Event Burden

| record | sleep h | events | burden/h | range | source AHI | source note | delta | obstructive/h | central/h | hypopnea/h |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| slp01a | 1.93 | 37 | 19.1 | moderate range | 17.0 |  | 2.1 | 0.0 | 0.0 | 19.1 |
| slp01b | 1.50 | 60 | 40.0 | severe range | 22.3 |  | 17.7 | 1.3 | 3.3 | 35.3 |
| slp02a | 2.57 | 80 | 31.2 | severe range | 34.0 |  | -2.8 | 27.3 | 0.0 | 3.9 |
| slp02b | 1.35 | 28 | 20.7 | moderate range | 22.2 |  | -1.5 | 19.3 | 0.0 | 1.5 |
| slp03 | 4.74 | 250 | 52.7 | severe range | 43.0 |  | 9.7 | 7.6 | 2.5 | 42.6 |
| slp04 | 4.65 | 339 | 72.9 | severe range | 59.8 |  | 13.1 | 72.7 | 0.0 | 0.2 |
| slp14 | 3.27 | 170 | 52.0 | severe range | 30.7 |  | 21.3 | 27.9 | 0.0 | 24.2 |
| slp16 | 3.15 | 252 | 80.0 | severe range | 53.1 |  | 26.9 | 63.5 | 4.8 | 11.7 |
| slp32 | 2.05 | 110 | 53.7 | severe range | 22.1 |  | 31.6 | 53.2 | 0.0 | 0.5 |
| slp37 | 5.19 | 567 | 109.2 | severe range | 100.8 |  | 8.4 | 109.2 | 0.0 | 0.0 |
| slp41 | 4.59 | 0 | 0.0 | minimal range | 60.0 | estimated_from_visual_review_apnea_annotations_unavailable | -60.0 | 0.0 | 0.0 | 0.0 |
| slp45 | 5.31 | 0 | 0.0 | minimal range | 5.0 | estimated_from_visual_review_apnea_annotations_unavailable | -5.0 | 0.0 | 0.0 | 0.0 |
| slp48 | 4.55 | 277 | 60.9 | severe range | 46.8 |  | 14.1 | 31.0 | 0.2 | 29.7 |
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
| slp32 | 53.7 | 22.1 | 31.6 | needs_manual_review | manual_review_high | obstructive_apnea | Inspect event tokens, sleep/wake exclusion, and source scoring assumptions. |
| slp16 | 80.0 | 53.1 | 26.9 | needs_manual_review | manual_review_high | obstructive_apnea | Inspect event tokens, sleep/wake exclusion, and source scoring assumptions. |
| slp60 | 82.4 | 59.2 | 23.2 | needs_manual_review | manual_review_high | obstructive_apnea | Inspect event tokens, sleep/wake exclusion, and source scoring assumptions. |
| slp14 | 52.0 | 30.7 | 21.3 | needs_manual_review | manual_review_high | obstructive_apnea | Inspect event tokens, sleep/wake exclusion, and source scoring assumptions. |
| slp01b | 40.0 | 22.3 | 17.7 | needs_manual_review | manual_review_high | hypopnea | Inspect event tokens, sleep/wake exclusion, and source scoring assumptions. |
| slp59 | 69.4 | 55.3 | 14.1 | needs_manual_review | manual_review_high | obstructive_apnea | Inspect event tokens, sleep/wake exclusion, and source scoring assumptions. |
| slp48 | 60.9 | 46.8 | 14.1 | needs_manual_review | manual_review_high | obstructive_apnea | Inspect event tokens, sleep/wake exclusion, and source scoring assumptions. |
| slp04 | 72.9 | 59.8 | 13.1 | needs_manual_review | manual_review_high | obstructive_apnea | Inspect event tokens, sleep/wake exclusion, and source scoring assumptions. |
| slp41 | 0.0 | 60.0 | -60.0 | source_ahi_estimated_annotation_unavailable | separate_source_review | none | Source AHI is estimated and apnea annotations are unavailable; do not interpret annotation burden as true no-OSA evidence. |
| slp45 | 0.0 | 5.0 | -5.0 | source_ahi_estimated_annotation_unavailable | separate_source_review | none | Source AHI is estimated and apnea annotations are unavailable; do not interpret annotation burden as true no-OSA evidence. |
| slp03 | 52.7 | 43.0 | 9.7 | roughly_aligned | manual_review_medium | hypopnea | Review scoring assumptions if this record is used as an example. |
| slp37 | 109.2 | 100.8 | 8.4 | roughly_aligned | manual_review_medium | obstructive_apnea | Review scoring assumptions if this record is used as an example. |
| slp61 | 49.1 | 41.2 | 7.9 | roughly_aligned | manual_review_medium | obstructive_apnea | Review scoring assumptions if this record is used as an example. |
| slp02a | 31.2 | 34.0 | -2.8 | roughly_aligned | low | obstructive_apnea | Token burden is close enough for the current educational proxy. |
| slp01a | 19.1 | 17.0 | 2.1 | roughly_aligned | low | hypopnea | Token burden is close enough for the current educational proxy. |
| slp02b | 20.7 | 22.2 | -1.5 | roughly_aligned | low | obstructive_apnea | Token burden is close enough for the current educational proxy. |

## Channel Quality

Some selected records include SO2/oximetry channels (slp59, slp60, slp61, slp66, slp67x); records without SO2 keep oxygen metrics unavailable.

| record | channel | unit | finite % | std | dynamic |
| --- | --- | --- | --- | --- | --- |
| slp01a | Resp (sum) | l | 100.00 | 0.4063 | True |
| slp01b | Resp (sum) | l | 100.00 | 0.5000 | True |
| slp02a | Resp (nasal) | l | 100.00 | 0.2992 | True |
| slp02b | Resp (nasal) | l | 100.00 | 0.2193 | True |
| slp03 | Resp (nasal) | l | 100.00 | 0.2226 | True |
| slp04 | Resp (nasal) | l | 100.00 | 0.1547 | True |
| slp14 | Resp (nasal) | l | 100.00 | 0.1671 | True |
| slp16 | Resp (nasal) | l | 100.00 | 0.1889 | True |
| slp32 | Resp (nasal) | l | 100.00 | 0.3136 | True |
| slp32 | Resp (chest) | l | 100.00 | 0.1749 | True |
| slp37 | Resp (nasal) | l | 100.00 | 0.0583 | True |
| slp37 | Resp (abdominal) | l | 100.00 | 0.2696 | True |
| slp41 | Resp (nasal) | l | 100.00 | 0.1939 | True |
| slp41 | Resp (abdominal) | l | 100.00 | 0.0006 | True |
| slp45 | Resp (nasal) | l | 100.00 | 0.2528 | True |
| slp45 | Resp (abdominal) | l | 100.00 | 0.2567 | True |
| slp48 | Resp (nasal) | l | 100.00 | 0.1610 | True |
| slp48 | Resp (chest) | l | 100.00 | 0.2715 | True |
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
| slp01a |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp01b |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp02a |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp02b |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp03 |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp04 |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp14 |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp16 |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp32 |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp37 |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp41 |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp45 |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp48 |  | no_spo2_channel | NA | NA | NA | NA | NA | NA | pre_event_rolling_baseline |
| slp59 | SO2 | available | 91.5 | 40.0 | 26.0 | 25.3 | 45.7 | 40.0 | pre_event_rolling_baseline |
| slp60 | SO2 | available | 93.0 | 70.7 | 15.2 | 20.1 | 45.6 | 37.1 | pre_event_rolling_baseline |
| slp61 | SO2 | available | 94.6 | 40.0 | 18.8 | 19.6 | 34.8 | 32.2 | pre_event_rolling_baseline |
| slp66 | SO2 | available | 90.8 | 81.9 | 30.9 | 42.1 | 53.2 | 24.1 | pre_event_rolling_baseline |
| slp67x | SO2 | available | 93.7 | 83.7 | 12.1 | 3.6 | 32.2 | 16.1 | pre_event_rolling_baseline |

## Oxygen Artifact Review

This table flags records where the ODI scorer should be reviewed against the generated waveform windows or raw SO2 channel before using the oxygen signal as clinical-learning evidence.

| record | status | priority | flags | ODI3 minus proxy | focus |
| --- | --- | --- | --- | --- | --- |
| slp01a | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp01b | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp02a | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp02b | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp03 | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp04 | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp14 | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp16 | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp32 | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp37 | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp41 | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp45 | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp48 | not_available | none |  | NA | No sleep-aligned plausible SO2 signal was available. |
| slp59 | artifact_review_recommended | medium | very_low_spo2_value | 3.8 | Inspect SO2 waveform windows and raw channel for dropout, motion artifact, baseline drift, and whether desaturations align with respiratory events. |
| slp60 | oxygen_review_ready | low |  | 6.5 | ODI output has no automatic artifact flags; spot-check event windows. |
| slp61 | artifact_review_recommended | medium | very_low_spo2_value | 5.4 | Inspect SO2 waveform windows and raw channel for dropout, motion artifact, baseline drift, and whether desaturations align with respiratory events. |
| slp66 | artifact_review_recommended | medium | high_sleep_time_below_90 | 7.7 | Inspect SO2 waveform windows and raw channel for dropout, motion artifact, baseline drift, and whether desaturations align with respiratory events. |
| slp67x | oxygen_review_ready | low |  | -8.8 | ODI output has no automatic artifact flags; spot-check event windows. |

## Event-Level Waveform Review

The event window table summarizes respiration channel windows around the first scored respiratory-event epochs per record. Generated figures overlay the scored 30 s event epoch on respiration and SO2 channels when available.

| record | epoch | tokens | stage | window s | resp mean | resp std |
| --- | --- | --- | --- | --- | --- | --- |
| slp01a | 12 | HA | N3 | 330.0-420.0 | 0.042 | 0.561 |
| slp01a | 13 | H LA | N3 | 360.0-450.0 | 0.037 | 0.373 |
| slp01a | 36 | LA HA LA | N3 | 1050.0-1140.0 | 0.046 | 0.430 |
| slp01a | 46 | H | N2 | 1350.0-1440.0 | 0.040 | 0.394 |
| slp01a | 49 | H | N2 | 1440.0-1530.0 | 0.034 | 0.378 |
| slp01b | 145 | H | N1 | 4320.0-4410.0 | -0.046 | 0.416 |
| slp01b | 147 | HA | N1 | 4380.0-4470.0 | -0.014 | 0.422 |
| slp01b | 148 | H | N2 | 4410.0-4500.0 | -0.033 | 0.393 |
| slp01b | 149 | H | N2 | 4440.0-4530.0 | -0.048 | 0.379 |
| slp01b | 150 | H | N2 | 4470.0-4560.0 | -0.060 | 0.378 |
| slp02a | 8 | X | N2 | 210.0-300.0 | -0.301 | 0.731 |
| slp02a | 9 | X | N2 | 240.0-330.0 | -0.379 | 0.508 |
| slp02a | 10 | X X | N2 | 270.0-360.0 | -0.345 | 0.526 |
| slp02a | 11 | X | N2 | 300.0-390.0 | -0.346 | 0.462 |
| slp02a | 13 | X | N2 | 360.0-450.0 | -0.353 | 0.446 |
| slp02b | 55 | LA H | N2 | 1620.0-1710.0 | -0.371 | 0.231 |
| slp02b | 67 | A X | N1 | 1980.0-2070.0 | -0.287 | 0.287 |
| slp02b | 68 | X | N1 | 2010.0-2100.0 | -0.312 | 0.286 |
| slp02b | 69 | X | N2 | 2040.0-2130.0 | -0.348 | 0.223 |
| slp02b | 72 | X | N2 | 2130.0-2220.0 | -0.373 | 0.280 |

Generated event plots:

- `figures/mit_bih_psg/all_record/slp01a_epoch_0012.png`
- `figures/mit_bih_psg/all_record/slp01a_epoch_0013.png`
- `figures/mit_bih_psg/all_record/slp01b_epoch_0145.png`
- `figures/mit_bih_psg/all_record/slp01b_epoch_0147.png`
- `figures/mit_bih_psg/all_record/slp02a_epoch_0008.png`
- `figures/mit_bih_psg/all_record/slp02a_epoch_0009.png`
- `figures/mit_bih_psg/all_record/slp02b_epoch_0055.png`
- `figures/mit_bih_psg/all_record/slp02b_epoch_0067.png`
- `figures/mit_bih_psg/all_record/slp03_epoch_0000.png`
- `figures/mit_bih_psg/all_record/slp03_epoch_0001.png`
- `figures/mit_bih_psg/all_record/slp04_epoch_0001.png`
- `figures/mit_bih_psg/all_record/slp04_epoch_0002.png`
- `figures/mit_bih_psg/all_record/slp14_epoch_0016.png`
- `figures/mit_bih_psg/all_record/slp14_epoch_0017.png`
- `figures/mit_bih_psg/all_record/slp16_epoch_0014.png`
- `figures/mit_bih_psg/all_record/slp16_epoch_0017.png`
- `figures/mit_bih_psg/all_record/slp32_epoch_0094.png`
- `figures/mit_bih_psg/all_record/slp32_epoch_0095.png`
- `figures/mit_bih_psg/all_record/slp37_epoch_0001.png`
- `figures/mit_bih_psg/all_record/slp37_epoch_0002.png`

## Clinical Learning Indicators

| record | domain | indicator | status | evidence |
| --- | --- | --- | --- | --- |
| slp01a | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 19.1 respiratory events per sleep hour (moderate range). |
| slp01a | source_consistency | annotation_burden_vs_source_ahi | roughly_aligned | Annotation burden minus source AHI is 2.1 events/h. |
| slp01a | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp01a | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp01a | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp01b | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 40.0 respiratory events per sleep hour (severe range). |
| slp01b | source_consistency | annotation_burden_vs_source_ahi | needs_manual_review | Annotation burden minus source AHI is 17.7 events/h. |
| slp01b | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp01b | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp01b | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp02a | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 31.2 respiratory events per sleep hour (severe range). |
| slp02a | source_consistency | annotation_burden_vs_source_ahi | roughly_aligned | Annotation burden minus source AHI is -2.8 events/h. |
| slp02a | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp02a | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp02a | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp02b | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 20.7 respiratory events per sleep hour (moderate range). |
| slp02b | source_consistency | annotation_burden_vs_source_ahi | roughly_aligned | Annotation burden minus source AHI is -1.5 events/h. |
| slp02b | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp02b | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp02b | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp03 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 52.7 respiratory events per sleep hour (severe range). |
| slp03 | source_consistency | annotation_burden_vs_source_ahi | roughly_aligned | Annotation burden minus source AHI is 9.7 events/h. |
| slp03 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp03 | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp03 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp04 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 72.9 respiratory events per sleep hour (severe range). |
| slp04 | source_consistency | annotation_burden_vs_source_ahi | needs_manual_review | Annotation burden minus source AHI is 13.1 events/h. |
| slp04 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp04 | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp04 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp14 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 52.0 respiratory events per sleep hour (severe range). |
| slp14 | source_consistency | annotation_burden_vs_source_ahi | needs_manual_review | Annotation burden minus source AHI is 21.3 events/h. |
| slp14 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp14 | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp14 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp16 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 80.0 respiratory events per sleep hour (severe range). |
| slp16 | source_consistency | annotation_burden_vs_source_ahi | needs_manual_review | Annotation burden minus source AHI is 26.9 events/h. |
| slp16 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp16 | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp16 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp32 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 53.7 respiratory events per sleep hour (severe range). |
| slp32 | source_consistency | annotation_burden_vs_source_ahi | needs_manual_review | Annotation burden minus source AHI is 31.6 events/h. |
| slp32 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp32 | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp32 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp37 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 109.2 respiratory events per sleep hour (severe range). |
| slp37 | source_consistency | annotation_burden_vs_source_ahi | roughly_aligned | Annotation burden minus source AHI is 8.4 events/h. |
| slp37 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp37 | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp37 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp41 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | below_osa_learning_threshold | Annotation burden 0.0 respiratory events per sleep hour (minimal range). |
| slp41 | source_consistency | annotation_burden_vs_source_ahi | source_ahi_estimated_annotation_unavailable | Annotation burden minus source AHI is -60.0 events/h. Source note: estimated_from_visual_review_apnea_annotations_unavailable. |
| slp41 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp41 | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp41 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp45 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | below_osa_learning_threshold | Annotation burden 0.0 respiratory events per sleep hour (minimal range). |
| slp45 | source_consistency | annotation_burden_vs_source_ahi | source_ahi_estimated_annotation_unavailable | Annotation burden minus source AHI is -5.0 events/h. Source note: estimated_from_visual_review_apnea_annotations_unavailable. |
| slp45 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp45 | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp45 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp48 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 60.9 respiratory events per sleep hour (severe range). |
| slp48 | source_consistency | annotation_burden_vs_source_ahi | needs_manual_review | Annotation burden minus source AHI is 14.1 events/h. |
| slp48 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp48 | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp48 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
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
