# MIT-BIH PSG Respiratory Pilot

## Purpose

This report starts the respiratory and OSA-style evidence phase. It turns MIT-BIH `.st` sleep/apnea annotations into an annotation burden per sleep hour, checks whether respiration or SpO2 channels are present, and maps the results to clinical learning questions.

It is an educational analysis, not a diagnosis, prescription, or triage tool.

## Records

- Records: slp01a, slp02a, slp03.
- Epoch size: 30 s; each `.st` annotation is interpreted as applying to the following epoch.
- Pilot records use actual PhysioNet record IDs `slp01a`, `slp02a`, and `slp03`; the `a` suffix matters for segmented records.

## Respiratory Event Burden

| record | sleep h | events | burden/h | range | source AHI | delta | obstructive/h | central/h | hypopnea/h |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| slp01a | 1.93 | 37 | 19.1 | moderate range | 17.0 | 2.1 | 0.0 | 0.0 | 19.1 |
| slp02a | 2.57 | 80 | 31.2 | severe range | 34.0 | -2.8 | 27.3 | 0.0 | 3.9 |
| slp03 | 4.74 | 250 | 52.7 | severe range | 43.0 | 9.7 | 7.6 | 2.5 | 42.6 |

## Channel Quality

The pilot records include respiration channels, but these three records do not expose SpO2/oximetry channels. That means oxygen desaturation burden cannot be interpreted from this pilot subset.

| record | channel | unit | finite % | std | dynamic |
| --- | --- | --- | --- | --- | --- |
| slp01a | Resp (sum) | l | 100.00 | 0.4063 | True |
| slp02a | Resp (nasal) | l | 100.00 | 0.2992 | True |
| slp03 | Resp (nasal) | l | 100.00 | 0.2226 | True |

## Clinical Learning Indicators

| record | domain | indicator | status | evidence |
| --- | --- | --- | --- | --- |
| slp01a | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 19.1 respiratory events per sleep hour (moderate range). |
| slp01a | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp01a | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this pilot record. |
| slp01a | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp02a | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 31.2 respiratory events per sleep hour (severe range). |
| slp02a | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp02a | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this pilot record. |
| slp02a | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |
| slp03 | sleep_disordered_breathing | apnea_hypopnea_annotation_burden | screen_positive_learning_signal | Annotation burden 52.7 respiratory events per sleep hour (severe range). |
| slp03 | signal_quality | respiration_channel_available | available | Respiration channel is present with dynamic sampled signal. |
| slp03 | oxygenation | spo2_desaturation_burden | not_available_in_record | No SpO2/oximetry channel detected in this pilot record. |
| slp03 | treatment_reasoning | osa_treatment_path | educational_question_only | Respiratory-event burden can motivate PAP/oral-appliance/referral questions, but treatment selection is not made from this pilot output. |

## How To Read This

- The core disease-style output is `ahi_style_events_per_sleep_hour`: respiratory event annotations divided by sleep hours.
- Adult AHI learning bands used here are: <5 minimal, 5-14 mild, 15-29 moderate, and >=30 severe events per sleep hour.
- A real clinical conclusion still needs scoring-rule context, symptoms, waveform review, oxygen desaturation, arousals, comorbidities, and clinician review.
- Treatment reasoning should be framed as questions: whether OSA evidence supports PAP evaluation, oral-appliance discussion, weight/lifestyle work, positional therapy, surgery referral, or another diagnosis.

## Next Data Step

Add MIT-BIH records with SO2 channels, such as `slp59`, `slp60`, `slp61`, `slp66`, or `slp67x`, or move to a PSG dataset with richer oximetry and respiratory-event scoring.

## Source Notes

- PhysioNet MIT-BIH PSG: https://physionet.org/content/slpdb/ and signal/annotation notes at https://archive.physionet.org/physiobank/database/slpdb/slpdb.shtml
- AHI bands cross-check: Cleveland Clinic AHI ranges, https://my.clevelandclinic.org/health/articles/apnea-hypopnea-index-ahi
