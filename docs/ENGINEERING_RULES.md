# Frontline Industrial Engineering Rules & Causality Codebook
## 一线实战工业认知工程原则与因果准则表

> **Architecture Philosophy (架构哲学)**:  
> 工业智能算法与制造现场的规则绝不能使用扁平无序的数字流水号（如 1-N），否则数据管道工程、系统基建与现场物理机理一旦新增规则就会全盘冲突混乱。  
> 本代码本采用**领域前缀标识分类体系（Domain-Prefixed Rule Taxonomy）**：
> - **`RULE-ORG-*`**：组织阵眼、专家隐性心智与实体消歧（Organizational & Expert Tacit Grounding）
> - **`RULE-FLU-*`**：流体力学、狭缝涂布流变与气动风刀（Fluid Dynamics & Aerodynamics）
> - **`RULE-THM-*`**：热力学温场、退火相变与光学显相（Thermodynamics, Shrinkage & Optical Metrology）
> - **`RULE-MEC-*`**：机械撞击接触、潜伏暗伤与时空解耦（Mechanical Shock & Spatiotemporal Stress）
> - **`RULE-PAR-*`**：因果归因极简律、奥卡姆剃刀与状态机（Causal Attribution, Parsimony & State Machine）
> - **`RULE-ONT-*`**：工业本体工程与方法论隔离防御（Ontology Engineering & Methodology Air-Gap）

---

### Category Index (规则分类总览)

| 类别前缀 | 涵盖领域 | 核心目标 | 包含规则 |
| :--- | :--- | :--- | :--- |
| **`RULE-ORG`** | 组织与人员实体 | 抑制表面发信噪音，锁定真正技术决策阵眼，激活专家隐性心智 | ORG-01 至 ORG-05 |
| **`RULE-FLU`** | 流体力学与涂布 | 突破原厂保守间隙，解耦走线微观拦水坝，消除风刀气压与微腐蚀白条 | FLU-01 至 FLU-04 |
| **`RULE-THM`** | 热力学与光学相位 | 治理顶针局域微温差漏热，解耦退火体积收缩显影与目检防线后移 | THM-01 至 THM-03 |
| **`RULE-MEC`** | 机械暗伤与时空解耦 | 解耦常温机械受创与高温真空引爆粉碎，多重过机加权锁定真凶 | MEC-01 至 MEC-02 |
| **`RULE-PAR`** | 极简归因与奥卡姆剃刀 | 剥离管理汇报 4M 复合借口，四维反问倒查硬件状态机，单点物理破局 | PAR-01 至 PAR-04 |
| **`RULE-ONT`** | 本体落地与方法论隔离 | 关系表 3NF 范式化与 Auto-Ontology 语义对齐，开源母机与数据物理隔离 | ONT-01 至 ONT-02 |

---

### 1. 组织决策与专家心智 (RULE-ORG: Organizational & Expert Tacit Grounding)

#### `RULE-ORG-01`: Mentor Anchor vs Apprentice Noise Suppression (组织阵眼与新人噪声对冲法则)
- **Problem / 陷阱**: 新人工程师承担现场交接班、巡检与机械记录，表面发信量往往是资深老法师的 5~10 倍。通用统计算法若按“发信量（Count）”加权，会极其荒谬地把新人当成技术主导者，被大量事务性噪音淹没。
- **Methodology / 方法**:
  1. *新人事务性抑制（Apprentice Noise Suppression）*：对排班通知、日常值班日志等低技术参数密度的邮件执行权重抑制。
  2. *技术阵眼定锚（Mentor Anchor Tracking）*：技术 Ground Truth 必须坚决锚定在发信量少但字字千钧的资深主管与师傅（`David Chen` / `[MENTOR]`），其指令具有高密度物理参数（Slot、Recipe、Dose）与定案拍板特征。
  3. *见习期客观定位（Observer Archive）*：工程师在学徒期间仅作为抄送/记录者的历史语料，界定为“第三方见闻卷宗”，严禁过度脑补因果。

