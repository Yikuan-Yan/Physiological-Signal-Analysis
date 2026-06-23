# Physiological Signal Analysis Technical Review

Review date: 2026-06-23

Review target: `Physiological Signal Analysis`

Conclusion label: mature research prototype / educational method-development workbench

This English document replaces the original Chinese technical review in the public-facing report path. The Chinese source version is preserved in `zh/physiological_signal_analysis_technical_review.zh.md`.

## 0. Executive Summary

The repository implements three public-data physiological signal analysis pipelines:

1. **Fantasia ECG/HRV method validation**: data inventory, R-peak detection, peak matching, RR/NN interval construction, time-domain and frequency-domain HRV, artifact injection, correction-strategy comparison, and record-level bootstrap uncertainty.
2. **Sleep-EDF sleep staging and sleep-quality educational analysis**: manual stage-label expansion, stage mapping, baseline evaluation, optional YASA staging, performance metrics, sleep architecture metrics, and clinical-education style interpretation.
3. **MIT-BIH PSG respiratory/oxygen evidence analysis**: stage/event token parsing, respiratory-event burden, source-AHI alignment, channel quality, SpO2/ODI proxy metrics, event-window review, and dataset-readiness gates.

The repository is not a shallow demo. It includes configuration files, a CLI, manifests/checksums, a lockfile, tests, machine-readable outputs, figures, reports, and a historical release bundle. It is a fairly mature research prototype.

It is not production-ready clinical software. The important risks are not cosmetic documentation issues; they are correctness and provenance issues that can change result semantics:

- downloader provenance can accidentally trust local corrupted files if expected and observed hashes are conflated;
- sleep-quality metrics can be distorted if excluded/gap epochs are compressed out of the timeline;
- HRV artifact correction must preserve recording span when the artifact model claims to preserve it;
- report gates must be based on real validation evidence, not hard-coded pass statements;
- target-derived majority baselines must be explicitly named as oracle baselines;
- orchestration paths need more branch and integration coverage.

## 1. Overall Rating

| Dimension | Rating | Judgment |
| --- | ---: | --- |
| Functional completeness | 7/10 | Three real pipelines exist, with meaningful tracked outputs. Some planned features remain incomplete. |
| Architecture | 6/10 | Layering intent is clear, but `mit_bih_psg.py` and `sleep_quality.py` remain procedural hotspots. |
| Code quality | 6/10 | Type hints, dataclasses, and configuration are useful. Long functions and implicit assumptions remain. |
| Correctness and robustness | 6/10 after closure | Major P0/P1 issues were addressed, but full release-level reproducibility is not complete. |
| Testing and validation | 6/10 | Regression coverage improved to 70 tests, but CLI/integration/CI coverage is still limited. |
| Performance and resources | 5/10 | Workflows run, but repeated reads, large CSVs, and limited caching remain. |
| Reproducibility | 6/10 | Lockfile, configs, manifests, seeds, and tracked outputs exist. Run manifests and atomic outputs remain missing. |
| Documentation and usability | 7/10 | Public-facing English README/guide and detailed reports exist. CLI help still needs polish. |
| Security and privacy | 6/10 | No obvious secrets or raw data are committed. Data integrity and supply-chain provenance remain main risks. |
| Research/engineering value | 8/10 | Provenance, annotation uncertainty, readiness gates, and machine-readable audit outputs are strong. |

## 2. Review Scope

The review covered:

- project configuration and environment: `pyproject.toml`, `uv.lock`, `configs/`;
- orchestration entrypoint: `src/physio_signal_lab/cli.py`;
- data download and access: `src/physio_signal_lab/io/`;
- feature and evaluation modules: `src/physio_signal_lab/features/`, `src/physio_signal_lab/evaluation/`;
- domain pipelines: `sleep_edf_benchmark.py`, `sleep_quality.py`, `mit_bih_psg.py`;
- tests;
- `docs/`, `reports/`, `results/`, `figures/`;
- release bundle and manifests;
- tracked CSV row counts, timing semantics, and repeated artifacts.

Evidence classes:

