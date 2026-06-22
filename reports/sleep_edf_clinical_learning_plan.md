# Sleep-EDF Clinical Learning Implementation Plan

## Goal

Turn real Sleep-EDF hypnogram data into an educational bridge from raw physiological recording to sleep quality metrics, disease hypotheses, diagnostic evidence requirements, and treatment questions.

This is not a publication claim-review plan. The goal is to understand what the data can teach and where clinical evidence is still missing.

## Implementation Tasks

1. Done: compute sleep quality metrics from 30 s stage epochs.
2. Done: separate full recording metrics from inferred main sleep-period metrics.
3. Done: generate clinical learning indicators for sleep duration, continuity, latency, REM timing, and fragmentation.
4. Done: mark disorder areas that cannot be diagnosed from stage metrics alone.
5. Done: add a treatment learning map that shows how confirmed evidence would guide clinical questions.
6. Done: add hypnogram timelines, sleep architecture plots, model discrepancy tables, and clinical question rankings.
7. Done: write pilot and five-record educational reports that map data patterns to next clinical questions and missing data.
8. Done: keep raw EDF files out of git while committing compact metrics, reports, and figures.
9. Next: add a respiratory PSG dataset so OSA-style reasoning can use airflow, effort, SpO2, and apnea/hypopnea annotations.

## Diagnostic Reasoning Boundaries

- Sleep quality can be estimated from stages and continuity metrics.
- Insomnia requires subjective complaint, sleep opportunity, duration, and daytime impairment.
- OSA requires respiratory event evidence such as airflow, effort, SpO2, arousals, and AHI.
- Narcolepsy requires symptoms and usually MSLT; overnight REM latency alone is not enough.
- Treatment decisions require clinician review and disorder-specific evidence, but the report should show the reasoning path.

## Current Commands

```bash
uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf.yaml --records SC4001,SC4011 --output-prefix pilot --include-yasa
uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041 --output-prefix five_record --include-yasa
```

## Next Dataset Direction

Use `reports/respiratory_dataset_candidates.md` to start the respiratory-event phase. The recommended first integration target is the MIT-BIH Polysomnographic Database because it is small, open, and includes sleep/apnea annotations plus respiration signals.