#### `RULE-ORG-02`: Bilingual Cadre Alias Resolution & Entity Disambiguation (中英文干部别名实体消歧法则)
- **Problem / 陷阱**: 半导体与高世代产线中，资深台籍/外籍干部常在正式会议纪要写中文名（如 `周清文`），在口头交代与邮件沟通中使用英文昵称（如 `Joe Chou`、`LMW`）。算法若缺乏别名映射，会撕裂为两个人，割断同一事件的因果链。
- **Methodology / 方法**:
  1. *署名与抄送映射矩阵*：穿透邮件签名档、抄送括号配对（`Name (English Alias)`）与内部通讯录，建立双向映射表。
  2. *底层统一 UUID*：在实体抽取前将中英文别名归一化至唯一的 `Engineer_UUID`，确保跨语言决策树完全闭环。

#### `RULE-ORG-03`: Seniority Baseline & Onboarding Anchor (入职基准时钟与成熟度推断双重定锚法则)
- **Problem / 陷阱**: 依靠代收邮件的最早时间判断入职会导致数月至数年的“代收配置延迟时钟误差”；且企业 HTML 签名模板内嵌的 `cid:...@DDMMYYYY-...` 仅代表企业 IT 统一更新模板时间，非个人入职时钟。
- **Methodology / 方法**:
  1. *业务成熟度反推*：第一天邮件即在下发光阻评估、拒绝高危膜厚者，必为成熟骨干而非新人。
  2. *工号序列批次交叉核验*：利用工号的年份编码规律（如 `F` + 年份代码 + 流水号）与全厂人员库对齐。
  3. *首封内部测试信定锚*：穿透检索发件人与收件人均为本人的第一封内部 `test` / `测试消息` 原始时间戳，物理锁定到岗第一天。

#### `RULE-ORG-04`: Expert Alignment & The 20/80 Rule of Tacit Know-How (专家对齐与隐性心智模型激活法则)
- **Problem / 陷阱**: 工厂历史记录（工单、邮件、PPT）中显性记录的仅占 20%（改了什么参数、换了什么零件）；真正高价值的 80%（为何这样改、机台机械干涉与系统权衡）沉睡在专家隐性心智模型（Mental Model）中。
- **Methodology / 方法**:
  1. *事实骨架拼装（Skeleton Extraction）*：算法从海量数据中理清时间线、机台号与参数变动。
  2. *交互式矛盾追问（Dialogue Probing）*：主动向专家抛出逻辑冲突点（如“为何只有特定点位加温？”、“为何特定机型才暴雷？”）。
  3. *隐性因果激活*：由专家一句话揭示深层物理约束，完成从参数记录到 DFM 设计红线的升华。

#### `RULE-ORG-05`: The Primacy of Human Tacit Knowledge in Know-How Mining (专家心智价值第一性法则)
- **Problem / 陷阱**: 迷信纯算法无监督挖掘能自动从海量文字中“领悟”高阶制造机理。
- **Methodology / 方法**:
  1. *切片 vs 合成器*：文字永远只是现场动作的碎片；串联前道形貌、本道流变与后道量测的因果网络来自于人类专家的心智结构。
  2. *人机协同边界*：算法是高精度过滤探针，人类专家是物理因果的终极裁决者与知识结晶的源泉。

---

### 2. 流体力学与涂布风刀 (RULE-FLU: Fluid Dynamics & Aerodynamics)

#### `RULE-FLU-01`: Equipment Physical Boundary Probing & Boundary Tuning (倒逼设备物理极限与原厂安全边界探针法则)
- **Problem / 陷阱**: 设备原厂（TEL、DNS、Nikon 等）出于质保免责给出的常规工艺窗口极其保守（如涂布 Gap 160~180μm、速度 50~80mm/s）。在高粘度特种厚有机膜工艺中，照搬原厂窗口会遭遇整面破膜与严重不良。
- **Methodology / 方法**:
  1. *倒逼原厂绝对机械底线*：抛开均匀性考量，直接逼问原厂硬件不发生物理撞刀的极限间隙（如 60μm）。
  2. *建立现场安全试验带*：在绝对底线上方设定极低参数带（如 Gap 130~140μm、速度 20~35mm/s）。
  3. *毛细弯月面稳定机理*：极端压低狭缝间隙极大增强液桥毛细吸附力，彻底消灭拉丝气泡与破膜。

