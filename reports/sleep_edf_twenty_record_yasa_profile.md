# Sleep-EDF YASA Runtime Profile

## Scope

This report profiles YASA runtime in a child process with a hard timeout. It is a runtime gate, not a sleep-stage benchmark.

No sleep-quality, clinical, diagnostic, or YASA performance claims are made here.

## Summary

- completed: 20
- timed out: 0
- errored: 0

| record | status | crop_s | timeout_s | wall_s | epochs | total_s |
| --- | --- | --- | --- | --- | --- | --- |
| SC4001 | completed | None | 180.0 | 13.430 | 2650 | 11.728093 |
| SC4011 | completed | None | 180.0 | 13.383 | 2802 | 11.712334 |
| SC4021 | completed | None | 180.0 | 13.285 | 2804 | 11.562618 |
| SC4031 | completed | None | 180.0 | 13.223 | 2820 | 11.549121 |
| SC4041 | completed | None | 180.0 | 13.095 | 2570 | 11.387945 |
| SC4051 | completed | None | 180.0 | 13.861 | 2722 | 12.11052 |
| SC4061 | completed | None | 180.0 | 13.318 | 2770 | 11.665597 |
| SC4071 | completed | None | 180.0 | 13.416 | 2810 | 11.772685 |
| SC4081 | completed | None | 180.0 | 13.428 | 2796 | 11.75508 |
| SC4091 | completed | None | 180.0 | 13.367 | 2732 | 11.758317 |
| SC4101 | completed | None | 180.0 | 13.089 | 2720 | 11.444616 |
| SC4111 | completed | None | 180.0 | 13.266 | 2642 | 11.589615 |
| SC4121 | completed | None | 180.0 | 13.354 | 2786 | 11.724048 |
| SC4131 | completed | None | 180.0 | 13.395 | 2814 | 11.718696 |
| SC4141 | completed | None | 180.0 | 13.416 | 2756 | 11.698361 |
| SC4151 | completed | None | 180.0 | 13.049 | 2620 | 11.402097 |
| SC4161 | completed | None | 180.0 | 13.184 | 2626 | 11.487141 |
| SC4171 | completed | None | 180.0 | 13.464 | 2742 | 11.809845 |
| SC4181 | completed | None | 180.0 | 13.530 | 2756 | 11.810519 |
| SC4191 | completed | None | 180.0 | 13.448 | 2774 | 11.808462 |

## Decision Rule

YASA metrics may be committed only after a profiling run completes and the subsequent `--include-yasa` benchmark writes aligned predictions for all included pilot epochs.
