# Sleep-EDF Next Work Plan

## Current State

The project now has a scoped Sleep-EDF workflow for pilot and expanded analyses.

Completed:

- ECG/HRV core frozen at `hrv-core-v0.1.0`.
- Sleep-EDF preflight, manifest, and first-night Sleep Cassette selection.
- Pilot YASA benchmark for `SC4001`, `SC4011`.
- Five-record benchmark for `SC4001` through `SC4041`.
- Five-record sleep-quality and clinical-learning report.
- Scope-specific output prefixes so expanded runs do not overwrite pilot artifacts.
- Hypnogram timeline plots and sleep architecture plots.
- Reference-vs-YASA discrepancy tables.
- Clinical question ranking for duration, continuity, architecture, respiratory-evidence need, and lights-out context.
- Download and checksum validation through `SC4191`.
- Eight-record YASA runtime profile, benchmark, and clinical-learning report for `SC4001` through `SC4071`.
- MIT-BIH PSG respiratory pilot implementation for apnea/hypopnea annotation burden.
- MIT-BIH PSG SO2-channel oxygenation analysis and event-level waveform review.
- Eleven-record Sleep-EDF YASA runtime profile, benchmark, and clinical-learning report for `SC4001` through `SC4101`.
- Twenty-record Sleep-EDF YASA runtime profile, benchmark, and clinical-learning report for `SC4001` through `SC4191`.
- Sleep-only MIT-BIH SO2 proxy metrics so oxygen evidence is aligned to sleep epochs instead of whole-recording counts.
- MIT-BIH source AHI alignment audit outputs for prioritizing manual scoring-rule review.
- Documented pre-event rolling-baseline ODI scorer for sleep-only SO2 desaturation evidence.
- Oxygen artifact review outputs for prioritizing SO2 waveform/raw-channel checks.

Raw EDF files remain ignored under `data/raw/`.

## Current Local Data

Validated Sleep-EDF records:

- `SC4001`
- `SC4011`
- `SC4021`
- `SC4031`
- `SC4041`
- `SC4051`
- `SC4061`
- `SC4071`
- `SC4081`
- `SC4091`
- `SC4101`
- `SC4111`
- `SC4121`
- `SC4131`
- `SC4141`
- `SC4151`
- `SC4161`
- `SC4171`
- `SC4181`
- `SC4191`

Current validation summary:

- EDF files validated: 40
- bytes: 998,070,310
- missing files: 0
- checksum mismatches: 0

## Current Eight-Record Results

Eight-record outputs:

- `reports/sleep_edf_eight_record_yasa_profile.md`
- `reports/sleep_edf_eight_record_benchmark.md`
- `reports/sleep_edf_eight_record_clinical_education.md`
- `results/sleep_edf/eight_record_yasa_runtime_profile.csv`
- `results/sleep_edf/eight_record_yasa_metrics.csv`
- `results/sleep_edf/eight_record_sleep_quality_metrics.csv`
- `results/sleep_edf/eight_record_clinical_indicators.csv`
- `figures/sleep_edf/eight_record_hypnogram_timeline.png`
- `figures/sleep_edf/eight_record_sleep_architecture.png`

## Current Eleven-Record Results

Eleven-record YASA benchmark:

| records | epochs | accuracy | balanced accuracy | macro-F1 | Cohen's kappa |
| --- | --- | --- | --- | --- | --- |
| SC4001-SC4101 | 30,183 | 0.803 | 0.703 | 0.633 | 0.632 |

Eleven-record outputs:

- `reports/sleep_edf_eleven_record_yasa_profile.md`
- `reports/sleep_edf_eleven_record_benchmark.md`
- `reports/sleep_edf_eleven_record_clinical_education.md`
- `results/sleep_edf/eleven_record_yasa_runtime_profile.csv`
- `results/sleep_edf/eleven_record_yasa_metrics.csv`
- `results/sleep_edf/eleven_record_sleep_quality_metrics.csv`
- `results/sleep_edf/eleven_record_clinical_indicators.csv`
- `figures/sleep_edf/eleven_record_hypnogram_timeline.png`
- `figures/sleep_edf/eleven_record_sleep_architecture.png`

## Current Twenty-Record Results

Twenty-record YASA benchmark:

