# 公开真实生理信号分析项目 v4：HRV 核心验证，睡眠与设备采集后置

> 版本：4.0  
> 修订日期：2026-06-21  
> 当前状态：可执行方案  
> 核心原则：先完成公开真实数据上的可复现分析；设备购买、个人数据采集和长期健康监控仅作为通过阶段门槛后的可能方向。

## 1. 方案概述

### 1.1 目标与适用对象

本项目面向具备 Python、基础统计和 signal processing 能力的个人研究者或小型研究团队。当前目标不是选择可穿戴设备，也不是建立个人健康监控系统，而是完成一套能够被复查、复现和扩展的真实人体生理信号分析流程。

项目先以 **ECG / RR / HRV** 为强制核心线，再将 **PSG / EEG sleep staging** 和 **wearable proxy sleep staging** 设为门控扩展线。这样可以在较低数据与工程成本下先验证数据读取、annotation 对齐、artifact handling、指标计算、误差传播和科学报告能力。

### 1.2 当前范围

当前阶段包含：

- 公开或受许可约束的真实人体数据集调研；
- 数据版本、许可和 provenance 记录；
- ECG、R peak、RR/NN interval 和 HRV 分析；
- 可选的 Sleep-EDF 自动 sleep staging 外部评估；
- 可选的 wearable proxy sleep staging benchmark；
- 测试、复现、误差分析和技术报告。

当前阶段不包含：

- 购买任何设备；
- 采集本人或他人的新数据；
- 医疗诊断、风险评分或治疗建议；
- 用 LLM 替代 waveform processing、peak detection、sleep staging 或统计计算；
- 用跨受试者公开数据宣称已验证“个人基线建模”；
- 把算法输出或专家 annotation 称为无误差的 ground truth。

### 1.3 核心产出

强制产出为：

1. `analysis_plan.md`：分析前冻结研究问题、数据子集、排除规则、指标、统计方法和成功标准；
2. `data_manifest.csv`：记录数据集名称、版本、DOI、许可、访问日期、文件范围和 checksum；
3. 一个可从命令行运行的 Fantasia ECG/HRV pipeline；
4. 一组 detector error、artifact injection 和 HRV sensitivity 结果；
5. 自动化测试、固定 split/seed 和锁定依赖环境；
6. `reports/hrv_core_report.md` 与可重建 figures；
7. 一份阶段决策记录，说明继续睡眠扩展、停止或转向的依据。

### 1.4 成功标准

项目核心阶段只有在以下条件全部满足时才算通过：

- 对 Fantasia 全部 40 个记录完成可重复读取和 metadata 校验；
- 使用官方 beat annotation 评估至少一个 R-peak detector，并报告逐记录 sensitivity、positive predictive value、F1 和 timing error；
- 明确区分 RR interval 与清洗后的 NN interval，并保留所有排除与修正规则；
- 完成至少四类可控 artifact injection，并量化其对 RMSSD、SDNN、pNN50、LF、HF 的偏差；
- 频域分析明确处理非均匀采样，并至少比较一种插值后 PSD 方法与 Lomb–Scargle sensitivity analysis；
- 所有结果按受试者/记录报告，并给出 uncertainty，而不是只给 pooled point estimate；
- 从全新环境运行一个命令即可生成核心表格、图和报告数据；
- 报告中没有诊断性或未经支持的生理因果表述。

Sleep-EDF 和 wearable proxy 均为扩展产出，不影响核心阶段是否成功。

## 2. 背景与依据

### 2.1 证据标记

本文使用以下标记区分信息状态：

- **[资料支持]**：由官方数据页、官方文档、同行评议论文或监管机构资料直接支持；
- **[合理推断]**：基于项目规模、工程经验或方法学原则作出的设计选择，不代表行业统一标准；
- **[待确认]**：开始实施前仍需由用户、团队、数据提供方或机构确认。

### 2.2 数据集适用性

