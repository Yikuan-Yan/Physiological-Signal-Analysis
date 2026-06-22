# Sleep-EDF YASA Runtime Gate

## Status

Passed for the current two-record pilot on Python 3.12.13 with YASA 0.7.0, MNE 1.12.1, and scikit-learn 1.9.0.

This report does not evaluate sleep quality, diagnose sleep disorders, or make clinical claims.

## Runtime Result

The bounded child-process profile completed for both pilot records:

| record | scope | limit | wall seconds | epochs | result |
| --- | --- | --- | --- | --- | --- |
| SC4001 | full night | 180 s | 58.617 | 2650 | completed |
| SC4011 | full night | 180 s | 55.327 | 2802 | completed |

Detailed timings are stored in `results/sleep_edf/yasa_runtime_profile.csv`, with the generated summary in `reports/sleep_edf_yasa_profile.md`.

## Benchmark Result

The opt-in YASA benchmark completed and wrote aligned predictions, probabilities, and metrics for all 5,452 included pilot epochs:

- `results/sleep_edf/pilot_yasa_predictions.csv`
- `results/sleep_edf/pilot_yasa_probabilities.csv`
- `results/sleep_edf/pilot_yasa_metrics.csv`
- `reports/sleep_edf_pilot_benchmark.md`

Pilot-level YASA metrics:

| records | accuracy | balanced accuracy | macro-F1 | Cohen's kappa |
| --- | --- | --- | --- | --- |
| SC4001, SC4011 | 0.744 | 0.667 | 0.595 | 0.544 |

## Compatibility Note

YASA 0.7.0 emits a scikit-learn `InconsistentVersionWarning` because its bundled estimator was pickled with scikit-learn 0.24.2 and is being loaded with scikit-learn 1.9.0. Treat this as a reproducibility caveat for downstream comparisons until the model/runtime versions are pinned or independently cross-checked.

## Reproduce

```bash
uv sync --python 3.12 --extra sleep --extra dev
uv run python -m physio_signal_lab.cli profile-yasa-runtime --config configs/sleep_edf.yaml --records SC4001,SC4011 --full-night --timeout-seconds 180
uv run python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf.yaml --records SC4001,SC4011 --include-yasa
```

## Next Decision

Download and validate the next frozen Sleep-EDF records while keeping YASA behind the child-process timeout gate. New records should pass checksum validation and a bounded YASA profile before their YASA metrics are committed.