#### `RULE-FLU-02`: Fluid Anisotropy vs DFM Topological Alignment (流体各向异性与 DFM 走线拓扑反推法则)
- **Problem / 陷阱**: 相同 Panel 版图在不同排版方向上涂布特种平坦化有机膜（PLN）时，良率出现灾难性分化。
- **Methodology / 方法**:
  1. *微观拦水坝效应*：涂布前进方向垂直于微观密集金属走线（Data/Gate）时，万道台阶引发接触线钉扎与背向空化脱气，形成鱼鳞状破膜（Poor Coating）。
  2. *毛细导流槽效应*：涂布前进方向与密集走线平行时，走线间隙变成微观毛细导流槽，流平平整顺滑。
  3. *DFM 规则固化*：底层台阶 > 0.8μm 且要求 PLN ≤ 2.3μm 时，强制要求主密集走线必须与涂布方向平行，禁止大板拼版 90° 旋转混排。

#### `RULE-FLU-03`: Longitudinal Stripe Mura: Slit Coater Falsehood vs Develop Air Dry Knife Truth (显影风刀气动湍流与微腐蚀白条机理)
- **Problem / 陷阱**: 面板出现纵向条纹斑纹（Suji Mura / 白条）时，传统直觉习惯性怀疑涂布机刀头（Nozzle）堵塞或抖动，陷入漫长 4M 排查。
- **Methodology / 方法**:
  1. *风刀近距离湍流压差机理*：显影后段水洗风刀（RAK）距基板过近（如 10mm），高速气流直吹形成剧烈局部湍流压差，吹出条纹。对策：高度提升至 15mm 消除剧烈湍流，风量由 780 降至 380 L/min 并加装均压管。
  2. *TMAH 烘烤浓缩微腐蚀机理*：显影后段 CDA 风刀流量不足，残留微液滴中含微量 TMAH 碱液；在后烘烤急剧脱水浓缩，微溶有机光阻表面形成白条 Mura。对策：风刀流量由 1200 提升至 1650 L/min 彻底切断水膜。

#### `RULE-FLU-04`: Coating Standby Drying & Hardware Root Cause Protocol (狭缝涂布停机防干槽与树脂刮刀根治规范)
- **Problem / 陷阱**: 狭缝涂布条纹反复爆发，现场频繁做临时后烘补偿与简单擦拭，治标不治本。
- **Methodology / 方法**:
  1. *防干槽液位死锁*：重新标定待机溶剂浸润液位与刀唇悬置距离，严防洁净室微风导致局部干胶结皮。
  2. *树脂刮片资质化*：严禁用金属/硬质刮刀损伤刀唇，全面替换为特种树脂刮刀并由资深技术员标准手法擦拭。
  3. *供胶管路老化淘汰*：氟树脂输胶软管受溶剂长期浸泡内壁脱皮（Peeling）会产生批量内源颗粒，设立硬性寿命淘汰制。

---

### 3. 热力学、相变与光学显像 (RULE-THM: Thermodynamics, Shrinkage & Metrology)

#### `RULE-THM-01`: Lift Pin Thermal Sink, Local CD Shrinkage & Dark Cluster Mitigation (顶针局域微温差诱发 CD 收缩与宏观暗团闭环法则)
- **Problem / 陷阱**: 440+ PPI 超高密度面板点亮时在固定几何点位出现发暗黑团（Dark Cluster Mura），但宏观膜厚量测正常。
- **Methodology / 方法**:
  1. *顶针局域热沉*：预烘热板（Hot Plate）合金顶针在接触基板时形成局部导热漏热。
  2. *微观 CD 收缩*：微温差导致溶剂挥发差与感光度微漂，接触孔/电极 CD 偏小 0.2μm。
  3. *光学显示放大*：高 PPI 下微米级收缩导致低灰阶驱动电场严重不足，液晶偏转不够宏观呈现黑团。
  4. *三位一体对策*：更换陶瓷低导热顶针 + 热板对应温区（Zone 11）微升温 1~2°C 补偿 + 跨机台 Recipe 强制同步。