| 数据集 | 资料支持的事实 | 在本项目中的用途 | 关键限制 |
|---|---|---|---|
| **Fantasia Database v1.0.0** | 40 名严格筛选的健康受试者，20 名年轻、20 名老年；仰卧静息 120 min；ECG/respiration 250 Hz；beat annotation 经自动检测后人工复核；Open Data Commons Attribution License [资料支持] | 核心 ECG loader、R-peak benchmark、短时 HRV、artifact sensitivity | 单次实验室静息记录，不是 morning protocol、ambulatory monitoring 或 longitudinal baseline 数据 |
| **Sleep-EDF Expanded v1.0.0** | 197 个 PSG 记录；含 Fpz-Cz/Pz-Oz EEG、EOG、chin EMG 和 hypnogram；annotation 按 1968 R&K 规则人工评分；SC 与 ST 来自不同 protocol；8.1 GB；开放许可 [资料支持] | PSG/EEG 外部评估扩展 | R&K 不是当前 AASM stage schema；SC/ST 人群与场景不同；annotation 有 scorer uncertainty；通道并非 YASA 首选 central derivation |
| **RR interval time series from healthy subjects v1.0.0** | 147 人中 71 人不足一岁，只有 10 人超过 18 岁；artifact segment 已删除，删除前后不连续片段被直接拼接 [资料支持] | 可选的长序列 nonlinear 方法练习 | 不适合验证 artifact detector/correction，也不能代表一般成年人的个人基线；无 raw ECG |
| **BiD Sleep v1.0.0** | 47 名健康成人、253 夜；Apple Watch instantaneous HR 与 accelerometry；Dreem 2 EEG 标签经一名 expert 复核；Dreem 2 不是 full PSG；27.9 GB；开放许可 [资料支持] | wearable proxy 扩展的首选开放数据 | 单一 expert、无 inter-scorer adjudication；HR 约 0.2 Hz 且不规则采样；结论只适用于该设备、样本和 reference |
| **DREAMT v2.2.0** | 100 名 sleep-lab 参与者；Empatica E4 BVP/ACC/EDA/TEMP 及 PSG labels/signals；研究人群以 sleep-disorder lab 为背景；数据有重采样版本；需注册并签署 DUA，受 Restricted Health Data License 约束 [资料支持] | wearable + PSG domain-shift 扩展 | 不是零摩擦开放数据；不能把 resampled signal 当作 native sampling；许可、安全和禁止重识别义务必须优先于工程便利 |

### 2.3 方法学依据

**睡眠标签不是无误差真值。** Sleep-EDF 的 hypnogram 是人工 R&K scoring；不同 scorer 之间存在可观差异，尤其是 N1 和 transition epochs。因此文档统一使用“reference annotation/label”，不使用绝对化的“ground truth”。[资料支持]

**R&K 与 AASM 必须显式映射。** Sleep-EDF 的 stage 3 和 stage 4 在五分类 benchmark 中应预先合并为 N3，Movement 与 unscored 应排除或单独标记；mapping 必须写入配置并单元测试。[资料支持]

**YASA 不能套用通用预滤波。** YASA `SleepStaging` 文档明确要求在运行前不要自行 z-score 或 filter，并推荐 central EEG derivation；Sleep-EDF 的 Fpz-Cz/Pz-Oz 与其首选通道存在 domain/channel mismatch。因此 staging、spectral analysis 和 event detection 必须使用独立 preprocessing branch。[资料支持]

**HRV 依赖 protocol 与 preprocessing。** recording duration、posture、respiration、stationarity、beat classification 和 artifact correction 都会影响结果。LF/HF 不应被解释为简单的 sympathetic/parasympathetic balance；本项目把 LF/HF ratio 降为 secondary descriptive metric。[资料支持]

**模型评估必须按 participant 分组。** 多夜或多 epoch 数据若随机按 epoch 切分，会让同一参与者进入 train/test 两侧；所有 normalization、feature selection、class weighting 和 hyperparameter tuning 也必须只在 training fold 内拟合。[资料支持]

**软件接口会变化。** YASA 0.7.0 引入新的 `Hypnogram` API 并要求 Python 3.10+；MNE 当前也要求 Python 3.10+。项目必须使用 lockfile、版本报告和 regression tests，而不是只写包名。[资料支持]

## 3. 修订后的完整方案

### 3.1 研究问题与范围冻结

核心阶段只回答三个方法问题：

1. **R-peak detector 的漏检、误检与 timing error 会怎样传播到 RR/NN 和 HRV？**
2. **不同 artifact 类型、比例与 correction strategy 会怎样改变 HRV 估计？**
3. **在固定静息数据上，不同 window length 和 PSD implementation 的结果有多稳定？**

以下问题明确留到后续：个人 baseline、疾病检测、stress inference、睡眠质量诊断、设备准确率排名和设备购买决策。

### 3.2 项目结构与工程基线

建议 repo：

```text
physio-signal-public-data-lab/
  README.md
  LICENSE
  CITATION.cff
  pyproject.toml
  uv.lock
  analysis_plan.md
  data_manifest.csv
  .gitignore
  configs/
    hrv_core.yaml
    sleep_edf.yaml
    proxy_sleep.yaml
  data/
    README.md
    raw/                 # 不进 git
    interim/             # 不进 git
    fixtures/            # 仅合成或许可允许的小样本
  src/physio_signal_lab/
    io/
    preprocessing/
    features/
    evaluation/
    plots/
    cli.py
  notebooks/             # 仅探索，不承载最终 pipeline
  tests/
    test_data_contracts.py
    test_peak_matching.py
    test_rr_metrics.py
    test_epoch_alignment.py
    test_group_splits.py
  results/               # machine-readable outputs
  figures/
  reports/
```

