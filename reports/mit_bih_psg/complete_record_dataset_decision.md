# MIT-BIH PSG Dataset Readiness And Richer PSG Decision

## Decision

Keep MIT-BIH PSG as the current respiratory clinical-learning dataset. Do not automatically add a richer PSG dataset until manual source-AHI alignment and SO2 artifact review are completed.

## Why

- Records analyzed: 18.
- Source alignment statuses: needs_manual_review=10, roughly_aligned=6, source_ahi_estimated_annotation_unavailable=2
- Source alignment priorities: low=3, manual_review_high=10, manual_review_medium=3, separate_source_review=2
- Oxygen review statuses: artifact_review_recommended=3, not_available=13, oxygen_review_ready=2
- Clinical-style example tiers: manual_source_alignment_needed=10, respiratory_annotation_learning_ready=6, source_context_only=2

## What The Current Data Can Teach

- Respiratory event burden from sleep/apnea annotations, especially records with roughly aligned source AHI: slp01a, slp02a, slp02b, slp03, slp37, slp61.
- Sleep-aligned oxygen desaturation evidence from SO2 records ready for spot checking: slp60, slp67x.
- Channel-quality and event-window review for connecting annotations to waveforms.
- Clinical reasoning boundaries: evidence can support questions and hypotheses, not diagnosis or treatment selection.

## What Still Blocks Stronger Clinical Claims

- High/medium-priority source-AHI review is still needed for: slp01b, slp03, slp04, slp14, slp16, slp32, slp37, slp48, slp59, slp60, slp61, slp66, slp67x.
- SO2 artifact review is still needed for: slp59, slp61, slp66.
- Full hypopnea scoring is not implemented because airflow-reduction and arousal adjudication are not available in this pipeline.
- Treatment reasoning remains conditional because symptoms, exam, comorbidities, contraindications, and clinician interpretation are outside the dataset.

## Richer PSG Dataset Gate

Add UCDDB, SHHS, or another richer PSG dataset only if the next research question requires one of these:

- arousal-linked respiratory scoring rather than annotation-token burden;
- richer airflow/effort/oximetry cross-checks after MIT-BIH artifact review;
- population-scale severity, comorbidity, or treatment-risk examples;
- source-provided scored respiratory indices that can be audited against this pipeline.

## Next Manual Work

1. Review the high/medium-priority source-AHI rows in the relevant `*_source_ahi_alignment.csv`; for the full run, use `results/mit_bih_psg/complete_record_source_ahi_alignment.csv`.
2. Inspect SO2 waveform/raw-channel evidence from the relevant `*_oxygen_artifact_review.csv`; for the full run, use `results/mit_bih_psg/complete_record_oxygen_artifact_review.csv`.
3. Re-run the richer PSG gate after those two reviews; only then download a heavier dataset if MIT-BIH cannot support the desired examples.
