# Sleep-EDF Pilot Benchmark Report

## Scope

This pilot benchmark verifies EDF reading, 30 s hypnogram expansion, R&K-to-five-class mapping, and a majority-stage baseline on the downloaded Sleep Cassette pilot records.

This report does not evaluate sleep quality, diagnose sleep disorders, or make event-detector accuracy claims.

## Records

- Records: SC4001, SC4011.
- MNE status: available.
- scikit-learn status: available.
- YASA status: missing.

YASA staging was not run in this stage because the current Python 3.13 environment could not resolve a compatible YASA dependency set. The benchmark therefore reports only the frozen majority-stage baseline.

## Stage Distribution

| record | included | excluded | WAKE | N1 | N2 | N3 | REM |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SC4001 | 2650 | 0 | 1997 | 58 | 250 | 220 | 125 |
| SC4011 | 2802 | 0 | 1856 | 109 | 562 | 105 | 170 |

## Majority-Stage Baseline

| record | epochs | majority ref | accuracy | balanced accuracy | macro-F1 | kappa |
| --- | --- | --- | --- | --- | --- | --- |
| SC4001 | 2650 | WAKE | 0.754 | 0.200 | 0.172 | 0.000 |
| SC4011 | 2802 | WAKE | 0.662 | 0.200 | 0.159 | 0.000 |
| all | 5452 | WAKE | 0.707 | 0.200 | 0.166 | 0.000 |

- Overall included epochs: 5452.
- Overall majority-stage accuracy: 0.707.
- Overall balanced accuracy: 0.200.
- Overall macro-F1: 0.166.
- Overall Cohen's kappa: 0.000.

## Reproduce

```bash
uv sync --extra sleep --extra dev
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml --records SC4001,SC4011
uv run python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf.yaml --records SC4001,SC4011
```

## Next Step

Resolve the YASA dependency blocker or run the sleep benchmark in a compatible Python environment, then add YASA predictions and probability outputs using the same aligned epoch table.
