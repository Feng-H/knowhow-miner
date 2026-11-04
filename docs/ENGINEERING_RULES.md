# Frontline Industrial Engineering Rules & Causality Codebook
## 一线实战工业认知工程原则与因果准则表

> **Scope**: Standard methodology rules for industrial tacit knowledge extraction, causal disambiguation, and DFM rule derivation in `knowhow-miner`.  
> **Governance**: Enforces synthetic personas (`David Chen` / `陈大卫`, `Alex Wang` / `王亚历`, `[MENTOR]`) and capability-based domain designations (`Fab-G6`, `Fab-G8.5`, `MedTech-MEMS`). Completely isolated from proprietary fab records.

---

### Table of Contents (目录)

1. [Rule 41: Mentor Anchor vs Apprentice Noise Suppression (组织阵眼与新人噪声对冲法则)](#rule-41)
2. [Rule 43: Bilingual Cadre Alias Resolution & Entity Disambiguation (中英文干部别名实体消歧法则)](#rule-43)
3. [Rule 44: Seniority & Baseline Onboarding Anchor (入职基准时钟与成熟度推断双重定锚法则)](#rule-44)
4. [Rule 45: Equipment Physical Boundary Probing & Boundary Tuning (倒逼设备物理极限与原厂安全边界探针法则)](#rule-45)
5. [Rule 46: Fluid Anisotropy vs DFM Topological Alignment (流体各向异性与 DFM 走线拓扑反推法则)](#rule-46)
6. [Rule 47: Thermal Sink, Local CD Shrinkage & Dark Cluster Mitigation (顶针局域热沉微温差诱发关键尺寸收缩与宏观暗团闭环法则)](#rule-47)
7. [Rule 48: Expert Alignment & The 20/80 Rule of Tacit Know-How (专家对齐与隐性心智模型激活法则)](#rule-48)
8. [Rule 50: IS/IS-NOT Differential & Tool State Machine Auditing (控制变量对比法与设备硬件状态机穿透归因法则)](#rule-50)
9. [Rule 51: Organic Film Spec Rationalization & Thinning Pitfalls (高分子有机膜极限减薄与量化规格解耦准则)](#rule-51)
10. [Rule 52: Anti-Over-Retrieval & Attribution Parsimony (严防过度检索与强行拼装的因果污染法则)](#rule-52)
11. [Rule 53: The Primacy of Human Tacit Knowledge in Know-How Mining (专家心智价值第一性法则)](#rule-53)
12. [Rule 54: Latent Damage Mechanics & Multi-Pass Exposure Model (暗伤潜伏与多重循环累积暴露因果模型)](#rule-54)
13. [Rule 55: Substrate Breakage & Double Roller Impact Chipping (微观暗伤与对辊机械接触应力溯源法则)](#rule-55)
14. [Rule 56: Thermal Manifestation & Post-Anneal Inspection Realignment (高分子薄膜退火显像与宏观目检防线后移法则)](#rule-56)
15. [Rule 57: Inspection Gating vs Physical Root Cause Elimination (防守截流 vs 进攻根治：条纹缺陷前后端解耦法则)](#rule-57)
16. [Rule 58: Occam's Razor & Singular Physical Trigger vs 4M Management Narratives (奥卡姆剃刀与极简归因法则)](#rule-58)
17. [Rule 59: Longitudinal Stripe Mura: Slit Coater Falsehood vs Develop Air Dry Knife Physical Truth (显影风刀机理与条纹真因甄别准则)](#rule-59)
18. [Rule 60: Two-Stage Relational Grounding for Enterprise Auto-Ontology (NVIDIA Auto-Ontology 语义图谱与确定性推理范式)](#rule-60)
19. [Rule 61: Methodology Engine vs Domain Knowledge Store (方法论母机与领域私有知识库解耦隔离准则)](#rule-61)

---

<a id="rule-41"></a>
### Rule 41: Mentor Anchor vs Apprentice Noise Suppression (组织阵眼与新人噪声对冲法则)

- **Problem / 陷阱**: In early factory communication archives, junior engineers handle daily routine shifts, logging, and transactional handovers. Surface email metrics show apprentices having 5x to 10x higher volume than senior experts. Blind algorithmic count-based attribution erroneously assigns technical authority to junior loggers.
- **Methodology / 方法**:
  1. *Apprentice Noise Suppression*: Downweight repetitive shift handovers and transactional logs containing low technical parameter density.
  2. *Mentor Anchor Tracking*: Anchor technical ground truth to senior master engineers (`[MENTOR]` / `David Chen`). While their message frequency is low, their directives contain high-density parameters, recipe locks, and signed approval attachments.
  3. *Observer Archive Labeling*: Classify archives where the engineer was merely observing/learning as secondary contextual evidence rather than primary causal ground truth.

---

<a id="rule-43"></a>
### Rule 43: Bilingual Cadre Alias Resolution & Entity Disambiguation (中英文干部别名实体消歧法则)

- **Problem / 陷阱**: In semiconductor and advanced display fabs, senior expatriate and regional technical directors frequently alternate between English aliases (e.g. `Joe Chou`, `LMW`) and full Chinese names in official minutes. Naive extraction treats them as separate entities, tearing apart causal discussion threads.
- **Methodology / 方法**:
  1. *Cross-Language Signature Mapping*: Parse email sign-offs, CC bracket pairs (`Name (English Alias)`), and mobile directories to construct a deterministic alias mapping table.
  2. *Unified Identity UUID*: Resolve all mentions to a canonical `Engineer_UUID` across both languages before constructing thread DAGs and decision trees.

---

<a id="rule-44"></a>
### Rule 44: Seniority & Baseline Onboarding Anchor (入职基准时钟与成熟度推断双重定锚法则)

- **Problem / 陷阱**: Relying naively on the earliest date of a forwarded email archive creates artificial onboarding lag (mail sync was often configured months after actual factory deployment). Furthermore, HTML signature template creation timestamps (`cid:...@DDMMYYYY-...`) reflect IT department template releases, not individual start dates.
- **Methodology / 方法**:
  1. *Functional Maturity Heuristics*: Check early activity: an engineer challenging NPI recipe margins on day one was already a seasoned practitioner.
  2. *Badge Serialization (Cohort Analysis)*: Cross-verify corporate badge patterns (e.g., `F` + year prefix + batch number) against company-wide hiring announcements.
  3. *Self-Sent Test Email Mining*: Locate the initial inner RFC822 `test` message sent by the engineer to themselves immediately upon IT mailbox setup for deterministic day-zero physical anchoring.

---

<a id="rule-45"></a>
### Rule 45: Equipment Physical Boundary Probing & Boundary Tuning (倒逼设备物理极限与原厂安全边界探针法则)

- **Problem / 陷阱**: Equipment vendors (TEL, DNS, Nikon) specify conservative operational envelopes (e.g., Slit Coater Gap 160–180μm, speed 50–80mm/s). For specialized high-viscosity thick organic films, conventional parameters fail completely, producing severe poor coating and striations.
- **Methodology / 方法**:
  1. *OEM Safety Boundary Inquiry*: Directly probe vendor design engineers for the absolute mechanical interference limit (e.g., minimum mechanical clearance 60μm without nozzle collision).
  2. *Safety Band DOE*: Establish an aggressive yet safe production band just above the hardware floor (e.g., 130–140μm gap, 20–35mm/s speed).
  3. *Fluid Meniscus Stabilization*: Lowering gap dramatically enhances capillary meniscus suction stability, eliminating air entrainment and coating breakage.

---

<a id="rule-46"></a>
### Rule 46: Fluid Anisotropy vs DFM Topological Alignment (流体各向异性与 DFM 走线拓扑反推法则)

- **Problem / 陷阱**: Identical panel schematics laid out in different panel orientations exhibit drastically different coating yields on thick organic planarization (PLN) layers.
- **Methodology / 方法**:
  1. *Microscopic Dam Effect*: When slit nozzle scan direction is perpendicular to dense metal traces (Data/Gate lines), the microscopic step heights act as fluid barriers, causing contact line pinning, cavitation, and fish-scale dewetting.
  2. *Capillary Channeling*: When scan direction is parallel to metal traces, trace spaces serve as micro-fluidic guide channels, ensuring smooth fluid leveling.
  3. *DFM Redline Formulation*: When underlying topography step height > 0.8μm and target PLN thickness ≤ 2.3μm, mandatory DFM CAD rule enforces principal dense metal routing parallel to coater scan direction. 90-degree rotated panel nesting is strictly forbidden.

---

<a id="rule-47"></a>
### Rule 47: Thermal Sink, Local CD Shrinkage & Dark Cluster Mitigation (顶针局域热沉微温差诱发关键尺寸收缩与宏观暗团闭环法则)

- **Problem / 陷阱**: Ultra-high PPI mobile panels (440+ PPI) display localized dark clusters (Dark Cluster Mura) at specific coordinates during optical test, while macro film thickness measurements show normal uniformity.
- **Methodology / 方法**:
  1. *Thermal Sinking Mechanism*: Hot plate lift pins made of conductive alloy create localized cold spots on the glass back during proximity pre-baking.
  2. *Photolithography CD Shrinkage*: Local temperature deficit reduces photoresist solvent evaporation and alters photospeed, causing sub-micron electrode shrinkage (e.g., contact hole CD narrows by 0.2μm).
  3. *Electro-Optical Transfer Deficit*: Under 64/128 grey levels, weakened drive electric fields fail to tilt liquid crystals sufficiently, manifesting as localized optical dark clusters.
  4. *Countermeasure Triad*:
     - Hardware: Low-thermal-conductivity ceramic pins with minimized contact area.
     - Multi-Zone Thermal Tuning: Fine-tune local hot plate heating zones (+1–2°C) matching lift pin coordinates.
     - Recipe Synchronization: Propagate verified recipes across all compatible inline tracks.

---

<a id="rule-48"></a>
### Rule 48: Expert Alignment & The 20/80 Rule of Tacit Know-How (专家对齐与隐性心智模型激活法则)

- **Problem / 陷阱**: Text logs, shift handovers, and tickets capture only ~20% of engineering reality (what was adjusted). The remaining 80% (why it was adjusted, underlying mechanical couplings, systemic constraints) resides in the unwritten mental models of frontline experts.
- **Methodology / 方法**:
  1. *Skeleton Extraction*: Pipeline assembles the structural timeline, machine IDs, and parameter deltas.
  2. *Interactive Dialogue Probing*: The miner actively formulates targeted technical contradictions to human experts (e.g., *"Why was Zone 11 specifically compensated while other pins were untouched?"*).
  3. *Tacit Knowledge Elicitation*: Expert response uncovers hidden physical boundary conditions, completing the jump from simple parameter logging to executable DFM rules.

---

<a id="rule-50"></a>
### Rule 50: IS/IS-NOT Differential & Tool State Machine Auditing (控制变量对比法与设备硬件状态机穿透归因法则)

- **Problem / 陷阱**: Faced with a catastrophic 1.0μm CD drop on a critical layer, engineers intuitively attempt downstream thermal or exposure compensation, triggering secondary yield fallout.
- **Methodology / 方法**:
  1. *Hardware State Machine Auditing*: A 1.0μm deviation cannot stem from minor thermal drift; it indicates a step-function hardware change. Mandate an audit of the preceding 30-day maintenance log (nozzle replacement, pump seal rebuild, mechanical zero shift).
  2. *IS/IS-NOT Matrix*:
     - *Location*: Zone 11 vs other zones (shutter leak thermal profile).
     - *Product*: 440+ PPI product vs legacy low-density panels (non-linear sensitivity threshold).
     - *Machine*: Line 100 vs Line 600 (recipe drift).
     - *Substrate*: Rigid glass vs flexible PI (carrier bow metrology artifact).
  3. *Island Recipe Auditing*: Verify whether new or low-volume recipes inherited baseline changes following major equipment overhauls.

---

<a id="rule-51"></a>
### Rule 51: Organic Film Spec Rationalization & Thinning Pitfalls (高分子有机膜极限减薄与量化规格解耦准则)

- **Problem / 陷阱**: Enforcing inorganic thin-film uniformity specifications (`U% ≤ 5%`) on thick organic planarization (PLN 2–3μm) layers causes persistent false alarms and needless line shutdowns.
- **Methodology / 方法**:
  1. *Spec Rationalization*: Fluid rheology of high-viscosity organic resin sets a physical limit of `U% ~ 7–8%` in high-volume manufacturing.
  2. *Three-Pronged Root Cause Framework*:
     - *Dimension 1 (Underlayer Topography)*: Smooth underlying metal density differences via dummy metal fills to eliminate resin sagging.
     - *Dimension 2 (Autonomous Leveling)*: Optimize pre-bake thermal ramp rates to prevent surface skinning before solvent evaporation.
     - *Dimension 3 (Metrology Baseline)*: Realign measurement beam coordinates to avoid macro-topography steps and calibrate optical n/k constants against fully cured films.

---

<a id="rule-52"></a>
### Rule 52: Anti-Over-Retrieval & Attribution Parsimony (严防过度检索与强行拼装的因果污染法则)

- **Problem / 陷阱**: Generic LLMs and vector RAG concatenate unrelated concurrent engineering events (e.g. connecting an unrelated vacuum dry test to an organic film baking issue) to craft elaborate synthetic 4M1E narratives.
- **Methodology / 方法**:
  1. *Strict Station & Layer Separation*: Causal links must not traverse mismatched physical stations (e.g. Track DP vacuum drying vs Anneal Oven baking) without direct evidence.
  2. *Attribution Parsimony (Occam's Razor)*: If a singular physical parameter change accounts for yield recovery, prune multi-factor composite hypotheses.

---

<a id="rule-53"></a>
### Rule 53: The Primacy of Human Tacit Knowledge in Know-How Mining (专家心智价值第一性法则)

- **Problem / 陷阱**: Believing that raw text corpora alone can automatically generate high-level physical models without expert intervention.
- **Methodology / 方法**:
  1. *Text Slices vs Mental Synthesizer*: Factory emails provide fragmented action slices. The overarching causal architecture is supplied by the human expert's internalized physical intuition.
  2. *Human-in-the-Loop Arbitration*: Algorithms act as clean data sifting probes; the domain expert remains the ultimate arbitrator of physical causality.

---

<a id="rule-54"></a>
### Rule 54: Latent Damage Mechanics & Multi-Pass Exposure Model (暗伤潜伏与多重循环累积暴露因果模型)

- **Problem / 陷阱**: When glass substrates break inside high-temperature vacuum chambers (e.g. CVD 300°C+), standard MES path analysis flags the chamber as the culprit, while inspection of the chamber reveals no mechanical anomalies.
- **Methodology / 方法**:
  1. *Spatiotemporal Decoupling*: Mechanical contact in upstream wet stations (double rollers, lifter pins, robot chucks) induces sub-surface micro-cracks invisible to standard optical break sensors.
  2. *Thermal Detonation*: Entering high-temperature vacuum concentrates thermal stress at crack tips, causing delayed catastrophic fracture.
  3. *Multi-Pass Weighted Analysis*: Correlate breakage rates against cumulative pass counts through upstream wet processing units rather than the terminal fracture station.

---

<a id="rule-55"></a>
### Rule 55: Substrate Breakage & Double Roller Impact Chipping (微观暗伤与对辊机械接触应力溯源法则)

- **Problem / 陷阱**: Mysterious corner chipping (e.g. 4mm x 26mm bevel damage) recurring across diverse downstream lots.
- **Methodology / 方法**:
  1. *Sequential Interception Protocol*: Establish microscopic inspection gates before and after key wet processing transitions.
  2. *Physical Source Pinpointing*: Inspect double rollers in wet strip/clean modules for chemical salt crystallization on upper-roller guide rails, causing roller dampening lockup and axial edge impact.

---

<a id="rule-56"></a>
### Rule 56: Thermal Manifestation & Post-Anneal Inspection Realignment (高分子薄膜退火显像与宏观目检防线后移法则)

- **Problem / 陷阱**: Conducting macro visual inspection (MAC) directly after photolithography development (PHT) gives a clean bill of health, yet severe suji mura (stripe mura) emerges downstream.
- **Methodology / 方法**:
  1. *Solvent Masking Effect*: Unbaked photoresist retains 15–25% solvent, dampening refractive index contrast across nanometer-scale thickness variations.
  2. *Thermal Anneal Shrinkage*: 230°C annealing induces 20–30% resin volume shrinkage, geometrically amplifying optical interference phase differences into visible stripes.
  3. *Gate Realignment*: Move macro inspection to post-annealing (ANN) gate. Implement dynamic staging (Slot 1 / Slot 15 / Slot 30 sampling) following maintenance overhauls.

---

<a id="rule-57"></a>
### Rule 57: Inspection Gating vs Physical Root Cause Elimination (防守截流 vs 进攻根治：条纹缺陷前后端解耦法则)

- **Problem / 陷阱**: Treating inspection relocation (MAC moved to post-ANN) as the permanent corrective action (PCA) for suji mura.
- **Methodology / 方法**:
  1. *Defense vs Offense Decoupling*: Inspection gating stops defect escape (Mean Time to Detect); true root cause elimination resides in upstream coating/drying fluid mechanics.
  2. *Four-Pillar Coating Root Cause Protocol*:
     - Solvent bath distance & vapor concentration calibration during idle standby.
     - Replacement of metal/hard scrapers with special resin wipers for nozzle lips.
     - Restricting nozzle shim assembly to certified senior technicians.
     - Scheduled retirement of fluororesin dispense tubing to prevent inner-wall delamination particles.

---

<a id="rule-58"></a>
### Rule 58: Occam's Razor & Singular Physical Trigger vs 4M Management Narratives (奥卡姆剃刀与极简归因法则)

- **Problem / 陷阱**: Confusing corporate 8D presentations (which synthesize 4M1E matrices to pacify management) with frontline shopfloor truth.
- **Methodology / 方法**:
  1. *Single Physical Trigger*: Stable manufacturing lines suddenly fail due to singular, discrete physical changes (e.g., localized resin crust on nozzle lip, worn vacuum seal, station re-indexing), never broad multi-variable resonance.
  2. *Binary Resolution*: Disentangle whether a sudden defect spike stems from:
     - *Branch 1*: Observability shift (defect was latent, now visible due to inspection gate or recipe shift).
     - *Branch 2*: Singular hardware/fluid boundary collapse.

---

<a id="rule-59"></a>
### Rule 59: Longitudinal Stripe Mura: Slit Coater Falsehood vs Develop Air Dry Knife Physical Truth (显影风刀机理与条纹真因甄别准则)

- **Problem / 陷阱**: Longitudinal white stripes across panels are routinely assumed to be slit coater nozzle clogs.
- **Methodology / 方法**:
  1. *Turbulent Air Impingement Mechanism*: Developer Rinse Air Knife (RAK) placed too close to glass (10mm) creates localized turbulence and pressure differentials. Raising height to 15mm, cutting airflow (780 -> 380 L/min), and installing pressure-equalization buffers eliminates turbulence stripes.
  2. *TMAH Evaporative Micro-Etch Mechanism*: Insufficient CDA knife airflow fails to clear rinse water micro-droplets containing trace TMAH developer. Downstream hard-bake rapidly evaporates water, concentrating alkaline TMAH and micro-etching organic films into distinct white stripes. Raising air flow (e.g., 1200 -> 1650 L/min) cures the defect.

---

<a id="rule-60"></a>
### Rule 60: Two-Stage Relational Grounding for Enterprise Auto-Ontology (NVIDIA Auto-Ontology 语义图谱与确定性推理范式)

- **Problem / 陷阱**: Unstructured vector RAG over technical manufacturing communication produces hallucinations and cannot handle exact parameter offsets.
- **Methodology / 方法**:
  1. *Stage 1 (Relational Normalization)*: Mine raw communication into 3NF relational PostgreSQL tables (`dim_equipment`, `dim_process_layer`, `dim_defect_type`, `fact_defect_incident`, `fact_root_cause_action`) with explicit parameter boundaries and units.
  2. *Stage 2 (Auto-Ontology Compilation)*: Map domain terms and synonyms (`Air Knife`, `Suji Mura`, `Organic Layer`) to relational columns in NVIDIA Auto-Ontology for deterministic Text-to-SQL query generation.

---

<a id="rule-61"></a>
### Rule 61: Methodology Engine vs Domain Knowledge Store (方法论母机与领域私有知识库解耦隔离准则)

- **Problem / 陷阱**: Conflating open-source methodology tools with proprietary manufacturing secrets, leading to fear of pushing updates to public repositories.
- **Methodology / 方法**:
  1. *Open-Source Methodology Engine (`knowhow-miner`)*: Houses general parsers, validators, evaluation harnesses, and synthetic benchmark suites. Regularly versioned and pushed.
  2. *Proprietary Knowledge Store*: Production databases, real factory emails, internal equipment tags, and confidential recipe parameters remain air-gapped on local servers.
