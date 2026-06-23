# MIT-BIH PSG Respiratory Pilot

## Purpose

This report starts the respiratory and OSA-style evidence phase. It turns MIT-BIH `.st` sleep/apnea annotations into an annotation burden per sleep hour, checks whether respiration or SpO2 channels are present, and maps the results to clinical learning questions.

It is an educational analysis, not a diagnosis, prescription, or triage tool.

## Records

- Records: slp01a, slp02a, slp03.
- Epoch size: 30 s; each `.st` annotation is interpreted as applying to the following epoch.
- Record IDs are PhysioNet WFDB record IDs; segmented records such as `slp01a` and `slp02a` keep their suffixes.

## Respiratory Event Burden

| record | sleep h | events | burden/h | range | source AHI | source note | delta | obstructive/h | central/h | hypopnea/h |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| slp01a | 1.93 | 37 | 19.1 | moderate range | 17.0 |  | 2.1 | 0.0 | 0.0 | 19.1 |
| slp02a | 2.57 | 80 | 31.2 | severe range | 34.0 |  | -2.8 | 27.3 | 0.0 | 3.9 |
| slp03 | 4.74 | 250 | 52.7 | severe range | 43.0 |  | 9.7 | 7.6 | 2.5 | 42.6 |

## Channel Quality

The selected records include respiration channels, but no SpO2/oximetry channels. Oxygen desaturation burden cannot be interpreted from this subset.

| record | channel | unit | finite % | std | dynamic |
| --- | --- | --- | --- | --- | --- |
| slp01a | Resp (sum) | l | 100.00 | 0.4063 | True |
| slp02a | Resp (nasal) | l | 100.00 | 0.2992 | True |
| slp03 | Resp (nasal) | l | 100.00 | 0.2226 | True |

## Oxygen Saturation

SO2 metrics are computed only when an oximetry channel is present. The report table uses sleep-only low-oxygen and ODI proxy values; recording-wide oxygen summaries remain in the CSV for audit. Desaturation counts are labeled as proxy metrics because this code uses a percentile-derived baseline and has not replaced clinical scoring rules.

| record | SO2 channel | status | median % | min % | below 90 % | below 90 % sleep | ODI 3% proxy | ODI 4% proxy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| slp01a |  | no_spo2_channel | NA | NA | NA | NA | NA | NA |
| slp02a |  | no_spo2_channel | NA | NA | NA | NA | NA | NA |
| slp03 |  | no_spo2_channel | NA | NA | NA | NA | NA | NA |

## Event-Level Waveform Review

The event window table summarizes respiration channel windows around the first scored respiratory-event epochs per record. Generated figures overlay the scored 30 s event epoch on respiration and SO2 channels when available.

| record | epoch | tokens | stage | window s | resp mean | resp std |
| --- | --- | --- | --- | --- | --- | --- |
| slp01a | 12 | HA | N3 | 330.0-420.0 | 0.042 | 0.561 |
| slp01a | 13 | H LA | N3 | 360.0-450.0 | 0.037 | 0.373 |
| slp01a | 36 | LA HA LA | N3 | 1050.0-1140.0 | 0.046 | 0.430 |
| slp01a | 46 | H | N2 | 1350.0-1440.0 | 0.040 | 0.394 |
| slp01a | 49 | H | N2 | 1440.0-1530.0 | 0.034 | 0.378 |
| slp02a | 8 | X | N2 | 210.0-300.0 | -0.301 | 0.731 |
| slp02a | 9 | X | N2 | 240.0-330.0 | -0.379 | 0.508 |
| slp02a | 10 | X X | N2 | 270.0-360.0 | -0.345 | 0.526 |
| slp02a | 11 | X | N2 | 300.0-390.0 | -0.346 | 0.462 |
| slp02a | 13 | X | N2 | 360.0-450.0 | -0.353 | 0.446 |
| slp03 | 0 | HA | N2 | 0.0-60.0 | -0.029 | 0.223 |
| slp03 | 1 | HA | N2 | 0.0-90.0 | -0.024 | 0.239 |
| slp03 | 2 | HA | N2 | 30.0-120.0 | -0.025 | 0.256 |
| slp03 | 3 | HA HA | N2 | 60.0-150.0 | -0.020 | 0.287 |
| slp03 | 4 | HA | N2 | 90.0-180.0 | -0.025 | 0.284 |

Generated event plots:

- `figures/mit_bih_psg/slp01a_epoch_0012.png`
- `figures/mit_bih_psg/slp01a_epoch_0013.png`
- `figures/mit_bih_psg/slp02a_epoch_0008.png`
- `figures/mit_bih_psg/slp02a_epoch_0009.png`
- `figures/mit_bih_psg/slp03_epoch_0000.png`
- `figures/mit_bih_psg/slp03_epoch_0001.png`

## Clinical Learning Indicators

| record | domain | indicator | status | evidence |
| --- | --- | --- | --- | --- |
| slp01a | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 19.1 respiratory events per sleep hour (moderate range). |
| slp01a | source_consistency | annotation_burden_vs_source_ahi | roughly_aligned | Annotation burden minus source AHI is 2.1 events/h. |
| slp01a | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp01a | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp01a | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp02a | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 31.2 respiratory events per sleep hour (severe range). |
| slp02a | source_consistency | annotation_burden_vs_source_ahi | roughly_aligned | Annotation burden minus source AHI is -2.8 events/h. |
| slp02a | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp02a | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp02a | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp03 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 52.7 respiratory events per sleep hour (severe range). |
| slp03 | source_consistency | annotation_burden_vs_source_ahi | roughly_aligned | Annotation burden minus source AHI is 9.7 events/h. |
| slp03 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp03 | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this record. |
| slp03 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |

## How To Read This

- The core disease-style output is `ahi_style_events_per_sleep_hour`: respiratory event annotations divided by sleep hours.
- Adult AHI learning bands used here are: <5 minimal, 5-14 mild, 15-29 moderate, and >=30 severe events per sleep hour.
- A real clinical conclusion still needs scoring-rule context, symptoms, waveform review, oxygen desaturation, arousals, comorbidities, and clinician review.
- SO2-derived desaturation metrics add oxygenation evidence, but artifact review and clinical scoring rules are still required before diagnostic use.
- Treatment reasoning should be framed as questions: whether OSA evidence supports PAP evaluation, oral-appliance discussion, weight/lifestyle work, positional therapy, surgery referral, or another diagnosis.

## Next Data Step

Next, compare annotation burden, oxygen desaturation proxies, and waveform windows across a larger record set, then decide whether a richer PSG dataset is needed for clinical-style examples.

## Source Notes

- PhysioNet MIT-BIH PSG: https://physionet.org/content/slpdb/ and signal/annotation notes at https://archive.physionet.org/physiobank/database/slpdb/slpdb.shtml
- AHI bands cross-check: Cleveland Clinic AHI ranges, https://my.clevelandclinic.org/health/articles/apnea-hypopnea-index-ahi