#### `RULE-THM-02`: Thermal Manifestation & Post-Anneal Inspection Realignment (高分子薄膜退火显像与宏观目检防线后移法则)
- **Problem / 陷阱**: 在光刻显影后（PHT）进行宏观目检（MAC）显示全良，但在后道却爆发大面积严重 Suji Mura。
- **Methodology / 方法**:
  1. *溶剂掩盖假象*：未退火湿膜含 15%~25% 溶剂，微观厚度差的光学相位差极微弱，肉眼不可见。
  2. *退火体积收缩显像*：230°C 退火坚膜（ANN）使树脂剧烈交联收缩 20%~30%，微观厚度差被几何放大数十倍，条纹剧烈显现。
  3. *关卡后移与阶梯放行*：严禁在未相变的中间态设卡，将 MAC 目检强制后移至退火（ANN）后；复机执行 Slot 1/15/30 抽检阶梯放行。

#### `RULE-THM-03`: Organic Planarization Film Spec Rationalization (高分子有机平坦化层规格解耦与极限减薄准则)
- **Problem / 陷阱**: 拿无机薄膜的均一性指标（`U% ≤ 5%`）苛求 2~3μm 厚有机膜（PLN），引发产线常态化假报警。
- **Methodology / 方法**:
  1. *规格物理合理化*：受流变学挥发制约，量产基准合理界定为 `7%~8%`。
  2. *三维工程治理*：
     - 前道：通过 DFM 哑元线填充削减微观台阶段差；
     - 本道：优化升温阶梯防止表面结皮（Skin Effect）引发火山口；
     - 量测：坐标与 CAD 叠图避开微观台阶边缘，采用退火态真实动态折射率拟合。

---

### 4. 机械应力与时空解耦 (RULE-MEC: Mechanical Shock & Spatiotemporal Stress)

#### `RULE-MEC-01`: Latent Damage Mechanics & Multi-Pass Exposure Model (暗伤潜伏与多重循环累积暴露因果模型)
- **Problem / 陷阱**: 基板在后道高温真空腔室（如 CVD 300°C+）粉碎性炸裂，MES 路径分析将所有后道机台列为嫌疑犯，排查瘫痪。
- **Methodology / 方法**:
  1. *时空解耦*：前道常温湿法机构（对辊、顶针、机械手）撞击在倒角植入微裂纹（Micro-crack），常温下漏检潜伏；后道急热真空将热应力集中在裂纹尖端引发粉碎。
  2. *多重循环累积加权*：逆向统计破片在全生命周期经历各前道设备的累积次数（Total Pass Count），通过过机风险比（Multi-pass Risk Ratio）锁定真正始发暗伤机台。

#### `RULE-MEC-02`: Substrate Breakage & Double Roller Impact Chipping (微观暗伤与湿法对辊机械接触应力溯源法则)
- **Problem / 陷阱**: 全线突发固定坐标倒角微缺损（如 4mm x 26mm bevel chipping）。
- **Methodology / 方法**:
  1. *四道关卡截流*：在成膜与刻蚀前后设置高倍显微镜/白光抽检，区间收敛始发工序。
  2. *对辊卡滞定位*：剥膜清洗机上下驱动对辊（Double Roller）受药液结晶浸润导致上辊导轨阻尼卡滞失去浮动柔性，在玻璃切入时产生硬撞击。清除结晶并调校边缘轴肩间隙。

---

### 5. 极简归因与奥卡姆剃刀 (RULE-PAR: Causal Attribution, Parsimony & State Machine)

