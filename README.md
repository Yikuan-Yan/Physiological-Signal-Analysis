# Physio Signal Lab

面向公开生理信号数据的可审计分析工具包：覆盖 ECG/HRV method validation、Sleep-EDF sleep staging evaluation，以及 MIT-BIH PSG respiratory/SpO₂ educational analysis。

> **项目边界**：这是 research/education prototype，不是 clinical decision-support software。当前归档不含 `data/raw/`，仓库中的 CSV、图和报告属于 tracked artifacts，不能视为本次从原始波形独立重算的结果。

## 项目目标

本仓库试图把公开 physiological signal analysis 组织成可追踪、可检查的 workflow，而不只提供零散 notebook：

- 用 YAML 固定 dataset selection、algorithm parameters 与 output paths；
- 用 manifest 记录 source URL、local path、SHA-256 和 inclusion status；
- 通过 CLI 运行 validation、benchmark、feature extraction、reporting 与 release；
- 保存机器可读 CSV、解释性 figures 和 Markdown reports；
- 用 tests 覆盖核心数值逻辑、数据契约与 release behavior。

## 核心功能

| Pipeline | 数据集 | 已实现功能 | 当前范围 |
| --- | --- | --- | --- |
| ECG / HRV | [Fantasia Database](https://physionet.org/content/fantasia/1.0.0/) | ECG inventory、NeuroKit2 R-peak benchmark、RR/NN filtering、time/frequency-domain HRV、artifact sensitivity、record-level bootstrap uncertainty、gated report | 40 records |
| Sleep staging | [Sleep-EDF Expanded](https://physionet.org/content/sleep-edfx/1.0.0/) | R&K→5-stage mapping、global-majority baseline、YASA staging、per-stage metrics、sleep-quality proxies、discrepancy reports | Sleep Cassette subjects 400–419 的 first available night，共 20 records |
| Respiratory / SpO₂ | [MIT-BIH Polysomnographic Database](https://physionet.org/content/slpdb/1.0.0/) | `.st` annotation parsing、AHI-style burden、source-AHI alignment、SpO₂/ODI proxy、event windows、dataset-readiness gate | 全部 18 records；5 records 有 oxygen channel |

### 重要方法边界

- HRV downstream metrics 使用 **reference annotations** 构造 RR/NN；NeuroKit2 detected peaks 只进入 detector benchmark，detector error 尚未传播到 HRV outputs。
- Sleep baseline 的 majority stage 从同一 evaluation truth 得到，属于 descriptive target-aware baseline，不是可部署模型。
- MIT-BIH 的 AHI-style burden 与 ODI proxy 未完成 clinical validation；仓库没有实现正式的完整 hypopnea scoring workflow。

## Tracked results 快照

下列数字直接读取自归档中的 tracked CSV，未在本次 no-raw 环境中从波形端重算。

| Track | Tracked snapshot | 证据 |
| --- | --- | --- |
| HRV | 50 ms tolerance 下 median F1 `0.999361`；285,494 reference intervals；977 个 300 s windows；38,400 个 artifact scenarios | `results/hrv/` |
| Sleep-EDF | 54,587 included epochs；YASA accuracy `0.823310`、balanced accuracy `0.721763`、macro-F1 `0.658405`、κ `0.675571` | `results/sleep_edf/twenty_record_*` |
| MIT-BIH PSG | 10,197 annotation epochs；3,162 sleep-only respiratory tokens；oxygen review 为 13 unavailable、3 artifact review、2 ready | `results/mit_bih_psg/all_record_*` |

详细结果、算法解释和评价见 [`WORK_GUIDE.md`](WORK_GUIDE.md)。

## 仓库结构

```text
configs/                         三条 pipeline 的 YAML 配置
  hrv/core.yaml
  sleep_edf/default.yaml
  mit_bih_psg/default.yaml

data/manifests/                  数据来源、local path、SHA-256 契约
docs/                            项目计划与结构说明
src/physio_signal_lab/           Python package 与 CLI
  cli.py                         17 个 CLI subcommands
  io/                            WFDB / EDF data access
  evaluation/                    peak matching、artifacts、sleep staging
  features/                      RR/NN、HRV、sleep features、uncertainty
  reporting.py                   HRV report gate
  release.py                     HRV release metadata bundle
  sleep_*.py                     Sleep-EDF workflows
  mit_bih_psg.py                 Respiratory/SpO₂ workflow

tests/                           11 个 test files
results/                         tracked CSV outputs
reports/                         tracked Markdown reports
figures/                         tracked figures
releases/hrv-core-v0.1.0/        已有 HRV provenance bundle
```

## 环境要求

[`pyproject.toml`](pyproject.toml) 声明：

- Python `>=3.11,<3.14`；
- core：NumPy、pandas、SciPy、Matplotlib、PyYAML、WFDB、NeuroKit2；
- sleep extra：MNE、scikit-learn、YASA；
- build backend：Hatchling；
- dependency lock：[`uv.lock`](uv.lock)。

完整 Sleep/YASA 流程建议使用 **Python 3.12**。`pyproject.toml` 对 YASA 设置了 Python `<3.13` 的 environment marker。

## 安装

推荐使用 [uv](https://docs.astral.sh/uv/concepts/projects/sync/) 和 lockfile：

```bash
uv sync --frozen --python 3.12 --extra dev --extra sleep
```

只运行 ECG/HRV：

```bash
uv sync --frozen --extra dev
```

基础 smoke check：

```bash
uv run python -m compileall -q src
uv run physio-signal-lab --help
uv run pytest -q
```

> 本次审计环境因无法解析 PyPI 域名，`uv sync --frozen --extra dev` 在下载 locked dependency 时中止；这不是 lockfile 本身错误的证据。当前环境缺少 WFDB、NeuroKit2 和 YASA，因此没有完成 full dependency/full-data rerun。

## 数据准备

原始数据被 `.gitignore` 排除，期望目录位于 `data/raw/`。请先阅读并核对：

- `data/manifests/fantasia.csv`
- `data/manifests/sleep_edf.csv`
- `data/manifests/mit_bih_psg.csv`

### Fantasia

仓库没有 Fantasia downloader。按 manifest 中的 `source_url` 和 `local_path` 从 [PhysioNet Fantasia](https://physionet.org/content/fantasia/1.0.0/) 恢复文件到：

```text
data/raw/fantasia/1.0.0/
```

随后验证：

```bash
uv run physio-signal-lab validate-data \
  --manifest data/manifests/fantasia.csv
```

### Sleep-EDF

```bash
uv run physio-signal-lab run-sleep-edf-preflight \
  --config configs/sleep_edf/default.yaml

uv run physio-signal-lab download-sleep-edf \
  --config configs/sleep_edf/default.yaml

uv run physio-signal-lab validate-sleep-edf \
  --config configs/sleep_edf/default.yaml
```

### MIT-BIH PSG

```bash
uv run physio-signal-lab download-mit-bih-psg \
  --config configs/mit_bih_psg/default.yaml

uv run physio-signal-lab validate-mit-bih-psg \
  --config configs/mit_bih_psg/default.yaml
```

Downloader 会为本地文件记录 SHA-256，但当前实现没有独立读取 upstream checksum manifest 进行首次下载交叉验证。

## 最小使用示例

在 Fantasia `f1y01` 文件已就位后，先运行单 record inventory，避免覆盖默认 full-run output：

```bash
uv run physio-signal-lab inventory-fantasia \
  --config configs/hrv/core.yaml \
  --records f1y01 \
  --out results/hrv/data_quality/smoke_f1y01.csv
```

完整 ECG/HRV pipeline：

```bash
uv run physio-signal-lab run-ecg-core \
  --config configs/hrv/core.yaml
```

Sleep-EDF two-record benchmark：

```bash
uv run physio-signal-lab run-sleep-edf-pilot-benchmark \
  --config configs/sleep_edf/default.yaml \
  --records SC4001,SC4011 \
  --output-prefix pilot \
  --include-yasa
```

MIT-BIH PSG 18-record analysis：

```bash
uv run physio-signal-lab run-mit-bih-psg-respiratory-pilot \
  --config configs/mit_bih_psg/default.yaml \
  --output-prefix all_record
```

## 当前状态

**完成度：research/education prototype，三条 pipeline 均有实际实现与 tracked artifacts；尚未达到 clean-checkout reproducible release。**

本次对上传归档的直接检查结果：

- `python -m compileall -q src`：通过；
- 原样 `pytest -q`：因当前环境未安装 `wfdb`，在 collection 阶段中止；
- 对不依赖缺失 I/O packages 的 tests：`63 passed, 1 failed`；
- 失败项为 `tests/test_reporting.py::test_build_hrv_core_report_contains_gate_and_limitations`：tracked CSV 存在，但 dynamic report 会重新校验缺失 raw files 并正确返回 gate failure，而 test 硬编码要求 pass；
- 当前 no-raw 归档验证结果：Fantasia 123 files missing、Sleep-EDF 40 files missing、MIT-BIH PSG 72 files missing。

仓库内 `reports/project/final_state_and_technical_review_response.md` 记录过 `70 passed`、full-data validation 通过及 commit `f971715`。由于上传归档没有 `.git/` 和 raw data，本次无法独立复核这些历史陈述。

### 已知主要缺口

- 没有 code License、CI workflow、coverage report、tiny integration fixtures 或 root-level release instructions；
- reporting test 依赖 checkout 外部 raw-data 状态，不是 hermetic test；
- output paths 缺少统一 run ID、atomic directory、schema version 和 stale-output detection；
- `mit_bih_psg.py` 与 `sleep_quality.py` 较大，混合 parsing、metrics、plotting、policy 和 reporting；
- HRV release bundle 主要是 provenance metadata，不包含完整 source/lock/results offline snapshot；
- clinical-style metrics 仍是 educational proxies，需要独立 scorer、formal protocol 和 external validation。

## References

- [Fantasia Database v1.0.0](https://physionet.org/content/fantasia/1.0.0/)
- [Sleep-EDF Database Expanded v1.0.0](https://physionet.org/content/sleep-edfx/1.0.0/)
- [MIT-BIH Polysomnographic Database v1.0.0](https://physionet.org/content/slpdb/1.0.0/)
- [WFDB Python documentation](https://wfdb-python.readthedocs.io/en/latest/)
- [NeuroKit2 ECG API](https://neuropsychology.github.io/NeuroKit/functions/ecg.html) and [paper](https://doi.org/10.3758/s13428-020-01516-y)
- [SciPy Welch PSD](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html) and [Lomb–Scargle](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lombscargle.html)
- [HRV Task Force standards](https://doi.org/10.1161/01.CIR.93.5.1043)
- [MNE `read_raw_edf`](https://mne.tools/stable/generated/mne.io.read_raw_edf.html)
- [YASA `SleepStaging`](https://yasa-sleep.org/generated/yasa.SleepStaging.html) and [paper](https://doi.org/10.7554/eLife.70092)
- [AASM hypopnea scoring rule discussion](https://doi.org/10.5664/jcsm.9952)
- Related tools: [pyHRV](https://github.com/PGomes92/pyhrv), [HeartPy](https://github.com/paulvangentcom/heartrate_analysis_python)

## Citation

Please cite this repository using [`CITATION.cff`](CITATION.cff), and cite the original public datasets and method libraries used in any derived analysis.

## License

Repository code and documentation are released under the [MIT License](LICENSE). Third-party datasets remain governed by their own PhysioNet terms and citations; raw data are not redistributed in this repository.
