# Changelog

All notable changes to the **KnowhowCraft Industrial Know-How Miner** (`knowhow-miner`) project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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