工程规则：

- **[合理推断]** 统一使用 Python 3.11、`pyproject.toml` 与 `uv.lock`；不要同时维护 `environment.yml` 和另一套依赖源；
- 记录 `python --version`、`uv lock`、`pip/uv` 环境信息以及 `mne.sys_info()`；
- 每次运行保存 config、Git commit、dataset version、随机种子和 split index；
- 公开 repo 不包含 raw data、restricted data、凭据或可逆个人标识；
- CI 只运行 synthetic/tiny fixtures，不下载完整数据；
- 所有 notebook 中稳定逻辑在第一次复用时移入 `src/`。

### 3.3 Phase 0：分析前冻结（1–2 个 focused session）

建立 `analysis_plan.md`，至少冻结：

- 数据集与版本：Fantasia v1.0.0；
- 样本：最终分析使用全部 40 个 records；pilot 只用 `f1y01` 与 `f1o01`；
- 术语：所有相邻 R peak 间隔称 RR；排除非正常 beat 与 invalid interval 后称 NN；PP/IBI 只在未来 PPG/wearable 分支使用；
- R-peak matching：**[合理推断]** primary tolerance 50 ms，同时报告 100 ms sensitivity analysis；此处是项目参数，不宣称为统一标准；
- HRV window：固定非重叠 5 min windows；window selection 不按结果好坏事后挑选；
- primary metrics：MeanNN、SDNN、RMSSD、pNN50、LF、HF；
- secondary metrics：LF/HF、SD1、SD2；
- exploratory metrics：sample entropy、DFA；不进入核心通过条件；
- artifact 类型、注入率、重复次数和 correction methods；
- exclusion rule、missingness rule、statistical summary 和 figure list；
- 不做临床阈值、组间因果推断或个体健康解释。

建立 `data_manifest.csv`，字段至少为：

```text
dataset, version, doi, license, access_date, source_url,
record_id, local_path, sha256, included, exclusion_reason
```

### 3.4 Phase 1：Fantasia 数据接入与完整性检查（2–3 sessions）

1. 用 WFDB 读取 waveform、header、respiration 和 `.ecg` annotation；
2. 对 pilot records 检查 sampling rate、channel order、duration、units、annotation symbol 和起止时间；
3. 与官方 `SHA256SUMS.txt` 或本地 manifest 比对 checksum；
4. 生成 data contract tests：40 个 record 均可读取、250 Hz、期望时长范围、annotation 单调递增；
5. 输出 `results/data_quality/fantasia_inventory.csv`；
6. 人工抽查年轻组和老年组各至少两个 waveform/annotation overlay。

**验收：** 全部记录可读取；任何偏离均在 manifest 中记录，不静默修复。

### 3.5 Phase 2：R-peak detection benchmark（3–4 sessions）

1. 将官方人工复核 beat annotation 作为 reference annotation，而非绝对真值；
2. 运行一个固定的 primary detector，例如 NeuroKit2 `ecg_peaks`；可再加入一个 detector 作为 robustness check，但不是强制项；
3. 使用 one-to-one temporal matching，分别在 50 ms 和 100 ms tolerance 下计算：
   - sensitivity/recall；
   - positive predictive value/precision；
   - F1；
   - matched timing error 的 median、IQR 和 tail quantiles；
4. 按 record 输出，不只汇总全部 beats；
5. 对性能最差的 5 个 segments 画 ECG + reference + detected peaks，并建立 failure taxonomy：baseline drift、low amplitude、noise、double detection、missed peak 等；
6. 不在最终 test records 上反复调 detector threshold。若确需调参，先固定 training/validation records，再对其余 records 做一次 final evaluation。

**验收：** 生成 `peak_benchmark_by_record.csv`、aggregate uncertainty 与至少 5 个 failure plots。

### 3.6 Phase 3：RR/NN 构造与 artifact experiment（3–4 sessions）

#### 3.6.1 Reference NN series

- 先审查 annotation symbols，再明确哪些 beat 可进入 NN；
- 保存 raw RR、beat type、exclusion flag、correction flag 和 provenance；
- 不把“删除异常值后的 RR”自动命名为 NN，只有规则明确且可审计时才使用 NN；
- 每个 5 min window 报告总 beats、excluded beats、corrected beats 和有效比例。

#### 3.6.2 可控 artifact injection

从 reference series 复制出 corrupted series，至少注入：