- **Fact:** directly confirmed by files, implementation, configuration, or local execution.
- **Inference:** high-confidence conclusion based on structure, outputs, and engineering judgment.
- **Needs confirmation:** requires raw data, upstream metadata, author intent, or external review.

## 3. Project Understanding

The project goal is to build a traceable public-data physiological signal analysis workflow. It uses public datasets and explicitly avoids personal data collection, diagnosis, treatment prescription, or treating model predictions as clinical truth.

The current implementation is best summarized as:

> A configuration-driven research workbench that starts from public WFDB/EDF files and annotations, runs ECG peak detection, RR/NN and HRV computation, sleep-stage benchmarking, sleep-architecture summaries, and respiratory/oxygen proxy analysis, then records provenance, tests, tables, figures, and reports as auditable outputs.

The appropriate maturity label is:

> Mature research prototype with educational analysis and method-development value; not production deployment, clinical validation, or stable public API.

## 4. Implemented Pipelines

### 4.1 HRV

Typical flow:

```text
configs/hrv/core.yaml
  -> validate Fantasia manifest
  -> inventory records
  -> NeuroKit R-peak detection
  -> match detected peaks to reference annotations
  -> construct RR/NN intervals
  -> compute time-domain and frequency-domain HRV
  -> run artifact injection and correction comparisons
  -> record-level bootstrap
  -> write CSV, figures, and Markdown report
```

Tracked capabilities:

- Fantasia 40-record inventory;
- R-peak benchmark against public annotations;
- RR/NN interval construction with exclusion reasons;
- MeanNN, SDNN, RMSSD, pNN50;
- Welch and Lomb-Scargle frequency-domain sensitivity;
- controlled artifact sensitivity;
- record-level bootstrap uncertainty;
- gated HRV report.

### 4.2 Sleep-EDF

Typical flow:

```text
configs/sleep_edf/default.yaml
  -> validate manifest and record selection
  -> read PSG EDF and Hypnogram EDF
  -> expand 30-second stage labels using real onset
  -> map R&K labels to W/N1/N2/N3/REM
  -> global-majority baseline
  -> optional YASA staging
  -> metrics, confusion summaries, probabilities
  -> sleep-quality metrics and educational indicators
  -> write CSV, figures, and Markdown reports
```

Tracked capabilities:

- 20 selected Sleep Cassette first-night records;
- onset-based annotation expansion;
- global majority baseline and explicit per-record oracle baseline;
- optional YASA profiling and prediction;
- sleep-quality metrics using elapsed-time semantics and observed-valid-time semantics;
- clinical-learning reports with explicit limitations.

### 4.3 MIT-BIH PSG

Typical flow:

```text
configs/mit_bih_psg/default.yaml
  -> validate WFDB manifest
  -> read .st annotations
  -> parse stage and event tokens
  -> compute respiratory annotation burden
  -> source-AHI alignment audit
  -> channel quality and SpO2/ODI proxy
  -> event-window summaries
  -> dataset-readiness gate
  -> write CSV, figures, and Markdown reports
```

Tracked capabilities:

- all 18 MIT-BIH PSG records;
- sleep/apnea annotation parsing;
- sleep-hour-normalized AHI-style respiratory burden;
- source-AHI alignment audit;
- SO2 availability and sleep-only ODI proxy;
- oxygen artifact review flags;
- dataset-readiness tiers.

## 5. Confirmed Issues And Current Response

### P0-1: Downloader Could Certify A Corrupted Existing File

Original risk:

- Existing local files could be skipped and their observed local hash could be written back as the expected manifest checksum.
- That would convert a corrupted file into a trusted input.

Current response:

- Sleep-EDF and MIT-BIH downloaders now separate observed local hash from expected upstream checksum.
- `skipped_existing` records local observation metadata but does not rewrite expected checksums.
- Validation fails when local hashes do not match expected hashes.

Status: fixed for the current downloader model. Full upstream checksum cross-verification remains future work.

### P0-2: Sleep-Quality Metrics Compressed Excluded/Gapped Epochs

Original risk:

- Dropping excluded rows before computing sleep period, WASO, transitions, and REM latency compresses real elapsed time.
- Gap/exclusion periods can disappear from the timeline.

Current response:

- Sleep metrics retain elapsed timeline semantics.
- Missing/excluded epochs are counted explicitly.
- Outputs include `missing_epoch_count`, `missing_minutes`, `missing_epochs_within_sleep_period`, and `continuity_break_count`.
- Observed-valid-time metrics are reported separately from elapsed-time metrics.

Status: fixed.

### P0-3: Sleep Annotation `epoch_index` Did Not Come From True Onset

Original risk:

- Sequential indices ignore non-zero starts, gaps, overlaps, and non-grid annotations.
- Reference labels and model predictions can become misaligned.

Current response:

- `expand_stage_annotations()` derives epoch index from `onset_seconds / epoch_duration_seconds`.
- Non-grid onset, overlap, and gap conditions are validated.
- Missing annotation gaps are preserved rather than silently compressed.

Status: fixed.

### P0-4: HRV Artifact Correction Did Not Preserve Total Duration

Original risk:

- Missed/spurious beat correction could change the total recording span, distorting duration-dependent HRV metrics.

Current response:

- Artifact injection/correction uses `beat_times_ms` as canonical representation.
- Missed/spurious/jitter/ectopic perturbations operate on boundaries/timestamps.
- Duration-preserving correction strategies maintain first/last recording span.

Status: fixed for duration-preserving strategies. Deliberately span-changing comparison strategies must remain clearly labeled.

### P0-5: HRV Report Gate Could Hard-Code Pass

Original risk:

- A report could show a passing decision even if input validation or required outputs failed.

Current response:

- `RunGateResult(name, status, evidence)` was introduced.
- Gate statuses are `pass`, `fail`, `warning`, or `not_run`.
- Required gate failures force the report decision to fail.
- Manifest validation and output/schema evidence are included in the report.

Status: fixed for the HRV report path.

### P1-1: `flagged_interpolate()` NaN Shape Mismatch

Original risk:

- Non-finite values could cause mask shape mismatch.

Current response:

- The function validates the original shape first.
- It merges the explicit invalid mask with non-finite values in original index space.

Status: fixed.

### P1-2: Majority Baseline Used Same-Record Truth

Original risk:

- A same-record majority baseline is a target-derived oracle, not a deployable baseline.

Current response:

- The old behavior is explicitly named `per_record_majority_oracle`.
- A true `global_majority_stage_baseline` was added and used in benchmark outputs.

Status: fixed.

### P1-3: Peak Matcher Did Not Minimize Timing Error After Maximizing Matches

Original risk:

- A valid match assignment could maximize matches but not minimize timing error.

Current response:

- Matching now maximizes match count first and minimizes total absolute timing error second.
- Regression coverage includes the synthetic case `reference=[0,8]`, `detected=[5]`, `tolerance=5`.

Status: fixed.

### P1-4: Selection And Manifest Contracts Were Loose

Original risk:

- Missing or excluded requested records could be silently mishandled.
- Invalid config ranges or output path collisions could pass preflight.

Current response:

- Requested IDs must exactly match included manifest records.
- Empty record lists fail explicitly.
- Key config ranges and output path collisions are checked.

Status: mostly fixed. Full typed schema validation remains future work.

### P1-5: Release Bundle Was Not A Complete Executable Snapshot

Original risk:

- Same-name release directories could mix old and new artifacts.
- The bundle did not contain a full offline rebuild contract.

Current response:

- Same-name release directories now fail instead of mixing files.

Status: partially fixed. A full v0.2 reproducibility snapshot remains future work.

### P1-6: MIT-BIH Annotation/ODI Assumptions Were Under-Encoded

Original risk:

- Annotation token counting and ODI proxy assumptions could be mistaken for clinical scoring.

Current response:

- Source-AHI alignment audit tables exist.
- SO2 availability and artifact-review statuses exist.
- Dataset-readiness tiers separate ready, manual-review, and source-context-only records.
- Reports describe AHI/ODI outputs as educational proxies.

