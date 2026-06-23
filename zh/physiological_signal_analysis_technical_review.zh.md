# Physiological Signal Analysis 代码库技术审查报告

> 审查对象：`Physiological Signal Analysis`
>
> 审查日期：2026-06-23
>
> 报告语言：中文；代码标识、模块名和技术术语保留英文
>
> 结论标签：**mature research prototype / educational method-development workbench**

---

## 0. Executive Summary

该代码库实际实现了三条面向公开生理信号数据集的分析 pipeline：

1. **Fantasia ECG/HRV 方法验证**：完成数据清点、R-peak detection、峰值匹配、RR/NN interval 构造、time-domain/frequency-domain HRV、artifact injection、correction strategy 比较与 record-level bootstrap。
2. **Sleep-EDF sleep staging 与 sleep-quality 教学分析**：完成人工 stage label 展开、stage mapping、majority baseline、optional YASA staging、性能评价、sleep architecture 指标与临床教育型解释。
3. **MIT-BIH PSG respiratory/oxygen evidence 分析**：完成 stage/event token 解析、respiratory-event burden、source-AHI 对齐、channel quality、SpO₂/ODI proxy、event-window review 与 dataset-readiness gate。

代码库并非表层 demo。它具备配置文件、CLI、manifest/checksum、lockfile、测试、machine-readable outputs、图表、报告和历史 release bundle，已经达到较成熟的 research prototype 水平。

但它尚未达到 production-ready。最关键的阻塞不是“文档不够漂亮”，而是若干会改变结果定义或破坏 provenance 的 correctness 问题：

- Sleep-EDF/MIT-BIH downloader 可能把已有损坏文件的本地 hash 回写为 manifest 中的 expected checksum；
- sleep-quality 计算删除 excluded/gap epochs 后压缩时间轴，改变 sleep-period duration、efficiency、WASO 和 transition semantics；
- HRV artifact correction 在 missed/spurious beat 情形下不保持总 recording duration；
- HRV report 中存在无条件 `pass` gate，不能证明结果来自已验证输入；
- majority baseline 使用当前 record 的 reference labels 选取 majority class，方法学上属于 target-derived oracle baseline；
- CLI、完整 benchmark runner、YASA worker 等关键 execution path 缺少有效 branch coverage。

### 总体评级

| 维度 | 评级 | 核心判断 |
|---|---:|---|
| 功能完整性 | 7/10 | 三条主 pipeline 均有真实输出，但部分计划内容未实现，若干结论受 correctness 问题影响 |
| 架构设计 | 6/10 | 分层意图明确，但 `mit_bih_psg.py`、`sleep_quality.py` 已形成 procedural monolith |
| 代码质量 | 6/10 | type hints、dataclass、配置化较好；超长函数、重复 I/O、隐式 assumptions 较多 |
| 正确性与鲁棒性 | 4/10 | 存在 checksum trust、时间轴、artifact invariance、report gate 等高影响问题 |
| 测试与验证 | 5/10 | 54 tests 通过，但关键 orchestration path 基本未覆盖 |
| 性能与资源 | 5/10 | 可运行，但存在多轮重复读盘、全量 preload、无 cache/checkpoint 等问题 |
| 可复现性 | 6/10 | 有 `uv.lock`、config、manifest、seed、tracked outputs；缺少 run manifest 与 atomic output |
| 文档与可用性 | 6/10 | 研究计划和结果报告详细；缺少根 README、examples、CLI contract |
| 安全与隐私 | 6/10 | 无明显 secret 泄露；主要风险是 data integrity 和 supply-chain provenance |
| 研究/工程价值 | 8/10 | provenance 意识、annotation uncertainty、readiness gate 和 machine-readable outputs 价值较高 |

---

# 1. 审查范围与方法

## 1.1 阅读范围

本次审查覆盖：

- 项目配置与环境：`pyproject.toml`、`uv.lock`、`configs/`；
- 入口与 orchestration：`src/physio_signal_lab/cli.py`；
- 数据读取与下载：`src/physio_signal_lab/io/`；
- 核心 feature/evaluation 模块：`src/physio_signal_lab/features/`、`src/physio_signal_lab/evaluation/`；
- domain pipeline：`sleep_edf_benchmark.py`、`sleep_quality.py`、`mit_bih_psg.py`；
- tests；
- `docs/`、`reports/`、`results/`、`figures/`；
- release bundle 和 manifest；
- tracked CSV 的记录数、关键统计量、时间轴和重复产物。

代码与测试合计约 **9,169 行**。主要大模块包括：

- `src/physio_signal_lab/mit_bih_psg.py`：约 2,160 行；
- `src/physio_signal_lab/sleep_quality.py`：约 972 行；
- `src/physio_signal_lab/cli.py`：约 580 行。

## 1.2 动态验证范围

### 已执行

- 运行 pytest；
- 检查 branch coverage；
- 对纯数值函数构造动态反例；
- 检查 tracked CSV 的行数、重复文件和时间轴一致性；
- 验证 artifact correction、sleep gap compression、peak matching 等具体行为。

### 运行结果

| 检查 | 结果 |
|---|---|
| pytest | **54 passed，6 skipped** |
| skipped tests | 4 个 data-contract tests；2 个 RR/NN integration tests |
| skip 原因 | 上传内容删除了 Fantasia raw data |
| branch coverage | 约 **45%** |
| clean dependency installation | 未完成；当前容器无法联网下载缺失依赖 |
| full pipeline rerun | 未完成；raw waveform 被删除，且网络不可用 |

为运行不触发 raw I/O 的数值 tests，测试环境中使用了一个不实现 WFDB I/O 的最小 import stub。所有真实 WFDB 读取测试都在调用前因 raw data 缺失而 skip，因此该 stub 没有代替实际数据验证。

## 1.3 证据分级

本文使用以下标签：

- **[事实]**：可由文件、函数实现、配置或本次动态运行直接确认；
- **[推断]**：基于代码结构、输出和工程经验作出的高置信判断；
- **[待确认]**：必须依赖完整 raw data、作者意图或独立外部验证才能确定。

---

# 2. 项目理解

## 2.1 项目目标

研究计划位于：

```text
docs/plans/public_real_physiological_signal_analysis_plan_v4.md
```

计划的核心目标是建立一套可复查、可复现、可扩展的真实人体生理信号分析流程，并将 ECG/RR/HRV 作为核心主线，将 PSG/sleep staging 作为扩展线。

计划同时明确：

- 使用公开数据；
- 不采集新个人数据；
- 不提供诊断；
- 不将模型预测包装为临床 ground truth；
- 强调 annotation uncertainty、artifact sensitivity 和 reproducibility。

当前实现已从单一 HRV 项目扩展为三个 domain：

```text
reports/project/repo_work_summary.md
```

其中概括了：

1. ECG/HRV 方法验证；
2. Sleep-EDF sleep architecture 与 sleep-quality learning；
3. MIT-BIH PSG respiratory-event、SO₂ 与 source-AHI alignment。

## 2.2 当前实现的一段话概括

**该代码库是一个面向公开生理信号数据集的配置化研究分析工作台：它从原始 WFDB/EDF 文件和人工 annotations 出发，执行 ECG peak detection、RR/NN 与 HRV 计算、sleep-stage benchmark、sleep architecture summary、respiratory/oxygen proxy 分析，并将 provenance、测试、结果表、图和方法学报告组织为可复查输出。**

其当前阶段应定义为：

> **成熟 research prototype，兼具 educational analysis 和 method-development 属性；尚不具备 production deployment、clinical validation 或稳定 public API 的条件。**

## 2.3 典型使用流程

### HRV

```text
配置 configs/hrv/core.yaml
    ↓
验证 Fantasia manifest
    ↓
扫描 records / inventory
    ↓
NeuroKit R-peak detection
    ↓
与 reference annotations 匹配
    ↓
构造 RR/NN intervals
    ↓
time-domain / frequency-domain HRV
    ↓
artifact injection + correction comparison
    ↓
record-level bootstrap
    ↓
写 CSV / figures / Markdown report
```