1. missed beat；
2. spurious extra beat；
3. timestamp jitter；
4. ectopic-like short–long interval pair。

**[合理推断]** 注入比例使用 0.1%、0.5%、1% 和 3%，每个 record、artifact 类型与比例重复 20 次并固定随机种子。该设计用于绘制 error-response curve，不代表真实设备 artifact prevalence。

比较至少三种策略：

- no correction；
- deletion with explicit gap handling；
- interpolation/correction algorithm（记录实现和参数）。

评估目标是相对于未扰动 reference 的 metric bias，而不是仅比较“清洗后曲线是否更平滑”。输出 absolute error、relative error、failure rate 和 correction-induced bias。

**验收：** 每类 artifact 均有可复现实验；correction 不得使用未来信息而未披露；结果按 metric 和 artifact type 分层。

### 3.7 Phase 4：HRV 指标、频域与 uncertainty（3–4 sessions）

#### 3.7.1 Time domain

计算 MeanNN、SDNN、RMSSD、pNN50。用手算小序列和独立实现做 unit test，设置数值 tolerance。

#### 3.7.2 Frequency domain

Primary implementation：

1. 将 NN tachogram 按真实 cumulative time 定位；
2. 以 4 Hz 插值到均匀时间轴；
3. 使用 Welch PSD；
4. 积分 LF 0.04–0.15 Hz、HF 0.15–0.40 Hz；
5. 同时估计 respiration rate，并检查 respiratory peak 是否落在 canonical HF band；
6. 报告 absolute LF/HF power，LF/HF ratio 仅作为 secondary descriptive output。

Sensitivity implementation：直接对不均匀 NN time series 使用 Lomb–Scargle，并比较 LF/HF power 的方法差异。

禁止：对 RR 序号直接做 naive FFT；把 LF/HF 解释为单一 autonomic balance；在没有 respiration/context 时给出生理因果结论。

#### 3.7.3 Nonlinear metrics

Poincaré SD1/SD2 可进入 secondary analysis。Sample entropy 和 DFA 只在较长、连续且参数冻结的 segment 上做 exploratory analysis；必须记录 embedding dimension、tolerance、scale range、segment length，并做参数 sensitivity。[合理推断]

#### 3.7.4 Statistical summary

- primary unit 是 record/participant，而不是 beat 或 window；
- 报告每个 record 分布、median/IQR；
- **[合理推断]** 用 participant-level bootstrap 生成 95% confidence interval；
- young vs old 只作为预先声明的 exploratory descriptive comparison，不声称 age 的因果效应；
- artifact experiment 报告 bias curve 与 correction ranking 的 uncertainty。

**验收：** 所有核心指标有公式测试、per-record 输出、方法 sensitivity 和 uncertainty。

### 3.8 Phase 5：复现、报告与核心 Gate（2–3 sessions）

建立统一命令，例如：

```bash
uv sync --frozen
python -m physio_signal_lab.cli fetch-fantasia
python -m physio_signal_lab.cli run-hrv-core --config configs/hrv_core.yaml
python -m physio_signal_lab.cli build-report hrv-core
pytest -q
```

`reports/hrv_core_report.md` 必须包含：

1. question 与 scope；
2. dataset/protocol/许可；
3. annotation 和术语定义；
4. preprocessing flowchart；
5. peak benchmark；
6. RR/NN 与 artifact experiment；
7. HRV implementation 与 sensitivity；
8. uncertainty；
9. failure cases；
10. limitations；
11. reproducibility instructions；
12. 后续方向 decision record。

核心 Gate 通过条件：

| 条件 | 验收方式 |
|---|---|
| 数据与许可可追溯 | `data_manifest.csv` 完整，DOI/version/license/access date 可查 |
| 计算正确 | unit tests + synthetic checks + independent library cross-check |
| detector 被真实 annotation 评估 | per-record benchmark 与 failure plots |
| artifact 影响被量化 | 四类 artifact、四档比例、固定 seed/repeats |
| 频域处理合理 | cumulative-time axis、Welch 与 Lomb sensitivity |
| 结果可复现 | clean environment 一条命令重建核心 outputs |
| 解释不过界 | 无医疗诊断、无 LF/HF 简化叙述、无个人基线结论 |

若核心 Gate 未通过，停止扩展，不购买设备，也不开始个人数据采集。

### 3.9 可选扩展 A：Sleep-EDF / YASA 外部评估

只有核心 Gate 通过后进入。

#### 数据与 cohort