Status: partially fixed. Formal AASM/CMS hypopnea scoring and manual adjudication remain outside the current implementation.

## 6. Architecture And Maintainability

Strengths:

- clear dataset-specific workflows;
- YAML-driven configuration;
- tracked machine-readable outputs;
- meaningful regression tests for several numerical contracts;
- explicit evidence boundaries in reports.

Weaknesses:

- `mit_bih_psg.py` remains too large and mixes parsing, metric computation, plotting, and reporting.
- `sleep_quality.py` mixes metrics, clinical heuristics, figures, and reporting.
- CLI imports remain relatively eager.
- Output generation is not yet run-ID or schema-version based.

Recommended future split:

```text
mit_bih_psg/
  annotations.py
  respiratory_metrics.py
  oximetry.py
  readiness.py
  reports.py

sleep/
  quality_metrics.py
  clinical_learning_policy.py
  figures.py
  reports.py
```

## 7. Testing And Validation

Current strengths:

- regression tests cover artifact duration invariants;
- NaN interpolation regression is covered;
- sleep gap/overlap/non-grid annotation behavior is covered;
- peak matching tie behavior is covered;
- report gate behavior is covered;
- release-directory collision is covered.

Remaining gaps:

- no GitHub Actions workflow;
- no coverage report;
- limited CLI branch coverage;
- limited end-to-end synthetic fixtures;
- no hermetic full pipeline smoke test independent of public raw data.

Recommended CI shape:

```text
python -m compileall -q src tests
uv run pytest -q
git diff --check
secret scan
tiny synthetic integration smoke
```

## 8. Reproducibility

What exists:

- `uv.lock`;
- YAML configs;
- dataset manifests;
- tracked CSV outputs;
- Markdown reports;
- figures;
- HRV release metadata bundle;
- validation commands.

What remains missing:

- complete run manifest;
- output hashes;
- config hash in outputs;
- atomic output directories;
- schema versioning;
- signed release checksums;
- SBOM or dependency audit;
- complete offline reproducibility snapshot.

## 9. Security, Privacy, And Supply Chain

Public repository checks found:

- no raw waveform data tracked under `data/raw/`;
- no typical API keys, GitHub tokens, AWS keys, or private keys;
- no tracked file above GitHub's hard file-size limit;
- raw waveform file extensions are not tracked.

Remaining recommendations:

- add CI secret scanning;
- add dependency audit;
- add signed release checksums for future releases;
- document raw-data acquisition and citation responsibilities clearly.

## 10. Clinical Boundary

This repository can teach how real data support clinical reasoning questions:

- sleep architecture and continuity;
- respiratory annotation burden;
- oxygen desaturation-style proxies;
- evidence gaps between data and diagnosis.

It must not be presented as:

- a diagnostic system;
- a treatment selector;
- a triage tool;
- a medical device;
- a personal health baseline system;
- a validated clinical scoring engine.

Any future clinical claim would require:

- expert scoring protocol;
- clinical symptoms and history;
- waveform review;
- arousal and airflow adjudication;
- comorbidity context;
- external validation;
- governance and regulatory review where applicable.

## 11. Roadmap If Reopened

The current project is closed for implementation. If reopened, the defensible sequence is:

1. Build a tiny hermetic integration fixture set.
2. Add CI and coverage.
3. Add full typed config and output schema validation.
4. Split large domain modules.
5. Add run manifests, output hashes, and atomic output directories.
6. Manually adjudicate MIT-BIH source-AHI alignment rows.
7. Manually review SO2 artifact-review records.
8. Build a v0.2 frozen reproducibility snapshot.
9. Decide whether a richer PSG dataset is justified.

## 12. Final Technical Judgment

The repository's strongest contribution is not a new detector or clinical model. Its value is the disciplined organization of public physiological data analysis into auditable workflows with provenance, annotation uncertainty, method sensitivity, readiness gates, and machine-readable artifacts.

After the correctness-closure work, the project is suitable for public release as a research and education prototype. It should not be described as production-ready, clinically validated, or a medical decision-support system.