### Sleep-EDF

```text
配置 configs/sleep_edf/default.yaml
    ↓
验证 manifest 与 record selection
    ↓
读取 PSG EDF + Hypnogram EDF
    ↓
展开 30 s stage labels
    ↓
映射 R&K stages → W/N1/N2/N3/REM
    ↓
majority baseline
    ↓
optional YASA staging
    ↓
metrics / confusion / probabilities
    ↓
sleep-quality metrics / educational indicators
    ↓
写 CSV / figures / Markdown report
```

### MIT-BIH PSG

```text
配置 configs/mit_bih_psg/default.yaml
    ↓
验证 WFDB manifest
    ↓
读取 .st annotations
    ↓
解析 stage 和 event tokens
    ↓
计算 respiratory annotation burden
    ↓
source-AHI alignment
    ↓
channel quality / SpO₂ / ODI proxy
    ↓
event-window summaries
    ↓
dataset-readiness gate
    ↓
写 CSV / figures / Markdown reports
```

## 2.4 输入、输出与运行环境

### 输入

- Fantasia WFDB files：`.hea`、`.dat`、`.ecg` 等；
- Sleep-EDF：PSG EDF 与 Hypnogram EDF；
- MIT-BIH PSG：`.hea`、`.dat`、`.st`、`.ecg`；
- YAML config；
- manifest 中的 URL、license、path、checksum 和 inclusion 信息。

### 输出

```text
results/hrv/
figures/hrv/
reports/hrv/

results/sleep_edf/
figures/sleep_edf/
reports/sleep_edf/

results/mit_bih_psg/
figures/mit_bih_psg/
reports/mit_bih_psg/
```

输出类型包括：

- inventory table；
- peak benchmark metrics；
- RR/NN interval table；
- HRV window metrics；
- artifact sensitivity table；
- sleep-stage predictions、probabilities 和 metrics；
- sleep-quality metrics；
- respiratory/source-alignment/oxygen metrics；
- readiness table；
- PNG figures；
- Markdown reports。

### 运行环境

`pyproject.toml` 中：

```toml
requires-python = ">=3.11,<3.14"
```

Core dependencies 包括：

- NumPy；
- Pandas；
- SciPy；
- Matplotlib；
- WFDB；
- NeuroKit2；
- PyYAML。

Sleep dependencies 包括：

- MNE；
- scikit-learn；
- YASA。

YASA extra 对 Python 版本有额外限制，见 `pyproject.toml` 的 optional dependencies。

---

# 3. 已提交结果所证明的功能

以下数字来自 tracked outputs，不等于本次基于 raw data 的独立重算。

## 3.1 Fantasia HRV

主要文件：

```text
results/hrv/data_quality/fantasia_inventory.csv
results/hrv/peak_benchmark/peak_benchmark_by_record.csv
results/hrv/rr_nn/reference_intervals.csv
results/hrv/artifacts/artifact_sensitivity.csv
results/hrv/frequency/frequency_window_metrics.csv
```

[事实]

- inventory records：40；
- detector benchmark rows：80，即 40 records × 2 个 tolerance；
- RR intervals：285,494；
- NN intervals：280,748；
- `non_normal_endpoint`：4,739；
- `invalid_rr_duration`：7；
- 5 min windows：977；
- 有有效 Welch 输出的 windows：969；
- artifact scenarios：38,400；
- 50 ms tolerance 下 median F1：约 0.99936；
- 最差 record F1：约 0.97265。

## 3.2 Sleep-EDF

主要文件：

```text
results/sleep_edf/twenty_record_epoch_labels.csv
results/sleep_edf/twenty_record_yasa_metrics.csv
results/sleep_edf/twenty_record_baseline_metrics.csv
```

[事实]

- label epochs：54,712；
- included epochs：54,587；
- excluded epochs：125；
- 20-record YASA pooled accuracy：约 0.82331；
- balanced accuracy：约 0.72176；
- macro-F1：约 0.65841；
- Cohen’s κ：约 0.67557；
- majority baseline accuracy：约 0.68533；
- majority baseline balanced accuracy：0.2；
- majority baseline κ：0。

## 3.3 MIT-BIH PSG

主要文件：

```text
results/mit_bih_psg/complete_record_*.csv
```

[事实]

- annotation epochs：10,197；
- respiratory/source-alignment/oxygen records：18；
- channel-quality rows：101；
- event-window summaries：140；
- source-AHI alignment：
  - `needs_manual_review`：10；
  - `roughly_aligned`：6；
  - `source_ahi_estimated_annotation_unavailable`：2；
- SpO₂ available：5 records；
- 无 SpO₂ channel：13 records；
- oxygen review：
  - ready：2；
  - recommended manual review：3；
  - unavailable：13；
- readiness：
  - respiratory annotation learning：6；
  - source alignment review：10；
  - source context only：2。

[推断]

MIT-BIH pipeline 的价值不在于宣称所有记录都可直接用于结论，而在于它显式输出 readiness gate，避免把 18 条记录统一包装为同等可信的数据。

---

# 4. 目录结构与模块职责

## 4.1 结构概览

| 路径 | 当前职责 | 评价 |
|---|---|---|
| `configs/` | 三个 domain 的参数、路径、selection、thresholds | 参数集中是优点；缺 schema、range 和 cross-field validation |
| `data/manifests/` | URL、license、path、SHA256、included flag | provenance 意图强；checksum 更新模型存在严重问题 |
| `src/physio_signal_lab/io/` | 下载、manifest validation、WFDB/EDF 读取 | dataset adapter 边界大致清楚 |
| `src/physio_signal_lab/features/` | HRV、RR/NN、uncertainty、sleep-stage mapping | 数值函数较小，结构相对最好 |
| `src/physio_signal_lab/evaluation/` | peak benchmark、artifact experiment、staging metrics | 职责合理；若干 assumptions 未编码为 invariants |
| `src/physio_signal_lab/cli.py` | subcommands 与 orchestration | 适合作为 composition root；缺 CLI tests 和统一 run context |
| `sleep_edf_benchmark.py` | Sleep benchmark orchestration、worker、I/O、report | 责任过多 |
| `sleep_quality.py` | metrics、heuristics、ranking、plots、report、runner | 972 行，职责混合 |
| `mit_bih_psg.py` | parsing、respiration、oxygen、quality、plots、reports、runner | 2,160 行，是最大维护风险 |
| `results/figures/reports` | tracked derived outputs | 便于审查；缺 run ID 与 stale-output detection |
| `releases/` | frozen metadata bundle | 尚不是完整、原子、可离线复现的 snapshot |

## 4.2 架构判断

[事实]

代码库存在明确的分层意图：

```text
io → features/evaluation → orchestration/report
```

[推断]

它不是无结构 notebook dump。早期 HRV 模块的边界较好；Sleep 和 MIT-BIH 后续扩展时没有继续拆分，导致 domain-specific orchestration、policy、numeric calculation、plotting 和 report generation 被塞入同一文件。

---

# 5. Core Execution Path

## 5.1 CLI 入口

console script 见：

```text
pyproject.toml
```

入口实现：

```text
src/physio_signal_lab/cli.py::main
```

## 5.2 HRV execution path

主命令：

```text
run-ecg-core
```

调用链：

```text
run_ecg_core()
  ├─ validate manifest
  ├─ inventory_fantasia()
  │    └─ build_inventory()
  ├─ benchmark_peaks()
  │    └─ benchmark_records()
  │         └─ benchmark_record()
  │              ├─ detect_r_peaks()
  │              └─ peak_metrics()
  ├─ run_rr_artifacts()
  │    ├─ build_reference_intervals()
  │    ├─ window_metrics()
  │    └─ artifact_experiment()
  ├─ run_frequency_hrv()
  │    ├─ build_reference_intervals()
  │    ├─ frequency_window_metrics()
  │    └─ bootstrap_uncertainty()
  └─ build_report()
```

关键位置：