- 先只使用 **Sleep Cassette (SC)** healthy cohort，不与 Sleep Telemetry (ST) 混合；
- pilot：2 名参与者各 1 夜；
- benchmark：**[合理推断]** 预先按 subject ID 选择 20 名参与者，每人第一晚可用记录；selection list 写入 config；
- 后续如研究 domain shift，再单独分析 ST，并明确 hospital、mild sleep-onset difficulty 与 temazepam/placebo protocol。

#### Label mapping

```text
W -> WAKE
1 -> N1
2 -> N2
3, 4 -> N3
R -> REM
M, ? -> excluded / unscored
```

mapping、epoch count 和 start-time alignment 必须单元测试。主分析使用全部 valid scored epochs；另做一个预先定义的 sleep-period sensitivity analysis，避免 wake-heavy 记录主导 accuracy。[合理推断]

#### 三条独立 preprocessing branch

1. **Staging branch**：直接按 YASA 文档要求输入，不预先 z-score 或 filter；记录 YASA version、model 和 metadata；
2. **Spectral branch**：明确 filter、window、overlap、PSD 和 band definitions；
3. **Event branch**：spindle/slow-wave detection 使用各自 frequency/threshold；不得沿用一个通用 0.5–30 Hz pipeline。

Sleep-EDF 的 Fpz-Cz/Pz-Oz 不是 YASA 首选 central derivation，必须把 channel mismatch 列入 limitation，不得针对同一 benchmark test set 反复调参。

#### 评估

- baseline：majority-stage predictor；
- model：YASA pretrained classifier；
- metrics：macro-F1、balanced accuracy、Cohen’s kappa、per-stage precision/recall/F1；
- 结果：per-subject distribution 与 participant-level bootstrap CI；
- error review：至少 20 个低置信度或错误 epochs，重点看 N1、N2/N3 与 transitions；
- reference label 使用“manual R&K-derived reference”，不写 clinical truth。

#### Event detection 边界

Sleep-EDF 没有 spindle/slow-wave event-level expert annotation。因此 YASA event detections 只能作为 exploratory visualization/summary，不能据此声称 detector accuracy。若目标变成 detector validation，需另选具有 event annotations 的数据集并重新做许可和 protocol 审查。

#### 扩展 A 验收

- label mapping 与 alignment tests 通过；
- 20 participant benchmark 可一键复现；
- 包含 baseline、uncertainty、channel mismatch 和 scorer uncertainty；
- event detection 没有越界 accuracy claim。

### 3.10 可选扩展 B：wearable proxy benchmark

只有核心 Gate 通过且确实需要理解 peripheral proxy modelling 时进入。

#### B1：BiD Sleep 优先

- 先下载 5 名参与者作 pilot，避免直接承担 27.9 GB 全量成本；
- final split 按 participant，所有同一人的 nights 必须处于同一 fold；
- normalization、imputation、feature selection 和 tuning 只在 training fold 内拟合；
- 若 tuning 超过固定少量参数，采用 grouped nested CV；
- primary reference 使用 expert-corrected Dreem 2 labels，但明确 Dreem 2 不是 full PSG，且只有一名 scorer。

模型顺序：

1. majority baseline；
2. time-of-night baseline；
3. HR-only；
4. accelerometry-only；
5. HR + accelerometry；
6. binary sleep/wake；
7. 3-class Wake/NREM/REM；
8. 5-stage 仅在前述任务稳定后尝试。

报告 macro-F1、balanced accuracy、per-stage recall、per-participant distribution 和 calibration。禁止把结果描述为 wearable 的“物理上限”；它只是特定 cohort、device、reference 和 pipeline 下的 empirical benchmark。

#### B2：DREAMT 作为 restricted/domain-shift 扩展

进入条件：

- PhysioNet 注册和 DUA 已批准；
- 数据存储位置、访问控制和备份符合 license/DUA；
- 不尝试重识别，不共享 access，不把 restricted data 发给第三方 LLM；
- 明确 E4 native rates 与 64/100 Hz resampled products 的区别；
- 把 sleep-lab/OSA-rich cohort 当作独立 domain，不与健康成人数据无条件合并。

无法取得 DREAMT 权限时，跳过，不影响项目成功。

### 3.11 时间、资源与责任分工

#### 时间安排

以下为 **[合理推断]** 的 focused-work 估计，不是承诺工期：

| 阶段 | Sessions | 估计 focused hours | 核心输出 |
|---|---:|---:|---|
| Phase 0：冻结方案与环境 | 1–2 | 2–4 h | analysis plan、lockfile、manifest schema |
| Phase 1：数据接入 | 2–3 | 4–6 h | loader、inventory、data tests |
| Phase 2：peak benchmark | 3–4 | 6–8 h | metrics、failure taxonomy |
| Phase 3：artifact experiment | 3–4 | 6–8 h | corruption/correction results |
| Phase 4：HRV 与 uncertainty | 3–4 | 6–8 h | tables、figures、sensitivity |
| Phase 5：复现与报告 | 2–3 | 4–6 h | final report、CLI、tests |
| **核心合计** | **14–20** | **28–40 h** | 完整 HRV core |
| 可选 Sleep-EDF | 8–14 | 20–30 h | external benchmark |
| 可选 wearable proxy | 10–18 | 25–45 h | grouped benchmark |

