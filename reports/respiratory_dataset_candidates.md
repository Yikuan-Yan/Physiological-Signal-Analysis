# Respiratory PSG Dataset Candidates For Clinical Reasoning

## Goal

Sleep-EDF can support sleep architecture and sleep-quality reasoning, but it cannot directly support obstructive sleep apnea, hypoventilation, oxygen desaturation, AHI/RDI, or respiratory-event treatment reasoning for the current selected records.

The next disease-focused phase should add a dataset with respiratory signals, oxygen saturation, and apnea/hypopnea annotations.

## Candidate Ranking

| rank | dataset | fit | why |
| --- | --- | --- | --- |
| 1 | MIT-BIH Polysomnographic Database | Best first integration | Small open PhysioNet dataset, 18 records, PSG signals, respiration, sleep/apnea annotations, and WFDB-compatible files. |
| 2 | Apnea-ECG Database | Best lightweight apnea screen | 70 ECG records with expert apnea annotations; 8 learning-set records include respiration and oxygen saturation. Good for apnea screening, weaker for full PSG sleep architecture. |
| 3 | UCDDB Sleep Apnea Database | Good suspected-SDB cohort | 25 full overnight PSGs from suspected sleep-disordered breathing subjects, with apnea and sleep-stage annotations. More dataset-specific parsing work. |
| 4 | Sleep Heart Health Study PSG Database | Best clinical richness, heavier access | Large PSG dataset with nasal airflow, respiratory effort, SaO2, arousals, respiratory events, and summary indices, but heavier access and scale. |

## Recommended Next Dataset

Start with the MIT-BIH Polysomnographic Database because it is small enough for fast iteration and includes both sleep/apnea annotations and respiration signals. It can bridge from the current Sleep-EDF sleep-stage pipeline to respiratory-event reasoning without immediately taking on SHHS-scale data management.

## What To Implement Next

1. Add `configs/mit_bih_psg.yaml`.
2. Add a manifest for a small pilot subset such as `slp01`, `slp02`, and `slp03`.
3. Download WFDB `.hea`, `.dat`, `.st`, and `.ecg` files.
4. Parse `.st` sleep/apnea annotations.
5. Compute respiratory-event burden per hour of sleep when annotation semantics are confirmed.
6. Add oxygen/respiration quality checks before interpreting desaturation or apnea burden.
7. Extend the clinical learning report with respiratory sections:
   - apnea annotation burden;
   - oxygen desaturation burden, when SpO2 exists;
   - respiratory-event evidence sufficiency;
   - treatment-learning map for PAP/oral appliance/referral questions.

## Evidence Boundaries

- Sleep-stage metrics alone can suggest poor sleep quality but cannot diagnose OSA.
- Respiratory-event labels plus sleep time can support an AHI/RDI-style learning calculation.
- Treatment reasoning should remain conditional: PAP, oral appliance, surgery, medication, or behavioral care require confirmed diagnosis, severity, symptoms, contraindications, and clinician review.

## Source Notes

- MIT-BIH Polysomnographic Database: PhysioNet describes over 80 hours of four-, six-, and seven-channel PSG with ECG, EEG, respiration, sleep-stage annotations, and apnea annotations.
- Apnea-ECG Database: PhysioNet describes 70 ECG records with expert apnea annotations; the challenge documentation notes that 8 records include respiration and oxygen saturation signals.
- UCDDB: PhysioNet describes 25 overnight polysomnograms from adults with suspected sleep-disordered breathing and provides sleep-stage annotation meanings.
- SHHS PSG Database: PhysioNet describes airflow, respiratory effort, SaO2, heart rate, sleep stages, respiratory events, arousals, and summary respiratory indices.

## References

- MIT-BIH Polysomnographic Database: https://physionet.org/content/slpdb/
- MIT-BIH signal/channel details: https://archive.physionet.org/physiobank/database/slpdb/slpdb.shtml
- Apnea-ECG Database: https://www.physionet.org/physiobank/database/apnea-ecg/
- Apnea-ECG extra respiration/SpO2 records: https://moody-challenge.physionet.org/2000/
- UCDDB: https://physionet.org/physiobank/database/ucddb/
- SHHS PSG Database: https://physionet.org/physiobank/database/shhpsgdb/
- SHHS annotation files: https://physionet.org/content/shhpsgdb/1.0.0/annotations.shtml