```text
src/physio_signal_lab/cli.py
src/physio_signal_lab/evaluation/peak_benchmark.py
src/physio_signal_lab/evaluation/peak_matching.py
src/physio_signal_lab/features/rr_nn.py
src/physio_signal_lab/features/hrv_frequency.py
src/physio_signal_lab/evaluation/artifacts.py
```

[事实]

`build_reference_intervals()` 在 `run_rr_artifacts()` 和 `run_frequency_hrv()` 中被重复调用，意味着 raw data 与 interval construction 存在重复工作。

## 5.3 Sleep-EDF execution path

主命令：

```text
run-sleep-edf-pilot-benchmark
```

调用链：

```text
validate_sleep_edf_manifest()
  ↓
paths_from_selection()
  ↓
read_sleep_edf_epoch_labels()
  ↓
majority_stage_predictions()
  ↓
optional YASA subprocess per record
  ↓
align_model_predictions()
  ↓
sleep_stage_metrics()
  ↓
write labels / predictions / probabilities / metrics / report
```

主 runner：

```text
src/physio_signal_lab/sleep_edf_benchmark.py
```

clinical education path：

```text
run-sleep-edf-clinical-education
  ↓
read_sleep_edf_epoch_labels()
  ↓
sleep_quality_metrics()
  ↓
build_clinical_indicators()
  ↓
build_clinical_question_ranking()
  ↓
plots + report
```

对应模块：

```text
src/physio_signal_lab/sleep_quality.py
```

## 5.4 MIT-BIH PSG execution path

主 runner：

```text
run_mit_bih_psg_respiratory_pilot()
```

调用链：

```text
manifest validation
  ↓
read_annotation_epochs()
  ↓
respiratory_metrics()
  ↓
source_ahi_alignment()
  ↓
channel_quality()
  ↓
oxygen_saturation_metrics()
  ↓
oxygen_artifact_review()
  ↓
dataset_readiness()
  ↓
event_window_summaries()
  ↓
plot_event_windows()
  ↓
clinical_indicators()
  ↓
write CSV + Markdown reports
```

集中位于：

```text
src/physio_signal_lab/mit_bih_psg.py
```

[推断]

该 runner 是一次性顺序 pipeline，没有 checkpoint、per-record failure isolation 或 atomic run directory。中间步骤失败时，可能留下部分新输出和部分旧输出。

---

# 6. 算法、模型、Assumptions 与适用范围

## 6.1 R-peak detection

ECG 读取：

```text
src/physio_signal_lab/io/fantasia.py
```

[事实]

非有限 ECG samples 通过线性插值修复。

R-peak detection：

```text
src/physio_signal_lab/evaluation/peak_benchmark.py::detect_r_peaks
```

实现使用 NeuroKit 的 ECG cleaning 和 peak detection。

### Assumptions

- reference annotations 足以作为 method benchmark 的近似 reference；
- 50 ms 和 100 ms tolerance 可表达 detector alignment 的两个尺度；
- annotation 与 waveform sample index 在同一时间基准上；
- ECG channel selection 和 units 已正确解析。

### 适用范围

适用于公开数据上的算法验证，不应直接等价为临床设备级 detector certification。

## 6.2 Peak matching

文件：

```text
src/physio_signal_lab/evaluation/peak_matching.py
```

当前 matcher 是按时间排序的 greedy one-to-one matching。

### 当前行为

- detection 和 reference 逐个推进；
- tolerance 内建立匹配；
- 一旦匹配即固定；
- 输出 TP、FP、FN、timing error。

### Assumption

在正常心率、峰间隔远大于 tolerance 时，greedy matching 与更严格的 bipartite matching 通常一致。

### 限制

在多个 reference/detection 同时落入 tolerance window 时，它不保证：

1. 最大 cardinality；
2. 在 cardinality 最大时最小化总 absolute timing error。

## 6.3 RR/NN 构造

文件：

```text
src/physio_signal_lab/features/rr_nn.py
```

公式：

\[
RR_i = \frac{s_{i+1}-s_i}{f_s}\times1000\ \mathrm{ms}.
\]

当前 NN 条件：

- 两个 endpoint symbols 都在 `normal_symbols`；
- interval duration 位于 300–2000 ms；
- interval finite 且 positive。

配置位置：

```text
configs/hrv/core.yaml
```

### Assumptions

- endpoint-based symbol rule 足以定义 NN；
- 300–2000 ms 是本数据集的合理 physiological filter；
- annotation symbols 已可靠映射。

### 限制

- 该规则不是通用 clinical NN definition；
- 不处理更复杂的 ectopy context、paced beats、interpolated beats 或 morphology；
- threshold 应被视为 project-level data-cleaning policy。

## 6.4 HRV time/frequency domain

文件：

```text
src/physio_signal_lab/features/hrv_time.py
src/physio_signal_lab/features/hrv_frequency.py
```

### Time-domain metrics

- MeanNN；
- SDNN；
- RMSSD；
- pNN50。

### Frequency-domain metrics

- 4 Hz interpolation 后 Welch PSD；
- unevenly sampled RR series 上 normalized Lomb–Scargle；
- LF：0.04–0.15 Hz；
- HF：0.15–0.40 Hz。

配置：

```text
configs/hrv/core.yaml
```

[事实]

报告代码区分 Welch 的 `ms²` band power 与 normalized Lomb power，没有将两者描述为相同单位。

### Assumptions

- 5 min window 对 short-term HRV 足够；
- interpolation 与 detrending 选择适合 Fantasia resting ECG；
- Lomb normalization 与项目内部比较目标匹配；
- window 级缺失处理不会系统性偏置年龄组比较。

### 适用范围

适用于方法比较和教学性 HRV 分析。若用于正式生理结论，需要进一步验证：

- window length sensitivity；
- stationarity；
- respiration rate；
- ectopy burden；
- participant-level confounding。

## 6.5 Artifact experiment

文件：

```text
src/physio_signal_lab/evaluation/artifacts.py
```

实现 artifact types：

- missed beat；
- spurious extra beat；
- timestamp jitter；
- ectopic short–long pair。

Correction strategies：

- no correction；
- delete flagged intervals；
- interpolate flagged intervals。

当前比较 metrics：

```text
MeanNN, SDNN, RMSSD, pNN50
```

[事实]

`METRIC_NAMES` 不包含 LF/HF。因此研究计划中“artifact 对 LF、HF 的传播”尚未实现。

### 核心 limitation

当前 artifact 被建模为 RR array 的长度和值变化，而 correction 仍在 interval-index space 中执行。这不足以表达 missed/spurious beat 的时间边界变化。

更合理的 state variable 应为：

```text
beat timestamps / beat boundaries
```

然后从修复后的 timestamps 重新构造 RR intervals。

## 6.6 Sleep staging

配置：

```text
configs/sleep_edf/default.yaml
```

Stage mapping：

- Wake → W；
- Stage 1 → N1；
- Stage 2 → N2；
- Stage 3/4 → N3；
- REM → REM；
- Movement / `?` → excluded。

YASA channels：

- Fpz-Cz；
- horizontal EOG；
- submental EMG。

### Assumptions

- 30 s epochs；
- label onset 可映射到连续 epoch index；
- selected channels 与 YASA model domain 相容；
- excluded epochs 可被安全处理；
- pooled epoch metrics 可用于初步 benchmark。

### 适用范围

YASA 输出属于 model prediction，不应替代人工 scorer。特别是 N1、睡眠障碍样本、channel mismatch、scorer disagreement 场景，需要独立 review。

## 6.7 Sleep-quality metrics

文件：

```text
src/physio_signal_lab/sleep_quality.py
```

指标包括：

- total recording time；
- total sleep time；
- sleep efficiency；
- sleep onset latency；
- sleep period duration；
- WASO；
- REM latency；
- stage proportions；
- transitions / fragmentation-like indicators。

### 当前主要 assumption

过滤掉 excluded epochs 后，剩余 stages 被视为连续时间序列。

该 assumption 在有 gap、Movement 或 unknown epoch 时不成立，详见后文 P0-2。

## 6.8 MIT-BIH respiratory burden

文件：

```text
src/physio_signal_lab/mit_bih_psg.py
```