不再使用“14 个自然日同时完成两条主线”的硬排期。建议以 3–5 周、每次 90–150 min 的 focused session 完成核心阶段。

#### 资源与成本

- 软件与核心开放数据费用：£0，不含既有电脑、电力和网络；
- **[合理推断]** 核心 Fantasia 工作空间预留 5 GB；Sleep-EDF subset 预留 15 GB；BiD pilot/full 分别预留约 10/35 GB；
- CPU 即可完成核心分析；无需 GPU；
- 16 GB RAM 通常足够处理按 record 流式读取的核心任务，[合理推断]；
- 不使用付费 cloud compute 作为默认路径；
- restricted data 的实际存储成本与机构要求在授权后再确认。[待确认]

#### 责任分工

| 角色 | 责任 | 默认负责人 |
|---|---|---|
| Project owner | scope、analysis plan、code、报告与 Gate 决策 | Yikuan |
| Data steward | license/DUA、manifest、存储、访问控制、删除策略 | Yikuan；若进入机构项目则由机构确认 |
| Methods reviewer | 检查 peak matching、HRV、sleep mapping、leakage 与 claims | 可选独立同学/研究人员；若无则执行 formal self-review checklist |
| Automation | unit tests、CI、rebuild、checksum | GitHub Actions 或本地 CI |

### 3.12 Fallback plan

| 触发条件 | Fallback | 不允许的做法 |
|---|---|---|
| Fantasia loader 或 annotation 解析失败超过一个 session | 固定两个 pilot records，写最小 parser/test，再扩到全量 | 换数据集逃避根因且不记录 |
| Detector 表现差 | 保留失败结果，先完成 reference-annotation HRV；把 detector improvement 设为独立任务 | 在全量 test set 上不断调参直到分数好看 |
| Artifact correction 没有统一赢家 | 按 metric/artifact type 报告 trade-off | 只选视觉最平滑的方法 |
| 频域方法差异大 | 将 Welch/Lomb 差异设为主结果，检查 interpolation、detrending、window | 静默挑一个更符合预期的方法 |
| 核心工作超过 40 focused hours | 冻结 nonlinear metrics 和 age comparison，只保留必选任务 | 同时开启 Sleep-EDF 与 wearable proxy |
| YASA 无法处理 channel/domain mismatch | 只做 spectral/hypnogram 分析，或把 staging 结果作为失败 benchmark | 在同一 20 人 benchmark 上反复调模型 |
| DREAMT 权限未获批 | 使用 BiD Sleep 或跳过 proxy 扩展 | 绕过 DUA 或使用非授权副本 |
| 数据/模型结论不稳定 | 报告 uncertainty 和不可识别范围，停止向设备/个人采集推进 | 将不稳定结果包装成健康洞察 |

### 3.13 设备与个人数据：仅作为后续可能方向

设备或个人数据只有在以下条件同时满足后才进入新的独立方案：

1. 核心公开数据 pipeline 已通过 Gate；
2. 已写出一个可证伪、可测量的具体问题；
3. 已明确需要 ECG、EEG、PPG、accelerometry 或 temperature 中哪一种原始信号；
4. 已定义 sampling、protocol、reference、missingness、artifact 和 stop rule；
5. 已核查当时的设备 raw-data access、API、许可、订阅和退货政策；
6. 已预算佩戴依从性、维护、充电、存储和数据出口成本；
7. 不以设备 app score 作为算法 truth；
8. 不以自采数据进行自我诊断。

若未来只采本人数据，仍应采用 data minimisation、本地加密、retention/deletion policy 和不向未经审查的 cloud/LLM 上传 raw waveform。若招募他人、代表机构研究或计划发表，必须在采集前确认 ethics、consent、data-controller、UK GDPR lawful basis 与 special-category condition；不能把 pseudonymisation 当作 anonymisation。[资料支持/待确认]

### 3.14 LLM 使用边界

当前项目中 LLM 只能接收：

- 已聚合且不含 restricted row-level information 的 tables；
- method/config 摘要；
- failure taxonomy；
- figure captions 和报告草稿。

LLM 不接收：

