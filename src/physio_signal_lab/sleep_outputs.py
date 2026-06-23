from __future__ import annotations

from pathlib import Path
import re


OUTPUT_PREFIX_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def clean_output_prefix(output_prefix: str) -> str:
    if not OUTPUT_PREFIX_RE.fullmatch(output_prefix):
        raise ValueError(
            "output_prefix may contain only letters, numbers, underscores, and hyphens"
        )
    return output_prefix


def scoped_sleep_edf_output_path(output_prefix: str, suffix: str) -> Path:
    prefix = clean_output_prefix(output_prefix)
    return Path("results") / "sleep_edf" / f"{prefix}_{suffix}"


def scoped_sleep_edf_report_path(output_prefix: str, suffix: str) -> Path:
    prefix = clean_output_prefix(output_prefix)
    return Path("reports") / "sleep_edf" / f"{prefix}_{suffix}"