`.st` annotation 的第一个 token 被视为 sleep stage，其余 token 被精确计数为 respiratory、leg、arousal 等事件。

当前 AHI-like 指标是：

```text
annotation event count / estimated sleep hours
```

其中 sleep hours 由 sleep epochs × fixed epoch duration 计算。

### Assumptions

- `.st` rows 与固定 30 s epoch 对齐；
- token count 代表 intended event count；
- 同一 epoch 的多个 token 可被逐个计数；
- stage-derived sleep duration 足以作为 denominator；
- source-reported AHI 可用于粗略 alignment。

### 适用范围

该值应表述为 **AHI-style annotation burden**，而不是根据 AASM rules 重建的临床 AHI。

## 6.9 SpO₂ 与 ODI proxy

配置：

```text
configs/mit_bih_psg/default.yaml
```

实现逻辑：

- 0–1.5 范围的 SpO₂ 信号启发式乘 100；
- plausible range 设为 40–100%；
- 以前 120 s rolling maximum 为 baseline；
- 下降至少 3 或 4 percentage points；
- 持续至少 10 s；
- 连续 segment 计为 desaturation event。

### Assumptions

- channel units 可通过 amplitude heuristic 推断；
- rolling maximum 足以近似局部 baseline；
- threshold/minimum duration 与项目分析目标一致；
- signal dropout 和 spike 已被 quality rule 充分控制。

### 限制

- rolling maximum 对高 spike 敏感；
- 没有外部 ODI scorer validation；
- 没有验证 threshold 与具体 source annotation 的一致性；
- 只有 5/18 records 有可用 SpO₂。

因此该模块应定位为 project-defined oxygen desaturation proxy。

---

# 7. 多维度评价

## 7.1 功能完整性

### 优点

[事实]

- 三条主 pipeline 都存在真实 machine-readable outputs；
- HRV 从 detector 到 uncertainty 形成完整方法链；
- Sleep 同时有 baseline 和 model benchmark；
- MIT-BIH 包含 readiness gate，而非只输出单一 summary；
- 输出不仅有 report，还有 interval/probability/alignment/audit tables。

### 缺口

1. HRV artifact experiment 未计算 LF/HF propagation；
2. 未实现系统性 window-length sweep；
3. 未证明 clean environment 下一条命令可重跑全部结果；
4. Sleep baseline 定义不独立；
5. Sleep gap semantics 不正确；
6. MIT ODI 尚无人工或 source-level validation；
7. release bundle 不能独立重建主要输出。

### 评级

**中上。** 项目目标大部分已被实现，但若干核心结果仍受 correctness 和 validation 缺口影响。

## 7.2 架构设计

### 优点

- `io`、`features`、`evaluation` 的分层意图明确；
- dataset-specific config 独立；
- CLI 作为 composition root 是合理方向；
- 多数数值函数可单独调用；
- manifest、results、reports 和 figures 目录职责清楚。

### 问题

- `mit_bih_psg.py` 同时负责 parsing、numeric calculation、quality policy、plotting、report 和 orchestration；
- `sleep_quality.py` 同时包含 metrics、clinical heuristics、ranking、figures、report 和 runner；
- MIT downloader 复用 Sleep downloader，形成 domain 反向依赖；
- 缺统一 `RunContext`；
- output schema 通过隐式 CSV columns 传递，没有版本；
- pipeline steps 没有 artifact contract 或 DAG。

### 评级

**中等。** 可维护性尚可，但 domain 扩张后模块边界已明显失稳。

## 7.3 代码质量

### 优点

- 较多 type hints；
- 使用 dataclass 表达结构化结果；
- 配置集中，不大量硬编码；
- numeric functions 多数命名直观；
- 报告代码显式表达 caveats。

### 问题

- 超长函数和文件增加认知负担；
- 重复 I/O 和重复 interval construction；
- 部分函数对空输入、NaN、缺字段的 contract 不明确；
- 大量隐式 assumptions 没有 `assert` 或 validation；
- CLI help 文本不足；
- report generation 与 quality gate 混合；
- duplicated output names 增加歧义。

### 评级

**中等。** 代码可读，但缺少 production-grade contracts 与模块化。

## 7.4 正确性与鲁棒性

这是当前最弱的维度。

已确认问题包括：

- checksum blessing；
- sleep gap compression；
- epoch index 不来自 onset；
- artifact correction 不保持时间跨度；
- report false pass；
- NaN interpolation shape mismatch；
- target-derived baseline；
- greedy peak matching timing bias；
- partial record selection 静默继续；
- MIT annotation spacing、token length、SpO₂ key collision 等 latent issues。

### 评级

**中下。** 数值流程有较强研究意图，但若干 correctness bug 会直接改变输出解释。

## 7.5 测试与验证

### 当前结果

- 54 passed；
- 6 skipped；
- branch coverage 约 45%。

覆盖率最弱模块：

- `cli.py`：0%；
- `evaluation/peak_benchmark.py`：0%；
- `sleep_edf_benchmark.py`：0%；
- `yasa_profile_worker.py`：0%；
- `plots.py`：0%；
- `features/rr_nn.py`：约 16%；
- `mit_bih_psg.py`：约 41%。

### 判断

[事实]

现有测试主要证明部分数值函数和 table-generation 逻辑。

[推断]

它们不能证明：

- CLI 参数正确传递；
- complete pipeline 在 clean environment 下可运行；
- downloader 与 manifest 的 trust model 正确；
- YASA subprocess failure 能被正确处理；
- output directory 不会混入 stale files；
- report gate 与实际输入验证一致。

### 评级

**中下。** 测试数量不算少，但集中在局部函数，缺少关键集成验证。

## 7.6 性能与资源使用

### HRV

[事实]

- inventory、peak benchmark、RR/artifact、frequency 会多轮读取 records；
- `build_reference_intervals()` 至少执行两次；
- peak benchmark 在绘图前保留全部 waveform objects。

[推断]

40 records × 2 h × 250 Hz × 8 bytes，仅 ECG 原始数组即约 0.58 GB；加 cleaned signal、respiration、BP 和 Python overhead，峰值内存可进一步升高。

### Artifact experiment

tracked scenarios：

\[
40\times4\times4\times20\times3=38{,}400.
\]

同一 corruption 在三种 strategy 下有可复用中间结果，也适合 record-level parallelism。

### Sleep

`yasa_profile_worker.py` 在 `preload=True` 后 crop，意味着短片段 profile 仍先加载整夜 EDF。

YASA records 串行处理，稳健但耗时。可增加受控 record-level parallelism，并限制 BLAS threads。

### MIT-BIH

oxygen metrics、event summary 和 plotting 可能重复读取同一 waveform。适合引入 per-record cache/context。

### 输出格式

大 CSV 包括：

- `reference_intervals.csv`：约 30 MiB；
- `artifact_sensitivity.csv`：约 15 MiB；
- `twenty_record_yasa_probabilities.csv`：约 5.6 MiB。

Parquet 更适合保留 dtypes、减少 I/O 和文件体积。

### 评级

**中下。** 当前规模可运行，但资源使用方式不利于扩展到更大 cohort。

## 7.7 可复现性

### 优点

- `uv.lock`；
- YAML config；
- manifest；
- random seed；
- tracked results；
- reports；
- release metadata。

### 问题

- manifest expected checksum 可被本地文件覆盖；
- 没有每次 run 的 Git commit、config hash、dependency version 和 output hash；
- output 不是原子写入；
- 无 CI；
- 无 canonical command-to-output mapping；
- release bundle 不包含完整结果和 lockfile 副本；
- 不能确认 tracked outputs 是否全部由当前 HEAD 生成。

### 评级

**意图中上，实现中等。** provenance 是项目强项，但 trust model 仍需修复。

## 7.8 文档与可用性

### 优点

- 研究计划详细；
- domain reports 对方法和 caveats 说明较多；
- tracked outputs 便于结果审查。

### 缺口

根目录缺少：

```text
README.md
LICENSE
CITATION.cff
examples/
CI workflow
```

`pyproject.toml` 使用一份长研究计划作为 package README，不适合作为新用户入口。

