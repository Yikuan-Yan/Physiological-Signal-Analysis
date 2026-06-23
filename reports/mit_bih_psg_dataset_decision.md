# MIT-BIH PSG Dataset Readiness And Richer PSG Decision

## Decision

Keep MIT-BIH PSG as the current respiratory clinical-learning dataset. Do not automatically add a richer PSG dataset until manual source-AHI alignment and SO2 artifact review are completed.

## Why

- Records analyzed: 3.
- Source alignment statuses: roughly_aligned=3
- Source alignment priorities: low=2, manual_review_medium=1
- Oxygen review statuses: not_available=3
- Clinical-style example tiers: respiratory_annotation_learning_ready=3

## What The Current Data Can Teach

- Respiratory event burden from sleep/apnea annotations, especially records with roughly aligned source AHI: slp01a, slp02a, slp03.
- Sleep-aligned oxygen desaturation evidence from SO2 records ready for spot checking: none.
- Channel-quality and event-window review for connecting annotations to waveforms.
- Clinical reasoning boundaries: evidence can support questions and hypotheses, not diagnosis or treatment selection.

## What Still Blocks Stronger Clinical Claims

- High/medium-priority source-AHI review is still needed for: slp03.
- SO2 artifact review is still needed for: none.
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
