# AGENTS.md — Contributor & AI Agent Operational Governance

> **Audience**: AI Agents (Hermes, Claude Code, Codex, OpenCode) and human contributors modifying `knowhow-miner`.
> **Enforcement**: Mandatory pre-commit gate. Every commit and file edit must strictly adhere to the rules codified below.

---

## 1. Absolute PII & Entity Redaction (Zero-Leakage Policy)

`knowhow-miner` is an open-source methodology and algorithm framework. It **MUST NEVER** carry real-world enterprise secrets, internal personnel identities, or confidential fab data.

### 1.1 Strict Personnel Anonymization (No Real Names)
- **Rule**: NEVER write real personnel names into ANY committed file (`README.md`, `CHANGELOG.md`, `docs/`, code comments, test fixtures, or commit messages). This includes managers, section chiefs, mentors, colleagues, or vendors.
- **Enforcement**: When providing examples of roles, alias disambiguation, or authoring:
  - **Permitted Synthetic Placeholders**: `David Chen` / `陈大卫`, `Alex Wang` / `王亚历`, `[ENGINEER]`, `[LEAD]`, `[MENTOR]`.
  - **Forbidden**: Any real name discussed during conversation or extracted from historical mail archives.
  - **Pre-Commit Check**: Always run `git diff` and search against sensitive name catalogs before creating a commit.

### 1.2 Enterprise & Fab Abstraction
- **Rule**: Never reference real-world company names or proprietary commercial project codes in the public repository.
- **Replacements**:
  - `华星光电 / CSOT` ➔ `Fab-G8.5` / `某高世代 a-Si 制造基地`
  - `天马 / Tianma` ➔ `Fab-G6` / `某头部 G6 LTPS/AMOLED 产线`
  - `微智医疗 / Intellimicro` ➔ `MedTech-MEMS` / `某微纳植入医疗器械基地`

### 1.3 Strict Data Isolation (Air-Gap)
- The public repo contains **ZERO real emails, ZERO SQLite production indices, ZERO mbox chunks, and ZERO raw Office attachments**.
- All sample data and unit tests must exclusively run against `miner/mock_generator.py` and `benchmarks/` synthetic fixtures.

---

## 2. Commit & Change Documentation Protocol

Every feature addition, bug fix, or architectural change must be tracked systematically across three layers:

1. **`CHANGELOG.md` Update**:
   - Must follow [Keep a Changelog](https://keepachangelog.com/) standards under `[Unreleased]` or semantic version tags (`[X.Y.Z]`).
   - Group entries under `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, or `Security`.
   - Use synthetic placeholders (`David Chen` / `陈大卫`) for any persona examples.
2. **`README.md` Consistency**:
   - Maintain parity between English and Chinese sections.
   - When new modules or methods are added to `miner/`, update both the English and Chinese module structure sections simultaneously.
3. **Commit Messages**:
   - Follow Conventional Commits (`feat:`, `fix:`, `docs:`, `legal:`, `refactor:`).
   - Commit messages must be purely technical; never mention real personnel or internal projects.

---

## 3. Engineering Rigor & Causality Directives

When modifying causal extraction logic or adding features to `miner/`:

1. **Temporal Causality ($T_{solution} > T_{incident}$)**:
   - Solutions and countermeasures must postdate the incident. Never treat a legacy static document as resolving an incident that occurred later.
2. **Process Step Topology Alignment**:
   - Anchor defect symptoms and physical mechanisms to specific step IDs and interfaces. Never perform keyword-greedy matching across mismatched physical steps.
3. **Envelope Unwrapping**:
   - Dissect auto-forwarding envelope headers (`From: huangfeng@...`) to extract the genuine internal author from the email body.
4. **Pre-mining Human Alignment**:
   - Use organizational triage to suppress apprentice transactional noise and anchor directives to senior mentor nodes.
5. **Bilingual Entity Disambiguation**:
   - Map English aliases and Chinese names to unified identity UUIDs.

---

## 4. Pre-Push Verification Checklist

Before running `git push`, the agent must verify:
- [ ] `git diff` contains no real personnel names or unredacted enterprise labels.
- [ ] `CHANGELOG.md` reflects all architectural and functional changes.
- [ ] English and Chinese sections in `README.md` are synchronized.
- [ ] Test suite and evaluation benchmark pass (`python3 -m miner.eval_runner`).