CLI subcommands 缺少充分的 `help`/`description`；安装、数据下载、Python 版本、YASA extra、完整运行命令和预计产物没有形成唯一入口。

### 评级

**中等。** 方法文档强于使用文档。

## 7.9 安全与隐私

### 优点

- 未发现硬编码 token、password、API key；
- `data/raw/` 被 `.gitignore` 排除；
- 项目使用公开数据；
- 研究计划明确非诊断定位；
- downloader 使用 temporary `.part` file 后 replace。

### 风险

- 最大风险是 data integrity，而非 PII；
- manifest trust model 可被本地坏文件污染；
- URL/path 来自 config，若未来暴露为服务，需要防 SSRF/path traversal；
- 无 SBOM、dependency audit、signed release；
- repo 缺 LICENSE，代码与派生输出的再分发边界不明确。

### 评级

**中等。** 本地 research CLI 风险可控，但 supply-chain provenance 不够强。

## 7.10 研究与工程价值

最有价值的资产：

1. **annotation uncertainty 意识**：没有把公开 annotation 无条件称为绝对 ground truth；
2. **HRV 方法链完整**：detector error → RR/NN → artifact sensitivity → frequency sensitivity → bootstrap；
3. **MIT readiness gate**：显式区分可用、需 review、仅 source context 的 records；
4. **machine-readable outputs**：保留 interval、probability、alignment 和 audit 级表格；
5. **caveat discipline**：持续强调非诊断、模型预测与临床 label 的边界；
6. **可复用 dataset adapters**：Fantasia、Sleep-EDF、MIT-BIH 的读取和 manifest 结构可继续扩展。

### 评级

**较高。** 该项目最有价值的不是单个指标，而是把数据 provenance、算法敏感性和结果解释组织成完整研究 workflow 的能力。

---

# 8. 已确认问题与证据

## P0-1：Downloader 可把损坏文件“认证”为正确输入

### 状态

**[事实，严重]**

### 证据位置

```text
src/physio_signal_lab/io/sleep_edf.py::download_file
src/physio_signal_lab/cli.py
src/physio_signal_lab/io/sleep_edf.py::update_manifest_checksums
src/physio_signal_lab/io/mit_bih_psg.py::update_manifest_checksums
```

### 当前逻辑

当目标文件已存在且未指定 overwrite 时，`download_file()` 直接返回本地文件的 SHA256。

随后 CLI 无条件把这个 hash 写回 manifest。

### 失败场景

```text
1. 本地已有被截断或修改的文件
2. download 返回 skipped_existing
3. 当前损坏文件 hash 被写入 expected checksum
4. 后续 validation 显示 checksum_ok=True
```

### 影响

- 破坏 provenance；
- 使 manifest 从“可信预期”退化为“当前文件状态记录”；
- 无法发现本地 corruption；
- release/report 可能基于错误输入继续生成。

### 修复原则

必须分离：

```text
upstream_expected_sha256
local_observed_sha256
```

expected checksum 只能来自：

- 官方 source；
- 独立可信 snapshot；
- 首次受控下载并经过外部确认的 immutable provenance process。

绝不能由待验证文件本身反向定义。

---

## P0-2：Sleep-quality 计算压缩 excluded/gap epochs

### 状态

**[事实，严重；tracked results 受影响]**

### 证据位置

```text
src/physio_signal_lab/sleep_quality.py::sleep_quality_metrics
```

### 当前逻辑

函数先删除 `included=False` rows，再把剩余 stage 转为连续 list。后续 sleep onset、sleep period、WASO、REM latency 和 transitions 都按 list position 计算。

### 问题

删除 excluded epoch 后，真实 elapsed time 被压缩；前后 stage 被直接拼接，产生虚假的 continuity。

### 对 tracked results 的检查

- excluded epochs：125；
- 位于 first-to-last included sleep span 内：24；
- 影响 records：7；
- `SC4091` 当前 `sleep_period_minutes=506.0`；
- 按真实 epoch span 应为 511.5 min；
- 当前 efficiency 高估约 1.04 percentage points。

### 正确处理策略

至少应提供两类量：

1. **elapsed-time metrics**：按 `onset_seconds` 或 `epoch_index` 计算；
2. **observed-valid-time metrics**：只在有效 epochs 上计算。

同时显式输出：

```text
missing_epoch_count
missing_minutes
missing_epochs_within_sleep_period
continuity_break_count
```

Gap 不应被自动解释为 wake，也不应被静默删除。

---

## P0-3：Sleep annotation 的 `epoch_index` 不来自真实 onset

### 状态

**[事实，latent bug；当前 tracked batch 未触发]**

### 证据位置

```text
src/physio_signal_lab/sleep_staging.py::expand_stage_annotations
```

### 当前逻辑

`epoch_index` 从 0 顺序递增，忽略 annotation onset。

### 动态反例

```text
onset = [0 s, 90 s]
当前输出 epoch_index = [0, 1]
真实 30 s bins 应为 [0, 3]
```

### 影响

- label 与 YASA prediction 可能错位；
- gap 被压缩；
- overlap/non-grid onset 无法检测；
- sleep-quality duration 进一步偏差。

### 当前 tracked data 状态

`twenty_record_epoch_labels.csv` 中：

```text
onset_seconds == epoch_index × 30 s
```

因此当前 20-record batch 没暴露该 bug，但实现仍不满足一般 contract。

---

## P0-4：Artifact interpolation 不保持总 RR duration

### 状态

**[事实，严重；动态复现]**

### 证据位置

```text
src/physio_signal_lab/evaluation/artifacts.py
src/physio_signal_lab/features/hrv_time.py::flagged_interpolate
```

### 反例

基准：

```text
[1000, 1000, 1000, 1000] ms
total = 4000 ms
```

当前结果：

| Artifact | corrupted total | interpolate 后 |
|---|---:|---:|
| missed beat | 4000 ms | `[1000,1000,1000]`，total 3000 ms |
| spurious beat | 4000 ms | 五个 1000 ms，total 5000 ms |

### 根因

missed/spurious beat 改变的是 beat boundary 数量，而当前 correction 仅替换 RR array 中的值。

### 影响

- MeanNN、SDNN、RMSSD、pNN50 误差混入 recording duration drift；
- 不同 correction strategy 比较失去共同时间基准；
- 对频域扩展会造成更严重的采样时间错误。

### 正确设计

artifact state 应定义在：

```text
beat timestamps
```

修复策略应：

- missed beat：恢复 missing boundary；
- spurious beat：删除 extra boundary；
- jitter：调整 timestamp；
- ectopic：修改局部 boundary，同时保持首尾 span。

然后统一由 timestamps 重算 RR。

---

## P0-5：HRV 报告 gate 可无条件通过

### 状态

**[事实，严重]**

### 证据位置

```text
src/physio_signal_lab/reporting.py::_gate_rows
src/physio_signal_lab/reporting.py::build_hrv_core_report
```

### 当前行为

- manifest gate 固定 `pass`；
- “No diagnostic claims” gate 固定 `pass`；
- 正文硬写 0 missing files / 0 checksum mismatches；
- 最终 Decision 固定为 pass；
- report builder 只读取结果 CSV，不接收真实 `ManifestValidation` 或 run metadata。

### 影响

旧 CSV、部分新 CSV、人工修改 CSV 或未验证输入，都可能生成带 `pass` 的报告。

### 修复

报告层必须接收实际 gate inputs：

```text
ManifestValidation
RunManifest
ExpectedOutputSchemaValidation
ResultCompletenessValidation
```

最终 Decision 必须由 gate aggregation 计算，而不是硬编码。

---

## P1-1：`flagged_interpolate()` 对 NaN 输入出现 shape mismatch

### 状态

**[事实；动态复现]**

### 证据位置

```text
src/physio_signal_lab/features/hrv_time.py::flagged_interpolate
```

### 反例

```python
intervals = [1000, NaN, 1000]
mask = [False, True, False]
```

当前产生：

```text
ValueError: interval_ms and invalid_mask must have the same shape
```

### 根因

