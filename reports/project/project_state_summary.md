# Project State Summary

Updated: 2026-06-24

This short summary preserves the executive-summary value of the previous Chinese `repo_work_summary.md`. The full Chinese source is archived at `zh/repo_work_summary.zh.md`.

## One-Paragraph Status

Physio Signal Lab has grown from a public-data physiological signal analysis plan into a runnable research and education prototype. It contains three implemented workflows: ECG/HRV method validation on Fantasia, Sleep-EDF sleep architecture and sleep-quality learning, and MIT-BIH PSG respiratory/oxygen educational analysis. The repository is suitable for method-development and teaching how evidence is derived from real data. It is not a diagnostic system, treatment recommender, or validated clinical decision-support tool.

## Data Coverage

| Dataset | Current scope | Validation state recorded in project reports | Tracked outputs |
| --- | ---: | --- | --- |
| Fantasia Database v1.0.0 | 40 records | HRV report records 0 missing files and 0 checksum mismatches | HRV benchmark, RR/NN, artifact, frequency, uncertainty CSVs; report; release bundle |
| Sleep-EDF Expanded Sleep Cassette | 20 first-night records, 40 EDF files | 998,070,310 bytes validated; 0 missing files; 0 checksum mismatches | benchmark CSVs, sleep-quality CSVs, clinical-learning reports, figures |
| MIT-BIH Polysomnographic Database | 18 records, 72 WFDB files | 662,914,296 bytes validated; 0 missing files; 0 checksum mismatches; 0 incomplete required rows | respiratory metrics, oxygen metrics, source-AHI alignment, readiness gates, reports, figures |

Raw waveform files remain outside Git under `data/raw/`. The repository commits compact metrics, reports, figures, manifests, configs, release metadata, and tests.

## Engineering Foundation

- Main package: `src/physio_signal_lab/`.
- CLI entrypoint: `src/physio_signal_lab/cli.py`.
- Configs: `configs/hrv/core.yaml`, `configs/sleep_edf/default.yaml`, `configs/mit_bih_psg/default.yaml`.
- Manifests: `data/manifests/*.csv`.
- Outputs: `results/`, `reports/`, `figures/`.
- HRV release bundle: `releases/hrv-core-v0.1.0/`.
- Chinese source documents: `zh/`.

The codebase already has a reusable package structure, CLI workflows, scoped output prefixes, validation commands, and regression tests. It is still not a fully hermetic clean-checkout release because full reruns require restored public raw data.

## ECG/HRV Track

The ECG/HRV track validates the basic path from public ECG data to HRV method outputs.

Implemented:

- inventory for 40 Fantasia records;
- manifest-based local file validation;
- R-peak benchmarking against reference `.ecg` annotations;
- RR and NN interval construction with exclusion reasons;
- time-domain HRV: MeanNN, SDNN, RMSSD, pNN50;
- frequency-domain HRV: Welch and Lomb-Scargle sensitivity;
- artifact injection and correction comparison;
- record-level bootstrap uncertainty;
- gated HRV core report.

Key tracked results:

- 50 ms R-peak benchmark: 285,032 TP, 1,280 FP, 502 FN;
- 50 ms median sensitivity: 0.99969;
- 50 ms median F1: 0.99936;
- median absolute timing error: 8.0 ms;
- RR intervals: 285,494;
- NN intervals: 280,748;
- excluded intervals: 4,746;
- artifact sensitivity scenarios: 38,400 rows;
- frequency-domain windows: 977, with 969 valid Welch windows.

The HRV track supports method-development discussion about detector behavior, interval construction, artifact sensitivity, frequency-method sensitivity, and uncertainty. It does not support personal baseline, disease diagnosis, stress inference, or treatment decisions.

## Sleep-EDF Track

The Sleep-EDF track expands the project into PSG-style sleep staging and sleep-quality learning.

Implemented:

- Sleep-EDF download, manifest, validation, and preflight workflow;
- selected first-night Sleep Cassette records from `SC4001` through `SC4191`;
- onset-based 30-second stage-label expansion;
- R&K to five-class sleep stage mapping;
- global majority-stage baseline;
- optional YASA sleep staging and runtime profiling;
- pilot, five-record, eight-record, eleven-record, and twenty-record reports;
- hypnogram timeline and sleep architecture figures;
- reference-vs-YASA discrepancy tables;
- sleep-quality metrics: total sleep time, sleep efficiency, WASO, REM latency, stage balance, awakening count, fragmentation proxies;
- clinical-learning indicators and clinical-question ranking.

Current twenty-record YASA snapshot:

- included epochs: 54,587;
- overall YASA accuracy: 0.823;
- balanced accuracy: 0.722;
- macro-F1: 0.658;
- Cohen's kappa: 0.676.

