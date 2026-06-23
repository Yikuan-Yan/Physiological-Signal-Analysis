# Physiological Signal Analysis 当前工作总结

更新时间：2026-06-23

## 总览

这个 repo 已经从一个公开真实生理信号分析计划，推进成一个可运行、可复现、可扩展的 public-data physiological signal analysis lab。当前主线有三条：

1. ECG/HRV 方法验证：从真实 ECG 到 R peak、RR/NN interval、HRV、artifact sensitivity 和 uncertainty。
2. Sleep-EDF 睡眠结构与睡眠质量学习：从 PSG hypnogram 到 sleep architecture、sleep-quality metrics 和 clinical-learning indicators。
3. MIT-BIH PSG 呼吸事件与氧饱和度学习：从 sleep/apnea annotations、respiration、SO2 到 OSA-style evidence、ODI、source AHI alignment 和 dataset-readiness gate。

当前 repo 不是医疗诊断系统。它的目标是帮助理解真实数据能告诉我们什么、不能告诉我们什么，以及从数据到睡眠质量、疾病假设、临床诊断或治疗判断之间还缺哪些证据。

## 当前数据覆盖

| 数据集 | 当前范围 | 验证状态 | 已提交成果 |
| --- | ---: | --- | --- |
| Fantasia Database v1.0.0 | 40 records | ECG workflow report 记录 0 missing、0 checksum mismatch | HRV/benchmark/artifact CSV、报告、release bundle |
| Sleep-EDF Expanded Sleep Cassette | 20 个 first-night records，40 个 EDF 文件 | 998,070,310 bytes validated；0 missing；0 checksum mismatch | benchmark CSV、sleep-quality CSV、clinical-learning reports、figures |
| MIT-BIH Polysomnographic Database | 18 records，72 个 WFDB 文件 | 662,914,296 bytes validated；0 missing；0 checksum mismatch；0 incomplete required row | respiratory metrics、oxygen metrics、source-AHI alignment、readiness gates、reports、figures |

Raw waveform 文件仍然保留在 `data/raw/`，不进入 git。repo 中提交的是 compact metrics、reports、figures、manifests、configs、release metadata 和 tests。

## 工程基础

代码主体在 `src/physio_signal_lab/`，命令行入口在 `src/physio_signal_lab/cli.py`。

已经建立的工程能力：

- 用 manifest 记录 dataset version、source URL、license/provenance、local path、checksum 和 validation status。
- 用 `configs/hrv_core.yaml`、`configs/sleep_edf.yaml`、`configs/mit_bih_psg.yaml` 驱动可复现 pipeline。
- 把机器可读结果写入 `results/`，报告写入 `reports/`，图像写入 `figures/`。
- 对 data contracts、peak matching、HRV features、sleep outputs、MIT-BIH parsing/metrics、artifact sensitivity、uncertainty、reporting、release metadata 建立 regression tests。
- 冻结了 ECG/HRV 核心 release bundle：`releases/hrv-core-v0.1.0/`。
- 支持 scope-specific output prefix，避免 pilot/five/eight/eleven/twenty/complete outputs 互相覆盖。

## ECG/HRV 核心阶段

ECG/HRV 是项目的第一条主线，用 PhysioNet Fantasia Database 验证从真实 ECG 到 HRV 的基础处理链。

已完成：

- 读取并 inventory 40 条 Fantasia records：20 young、20 old；报告中记录 sex balance。
- 通过 manifest workflow 验证本地数据可用性和 checksum。
- 使用 official `.ecg` annotations 作为 reference，benchmark NeuroKit2 R-peak detection。
- 构建 RR intervals 和 NN intervals，并保留 exclusion reasons。
- 计算 time-domain HRV：MeanNN、SDNN、RMSSD、pNN50。
- 实现 artifact injection：missed beat、spurious extra beat、timestamp jitter、ectopic-like short-long interval pairs。
- 比较 artifact correction strategies：no correction、delete flagged intervals、interpolate flagged intervals。
- 实现 frequency-domain HRV：Welch PSD 和 Lomb-Scargle sensitivity analysis。
- 实现 record-level bootstrap uncertainty。
- 生成 `hrv-core-v0.1.0` release bundle。

关键结果：

- 50 ms R-peak benchmark：285,032 TP、1,280 FP、502 FN。
- 50 ms median sensitivity：0.99969。
- 50 ms median F1：0.99936。
- Median absolute timing error：8.0 ms。
- RR intervals：285,494。
- NN intervals：280,748。
- Excluded intervals：4,746。
- Artifact sensitivity scenarios：38,400 rows。
- Frequency-domain windows：977；valid Welch windows：969。

这一阶段的成果是：repo 已经有一个可复现、带测试、带报告的 ECG/HRV method-development core。它可以支持 detector behavior、interval construction、artifact sensitivity、frequency-method sensitivity 和 uncertainty 的方法学讨论，但不做个人 baseline、疾病诊断、stress inference 或治疗判断。

