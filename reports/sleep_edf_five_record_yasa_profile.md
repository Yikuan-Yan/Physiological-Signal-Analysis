# Sleep-EDF YASA Runtime Profile

## Scope

This report profiles YASA runtime in a child process with a hard timeout. It is a runtime gate, not a sleep-stage benchmark.

No sleep-quality, clinical, diagnostic, or YASA performance claims are made here.

## Summary

- completed: 5
- timed out: 0
- errored: 0

| record | status | crop_s | timeout_s | wall_s | epochs | total_s |
| --- | --- | --- | --- | --- | --- | --- |
| SC4001 | completed | None | 180.0 | 15.372 | 2650 | 13.520893 |
| SC4011 | completed | None | 180.0 | 15.870 | 2802 | 13.922787 |
| SC4021 | completed | None | 180.0 | 40.536 | 2804 | 38.635576 |
| SC4031 | completed | None | 180.0 | 16.870 | 2820 | 14.792611 |
| SC4041 | completed | None | 180.0 | 17.658 | 2570 | 15.609188 |

## Decision Rule

YASA metrics may be committed only after a profiling run completes and the subsequent `--include-yasa` benchmark writes aligned predictions for all included pilot epochs.
