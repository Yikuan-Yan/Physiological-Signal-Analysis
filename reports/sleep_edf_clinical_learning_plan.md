# Sleep-EDF Clinical Learning Implementation Plan

## Goal

Turn real Sleep-EDF hypnogram data into an educational bridge from raw physiological recording to sleep quality metrics, disease hypotheses, diagnostic evidence requirements, and treatment questions.

This is not a publication claim-review plan. The goal is to understand what the data can teach and where clinical evidence is still missing.

## Implementation Tasks

1. Compute sleep quality metrics from 30 s stage epochs.
2. Separate full recording metrics from inferred main sleep-period metrics.
3. Generate clinical learning indicators for sleep duration, continuity, latency, REM timing, and fragmentation.
4. Mark disorder areas that cannot be diagnosed from stage metrics alone.
5. Add a treatment learning map that shows how confirmed evidence would guide clinical questions.
6. Write an educational report that maps data patterns to next clinical questions and missing data.
7. Keep raw EDF files out of git while committing compact metrics and reports.

## Diagnostic Reasoning Boundaries

- Sleep quality can be estimated from stages and continuity metrics.
- Insomnia requires subjective complaint, sleep opportunity, duration, and daytime impairment.
- OSA requires respiratory event evidence such as airflow, effort, SpO2, arousals, and AHI.
- Narcolepsy requires symptoms and usually MSLT; overnight REM latency alone is not enough.
- Treatment decisions require clinician review and disorder-specific evidence, but the report should show the reasoning path.

## Immediate Command

```bash
uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf.yaml --records SC4001,SC4011 --output-prefix pilot --include-yasa
```
