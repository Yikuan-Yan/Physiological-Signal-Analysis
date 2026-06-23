# Final State And Technical Review Response

Updated: 2026-06-23

This document records the latest project state after the correctness-closure work and responds directly to the issues raised in `reports/project/physiological_signal_analysis_technical_review.md`.

The project is being closed as a research/education repository for now. Items listed as limitations or future directions are preserved for traceability, not scheduled for immediate implementation.

## Final Position

The repository now supports three public-data analysis tracks:

1. Fantasia ECG/HRV method development: R-peak detection, peak matching, RR/NN construction, HRV features, artifact sensitivity, frequency-domain comparison, uncertainty, and a gated report.
2. Sleep-EDF sleep architecture and sleep-quality learning: stage-label expansion, baseline/YASA comparison, elapsed-timeline sleep-quality metrics, clinical-learning indicators, and reports up to the 20-record run.
3. MIT-BIH PSG respiratory learning: sleep/apnea annotation parsing, AHI-style event burden, source-AHI alignment audit, respiration/SO2 channel review, sleep-only ODI proxy, event windows, and dataset-readiness gates across 18 records.

The correct interpretation is:

- It is a mature research prototype and educational method-development workbench.
- It is not a production clinical system.
- It does not make diagnoses, prescriptions, triage decisions, treatment selections, or personal baseline claims.
- It shows how real physiological data can support clinical reasoning questions, and where the evidence stops.

## Latest Correctness Closure

The latest implementation closed the main technical-review correctness blockers before any further dataset expansion.

Commit recorded locally:

```text
f971715 Close correctness gaps in physiological pipelines
```

Validation after the closure:

```text
python -m compileall -q src\physio_signal_lab
uv run pytest -q
git diff --check
uv run python -m physio_signal_lab.cli validate-data --manifest data/manifests/fantasia.csv
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf/default.yaml
uv run python -m physio_signal_lab.cli validate-mit-bih-psg --config configs/mit_bih_psg/default.yaml
```

Observed results:

| Check | Result |
| --- | --- |
| compileall | passed |
| pytest | 70 passed |
| git diff --check | passed; only Git CRLF normalization warnings were printed |
| Fantasia validation | 123 rows, 40 records, 0 missing files, 0 checksum mismatches, 0 missing record files |
| Sleep-EDF validation | 40 EDF files, 998,070,310 bytes, 0 missing files, 0 checksum mismatches |
| MIT-BIH PSG validation | 72 WFDB files, 662,914,296 bytes, 0 missing files, 0 checksum mismatches, 0 incomplete required rows |

Affected HRV and Sleep-EDF reports/results were regenerated after semantic changes.

## Response To Technical Review Blockers

| Review issue | Current response | Status |
| --- | --- | --- |
| P0-1 downloader could bless corrupted existing files by writing local hash back as expected checksum | Sleep-EDF and MIT-BIH downloaders now separate observed local hash from expected upstream checksum. `skipped_existing` records only `local_observed_sha256`; skipped files do not update expected checksums. Validation fails on local/upstream mismatch. | Fixed |
| P0-2 sleep-quality metrics compressed excluded/gap epochs | Sleep metrics now retain elapsed timeline semantics and also expose observed-valid-time metrics. Missing/gap epochs are counted instead of silently compressed. | Fixed |
| P0-3 Sleep annotation `epoch_index` was not derived from true onset | `expand_stage_annotations()` derives epoch index from `onset_seconds / epoch_duration_seconds` and validates non-grid onset, overlap, and gaps. | Fixed |
| P0-4 HRV artifact correction did not preserve total recording duration | Artifact injection/correction now uses `beat_times_ms` as the canonical representation. Missed/spurious/jitter/ectopic perturbations preserve first/last recording span where the correction strategy is intended to preserve duration. | Fixed for duration-preserving strategies |
| P0-5 HRV report gate could hard-code pass | Report generation now uses `RunGateResult(name, status, evidence)` and aggregates manifest validation, output completeness, schema checks, and method gates. Required failures force a fail decision. | Fixed |
| P1-1 `flagged_interpolate()` NaN shape mismatch | The function now validates original shape first, merges invalid mask with non-finite values, and interpolates in original index space. | Fixed |
| P1-2 same-record majority baseline was a target-derived oracle | The old behavior is explicitly named `per_record_majority_oracle`; the benchmark now also includes a real `global_majority_stage_baseline`. | Fixed |
| P1-3 peak matcher did not minimize timing error after maximizing matches | Matching now prioritizes maximum match count and then minimum total absolute timing error. The synthetic case `reference=[0,8]`, `detected=[5]`, `tolerance=5` is covered. | Fixed |
| P1-4 selection/manifest/config contracts were loose | Record selection now requires exact requested IDs, respects `included`, rejects empty record lists, validates key config ranges, and rejects output path collisions. | Mostly fixed |
| P1-5 release bundle was not a complete executable snapshot | Same-name release directories now fail instead of mixing old files. A complete frozen snapshot with lockfile copy, output hashes, run manifest, and offline rebuild contract is not implemented. | Partially fixed |
| P1-6 MIT-BIH annotation/ODI assumptions were not encoded enough | MIT-BIH reports now include source-AHI alignment, SO2 availability, sleep-only ODI proxy, artifact-review gates, and dataset-readiness tiers. Formal AASM/CMS hypopnea scoring and manual adjudication remain outside the current implementation. | Partially fixed |