函数先通过 `finite_1d()` 删除非有限元素，之后再比较原始 mask shape。

### 修复

先验证原始 shape；然后：

```text
combined_invalid = invalid_mask OR ~isfinite(intervals)
```

在原 index space 中插值。

---

## P1-2：Majority baseline 使用当前 record 的真实 labels

### 状态

**[事实；方法学问题]**

### 证据位置

```text
src/physio_signal_lab/sleep_staging.py::majority_stage_predictions
```

### 当前逻辑

对每条 record：

1. 读取该 record 的 reference stage counts；
2. 选择该 record 的 majority stage；
3. 用该 stage 预测同一 record。

这不是独立 baseline，而是 per-record oracle prior。

### 合成反例

两条 records 具有相反 majority class：

```text
same-record oracle accuracy = 0.8
leave-one-record-out majority accuracy = 0.2
```

### 当前 tracked batch

20 条 records 的 majority 都是 WAKE，因此当前 pooled 结果等价于 constant-WAKE baseline，数值没有被 leakage 改变。

### 修复选项

- 改名为 `per_record_majority_oracle`，明确只作为上界式 sanity check；
- 新增 `global_training_majority`；
- 新增 leave-one-subject-out majority baseline。

---

## P1-3：Peak matcher 不最小化 timing error

### 状态

**[事实；动态复现]**

### 证据位置

```text
src/physio_signal_lab/evaluation/peak_matching.py
```

### 反例

```text
reference = [0, 8]
detected  = [5]
tolerance = 5
```

当前 greedy matcher：

```text
5 ↔ 0，error = +5
8 → FN
```

最近邻意义下应为：

```text
5 ↔ 8，error = -3
0 → FN
```

### 影响

- TP/F1 在低密度 ECG 上通常不变；
- timing-error distribution 可能偏置；
- tachycardia、duplicate detection 或密集候选下影响增大。

### 推荐定义

采用两级 objective：

1. maximize number of matches；
2. among maximum-cardinality matchings, minimize total absolute timing error。

---

## P1-4：Selection 与 manifest contract 不严格

### 证据

```text
src/physio_signal_lab/manifest.py::manifest_records
src/physio_signal_lab/sleep_staging.py::paths_from_selection
src/physio_signal_lab/features/rr_nn.py::build_reference_intervals
src/physio_signal_lab/config.py::load_config
```

### 问题

- `manifest_records()` 不检查 `included`；
- `paths_from_selection()` 只要找到至少一条 record 就继续；
- 空 record list 可能在 `pd.concat([])` 处产生低层异常；
- `load_config()` 只验证顶层是 mapping；
- 无统一范围检查和 cross-field validation。

### 应验证的具体约束

- requested IDs 必须 exact-match manifest；
- included flag 必须被尊重；
- `window_seconds > 0`；
- frequency bands 不重叠且单调；
- artifact rates 在 `[0,1)`；
- threshold names/columns 不冲突；
- epoch duration 与 annotations 对齐；
- output paths 不重叠。

---

## P1-5：Release bundle 不是完整可执行 snapshot

### 证据位置

```text
src/physio_signal_lab/release.py::build_release_bundle
```

### 当前问题

- 目标目录允许 `exist_ok=True`；
- 不清空旧文件；
- 只复制 config、manifest、report；
- `pyproject.toml`、`uv.lock` 和主要 result CSV 仅记录 hash，不复制；
- 不运行 correctness gates；
- 无 temp directory → atomic rename。

### 影响

旧文件可能混入新 release；bundle 无法离线完成完整审查或重建。

### 推荐定义

真正的 frozen bundle 至少应包含：

```text
source commit
pyproject.toml
uv.lock
configs/
immutable input manifest
run_manifest.json
results/
figures/
reports/
checksums.json
```

---

## P1-6：MIT-BIH annotation/ODI assumptions 未编码

### 证据位置

```text
src/physio_signal_lab/mit_bih_psg.py
configs/mit_bih_psg/default.yaml
```

### 具体问题

1. annotation rows 用 enumeration 作为 epoch index，未检查 sample spacing；
2. `zip(annotation.sample, aux_notes)` 对长度不一致会静默截短；
3. channel quality 只检查最初 60 s，无法发现后半夜 dropout；
4. SpO₂ threshold output key 使用 `int(threshold)`，3.0 和 3.5 可能碰撞；
5. rolling maximum baseline 对高 spike 敏感；
6. event review 取每条 record 的前 N 个 events，不是随机或分层抽样；
7. source-reported AHI provenance 未在代码中形成结构化 citation/audit trail。

### 影响

这些问题不证明当前结果全部错误，但意味着 ODI、source alignment 和 event examples 的适用范围比表面标题更窄。

---

# 9. 立即修复建议

## 9.1 P0：修复 provenance trust model

### 涉及模块

```text
src/physio_signal_lab/io/sleep_edf.py
src/physio_signal_lab/io/mit_bih_psg.py
src/physio_signal_lab/cli.py
src/physio_signal_lab/manifest.py
```

### 实施方案

定义 manifest schema：

```yaml
source_url: ...
upstream_sha256: ...
local_path: ...
included: true
license: ...
```

下载结果单独写 run metadata：

```yaml
local_observed_sha256: ...
download_status: downloaded|skipped_existing|failed
verified_against_upstream: true|false
```

禁止默认修改 `upstream_sha256`。

### 影响范围

Sleep-EDF 和 MIT-BIH 的全部输入验证、报告 gate 与 release provenance。

### 难度

中等。

### 验证方式

1. 预放一个内容错误但文件名正确的文件；
2. 运行 download；
3. 断言 manifest 不变；
4. validation exit code 必须为非零；
5. `--overwrite` 后下载正确文件，再验证通过。

---

## 9.2 P0：重建 Sleep 时间轴 contract

### 涉及模块

```text
src/physio_signal_lab/sleep_staging.py::expand_stage_annotations
src/physio_signal_lab/sleep_quality.py::sleep_quality_metrics
src/physio_signal_lab/sleep_edf_benchmark.py
```

### 实施方案

每个 epoch 保留：

```text
epoch_index
onset_seconds
duration_seconds
stage_raw
stage_mapped
included
missing_or_excluded_reason
```

`epoch_index` 应由：

\[
\mathrm{round}(onset/epoch\_duration)
\]

计算，并验证误差在 tolerance 内。

Gap 应：

- 显式插入 missing epoch rows；或
- 在 metrics 中按 onset 直接计算 elapsed time。

Transitions 不得跨 gap 自动连接。

### 影响范围

Sleep onset、sleep period、efficiency、WASO、REM latency、transitions、fragmentation indicators。

### 难度

中等。

### 验证方式

加入 tests：

- non-zero start；
- 90 s gap；
- overlap；
- non-grid onset；
- Movement inside sleep period；
- `SC4091` regression：elapsed sleep period 511.5 min。

---

## 9.3 P0：重做 artifact model

### 涉及模块

```text
src/physio_signal_lab/evaluation/artifacts.py
src/physio_signal_lab/features/hrv_time.py
```

### 实施方案

内部 canonical representation 改为：

```python
beat_times_ms: np.ndarray
```

Artifact injection 返回：

```python
@dataclass
class CorruptedBeatSeries:
    beat_times_ms: np.ndarray
    affected_regions: list[...]
    event_metadata: dict
```

Correction 也作用于 timestamps。

最终由：

```python
rr_ms = np.diff(beat_times_ms)
```

生成 interval series。

### 必须满足的 invariants

- timestamps strictly increasing；
- first/last timestamp 不变，除非 artifact model 明确允许；
- total recording span 不变；
- RR 全部 positive；
- event count 与 configured rate 一致；
- deterministic seed 可重现。

### 难度

中高。

### 验证方式

为 missed、spurious、jitter、ectopic 各建立 synthetic cases 和 property tests。

---

## 9.4 P0：让 report gate 与真实运行状态绑定

### 涉及模块

```text
src/physio_signal_lab/reporting.py
src/physio_signal_lab/cli.py
src/physio_signal_lab/release.py
```

### 实施方案

