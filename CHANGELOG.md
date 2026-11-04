# Changelog

All notable changes to the **KnowhowCraft Industrial Know-How Miner** (`knowhow-miner`) project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [1.3.0] - 2026-11-04

### Added
- **Centralized Frontline Industrial Engineering Rules (`docs/ENGINEERING_RULES.md`)**:
  - Published comprehensive codebook formalizing 20 frontline physical heuristics and causality principles, structured by domain-prefixed taxonomy:
    - `RULE-ORG-*` (Organizational & Expert Tacit Grounding: mentor anchor, bilingual alias, onboarding baseline, expert mental models)
    - `RULE-FLU-*` (Fluid Dynamics & Aerodynamics: OEM boundary probing, fluid anisotropy & DFM, air knife aerodynamics & TMAH micro-etch, nozzle standby)
    - `RULE-THM-*` (Thermodynamics & Metrology: lift pin thermal sink, thermal anneal phase contrast visibility shifts, organic film spec rationalization)
    - `RULE-MEC-*` (Mechanical Shock & Spatiotemporal Stress: latent micro-crack damage, multi-pass exposure models, wet double roller stiction)
    - `RULE-PAR-*` (Parsimony & State Machine: Occam's razor singular physical trigger, anti-over-retrieval, IS/IS-NOT 30-day state machine audit, defense vs offense gating)
    - `RULE-ONT-*` (Ontology Engineering & Air-Gap: two-stage relational grounding for Auto-Ontology, open methodology vs private data air-gap)
- **Parsimony Engine & Anti-Conflation (Rule 52)**:
  - Implemented Occam's razor validation in `miner/validator.py` to counter LLM reporting bias. Distinguishes genuine shopfloor single physical triggers (e.g. Air Knife velocity boundary, mechanical roller bearing stiction, isolated recipe inheritance failure) from verbose composite 4M1E excuses (Man, Machine, Material, Method) commonly packaged in corporate 8D presentations.
- **Process Visibility Shift Modeling (Rule 53)**:
  - Formulated inspection gate transition and optical phase contrast magnification modeling in `miner/validator.py`. Distinguishes inline hardware degradation from metrology threshold shifts (e.g., inspection relocating from wet PHT to post-ANN, where 230°C thermal annealing induces 20-30% resin volume shrinkage, geometrically amplifying nanometer thickness variations into visible optical interference stripes).
- **NVIDIA Auto-Ontology Semantic Bridge**:
  - Implemented `miner/auto_ontology_bridge.py` and `schemas/industrial_ontology_schema.sql` to compile mined causal quintets into normalized relational schemas (`dim_equipment`, `dim_process_layer`, `dim_defect_type`, `fact_defect_incident`, `fact_root_cause_action`).
  - Added automated term and synonym generation (`Air Knife`, `Suji Mura`, `Organic Layer`, `Root Cause & Action`) for NVIDIA Auto-Ontology semantic layer integration.
  - Enabled deterministic Text-to-SQL query generation over physical parameter deltas, bypassing probabilistic vector RAG hallucinations.
- **Benchmark Fixtures Expansion**:
  - Added synthetic benchmark cases `GT_005_DEVELOP_AIR_KNIFE_FLOW_MURA` and `GT_006_INSPECTION_STATION_VISIBILITY_SHIFT` into `benchmarks/gold_standard_v1.json` with 100% test coverage in `tests/test_auto_ontology_bridge.py`.

### Changed
- Enhanced dual-reality decoupling to flag multi-factor composite excuses and reward parsimonious physical mechanisms.
- Separated bilingual documentation into independent, reciprocal files: `README.md` (English) and `README_zh.md` (Chinese), preventing bloated multilingual mixing.
- Added explicit upstream attribution and acknowledgment to the [NVIDIA Auto-Ontology](https://github.com/NVIDIA/auto-ontology) open-source framework across all documentation.

---

## [1.2.0] - 2026-10-30

### Added
- **Pre-mining Human Alignment (Step 0: Mentor Mapping)**:
  - Formulated the *Org Triage & Mentor Anchor* methodology (`miner/annotator.py`), scanning meeting attendance and department trees to map senior mentors (Grade A authority) and suppress novice/apprentice transactional noise.
- **Bilingual Cadre Alias Resolution**:
  - Implemented entity disambiguation mapping Chinese names and English aliases (e.g. `David Chen` <-> `陈大卫`) into unified decision nodes, preventing cross-language context fragmentation common in early cross-strait fab management.
- **Envelope Unwrapping for Auto-Forwarded Corporate Mailboxes**:
  - Implemented `original_sender_unwrapping` in `miner/cleaner.py` and `miner/causal_extractor.py` to pierce auto-forwarding envelope headers (`From: [USER]`) and recover internal true authors (e.g. Lead Process Engineers).
- **Process Topology Context Validation**:
  - Enforced upstream/downstream station topological anchoring (Step A ➔ Step B ➔ Step C) to eliminate keyword-greedy false positives and prevent attributing pre-treatments across mismatched physical interfaces.
- **Strict Temporal Causality Enforcement**:
  - Implemented $T_{solution} > T_{incident}$ rule in `miner/causal_extractor.py` ensuring that countermeasures strictly postdate incidents, preventing legacy static SOPs from falsely masking live production disputes.

### Changed
- Updated bilingual `README.md` (English & Chinese) documenting the 4-phase methodology expansion: Temporal Causality, Process Topology Context, Envelope Unwrapping, and Pre-mining Human Alignment.
- Synchronized Level 5 and Level 6 evaluation harness criteria for organizational triage and temporal sequence verification.

---

## [1.1.0] - 2026-10-29

### Added
- **Native Model Context Protocol (MCP) Server**:
  - Built `miner/mcp_server.py` supporting standard tools: `fpd_diagnose_defect`, `fpd_get_preset_cases`, `fpd_query_dfm_rules`.
  - Added lightweight stdio-to-HTTP bridge `miner/mcp_bridge.py` for desktop agent integration (Tencent WorkBuddy, Cursor, Claude Desktop).
- **Commercial API Token, Concurrency & Rate Limiting Guard**:
  - Implemented `miner/auth_guard.py` with multi-tier quota control (Trial, Commercial, Enterprise) and active concurrency tracking per token.
  - Added `miner/token_admin.py` CLI utility for issuing, inspecting, and revoking commercial MCP tokens.
- **Web Anti-Theft & Honeypot Scanner Defense**:
  - Added Origin/Referer anti-leech verification blocking unauthorized third-party cross-origin embedding.
  - Added proxy-aware IP sliding window rate limiting (5 rpm for text queries) and honeypot mitigation (120s cooldown on repeated misses).
  - Implemented data tiering: qualitative physical explanations on public web, locking production recipe offsets for authenticated commercial tokens.

### Security & Legal
- Replaced PolyForm license with internationally recognized **CC BY-NC-SA 4.0** (Creative Commons Attribution-NonCommercial-ShareAlike 4.0).
- Formalized bilingual legal restrictions prohibiting commercial exploitation and proprietary closed-source derivative redistribution.

---

## [1.0.0] - 2026-10-28

### Added
- **Core Know-How Extraction Pipeline**:
  - `miner/cleaner.py`: PII redaction and critical manufacturing entity protection (0 false positives).
  - `miner/classifier.py`: Operational intent classification (`ALARM`, `DISPUTE`, `DOE_EXPERIMENT`, `REPORT_8D`).
  - `miner/aggregator.py`: Message-ID DAG conversation tree recovery and BCC thread reconciliation.
  - `miner/parsers/`: Deep inspection for binary attachments (PPT 5-Why Carver, Excel Split Table parser).
  - `miner/causal_extractor.py`: Distills structured causal quintets and derived DFM redlines.
  - `miner/validator.py`: Physics boundary gates and dual-reality decoupling (customer 8D defense vs engineering ground truth).
  - `miner/graph_builder.py`: Interactive topological causal graph generation (Vis.js HTML export).
- **Two-Tier Cognitive Retrieval Engine**:
  - L1 Distilled Crystals store (`knowledge_store.py`) for sub-millisecond confident responses.
  - L2 Deep Drill-Down store (`deep_retriever.py` + SQLite FTS5) for on-demand root-cause evidence retrieval.
- **Automated 6-Tier Evaluation Harness (`miner/eval_runner.py`)**:
  - Benchmarks covering cleaning fidelity, triage precision, causal truth, physics sanity, and citation tracing.
- **Production Air-Gapped Web Portal**:
  - Deployed `fpd.knowhowcraft.com` on Docker with read-only L1 crystal isolation and Discord webhook lead notifications.