## Sleep-EDF 睡眠结构阶段

Sleep-EDF 阶段把项目从 ECG/HRV 扩展到 PSG-style sleep staging 和 sleep-quality learning。

已完成：

- 增加 Sleep-EDF download、manifest、validation、preflight workflow。
- 选择 `SC4001` 到 `SC4191` 的 first-night Sleep Cassette records。
- 将 reference hypnogram 展开为 30 s epochs。
- 将 R&K stages 映射到 five-class sleep staging labels。
- 增加 majority-stage baseline benchmark。
- 增加 optional YASA sleep staging、runtime profiling 和 scoped outputs。
- 生成 pilot、five-record、eight-record、eleven-record、twenty-record reports。
- 生成 hypnogram timeline plots 和 sleep architecture plots。
- 生成 reference-vs-YASA discrepancy tables。
- 计算 sleep-quality metrics：total sleep time、recording sleep efficiency、sleep-period efficiency、WASO、REM latency、stage balance、awakening count、fragmentation proxies。
- 生成 clinical-learning indicators 和 clinical-question ranking。

当前 Sleep-EDF 验证：

- Validated records：20。
- EDF files validated：40。
- Bytes validated：998,070,310。
- Missing files：0。
- Checksum mismatches：0。

当前 twenty-record YASA benchmark：

- Included epochs：54,587。
- Overall YASA accuracy：0.823。
- Balanced accuracy：0.722。
- Macro-F1：0.658。
- Cohen's kappa：0.676。

Sleep-EDF 当前能支持：

- sleep architecture；
- total sleep time；
- sleep-period efficiency；
- WASO；
- REM latency；
- stage balance；
- fragmentation proxies；
- model-vs-reference staging discrepancy learning。

Sleep-EDF 当前不能单独支持：

- AHI/RDI；
- oxygen desaturation burden；
- apnea/hypopnea diagnosis；
- PAP/oral appliance treatment decisions；
- hypoventilation reasoning；
- respiratory-event severity。

这一阶段的成果是：repo 已经能从真实 hypnogram 数据解释睡眠质量相关问题，同时清楚说明为什么 OSA、hypoventilation、治疗判断等问题需要呼吸事件和氧饱和度证据。

## MIT-BIH PSG 呼吸与氧饱和度阶段

MIT-BIH PSG 阶段是在 Sleep-EDF 暴露出“stage-only data 不足以回答呼吸疾病问题”之后新增的 disease-relevant evidence track。

已完成：

- 增加 `configs/mit_bih_psg.yaml`。
- 增加 MIT-BIH PSG manifest generation、download、checksum update、validation。
- 下载并验证全部 18 个 MIT-BIH PSG WFDB records。
- 解析 `.st` sleep/apnea annotations，生成 epoch-level tables。
- 计算 sleep-hour-normalized AHI-style respiratory annotation burden。
- 计算 hypopnea、obstructive apnea、central apnea、arousal-associated respiratory tokens 的 event-type rates。
- 加入 source-reported AHI，并实现 source-AHI alignment audit。
- 将 `slp41` 和 `slp45` 标记为 source-AHI-estimated、apnea annotations unavailable 的特殊记录。
- 增加 respiration 和 SO2 channel quality checks。
- 生成 respiratory-event epochs 周围的 waveform event windows 和 plots。
- 增加 sleep-aligned SO2 oxygen metrics。
- 用 documented pre-event rolling-baseline ODI scorer 替代主 sleep-only oxygen proxy。
- 输出 ODI 3% 和 ODI 4% sleep-only metrics。
- 增加 oxygen artifact review gates。
- 增加 dataset-readiness CSV 和 richer-PSG decision reports。

当前 MIT-BIH 验证：

- Validated records：18。
- WFDB files validated：72。
- Bytes validated：662,914,296。
- Missing files：0。
- Checksum mismatches：0。
- Incomplete required rows：0。

当前 complete-record respiratory results：

- AHI-style learning severity：14 severe-range、2 moderate-range、2 minimal-range。
- Median AHI-style annotation burden：53.19 events/h。
- Highest AHI-style burden：`slp37`，109.21 events/h。
- Source-AHI alignment statuses：10 `needs_manual_review`、6 `roughly_aligned`、2 `source_ahi_estimated_annotation_unavailable`。
- Source-AHI review priorities：10 `manual_review_high`、3 `manual_review_medium`、3 `low`、2 `separate_source_review`。

当前 complete-record oxygen results：

- SO2 status：5 records available、13 records without SO2 channel。
- Oxygen review statuses：2 `oxygen_review_ready`、3 `artifact_review_recommended`、13 `not_available`。
- Oxygen-ready records：`slp60`、`slp67x`。
- SO2 artifact-review records：`slp59`、`slp61`、`slp66`。

当前 dataset-readiness gate：

