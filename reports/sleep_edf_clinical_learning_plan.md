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
7. Done: write pilot, five-record, eight-record, eleven-record, and twenty-record educational reports that map data patterns to next clinical questions and missing data.
8. Done: keep raw EDF files out of git while committing compact metrics, reports, and figures.
9. Done: add MIT-BIH PSG respiratory pilot so OSA-style reasoning can use respiration signals and apnea/hypopnea annotations.
10. Done: add SO2-channel MIT-BIH records so oxygen desaturation burden can be learned from real data.
11. Done: add event-level waveform windows and plots around scored respiratory-event epochs.
12. Done: run the complete 18-record MIT-BIH PSG report.
13. Done: align SO2 oxygen proxy metrics to sleep epochs while retaining recording-wide audit columns.
14. Next: manually reconcile simple annotation-token burden against source AHI and clinical scoring rules.
15. Next: formalize oxygen desaturation scoring and decide whether to add a richer PSG dataset.

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
uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041,SC4051,SC4061,SC4071 --output-prefix eight_record --include-yasa
uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041,SC4051,SC4061,SC4071,SC4081,SC4091,SC4101 --output-prefix eleven_record --include-yasa
uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041,SC4051,SC4061,SC4071,SC4081,SC4091,SC4101,SC4111,SC4121,SC4131,SC4141,SC4151,SC4161,SC4171,SC4181,SC4191 --output-prefix twenty_record --include-yasa
uv run python -m physio_signal_lab.cli run-mit-bih-psg-respiratory-pilot --config configs/mit_bih_psg.yaml --records slp01a,slp02a,slp03
uv run python -m physio_signal_lab.cli run-mit-bih-psg-respiratory-pilot --config configs/mit_bih_psg.yaml --records slp59,slp60,slp61,slp66,slp67x --output-prefix oxygen_record
uv run python -m physio_signal_lab.cli run-mit-bih-psg-respiratory-pilot --config configs/mit_bih_psg.yaml --output-prefix all_record
uv run python -m physio_signal_lab.cli run-mit-bih-psg-respiratory-pilot --config configs/mit_bih_psg.yaml --output-prefix complete_record
```

## Next Dataset Direction

MIT-BIH PSG is now integrated for respiratory-event and sleep-aligned SO2 oxygenation learning across all 18 records. Use `reports/respiratory_dataset_candidates.md` to drive source AHI alignment, formal desaturation scoring, and the richer-PSG dataset decision.