- DREAMT 等 restricted raw/row-level data；
- 未来个人 raw waveform、时间戳或生活事件明细；
- access token、credential、未公开 metadata；
- 要求其输出诊断或替代 deterministic calculation 的任务。

所有 LLM 生成内容必须由可复现计算结果支持，并进行人工 claim review。

### 3.15 维护机制

- 每个阶段完成后打 versioned release tag，并归档 config、environment、manifest 和 report；
- 每三个月或开始新阶段前检查 dataset version、license、YASA/MNE/NeuroKit API 与 security advisories；
- 不自动升级 major dependency；升级后先跑 regression tests；
- 保留一套 synthetic fixtures，确保未来版本仍能验证公式、alignment、split 和 peak matching；
- 若数据许可变化，停止分发受影响的 derived artifact，重新审查 repo；
- 设备/API 信息只在真正进入设备阶段时重新搜索，不在本方案中冻结多年后可能失效的采购事实。

## 4. 风险与缓解措施

| 风险 | 触发条件 | 影响 | 缓解措施 |
|---|---|---|---|
| Scope creep | 核心完成前增加 EEG、deep learning、设备或个人采集 | 项目长期无交付 | 一条强制核心线；扩展受 Gate 控制 |
| Annotation 被当作真值 | 报告使用 “ground truth” 且不提 scorer uncertainty | 夸大模型错误或准确性 | 统一改称 reference；报告 inter-scorer 背景与 ambiguity |
| R&K/AASM 标签错配 | 直接把 stage 3/4 当不同 AASM classes | 指标和 hypnogram 错误 | versioned mapping；3/4→N3；M/? 排除；单元测试 |
| SC/ST cohort 混杂 | 未分层混合健康 home recordings 与 hospital/drug study | domain effect 被误读 | Sleep-EDF MVP 只用 SC；ST 独立扩展 |
| Data leakage | 同一 subject 多夜或 epochs 分到 train/test | 过度乐观 performance | GroupKFold/StratifiedGroupKFold；split test；train-only transforms |
| Test-set tuning | 反复根据 final benchmark 修改 threshold/model | evaluation bias | 预先冻结参数；必要时 nested/grouped validation |
| Artifact correction circularity | 用清洗结果本身证明清洗正确 | 无法判断真实 bias | 从 reference series 注入已知 corruption；比较到未扰动 target |
| HRV 指标误读 | LF/HF 被解释成 autonomic balance；忽略 respiration/posture | 生理结论错误 | LF/HF secondary；记录 respiration、protocol、window 与 caveat |
| Nonlinear metrics 不稳定 | 短 segment 上报告 SampEn/DFA | 参数依赖、不可重复 | 移至 exploratory；冻结参数和最短长度；sensitivity analysis |
| 软件版本漂移 | YASA/MNE API 升级导致结果变化 | 无法重建旧结果 | lockfile、version report、regression tests、release artifacts |
| Restricted data 违规 | 未签 DUA、共享 access、上传第三方服务 | 合规与访问风险 | DREAMT 非核心；独立存储；按 license/DUA；禁止云端 LLM |
| 隐私误判 | 未来把 pseudonymised personal health data 当匿名数据 | UK GDPR/伦理风险 | data minimisation；法律/机构复核；不招募他人直到审批完成 |
| Storage/compute 超预算 | 直接下载 BiD/Sleep-EDF 全量或多份缓存 | 磁盘与维护成本 | pilot subset、streaming、单一 raw copy、manifest/checksum |
| 医疗化与自我焦虑 | 将 statistical fluctuation 转为健康判断 | 错误行动或 orthosomnia | 无诊断语言；停止规则；需要医疗判断时转向专业人员 |
| 无独立审阅 | 单人项目遗漏 mapping、leakage 或 claim error | 方法错误未发现 | formal checklist；关键报告争取一名 reviewer；公开 reproducible code |

## 5. 待确认事项

1. **[待确认]** 项目首要用途：研究训练、portfolio、科普素材、方法学报告，还是未来论文前期；用途会改变文档深度和 reviewer 标准。
2. **[待确认]** repo 是否公开。若公开，需要选择代码 license，并逐项确认 derived outputs 是否可再分发。
3. **[待确认]** 每周可投入的 focused hours；若少于 6 h/week，应进一步减少 optional figures 和 detector comparison。
4. **[待确认]** 本地操作系统、可用 RAM/磁盘和是否使用 GitHub Actions；据此锁定 environment 与 CI。
5. **[待确认]** 是否有一名懂 ECG/HRV 或 sleep scoring 的 reviewer；没有时使用 formal self-review，但不能把它等同独立审查。
6. **[待确认]** 是否申请 DREAMT。若申请，需要确认培训、DUA、存储和第三方处理限制的最新要求。
7. **[待确认]** Sleep-EDF benchmark 的 20 名 participant selection rule；必须在查看模型结果前固定。
8. **[待确认]** R-peak matching 的 50 ms primary tolerance 是否与拟使用 detector benchmark 文献一致；若更改，必须在 final evaluation 前冻结。
9. **[待确认]** 是否将 age-group comparison 保留为 secondary descriptive analysis；若时间有限应删除。
10. **[待确认]** 未来个人数据是否仅为私人 self-tracking，还是可能成为机构研究/公开成果；后者需要在采集前走 ethics/data-protection review。
11. **[待确认]** 实施当天重新核查 YASA、MNE、NeuroKit2、scikit-learn 和 WFDB 的稳定版本与 breaking changes。

