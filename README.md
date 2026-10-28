# knowhow-miner: Industrial Manufacturing Know-how Mining & Causal Pipeline

[English](#english) | [中文说明](#中文说明)

[![License: PolyForm Noncommercial](https://img.shields.io/badge/License-PolyForm%20Noncommercial-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

<a name="english"></a>
## English

### Overview & Author Background
**knowhow-miner** is an engineering-first knowledge extraction and causal graph reconstruction pipeline tailored for semiconductor and Flat Panel Display (FPD/Array) manufacturing. 

The system architecture is inspired by frontline engineering experiences as a **Photolithography (Yellow Beam / Photo Track) Engineer** in high-volume FPD fabs. It bridges the critical "cognitive divide" between design centers (CAD/EDA layout) and the physical shop floor (wafer/glass fabrication), transforming thousands of multi-department engineering emails, shift handovers, and 8D reports into structured **Recipe Tuning Offsets** and **Design-for-Manufacturing (DFM) Redline Rules**.

> **License Notice**: This project is licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE). It is strictly free for academic research, education, and personal study. **Commercial use, unauthorized resale, or integration into proprietary enterprise offerings without a commercial license is strictly prohibited.**

### Core Architecture
<p align="center">
  <img src="assets/architecture.svg" alt="knowhow-miner Core Architecture" width="100%"/>
</p>
<p align="center"><em>Interactive standalone HTML version available at <a href="assets/architecture.html">assets/architecture.html</a>.</em></p>

### Module Structure
- `miner/cleaner.py`: Text sanitization, legal notice purging, PII redaction, entity extraction.
- `miner/classifier.py`: Operational intent classification (`ALARM`, `DISPUTE`, `DOE_EXPERIMENT`, `REPORT_8D`, `SHIFT_HANDOVER`) and administrative noise filtration.
- `miner/annotator.py`: Multi-dimensional domain tagging across Technology (LTPS/a-Si/LTPO), Stations (Photo/Track/DET/WET/PVD/CVD/PI), Layers (M1/M2/ITO1/ITO2/ILD/PV), and Defect categories.
- `miner/aggregator.py`: DAG conversation tree recovery, BCC thread reconciliation, and incident lifecycle tracking.
- `miner/parsers/`: Deep inspection for binary attachments:
  - `ppt_parser.py`: Extracts slide texts, tables, and 5-Why comparisons from `.pptx` and legacy `.ppt` OLE streams.
  - `excel_parser.py`: Parses DOE Split Tables, identifying POR baselines vs experimental trial conditions.
- `miner/causal_extractor.py`: Distills structured causal quintets, recipe offsets, and DFM redline rules.
- `miner/validator.py`: Physics boundary verification and dual-reality decoupling (8D public defense vs physical ground truth).
- `miner/graph_builder.py`: Constructs the domain knowledge graph and exports interactive dark-themed HTML diagrams (Vis.js network).
- `miner/mock_generator.py`: Generates realistic mock incident datasets.
- `miner/pipeline.py`: End-to-end batch processing pipeline orchestrator.

### Privacy & Data Safety
**This public repository contains ZERO proprietary corporate emails or confidential fab records.** 
To test the pipeline out-of-the-box, an automated synthetic data generator is bundled.

### Quick Start with Mock Data
```bash
# 1. Generate synthetic anonymized manufacturing records (mimics M2 corrosion & ITO CD drift)
python3 -m miner.mock_generator

# 2. Run the extraction pipeline on mock data
python3 -m miner.pipeline --db mock_emails.db --keyword "M2" --output mock_m2_incidents.json
```

### How to Connect Your Own Private Data (e.g., in InstaBox or Local Sandbox)
If you are evaluating this engine on your own internal fab communications (such as in an ephemeral InstaBox or private on-prem server):
1. **Prepare your local SQLite index**:
   Create a local SQLite database containing an `emails` table with standard schema:
   `source_folder`, `seq_num`, `message_id`, `date_str`, `from_addr`, `to_addr`, `subject`, `body_preview`, `attachment_names`, `mbox_chunk`.
2. **Mount Cold Storage**:
   Mount your offline archive (MBOX/EML files) to a private path (e.g., `~/gdrive/archive/` or local SSD).
3. **Run Pipeline**:
   ```bash
   python3 -m miner.pipeline --db /path/to/private_index.db --keyword "ITO2" --limit 1000 --output private_incidents.json
   ```
4. **Data Isolation Guarantee**:
   All intermediate files and outputs under `data/`, `*.db`, and `*.mbox` are strictly ignored by `.gitignore`. Nothing will be leaked to git.

---

<a name="中文说明"></a>
## 中文说明

### 项目背景与作者介绍
**knowhow-miner** 是面向微纳半导体与平板显示（FPD/Array）制造的底层知识挖掘与因果图谱重构管线。

该系统的架构灵感与底层规则源于作者在大型显示面板工厂（FPD Fab）担任**黄光光刻（Photolithography / Photo Track）工程师**的一线实战经验。旨在打破设计端（EDA/版图）与制造车间（Fab 现场）之间的“认知鸿沟”，将工厂一线数万封跨部门往来邮件、异常复盘报告（8D/PPT）及分件实验表（Split Table）提纯为可直接防呆的**设计图纸红线（DFM Rules）**与**工艺参数调优账本（Recipe Offsets）**。

> **开源许可证与商用限制**：本项目遵循 [PolyForm Noncommercial License 1.0.0](LICENSE)。**仅限学术交流、个人学习与非商业研究，严禁任何形式的商业转售、商用系统打包或企业收费服务。**

### 核心架构图解（Architecture Diagram）
<p align="center">
  <img src="assets/architecture.svg" alt="knowhow-miner 核心架构图" width="100%"/>
</p>
<p align="center"><em>可在浏览器中直接打开独立交互式版本：<a href="assets/architecture.html">assets/architecture.html</a></em></p>

### 完整模块结构与职责
- `miner/cleaner.py`: 邮件正文清洗、法律免责声明剥离、个人隐私脱敏（PII Anonymization）与制造实体正则提取（Lot ID、Chamber 腔室、Defect Code、产品代号）。
- `miner/classifier.py`: 邮件运维意图分类器，精准识别 `ALARM`（报警）、`DISPUTE`（跨部门争议）、`DOE_EXPERIMENT`（实验分件）、`REPORT_8D`（结案报告）、`SHIFT_HANDOVER`（交接班），并自动过滤行政水邮件（订餐、调休、会议催办）。
- `miner/annotator.py`: 多维度制造特征标注器，自动打标技术路线（LTPS/a-Si/LTPO）、涉及工序（Photo/Track/DET/WET/PVD/CVD/PI）、工艺膜层（M1/M2/ITO1/ITO2/ILD/PV）及缺陷特征。
- `miner/aggregator.py`: 基于 DAG 的多轮工程会话树聚合器，解决跨文件夹密送 BCC 归集与时间窗口聚类，还原事件完整生命周期（报警 $\rightarrow$ 争议 $\rightarrow$ DOE探针 $\rightarrow$ 结案Release）。
- `miner/parsers/`: 二进制重型附件深度提取器：
  - `ppt_parser.py`: 自动穿透解构 `.pptx` 与旧版 `.ppt` OLE 二进制流，打捞 5-Why 分析表、因果对比图文本。
  - `excel_parser.py`: 自动识别并解析分件实验表（Split Table），结构化区分标准 POR 组与实验条件组。
- `miner/causal_extractor.py`: 五元组因果事实抽取器，提纯不良表象、推诿争端、实证探针、物理真因、治本措施与派生的 DFM 设计红线规则。
- `miner/validator.py`: 物理与工程逻辑守门员，内置曝光能量、焦深、温度等机台物理硬门禁，并实现**“对外客户防御免责话术（如偶发颗粒）”与“对内物理真实根因（如材质腐蚀、DRC公差断裂）”的双轨解耦**。
- `miner/graph_builder.py`: 工业制造因果知识图谱引擎，自动构建拓扑网络并导出交互式深色主题 HTML 动态图表（Vis.js 驱动，支持缩放、拖拽与节点点击查看完整机理）。
- `miner/mock_generator.py`: 合成数据生成器，供外部开发者快速体验管线逻辑。
- `miner/pipeline.py`: 端到端批量提炼执行入口。

### 隐私与安全隔离承诺
**本开源代码库绝不包含任何工厂真实邮件、商业机密或未脱敏数据。** 
`.gitignore` 已全局拉黑所有 `data/`、`*.db`、`*.mbox`、`*.ppt`、`*.eml` 等数据文件。

### 快速开始（使用模拟数据）
```bash
# 1. 生成高仿真工艺异常模拟数据库（包含 M2 铝腐蚀与 ITO2 CD 漂移经典案例）
python3 -m miner.mock_generator

# 2. 执行端到端事件时间轴提取
python3 -m miner.pipeline --db mock_emails.db --keyword "M2" --output mock_m2_incidents.json
```

### 如何在私有环境（如 InstaBox 容器或内网服务器）加载真实邮件
如果你需要在独立隔离沙箱（如 InstaBox 用完即弃环境）或企业内网对真实数据进行 PoC 演示：
1. **建立索引表**：将企业邮件元数据导入 SQLite（参考 `miner/mock_generator.py` 中的表结构）；
2. **挂载归档卷**：将包含大附件与原始邮件的存储卷挂载至本地（如 `~/archive/`）；
3. **指向私有库运行**：
   ```bash
   python3 -m miner.pipeline --db /path/to/my_private_index.db --keyword "铝腐" --output data/al_corrosion.json
   ```
4. **安全隔离**：所有输入数据均在本地沙箱内存计算，不会向外部上传任何原始文本。
