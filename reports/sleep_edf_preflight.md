# Sleep-EDF Preflight Report

## Scope

This preflight freezes the Sleep-EDF/YASA expansion protocol after the Fantasia HRV core gate. It selects the benchmark records and records the label mapping before any model results are inspected.

This report does not evaluate sleep quality, diagnose sleep disorders, or make event-detector accuracy claims.

## Dataset

- Dataset: Sleep-EDF Database Expanded v1.0.0.
- DOI: https://doi.org/10.13026/C2X676.
- License: Open Data Commons Attribution License v1.0.
- Access date: 2026-06-22.
- Source index: https://physionet.org/files/sleep-edfx/1.0.0/sleep-cassette/.
- Cohort included: Sleep Cassette only.
- Cohorts excluded: Sleep Telemetry, to avoid mixing home healthy recordings with hospital/temazepam protocol recordings.

## Frozen Selection

- Selection rule: first_available_night_for_first_20_sorted_sleep_cassette_subjects.
- Participants: 20 total; 2 pilot and 18 benchmark-only.
- Subject IDs: 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419.
- Recording per participant: first available paired PSG/Hypnogram night.

| subject_id | night | role | recording_id | psg_filename | hypnogram_filename |
| --- | --- | --- | --- | --- | --- |
| 400 | 1 | pilot | SC4001 | SC4001E0-PSG.edf | SC4001EC-Hypnogram.edf |
| 401 | 1 | pilot | SC4011 | SC4011E0-PSG.edf | SC4011EH-Hypnogram.edf |
| 402 | 1 | benchmark | SC4021 | SC4021E0-PSG.edf | SC4021EH-Hypnogram.edf |
| 403 | 1 | benchmark | SC4031 | SC4031E0-PSG.edf | SC4031EC-Hypnogram.edf |
| 404 | 1 | benchmark | SC4041 | SC4041E0-PSG.edf | SC4041EC-Hypnogram.edf |
| 405 | 1 | benchmark | SC4051 | SC4051E0-PSG.edf | SC4051EC-Hypnogram.edf |
| 406 | 1 | benchmark | SC4061 | SC4061E0-PSG.edf | SC4061EC-Hypnogram.edf |
| 407 | 1 | benchmark | SC4071 | SC4071E0-PSG.edf | SC4071EC-Hypnogram.edf |
| 408 | 1 | benchmark | SC4081 | SC4081E0-PSG.edf | SC4081EC-Hypnogram.edf |
| 409 | 1 | benchmark | SC4091 | SC4091E0-PSG.edf | SC4091EC-Hypnogram.edf |
| 410 | 1 | benchmark | SC4101 | SC4101E0-PSG.edf | SC4101EC-Hypnogram.edf |
| 411 | 1 | benchmark | SC4111 | SC4111E0-PSG.edf | SC4111EC-Hypnogram.edf |
| 412 | 1 | benchmark | SC4121 | SC4121E0-PSG.edf | SC4121EC-Hypnogram.edf |
| 413 | 1 | benchmark | SC4131 | SC4131E0-PSG.edf | SC4131EC-Hypnogram.edf |
| 414 | 1 | benchmark | SC4141 | SC4141E0-PSG.edf | SC4141EU-Hypnogram.edf |
| 415 | 1 | benchmark | SC4151 | SC4151E0-PSG.edf | SC4151EC-Hypnogram.edf |
| 416 | 1 | benchmark | SC4161 | SC4161E0-PSG.edf | SC4161EC-Hypnogram.edf |
| 417 | 1 | benchmark | SC4171 | SC4171E0-PSG.edf | SC4171EU-Hypnogram.edf |
| 418 | 1 | benchmark | SC4181 | SC4181E0-PSG.edf | SC4181EC-Hypnogram.edf |
| 419 | 1 | benchmark | SC4191 | SC4191E0-PSG.edf | SC4191EP-Hypnogram.edf |

## Label Mapping

| R&K label | mapped class | status |
| --- | --- | --- |
| W | WAKE | included |
| 1 | N1 | included |
| 2 | N2 | included |
| 3 | N3 | included |
| 4 | N3 | included |
| R | REM | included |
| M | excluded | excluded |
| ? | excluded | excluded |

Movement and unscored epochs are excluded from the primary five-class benchmark.

## YASA Branch Rules

- Staging branch: pass raw MNE object into YASA SleepStaging without project-side z-score or filter.
- Staging channels: EEG `Fpz-Cz`, EOG `EOG horizontal`, EMG `EMG submental`.
- Spectral branch and event branch must be implemented separately from staging preprocessing.
- Channel limitation: Sleep-EDF Fpz-Cz/Pz-Oz are not YASA's preferred central derivations.

## Acceptance Checks

- 20 Sleep Cassette participants are frozen before model execution.
- Each selected participant has one PSG file and one matching Hypnogram file.
- R&K label mapping is explicit and unit-tested.
- Baseline/model benchmark must report majority-stage baseline, macro-F1, balanced accuracy, Cohen's kappa, per-stage metrics, and participant-level uncertainty.
- Spindle and slow-wave detections remain exploratory summaries because Sleep-EDF has no event-level expert annotation.

## Next Implementation Step

Download the selected PSG/Hypnogram pairs into `data/raw/sleep-edfx/1.0.0`, then implement a benchmark command that reads EDF files, aligns 30 s hypnogram epochs, runs the majority baseline and YASA model, and writes participant-level metrics.