## 6. 参考资料

以下均为本次修订实际使用的来源；访问日期为 2026-06-21。

1. PhysioNet. **Fantasia Database v1.0.0**. https://physionet.org/content/fantasia/1.0.0/
2. PhysioNet. **Sleep-EDF Database Expanded v1.0.0**. https://physionet.org/content/sleep-edfx/1.0.0/
3. Moser D, et al. **Sleep classification according to AASM and Rechtschaffen & Kales: effects on sleep scoring parameters**. *Sleep* (2009). https://pmc.ncbi.nlm.nih.gov/articles/PMC2635577/
4. Lee YJ, et al. **Interrater reliability of sleep stage scoring: a meta-analysis**. *J Clin Sleep Med* (2022). https://pmc.ncbi.nlm.nih.gov/articles/PMC8807917/
5. Rosenberg RS, Van Hout S. **The AASM Inter-scorer Reliability Program: sleep stage scoring**. *J Clin Sleep Med* (2013). https://pmc.ncbi.nlm.nih.gov/articles/PMC3525994/
6. YASA. **SleepStaging documentation, v0.7.0**. https://yasa-sleep.org/generated/yasa.SleepStaging.html
7. YASA. **Changelog, v0.7.0**. https://yasa-sleep.org/changelog.html
8. YASA. **Spindle detection documentation**. https://yasa-sleep.org/generated/yasa.spindles_detect.html
9. YASA. **Slow-wave detection documentation**. https://yasa-sleep.org/generated/yasa.sw_detect.html
10. MNE-Python. **Installation and environment documentation**. https://mne.tools/stable/install/manual_install.html
11. PhysioNet. **RR interval time series from healthy subjects v1.0.0**. https://physionet.org/content/rr-interval-healthy-subjects/1.0.0/
12. Task Force of ESC/NASPE. **Heart rate variability: standards of measurement, physiological interpretation and clinical use**. *Circulation* (1996). https://pubmed.ncbi.nlm.nih.gov/8598068/
13. Billman GE. **The LF/HF ratio does not accurately measure cardiac sympatho-vagal balance**. *Front Physiol* (2013). https://pubmed.ncbi.nlm.nih.gov/23431279/
14. Bourdillon N, et al. **RMSSD Is More Sensitive to Artifacts Than Frequency-Domain Parameters**. *Front Physiol* (2022). https://pmc.ncbi.nlm.nih.gov/articles/PMC9157524/
15. Quigley KS, et al. **Publication guidelines for human heart rate and heart rate variability studies** (2024). https://pmc.ncbi.nlm.nih.gov/articles/PMC11539922/
16. Damoun N, et al. **Heart rate variability measurement and influencing factors** (2024). https://pmc.ncbi.nlm.nih.gov/articles/PMC11439429/
17. NeuroKit2. **HRV documentation**. https://neuropsychology.github.io/NeuroKit/functions/hrv.html
18. WFDB Python. **I/O documentation**. https://wfdb.readthedocs.io/en/latest/io.html
19. PhysioNet. **BiD Sleep dataset v1.0.0**. https://physionet.org/content/bidsleep-dataset/1.0.0/
20. PhysioNet. **DREAMT dataset v2.2.0**. https://physionet.org/content/dreamt/2.2.0/
21. PhysioNet. **Restricted Health Data License 1.5.0**. https://physionet.org/about/licenses/physionet-restricted-health-data-license-150/
22. scikit-learn. **GroupKFold**. https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html
23. scikit-learn. **StratifiedGroupKFold**. https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html
24. scikit-learn. **Nested versus non-nested cross-validation**. https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html
25. UK Information Commissioner’s Office. **What is personal data?** https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/personal-information-what-is-it/what-is-personal-data/what-is-personal-data/
26. UK Information Commissioner’s Office. **Pseudonymisation**. https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-sharing/anonymisation/pseudonymisation/
27. UK Information Commissioner’s Office. **Data minimisation**. https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/