引入：

```python
@dataclass
class RunGateResult:
    name: str
    status: Literal["pass", "fail", "warning", "not_run"]
    evidence: str
```

Report builder 接收 gate list，不自行假设 pass。

总 Decision：

```text
fail       if any required gate == fail
warning    if no fail and any warning/not_run
pass       otherwise
```

### 验证方式

注入：

- checksum mismatch；
- missing record；
- empty frequency output；
- stale output timestamp；
- failed test summary。

断言最终 report 不得写 pass。

---

## 9.5 P0：原子化 outputs 和 release

### 涉及模块

```text
src/physio_signal_lab/cli.py
src/physio_signal_lab/release.py
```

### 实施方案

```text
results/<domain>/.run-<uuid>.tmp/
```

所有步骤成功后：

```text
atomic rename → results/<domain>/<run_id>/
```

更新一个小型 `latest` pointer，而不是覆盖历史目录。

Release 同理：

- 同名目标存在时默认失败；
- 临时目录中完成全部 copy、hash、validation；
- 成功后 atomic rename。

### 验证方式

在 pipeline 中间注入 exception，正式 output directory 的内容和 hashes 必须完全不变。

---

# 10. 中期重构与增强

## 10.1 拆分 `mit_bih_psg.py`

建议结构：

```text
mit_bih_psg/
  annotations.py
  respiratory.py
  oxygen.py
  channel_quality.py
  source_alignment.py
  readiness_policy.py
  event_windows.py
  plots.py
  reports.py
  pipeline.py
```

### Rationale

当前 2,160 行文件使：

- 数值算法和 report policy 难以独立测试；
- 修改 oxygen scorer 可能影响 unrelated report code；
- reviewers 难以定位 data flow；
- merge conflict 风险高。

### 验证

每个子模块独立 unit tests；`pipeline.py` 只负责 orchestration，不包含计算公式。

## 10.2 拆分 `sleep_quality.py`

建议结构：

```text
sleep/
  metrics.py
  timeline.py
  clinical_learning_policy.py
  ranking.py
  plots.py
  reports.py
  pipeline.py
```

### 关键原则

将：

- 数值事实；
- 教学型 threshold；
- clinical wording；
- visualization；

彻底分离。

这样可以对 policy 版本化，而不改变核心 metrics。

## 10.3 统一 downloader/provenance

新建：

```text
src/physio_signal_lab/io/download.py
src/physio_signal_lab/provenance.py
```

统一支持：

- immutable expected checksum；
- observed checksum；
- content length；
- retry/backoff；
- `.part` file；
- atomic rename；
- resume policy；
- source metadata；
- explicit overwrite semantics。

MIT 不应反向 import Sleep downloader。

## 10.4 Typed config schema

可使用 dataclass、Pydantic 或 attrs。

每个 domain 应定义：

```python
@dataclass(frozen=True)
class HrvConfig: ...

@dataclass(frozen=True)
class SleepEdfConfig: ...

@dataclass(frozen=True)
class MitBihPsgConfig: ...
```

必须验证：

- required fields；
- types；
- ranges；
- enum values；
- cross-field constraints；
- path collision；
- threshold uniqueness；
- selection exactness。

## 10.5 引入 `RunContext`

建议结构：

```json
{
  "run_id": "...",
  "started_at": "...",
  "finished_at": "...",
  "git_commit": "...",
  "dirty_worktree": false,
  "python_version": "...",
  "dependency_versions": {},
  "config_sha256": "...",
  "input_files": {},
  "random_seed": 1234,
  "outputs": {},
  "gates": []
}
```

### 价值

- 解决 stale-output；
- 证明某个 report 对应哪些 inputs/config/code；
- 支持 release freezing；
- 支持多次运行比较。

## 10.6 复用 I/O 与中间产物

### HRV

一次生成 canonical interval table，后续 artifact 与 frequency 复用。

### Sleep

cache expanded epoch labels 和 preprocessed channel metadata。

### MIT-BIH

构建 per-record `RecordContext`：

```python
@dataclass
class RecordContext:
    header: ...
    annotations: ...
    channel_metadata: ...
    cached_signals: ...
```

避免 oxygen、event summary 和 plots 重复读取同一 record。

## 10.7 输出使用 Parquet

优先转换：

```text
reference_intervals
artifact_sensitivity
YASA probabilities
annotation epochs
```

CSV 可保留为 human-readable export，但 Parquet 应成为 canonical machine-readable output。

## 10.8 Participant-level uncertainty

### Sleep

- participant-level bootstrap；
- per-record metric distribution；
- class-wise confidence intervals；
- calibration curves；
- LOSO evaluation。

### MIT-BIH

- record-level source-alignment uncertainty；
- ODI threshold sensitivity；
- missing-SpO₂ selection bias；
- event sample uncertainty。

---

# 11. 具体测试建设方案

## 11.1 CLI smoke tests

目标：

```text
src/physio_signal_lab/cli.py
```

测试内容：

- parser 构造；
- 每个 command 的 required arguments；
- config path 传递；
- `--overwrite`；
- missing record；
- manifest fail exit code；
- report gate fail；
- release target exists。

使用 monkeypatch 替换重型 pipeline 函数，验证 orchestration contract。

## 11.2 Synthetic WFDB fixture

构造 60–120 s synthetic ECG：

- known sinusoidal/impulse peaks；
- known annotations；
- ectopic symbol；
- NaN segment；
- duplicate peak；
- shifted peak；
- sampling frequency variations。

覆盖：

```text
load_record()
benchmark_record()
peak_metrics()
reference_intervals_for_record()
```

## 11.3 Tiny EDF 或 mocked MNE fixture

测试：

- non-zero annotation onset；
- gap；
- overlap；
- Movement；
- unknown stage；
- missing requested record；
- prediction-label alignment；
- subprocess failure；
- probability column schema。

## 11.4 Artifact property tests

对随机 positive RR/timestamp series 验证：

- monotonic timestamps；
- duration conservation；
- nonnegative event count；
- configured rate bounds；
- deterministic seed；
- correction idempotence；
- no negative/zero RR；
- no silent length mismatch。

## 11.5 MIT waveform fixture

构造 synthetic `.st` annotations 和 SpO₂：

- exact 3% desaturation；
- exact 4% desaturation；
- duration 9.9 s / 10 s；
- baseline spike；
- dropout；
- unit 0–1 与 0–100；
- nonuniform annotation spacing；
- multiple tokens per epoch。

验证 exact ODI count、stage mask、quality gate 和 report wording。

## 11.6 End-to-end integration tests

每条 pipeline 至少一个 tiny dataset，从 CLI 到全部输出：

```text
config
  → manifest validation
  → computation
  → table
  → figure
  → report
  → run manifest
```

### Coverage 目标

- orchestration/CLI branch coverage ≥ 80%；
- core numeric modules ≥ 90%；
- overall branch coverage ≥ 70%；
- 每个已确认 bug 均有 regression test。

---

# 12. 文档与可用性改进

## 12.1 根 README

至少包含：

1. 项目定位；
2. 三条 pipeline；
3. 非诊断声明；
4. Python 版本；
5. core/sleep 安装命令；
6. data acquisition；
7. manifest validation；
8. 最小运行命令；
9. 输出目录；
10. tests；
11. reproducibility 与 release；
12. known limitations。

## 12.2 `examples/`

建议：

```text
examples/
  hrv_minimal.md
  sleep_edf_minimal.md
  mit_bih_psg_minimal.md
  synthetic_end_to_end/
```

## 12.3 Metadata

补充：

```text
LICENSE
CITATION.cff
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
```

`pyproject.toml` 中项目 description 应更新，不再只描述 ECG/HRV。

## 12.4 CLI help

每个 subcommand 应明确：

- 输入；
- 输出；
- 是否需要 raw data；
- 是否会下载；
- 是否会覆盖；
- 预期 runtime/资源级别；
- 常见错误。

---

# 13. 安全、隐私与供应链建议

## 13.1 Data integrity

优先级最高：