| records | epochs | accuracy | balanced accuracy | macro-F1 | Cohen's kappa |
| --- | --- | --- | --- | --- | --- |
| SC4001-SC4191 | 54,587 | 0.823 | 0.722 | 0.658 | 0.676 |

Twenty-record outputs:

- `reports/sleep_edf_twenty_record_yasa_profile.md`
- `reports/sleep_edf_twenty_record_benchmark.md`
- `reports/sleep_edf_twenty_record_clinical_education.md`
- `results/sleep_edf/twenty_record_yasa_runtime_profile.csv`
- `results/sleep_edf/twenty_record_yasa_metrics.csv`
- `results/sleep_edf/twenty_record_sleep_quality_metrics.csv`
- `results/sleep_edf/twenty_record_clinical_indicators.csv`
- `figures/sleep_edf/twenty_record_hypnogram_timeline.png`
- `figures/sleep_edf/twenty_record_sleep_architecture.png`

## Current Five-Record Results

Five-record YASA benchmark:

| records | epochs | accuracy | balanced accuracy | macro-F1 | Cohen's kappa |
| --- | --- | --- | --- | --- | --- |
| SC4001-SC4041 | 13,645 | 0.793 | 0.711 | 0.631 | 0.628 |

Five-record clinical-learning outputs:

- `reports/sleep_edf_five_record_clinical_education.md`
- `results/sleep_edf/five_record_sleep_quality_metrics.csv`
- `results/sleep_edf/five_record_clinical_indicators.csv`
- `results/sleep_edf/five_record_clinical_question_ranking.csv`
- `results/sleep_edf/five_record_yasa_discrepancy.csv`
- `figures/sleep_edf/five_record_hypnogram_timeline.png`
- `figures/sleep_edf/five_record_sleep_architecture.png`

## Key Interpretation

Reference hypnograms remain the primary view for sleep-quality learning. YASA is useful as a model-derived comparison, but the five-record discrepancy table shows that YASA can assign sleep stages in long wake regions. Those differences can strongly distort downstream clinical-style metrics such as WASO and sleep-period efficiency.

Sleep-EDF can support:

- sleep architecture;
- total sleep time;
- inferred sleep-period efficiency;
- inferred WASO;
- REM latency;
- stage balance;
- fragmentation proxies.

Sleep-EDF cannot directly support:

- AHI/RDI;
- oxygen desaturation burden;
- apnea/hypopnea diagnosis;
- PAP/oral appliance treatment reasoning;
- hypoventilation reasoning;
- respiratory-event severity.

## Next Implementation Track

### Track A: Source AHI Alignment

The Sleep-EDF 20-record selected set is now complete. The next priority is not more Sleep-EDF scaling; it is reconciling MIT-BIH annotation-token burden with source AHI and scoring assumptions.

### Track C: Respiratory PSG Dataset

MIT-BIH PSG is now the active disease-specific respiratory reasoning track.

Implementation outline:

1. Done: add `configs/mit_bih_psg.yaml`.
2. Done: download a small MIT-BIH PSG pilot subset.
3. Done: parse sleep/apnea annotations.
4. Done: compute apnea annotation burden per sleep hour.
5. Done: add respiration/SpO2 quality checks.
6. Done: extend the clinical-learning report with respiratory-event evidence.
7. Done: add SO2-channel MIT-BIH records for oxygen desaturation burden.
8. Done: generate event-level waveform windows and plots around scored respiratory events.
9. Done: run the 18-record `complete_record` MIT-BIH report.
10. Done: split SO2 outputs into recording-wide audit values and sleep-only clinical-learning proxy values.
11. Done: add source AHI alignment audit tables and CSVs.
12. Done: replace the main sleep-only oxygen proxy with a documented pre-event rolling-baseline ODI scorer.
13. Done: add oxygen artifact review tables and CSVs.
14. Next: manually adjudicate high-priority alignment rows against source scoring assumptions.
15. Next: decide whether to add a richer PSG dataset for clinical-style examples.

## Evidence Boundary

The goal is to learn how data supports clinical reasoning. The reports should show sleep-quality signals, disease hypotheses, and missing diagnostic evidence. They should not claim a final diagnosis or treatment decision without the signals required for that disorder.
