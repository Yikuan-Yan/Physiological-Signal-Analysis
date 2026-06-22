# Sleep-EDF YASA Runtime Profile

## Scope

This report profiles YASA runtime in a child process with a hard timeout. It is a runtime gate, not a sleep-stage benchmark.

No sleep-quality, clinical, diagnostic, or YASA performance claims are made here.

## Summary

- completed: 2
- timed out: 0
- errored: 0

| record | status | crop_s | timeout_s | wall_s | epochs | total_s |
| --- | --- | --- | --- | --- | --- | --- |
| SC4001 | completed | None | 180.0 | 58.617 | 2650 | 55.121344 |
| SC4011 | completed | None | 180.0 | 55.327 | 2802 | 52.38509 |

## Decision Rule

YASA metrics may be committed only after a profiling run completes and the subsequent `--include-yasa` benchmark writes aligned predictions for all included pilot epochs.