- immutable upstream checksum；
- atomic download；
- content-length validation；
- source URL pinning；
- run-time observed hash；
- release output hash；
- failure-closed validation。

## 13.2 Dependency supply chain

建议加入：

- `pip-audit` 或同类 dependency audit；
- SBOM；
- lockfile verification；
- CI 中的 vulnerability scan；
- release checksums/signature。

## 13.3 Path/URL trust

当前是 trusted local CLI，可以接受 config 驱动的 path/URL。

若未来产品化为 service，必须增加：

- URL allowlist；
- SSRF 防护；
- output root sandbox；
- path traversal 防护；
- file-size limits；
- timeout 和 resource quota。

## 13.4 临床声明边界

继续保留：

- non-diagnostic；
- educational/method-development；
- model prediction ≠ clinical label；
- project-defined proxy ≠ clinically validated metric。

但这些声明不能用硬编码 `pass` gate 表达，应通过 lint、review policy 和 release checklist 验证。

---

# 14. 后续研究方向

## 14.1 HRV

1. 多 detector 比较，而不是单一 NeuroKit pipeline；
2. 对 detector error 的 morphology/heart-rate stratification；
3. artifact 对 LF/HF 的传播；
4. window length sweep：2/5/10 min；
5. Welch interpolation rate 和 detrending sensitivity；
6. Lomb normalization sensitivity；
7. respiration frequency 与 HF interpretation；
8. participant-level hierarchical model；
9. detector → RR → HRV 的 uncertainty propagation。

## 14.2 Sleep staging

1. leave-one-subject-out validation；
2. participant-level bootstrap；
3. class calibration；
4. temporal smoothing ablation；
5. N1 error analysis；
6. channel-ablation study；
7. scorer disagreement；
8. first-night vs second-night effects；
9. gap/missingness sensitivity；
10. architecture metrics 对 staging error 的传播。

## 14.3 MIT-BIH PSG

1. source-AHI provenance 审计；
2. 人工 adjudication protocol；
3. respiratory token 与 airflow/effort/arousal cross-check；
4. ODI 与 source/manual scorer 的比较；
5. SpO₂ baseline algorithm sensitivity；
6. stage-stratified respiratory burden；
7. missing-SpO₂ selection bias；
8. event review 的 stratified sampling；
9. readiness policy 的版本化和 reviewer agreement。

## 14.4 产品化

长期才应考虑：

- stable Python API；
- dataset adapter plugin system；
- workflow DAG；
- cache/checkpoint；
- versioned output schema；
- signed artifacts；
- provenance UI；
- controlled execution environment；
- role-based review workflow。

在独立 validation、data governance、专业 review 和监管路径建立前，不应将该项目包装为 clinical decision-support system。

---

# 15. Roadmap

## 15.1 1 周内

| 交付 | 具体行动 | Exit criteria |
|---|---|---|
| 修复 checksum trust model | 分离 upstream expected hash 与 observed local hash | 损坏 existing file 不得更新 expected hash；validation 必须失败 |
| 修复 Sleep 时间轴 | onset-based epoch index；gap 保留或显式统计 | gap/non-zero onset/overlap tests 通过；`SC4091` elapsed period 修正 |
| 重做 artifact correction invariants | timestamps-based artifact/correction | 所有 correction 保持总 span；无负 RR |
| 修复 report gate | 使用真实 manifest/run/result gate | 任一 required gate fail 时 Decision 为 fail |
| 修复 NaN interpolation | 在原 index space 合并 nonfinite mask | NaN regression test 通过 |
| 严格 record selection | exact-set validation | requested missing ID 必须显式失败 |
| 建立最小 CI | Python 3.11/3.12 synthetic tests | push/PR 自动执行；不依赖完整公开数据下载 |
| 增加根 README | 安装、数据、命令、输出、限制 | clean clone 用户可找到唯一运行入口 |

## 15.2 1 个月内

| 交付 | 具体行动 | Exit criteria |
|---|---|---|
| 拆分大模块 | 拆 `mit_bih_psg.py`、`sleep_quality.py` | runner 仅 orchestration；计算/策略/报告独立 |
| Typed config schema | 三个 domain 配置类与 validation | 所有 invalid ranges/collisions 启动前失败 |
| Run manifest | 记录 commit/config/input/output/dependencies | 每个 run 可完整追踪 |
| Atomic outputs | temp directory + atomic rename | 中途失败不改变正式结果 |
| Tiny end-to-end fixtures | 三条 pipeline 各一套 | 从 CLI 到 report 全链通过 |
| Coverage 提升 | 针对 CLI、runner、worker | overall branch ≥70%，orchestration ≥80% |
| I/O 复用与 Parquet | canonical intermediate + cache | 输出数值一致，runtime/memory 明显下降 |
| 重跑 tracked results | clean Python 3.12 locked environment | 全部 outputs 带 run manifest 和 hashes |
| `v0.2` release | 完整 frozen bundle | 可离线验证全部 bundled artifacts |

## 15.3 长期

| 方向 | 目标 |
|---|---|
| HRV methodological validation | detector、artifact、window、frequency method 的系统 sensitivity analysis |
| Sleep generalization | LOSO、calibration、temporal model、scorer disagreement、night effect |
| MIT respiratory validation | 人工 adjudication、ODI/source-AHI 对齐、channel-level physiological evidence |
| Dataset expansion | 仅在当前 readiness 问题无法解决时引入更丰富 PSG 数据集 |
| Engineering platform | stable API、plugins、DAG/cache、versioned schemas、signed artifacts |
| Clinical pathway | 独立验证、数据治理、专业 review、监管分析完成前保持 research/education 定位 |

---

# 16. 事实、推断与待确认事项清单

## 16.1 代码与本次运行确定的事实

- 54 tests passed，6 raw-data tests skipped；
- branch coverage 约 45%；
- 三条 pipeline 和 tracked outputs 均存在；
- checksum blessing 可由代码路径确认；
- sleep gap compression 可由 tracked data 定量确认；
- artifact duration drift 可动态复现；
- report false-pass 为硬编码行为；
- NaN interpolation shape mismatch 可动态复现；
- current majority baseline 使用 same-record labels；
- `all_record_*` 与 `complete_record_*` 多组 MIT CSV 当前逐字节重复；
- tracked Sleep labels 的 onset 与 epoch index 当前对齐，但 excluded epochs 已影响 elapsed-time semantics。

## 16.2 基于结构的推断

- 项目属于 mature research prototype；
- HRV benchmark 峰值内存可能达到数百 MB 至 GB 量级；
- 无 run manifest 和 atomic output 时存在 mixed-run 风险；
- monolithic domain modules 会显著提高后续扩展成本；
- 当前测试不足以支持 production readiness 声明。

## 16.3 需要 raw data 或作者确认

1. tracked outputs 是否全部由当前 HEAD、当前 config 和当前 lockfile 生成；
2. `source_reported_ahi` 的逐 record 原始来源和人工估算过程；
3. MIT `.st` token 的精确语义与 event-count contract；
4. Sleep excluded epoch 应作为 missing、artifact、wake 还是 continuity break；
5. `clinical_question_ranking()` 的分数是否仅为 educational heuristic；
6. clean Python 3.12 + locked YASA 环境下完整 rerun 的 runtime 和 output hashes；
7. repo 代码、数据 manifest 和派生输出的最终 license/citation policy；
8. release bundle 的目标是 metadata archive 还是可执行 reproducibility snapshot。

---

# 17. 最终技术判断

该项目最值得保留和继续投资的部分，是其对 provenance、annotation uncertainty、方法敏感性和 machine-readable audit outputs 的重视。它已经形成一套可扩展的生理信号 research workflow，而不是一次性脚本。

当前下一阶段不应优先扩展更多数据集或增加更多图表。应先完成以下 correctness closure：

```text
immutable input provenance
→ correct time-axis semantics
→ duration-preserving artifact model
→ real report gates
→ atomic outputs
→ end-to-end synthetic tests
```

完成这些工作后，项目可进入稳定 research platform 阶段；在此之前，任何 production-ready 或 clinical validation 声明都缺乏足够证据。
