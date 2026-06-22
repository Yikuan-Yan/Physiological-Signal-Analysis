# hrv-core-v0.1.0

This bundle freezes the public-data ECG/HRV core stage.

Bundled files:

- `config/hrv_core.yaml`: frozen analysis configuration.
- `manifest/data_manifest.csv`: raw-data manifest with source URLs and checksums.
- `report/hrv_core_report.md`: core Gate report generated from tracked outputs.
- `environment.txt`: Python, platform, and package versions.
- `artifact_checksums.csv`: checksums for tracked result tables and figures.
- `release_manifest.json`: machine-readable release metadata.

Raw waveform files are intentionally excluded. Rebuild them from the manifest and PhysioNet source if needed.