Sleep-EDF supports learning about sleep architecture, total sleep time, sleep-period efficiency, WASO, REM latency, stage balance, fragmentation, and model/reference staging discrepancies. It does not directly support AHI/RDI, oxygen desaturation burden, apnea/hypopnea diagnosis, PAP/oral-appliance treatment reasoning, hypoventilation reasoning, or respiratory-event severity.

## MIT-BIH PSG Track

The MIT-BIH PSG track was added because stage-only Sleep-EDF data cannot answer respiratory disease questions.

Implemented:

- MIT-BIH PSG config, manifest generation, download, checksum update, and validation;
- all 18 MIT-BIH PSG WFDB records;
- `.st` sleep/apnea annotation parsing;
- epoch-level tables;
- sleep-hour-normalized AHI-style respiratory annotation burden;
- event-type rates for hypopnea, obstructive apnea, central apnea, and arousal-associated respiratory tokens;
- source-reported AHI alignment audit;
- special handling for `slp41` and `slp45`, where source AHI is estimated and apnea annotations are unavailable;
- respiration and SO2 channel quality checks;
- event windows and plots around respiratory-event epochs;
- sleep-aligned SO2 oxygen metrics;
- documented pre-event rolling-baseline ODI proxy;
- ODI 3% and ODI 4% sleep-only metrics;
- oxygen artifact-review gates;
- dataset-readiness CSVs and richer-PSG decision reports.

Current complete-record respiratory snapshot:

- AHI-style learning severity: 14 severe-range, 2 moderate-range, 2 minimal-range;
- median AHI-style annotation burden: 53.19 events/h;
- highest AHI-style burden: `slp37`, 109.21 events/h;
- source-AHI alignment statuses: 10 `needs_manual_review`, 6 `roughly_aligned`, 2 `source_ahi_estimated_annotation_unavailable`;
- source-AHI review priorities: 10 `manual_review_high`, 3 `manual_review_medium`, 3 `low`, 2 `separate_source_review`.

Current oxygen snapshot:

- SO2 status: 5 records available, 13 records without SO2 channel;
- oxygen review statuses: 2 `oxygen_review_ready`, 3 `artifact_review_recommended`, 13 `not_available`;
- oxygen-ready records: `slp60`, `slp67x`;
- SO2 artifact-review records: `slp59`, `slp61`, `slp66`.

Dataset-readiness tiers:

- respiratory annotation-burden learning records: `slp01a`, `slp02a`, `slp02b`, `slp03`, `slp37`, `slp61`;
- records needing manual source-AHI alignment before source-alignment claims: 10;
- source-context-only examples: `slp41`, `slp45`;
- richer PSG dataset decision: keep MIT-BIH PSG for now and do not add UCDDB, SHHS, or heavier PSG datasets until source-AHI and SO2 artifact review are complete.

## Clinical Learning Boundary

The repository can help answer:

- what ECG, sleep-stage, respiratory-event, and SO2 data contain;
- which metrics can be reproducibly computed from public data;
- which records show strong sleep-disordered-breathing-style signals;
- which records are suitable for sleep architecture, respiratory burden, or oxygen burden teaching examples;
- what evidence is missing between a data pattern and a clinical conclusion.

The repository does not claim:

- medical diagnosis;
- treatment prescription;
- personal health baseline;
- clinical risk score;
- device purchase advice;
- that public annotations are error-free truth.

## Main Entry Points

| Purpose | File |
| --- | --- |
| Public README | `README.md` |
| Detailed work guide | `WORK_GUIDE.md` |
| Final state and review response | `reports/project/final_state_and_technical_review_response.md` |
| Technical review | `reports/project/physiological_signal_analysis_technical_review.md` |
| HRV core report | `reports/hrv/core_report.md` |
| Frozen HRV release bundle | `releases/hrv-core-v0.1.0/` |
| Sleep-EDF twenty-record benchmark | `reports/sleep_edf/twenty_record_benchmark.md` |
| Sleep-EDF twenty-record clinical education | `reports/sleep_edf/twenty_record_clinical_education.md` |
| MIT-BIH complete respiratory report | `reports/mit_bih_psg/complete_record_respiratory_pilot.md` |
| MIT-BIH dataset decision | `reports/mit_bih_psg/complete_record_dataset_decision.md` |
| MIT-BIH readiness table | `results/mit_bih_psg/complete_record_dataset_readiness.csv` |

## Closed-For-Now Limitations

The remaining work is primarily evidence adjudication rather than simple code completion:

1. Manually review high/medium-priority source-AHI alignment rows in `results/mit_bih_psg/complete_record_source_ahi_alignment.csv`.
2. Manually inspect SO2 waveform/raw-channel evidence for `slp59`, `slp61`, and `slp66`.
3. Re-run richer-PSG readiness gates after manual review.
4. Add a richer PSG dataset only if the next research question requires arousal-linked respiratory scoring, richer airflow/effort/oximetry cross-checks, population-scale clinical context, or source-provided respiratory indices.

This project is currently best positioned as an educational and method-development repository, not a diagnostic system.
