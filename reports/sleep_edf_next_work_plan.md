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
- Download and checksum validation through `SC4071`.

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

Current validation summary:

- EDF files validated: 16
- bytes: 400,379,978
- missing files: 0
- checksum mismatches: 0

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

### Track A: Finish Sleep-EDF Downloads

Continue small batches:

```bash
uv run python -m physio_signal_lab.cli download-sleep-edf --config configs/sleep_edf.yaml --records SC4081,SC4091,SC4101
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4081,SC4091,SC4101

uv run python -m physio_signal_lab.cli download-sleep-edf --config configs/sleep_edf.yaml --records SC4111,SC4121,SC4131
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4111,SC4121,SC4131
```

### Track B: Eight-Record Clinical Report

The next expanded report should use the already validated `SC4001` through `SC4071`.

```bash
uv run python -m physio_signal_lab.cli profile-yasa-runtime --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041,SC4051,SC4061,SC4071 --full-night --timeout-seconds 180 --output-prefix eight_record
uv run python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041,SC4051,SC4061,SC4071 --output-prefix eight_record --include-yasa
uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041,SC4051,SC4061,SC4071 --output-prefix eight_record --include-yasa
```

### Track C: Respiratory PSG Dataset

Use `reports/respiratory_dataset_candidates.md` to start disease-specific respiratory reasoning. Recommended first target: MIT-BIH Polysomnographic Database.

Implementation outline:

1. Add `configs/mit_bih_psg.yaml`.
2. Download a small MIT-BIH PSG pilot subset.
3. Parse sleep/apnea annotations.
4. Compute apnea annotation burden per sleep hour.
5. Add respiration/SpO2 quality checks when channels are available.
6. Extend the clinical-learning report with respiratory-event evidence.

## Evidence Boundary

The goal is to learn how data supports clinical reasoning. The reports should show sleep-quality signals, disease hypotheses, and missing diagnostic evidence. They should not claim a final diagnosis or treatment decision without the signals required for that disorder.
