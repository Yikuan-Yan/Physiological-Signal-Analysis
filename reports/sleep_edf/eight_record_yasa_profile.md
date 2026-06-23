# Sleep-EDF YASA Runtime Profile

## Scope

This report profiles YASA runtime in a child process with a hard timeout. It is a runtime gate, not a sleep-stage benchmark.

No sleep-quality, clinical, diagnostic, or YASA performance claims are made here.

## Summary

- completed: 8
- timed out: 0
- errored: 0

| record | status | crop_s | timeout_s | wall_s | epochs | total_s |
| --- | --- | --- | --- | --- | --- | --- |
| SC4001 | completed | None | 180.0 | 13.085 | 2650 | 11.420836 |
| SC4011 | completed | None | 180.0 | 13.509 | 2802 | 11.870498 |
| SC4021 | completed | None | 180.0 | 13.604 | 2804 | 11.896157 |
| SC4031 | completed | None | 180.0 | 36.680 | 2820 | 34.916319 |
| SC4041 | completed | None | 180.0 | 36.170 | 2570 | 33.181402 |
| SC4051 | completed | None | 180.0 | 14.327 | 2722 | 12.51035 |
| SC4061 | completed | None | 180.0 | 14.601 | 2770 | 12.649988 |
| SC4071 | completed | None | 180.0 | 14.200 | 2810 | 12.411963 |

## Decision Rule

YASA metrics may be committed only after a profiling run completes and the subsequent `--include-yasa` benchmark writes aligned predictions for all included pilot epochs.