- 6 条记录适合 respiratory annotation-burden learning：`slp01a`、`slp02a`、`slp02b`、`slp03`、`slp37`、`slp61`。
- 10 条记录需要 manual source-AHI alignment，之后才能用于 source-alignment claims。
- 2 条记录是 source-context-only examples：`slp41`、`slp45`。
- 当前 richer PSG decision：继续使用 MIT-BIH PSG，不自动接入 UCDDB、SHHS 或更重的数据集；先完成 source-AHI review 和 SO2 artifact review。

这一阶段的成果是：repo 已经能展示真实 PSG annotation 和 SO2 数据如何支持 OSA-style clinical reasoning。它可以识别 severe-range respiratory burden 和 oxygen desaturation burden，但同时用 readiness gate 防止把 educational signal 误写成诊断或治疗结论。

## 临床学习边界

当前 repo 可以帮助回答：

- ECG、sleep-stage、respiratory-event、SO2 数据里分别有什么信息。
- 哪些指标可以从真实公开数据中可复现地计算出来。
- 哪些记录有强烈 sleep-disordered breathing signal。
- 哪些记录适合做 sleep architecture、respiratory burden、oxygen burden 的教学例子。
- 从数据到临床结论之间还缺哪些证据。

当前 repo 不主张：

- 最终医疗诊断；
- 治疗处方；
- 个人健康 baseline；
- 临床风险评分；
- 设备购买建议；
- 公开数据 annotation 是无误差真值。

## 主要入口文件

| 目的 | 文件 |
| --- | --- |
| ECG/HRV core report | `reports/hrv_core_report.md` |
| Frozen HRV release bundle | `releases/hrv-core-v0.1.0/` |
| Sleep-EDF next work plan | `reports/sleep_edf_next_work_plan.md` |
| Sleep-EDF twenty-record benchmark | `reports/sleep_edf_twenty_record_benchmark.md` |
| Sleep-EDF twenty-record clinical education | `reports/sleep_edf_twenty_record_clinical_education.md` |
| MIT-BIH complete respiratory report | `reports/mit_bih_psg_complete_record_respiratory_pilot.md` |
| MIT-BIH dataset decision | `reports/mit_bih_psg_complete_record_dataset_decision.md` |
| MIT-BIH readiness table | `results/mit_bih_psg/complete_record_dataset_readiness.csv` |
| Respiratory dataset candidates | `reports/respiratory_dataset_candidates.md` |

## 复现命令

基础验证：

```bash
uv run pytest -q
git diff --check
```

ECG/HRV core：

```bash
uv run python -m physio_signal_lab.cli validate-data --manifest data_manifest.csv
uv run python -m physio_signal_lab.cli run-ecg-core --config configs/hrv_core.yaml
```

Sleep-EDF twenty-record analysis：

```bash
uv run python -m physio_signal_lab.cli validate-sleep-edf --config configs/sleep_edf.yaml
uv run python -m physio_signal_lab.cli run-sleep-edf-pilot-benchmark --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041,SC4051,SC4061,SC4071,SC4081,SC4091,SC4101,SC4111,SC4121,SC4131,SC4141,SC4151,SC4161,SC4171,SC4181,SC4191 --output-prefix twenty_record --include-yasa
uv run python -m physio_signal_lab.cli run-sleep-edf-clinical-education --config configs/sleep_edf.yaml --records SC4001,SC4011,SC4021,SC4031,SC4041,SC4051,SC4061,SC4071,SC4081,SC4091,SC4101,SC4111,SC4121,SC4131,SC4141,SC4151,SC4161,SC4171,SC4181,SC4191 --output-prefix twenty_record --include-yasa
```

MIT-BIH PSG complete analysis：

```bash
uv run python -m physio_signal_lab.cli validate-mit-bih-psg --config configs/mit_bih_psg.yaml
uv run python -m physio_signal_lab.cli run-mit-bih-psg-respiratory-pilot --config configs/mit_bih_psg.yaml --output-prefix complete_record
```

## 当前剩余工作

剩余任务主要不是单纯代码实现，而是 evidence adjudication：

1. 人工复核 `results/mit_bih_psg/complete_record_source_ahi_alignment.csv` 中 high/medium-priority source-AHI alignment rows。
2. 人工检查 `slp59`、`slp61`、`slp66` 的 SO2 waveform/raw-channel evidence。
3. 完成上述人工复核后，重新运行 richer PSG gate。
4. 只有当下一阶段问题确实需要 arousal-linked respiratory scoring、更丰富 airflow/effort/oximetry cross-check、population-scale clinical context 或 source-provided respiratory indices 时，再接入 UCDDB、SHHS 或其他更重 PSG dataset。

## 总体成果

当前 repo 已形成完整的公开真实数据分析路径：

- 从 ECG/HRV 方法验证开始；
- 扩展到睡眠结构和睡眠质量学习；
- 再加入呼吸事件和氧饱和度证据，支持 OSA-style reasoning；
- 每个阶段都保留 data provenance、可复现命令、测试、报告和明确 clinical caveats。

当前状态适合定位为 educational and method-development repository，而不是 diagnostic system。
