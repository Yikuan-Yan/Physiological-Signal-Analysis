from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _positive_number(config: dict[str, Any], path: tuple[str, ...]) -> None:
    node: Any = config
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return
        node = node[key]
    if float(node) <= 0:
        dotted = ".".join(path)
        raise ValueError(f"Config value must be positive: {dotted}")


def _rate_list(config: dict[str, Any], path: tuple[str, ...]) -> None:
    node: Any = config
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return
        node = node[key]
    for value in node:
        rate = float(value)
        if rate < 0 or rate >= 1:
            dotted = ".".join(path)
            raise ValueError(f"Config rates must be in [0, 1): {dotted}")


def _validate_frequency_bands(config: dict[str, Any]) -> None:
    bands = config.get("hrv_frequency", {}).get("bands_hz")
    if not isinstance(bands, dict):
        return
    intervals = []
    for name, values in bands.items():
        low, high = float(values[0]), float(values[1])
        if low <= 0 or high <= low:
            raise ValueError(f"Invalid frequency band bounds: {name}")
        intervals.append((low, high, name))
    intervals.sort()
    for (_, previous_high, previous_name), (low, _, name) in zip(intervals, intervals[1:]):
        if low < previous_high:
            raise ValueError(f"Frequency bands overlap: {previous_name} and {name}")


def _validate_output_paths(config: dict[str, Any]) -> None:
    outputs = config.get("outputs")
    if not isinstance(outputs, dict):
        return
    file_paths = []
    for key, value in outputs.items():
        if key.endswith("_dir"):
            continue
        path = Path(str(value)).as_posix()
        file_paths.append((key, path))
    seen: dict[str, str] = {}
    for key, path in file_paths:
        if path in seen:
            raise ValueError(f"Output path collision: {seen[path]} and {key} -> {path}")
        seen[path] = key


def validate_config(config: dict[str, Any], *, path: Path | None = None) -> None:
    _positive_number(config, ("rr_nn", "window_seconds"))
    _positive_number(config, ("sleep_stages", "epoch_seconds"))
    _positive_number(config, ("annotations", "epoch_seconds"))
    _positive_number(config, ("hrv_frequency", "interpolation_hz"))
    _positive_number(config, ("hrv_frequency", "welch_nperseg_seconds"))
    _rate_list(config, ("artifact_experiment", "rates"))
    _validate_frequency_bands(config)
    _validate_output_paths(config)


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    if not isinstance(config, dict):
        raise ValueError(f"Config must be a mapping: {config_path}")
    validate_config(config, path=config_path)
    return config


def project_path(value: str | Path) -> Path:
    return Path(value).expanduser()
