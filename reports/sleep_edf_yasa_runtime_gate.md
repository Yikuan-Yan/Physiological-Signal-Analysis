# Sleep-EDF YASA Runtime Gate

## Status

YASA dependency resolution is fixed for a Python 3.12 sleep-extra environment, but local YASA execution has not yet completed within practical runtime limits. The committed benchmark outputs therefore remain baseline-only.

This report does not evaluate sleep quality, diagnose sleep disorders, or make YASA performance claims.

## Dependency Result

The following command completed successfully:

```bash
uv run --python 3.12 --isolated --with "yasa>=0.7.0" --with mne --with scikit-learn python -c "import sys, yasa, mne, sklearn; print(sys.version.split()[0]); print('yasa', yasa.__version__); print('mne', mne.__version__); print('sklearn', sklearn.__version__)"
```

Observed versions:

- Python: 3.12.13
- YASA: 0.7.0
- MNE: 1.12.1
- scikit-learn: 1.9.0

The project `sleep` extra now includes `yasa>=0.7.0` only for Python versions below 3.13. This prevents the Python 3.13 core environment from resolving to an incompatible YASA dependency set.

## Runtime Result

Two local YASA execution attempts were stopped because they exceeded the runtime budget:

| Attempt | Scope | Limit | Result |
| --- | --- | --- | --- |
| full pilot benchmark | `SC4001`, `SC4011`, full nights | 15 min | timed out |
| smoke crop | `SC4001`, first 10 min | 5 min | timed out |

No YASA prediction, probability, or metric CSV was committed from these attempts.

## Protected Pipeline

The default command remains baseline-only and completes:

```bash
uv run python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf.yaml --records SC4001,SC4011
```

YASA execution is explicit and opt-in:

```bash
uv sync --python 3.12 --extra sleep --extra dev
uv run --python 3.12 --extra sleep python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf.yaml --records SC4001,SC4011 --include-yasa
```

## Next Decision

Before using YASA as the model benchmark, resolve the runtime gate by testing a clean Python 3.12 environment, checking whether YASA feature extraction is blocked by local acceleration dependencies, and running a bounded profiling pass. Only commit YASA metrics after `--include-yasa` completes end-to-end and writes aligned predictions for all included pilot epochs.