#### `RULE-PAR-01`: Occam's Razor & Singular Physical Trigger vs 4M Management Narratives (奥卡姆剃刀与极简归因法则)
- **Problem / 陷阱**: 沉迷于管理汇报 PPT 中的“人机料法环（4M1E）复合借口”，掩盖真实物理机制。
- **Methodology / 方法**:
  1. *现场物理的一元性*：成熟机台突然暴雷必是单一的局部物理突变（Single Physical Trigger），绝非十几个微弱因素同时共振。
  2. *二元排查支路*：
     - *支路一（观测条件位移）*：瑕疵一直存在，因目检关卡后移到相变区而被突然放大显形；
     - *支路二（单点边界击穿）*：单一硬件或材料边界被破坏（如刀唇局部干胶、密封圈磨损）。

#### `RULE-PAR-02`: Anti-Over-Retrieval & Mismatched Station Conflation (严防跨工序强行拼装的因果污染法则)
- **Problem / 陷阱**: 大模型和通用检索为了宏大叙事，把同时期发生的减压干燥（DP）开度实验强行拼凑进厚有机膜（PLN）退火烘箱问题中。
- **Methodology / 方法**:
  1. *严守物理站点与工序边界*：无机光阻减压干燥与有机膜退火温场物理不相干，严禁跨工序串联。
  2. *克制归因（Attribution Parsimony）*：锁定直接因果闭环，剔除并发无关工作。

#### `RULE-PAR-03`: IS/IS-NOT Differential & Tool State Machine Auditing (控制变量对比法与设备硬件状态机穿透归因法则)
- **Problem / 陷阱**: 出现 1.0μm 级尺寸断崖时盲目微调下游温度或曝光量，引发次生报废。
- **Methodology / 方法**:
  1. *倒查 30 天状态机*：断崖突变必是硬件变动，强查前置 30 天是否有 Nozzle 更换、传动轴拆装或机械零点漂移。
  2. *四维对比（IS / IS-NOT）*：空间（Zone 11 vs 其它）、机型（超高 PPI vs 老品）、机台（100# vs 600#）、衬底（刚性玻璃 vs 柔性 PI）。
  3. *孤岛配方审查*：硬件大修后主量产品复机正常，独立私有配方仍停留在旧零点引发首跑暴雷。

#### `RULE-PAR-04`: Inspection Gating vs Physical Root Cause Elimination (防守截流 vs 进攻根治：条纹缺陷前后端解耦法则)
- **Problem / 陷阱**: 把“目检站点后移并拦截不良”当成了质量事故的终局解决方案。
- **Methodology / 方法**:
  1. *前后端解耦*：后道设卡是防守止血（缩短检出时间），前端涂布/显影才是进攻根治。
  2. *分类建库*：防守动作用于 SPC 监控与出货阻断，根治动作用于 Recipe 固化与设备改良。

---

### 6. 本体工程与方法论隔离 (RULE-ONT: Ontology Engineering & Methodology Air-Gap)

#### `RULE-ONT-01`: Two-Stage Relational Grounding for Enterprise Auto-Ontology (NVIDIA Auto-Ontology 两阶段范式化落地准则)
- **Problem / 陷阱**: 扁平向量 RAG 无法区分 0.8μm 与 1.5μm，且无法回答确切参数改变量。
- **Methodology / 方法**:
  1. *第一阶段（关系范式化）*：自动提纯为 3NF 关系表（`dim_equipment`、`dim_process_layer`、`dim_defect_type`、`fact_defect_incident`、`fact_root_cause_action`），明确参数量纲与前后数值。
  2. *第二阶段（Auto-Ontology 语义对齐）*：注册认证 Term 与同义词阵列（`Air Knife`、`Suji Mura`），由 Auto-Ontology 编译执行确定性 Text-to-SQL。

#### `RULE-ONT-02`: Methodology Engine vs Domain Knowledge Store Air-Gap (方法论母机与私有知识库解耦隔离准则)
- **Problem / 陷阱**: 因担心商业机密泄露，把通用算法框架与测试工具也锁在本地不敢更新。
- **Methodology / 方法**:
  1. *开源仓（`knowhow-miner`）*：纯粹沉淀通用提取管线、奥卡姆剃刀校验算法、通用 DDL 与合成基准用例，定期敏捷演进。
  2. *私有知识库*：真实工厂邮件、具体设备代号与量产配方通过 `.gitignore` 严密锁在本地隔离存储，零机密上云。
