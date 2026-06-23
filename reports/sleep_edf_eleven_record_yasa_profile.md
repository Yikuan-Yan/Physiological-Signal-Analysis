# Sleep-EDF YASA Runtime Profile

## Scope

This report profiles YASA runtime in a child process with a hard timeout. It is a runtime gate, not a sleep-stage benchmark.

No sleep-quality, clinical, diagnostic, or YASA performance claims are made here.

## Summary

- completed: 11
- timed out: 0
- errored: 0

| record | status | crop_s | timeout_s | wall_s | epochs | total_s |
| --- | --- | --- | --- | --- | --- | --- |
| SC4001 | completed | None | 180.0 | 18.873 | 2650 | 16.928077 |
| SC4011 | completed | None | 180.0 | 15.586 | 2802 | 13.681651 |
| SC4021 | completed | None | 180.0 | 16.099 | 2804 | 14.170069 |
| SC4031 | completed | None | 180.0 | 17.206 | 2820 | 15.276558 |
| SC4041 | completed | None | 180.0 | 14.539 | 2570 | 12.571112 |
| SC4051 | completed | None | 180.0 | 15.078 | 2722 | 13.27221 |
| SC4061 | completed | None | 180.0 | 15.549 | 2770 | 13.657048 |
| SC4071 | completed | None | 180.0 | 15.357 | 2810 | 13.519566 |
| SC4081 | completed | None | 180.0 | 16.268 | 2796 | 14.396209 |
| SC4091 | completed | None | 180.0 | 14.746 | 2732 | 12.957982 |
| SC4101 | completed | None | 180.0 | 14.426 | 2720 | 12.631288 |

## Decision Rule

YASA metrics may be committed only after a profiling run completes and the subsequent `--include-yasa` benchmark writes aligned predictions for all included pilot epochs.