## Other Review Findings

| Area | Current state |
| --- | --- |
| Branch/test coverage | Tests increased to 70 passing and now cover the closure regressions. Full branch coverage, CLI branch coverage, and CI matrix coverage are still not complete. |
| Module structure | The repository was reorganized by analysis domain, but some domain modules remain large and procedural, especially Sleep/MIT-BIH report and orchestration code. |
| Reproducibility | Configs, manifests, tracked compact outputs, and validation commands exist. Atomic output directories, run manifests, full output hash manifests, and a complete frozen v0.2 snapshot remain future work. |
| Documentation | Project summaries and domain reports exist. Some older generated report text still contains pilot-oriented reproduction wording and should be treated as stale documentation rather than current command truth. |
| Security and supply chain | No production security posture is claimed. SBOM, dependency audit, signed release artifacts, and release checksums are not implemented. |
| Clinical claims | Reports intentionally frame findings as educational/clinical-learning evidence. They do not claim diagnostic validity, treatment selection, or clinical deployment readiness. |

## Current Scientific Outputs

### ECG/HRV

Current HRV core outputs can support method-development claims about:

- R-peak detector behavior against public reference annotations;
- RR/NN interval construction and exclusion reasons;
- time-domain and frequency-domain HRV sensitivity;
- controlled artifact sensitivity;
- record-level uncertainty.

They cannot support:

- personal HRV baseline;
- disease detection;
- stress inference;
- treatment decisions;
- device purchase conclusions.

### Sleep-EDF

Current Sleep-EDF outputs can support educational analysis of:

- sleep architecture;
- total sleep time;
- sleep-period efficiency;
- WASO;
- REM latency;
- stage balance;
- fragmentation proxies;
- reference-vs-YASA staging discrepancy.

They cannot support, by themselves:

- AHI/RDI;
- oxygen desaturation burden;
- apnea/hypopnea diagnosis;
- PAP/oral-appliance treatment decisions;
- hypoventilation reasoning;
- respiratory-event severity.

### MIT-BIH PSG

Current MIT-BIH PSG outputs can support educational OSA-style reasoning from:

- sleep/apnea annotations;
- AHI-style respiratory event burden per sleep hour;
- event-type breakdowns;
- source-AHI alignment audit;
- respiration channel availability;
- SO2 availability and sleep-only ODI proxy;
- dataset-readiness gates.

Important current gate results:

- 18 records analyzed.
- Source alignment statuses: 10 `needs_manual_review`, 6 `roughly_aligned`, 2 `source_ahi_estimated_annotation_unavailable`.
- Oxygen review statuses: 2 `oxygen_review_ready`, 3 `artifact_review_recommended`, 13 `not_available`.
- Records suitable for respiratory annotation-burden learning: `slp01a`, `slp02a`, `slp02b`, `slp03`, `slp37`, `slp61`.
- SO2 artifact-review records: `slp59`, `slp61`, `slp66`.
- Special source-context-only records: `slp41`, `slp45`.

These outputs can show strong respiratory-event burden and oxygenation evidence in real data, but they are still educational signals. Final OSA diagnosis or treatment selection would require scoring-rule context, symptoms, waveform review, oxygen desaturation/arousal adjudication, comorbidities, and clinician interpretation.

## Known Remaining Defects And Limitations

These are the remaining gaps if the project is resumed later:

1. Manual source-AHI adjudication is still needed for high/medium-priority MIT-BIH rows before making stronger source-alignment claims.
2. SO2 artifact review is still needed for `slp59`, `slp61`, and `slp66` before using those oxygen metrics as strong clinical-learning examples.
3. Full hypopnea scoring is not implemented because airflow reduction and arousal adjudication are not fully encoded in this pipeline.
4. The ODI scorer is a documented project-defined proxy, not a validated clinical ODI implementation.
5. The release bundle prevents same-name directory contamination but is not yet a complete offline reproducibility snapshot.
6. The repo has no SBOM, dependency audit report, signed release checksums, or production supply-chain workflow.
7. Some generated reports still contain older pilot-oriented reproduction text; current canonical state is better represented by this document, `reports/project/project_state_summary.md`, and the latest validation commands above.
8. Domain modules remain larger than ideal, so future maintenance would benefit from splitting metrics, policy, plotting, reporting, and orchestration into smaller modules.
9. There is no stable public API guarantee; CLI and file schemas should still be treated as research-prototype interfaces.
10. The project should not be presented as clinical decision support, production deployment, or validated medical software.

## Closed-For-Now Direction

No further implementation is currently planned. If the project is reopened, the most defensible order would be:

1. Push or archive the current local commits.
2. Clean stale documentation wording.
3. Manually adjudicate MIT-BIH source-AHI rows.
4. Manually review SO2 artifact records.
5. Re-run MIT-BIH readiness gates.
6. Decide whether a richer PSG dataset is justified.
7. Build a v0.2 frozen reproducibility snapshot.

Those directions are preserved only as a record of unresolved scientific and engineering limits.
