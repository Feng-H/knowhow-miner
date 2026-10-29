# DevLog — knowhow-miner 开发日志

> 本文件为需求 → 实现 → 验证的可追溯开发记录。每个条目包含：需求原文（用户口径）、
> 落地实现（代码/模块）、验证方式与结果。用于校准"讲好的需求是否完成、前后是否矛盾"。

---

## [2026-10-29] 两层认知缓存与全文检索落地（Two-Tier Retrieval）

### 需求背景（用户原话校准）

1. **全文检索落地**
   > "本身是需要全文检索，但是在上面要抽取knowhow，初期全文，但是后面不是每次都全文，只有当置信度不高，才深入进入全文。不然随着运行，整个系统会越来越大。"

2. **此前评测的诚实反思**（用户质询）
   > "之前没有加这些东西，那我们之前你的测试怎么得到这么高的分？"

   结论：此前 Level 1~5 测的是"清洗/分类/校验器"的加工精度（数据直接喂到嘴边），
   从未测过端到端检索召回。本次新增 Level 6 补上该缺口。

3. **开发可追溯性要求**（用户指令）
   > "完成后相关的开发log也要记录，我们才可以追溯，而且整个开发需求、结果、验证结果要落成文件，而且传到github"

### 架构决策

- **拒绝纯向量 RAG**：通用 embedding 对 `0.8μm vs 1.5μm`、`HP04 vs HP08` 语义距离极小，
  工业参数毫厘之差无法靠余弦相似度区分；且切块会切断会话因果链。
- **两层分流（用户定义）**：
  - **L1 知识结晶层**：已收敛因果五元组 + DFM 规则 + 证据锚点，毫秒级、体积小，
    不随邮件库增长而变慢。
  - **L2 全文深潜层**：SQLite FTS5 倒排索引 + 会话树还原 + 附件证据解包。
  - **路由规则**：L1 置信度 >= 0.80 直接命中返回（零全文开销）；低于阈值才触发 L2 深潜；
    L2 深潜结果自动结晶回填 L1（认知进化，越用越快）。

### 落地模块

| 模块 | 职责 |
|---|---|
| `miner/fulltext_engine.py` | SQLite FTS5 倒排全文检索引擎（bm25 排序，取代 `LIKE` 全表扫描） |
| `miner/deep_retriever.py` | L2 深潜器：Message-ID/In-Reply-To 会话树还原（无头字段时回退主题归一化分组），附件证据识别（Excel split / PPT 5-Why） |
| `miner/knowledge_store.py` | L1 结晶存储器：plant_fingerprint 索引、置信度排序、命中计数 |
| `miner/distill.py` | 初期全量挖掘 → L1 结晶（金标准/管线输出按证据分级写入，Grade A=0.95 起步） |
| `miner/hybrid_router.py` | 自适应路由器：codebook 实体指纹提取 → L1 匹配置信打分 → 分流/深潜/回填 |
| `miner/search.py` | CLI 交互检索入口（`python3 -m miner.search`） |
| `miner/eval_runner.py` | 新增 Level 6 端到端检索评测 |
| `benchmarks/retrieval_cases.json` | 真实排查问题题库（L1 命中 / L2 深潜 / 认知进化三类用例） |
| `miner/mock_generator.py` | 新增第三组 PHT03 光阻残留事件（不在金标准内，专测 L2 深潜回填） |

### 验证结果（实测输出，非宣称）

- `python3 -m miner.eval_runner --index-db mock_emails.db`
  - Level 1~5 维持不变（100 / 85 / 100 / 100 / 100）
  - **Level 6: 100.0/100** — 路由准确率 100%、L1 缓存精度 100%、L2 Recall@K 100%、
    实体提取 100%、认知进化率 100%
  - **总评 97.8 / 100 [PASS]**
- `python3 -m unittest discover tests/` → OK（含 Level 6 断言）
- CLI 实测两条路由均符合预期：
  - M2/AZ99 查询 → `L1_CACHE_HIT`（confidence 1.0，返回真因+PCA+DFM+Grade A 引证）
  - PHT03 查询（L1 无结晶）→ `L2_DEEP_DIVE`（FTS5 召回 2 封、会话树还原、附件识别、
    自动回填结晶 `dive_*`）

### 过程中修复的缺陷

- [FIX] deep_retriever 主题归一化 fallback 分组对多 seed 重复计数（2 封显示 4 条）→ 按
  message_id 去重修复，回归通过。
- [FIX] FTS5 查询词清洗：字母数字编码（AZ99/A1PHT200）加引号防止语法注入。

### 已知边界（诚实声明）

- Level 6 当前在 mock 语料（8 封）上验证；真实 22k 封语料上的 Recall@K 待 CSOT/天马
  数据接入后复测。
- `unicode61` 分词器对中文按整段切词，长中文短语召回依赖字面匹配；真实库上若召回不足，
  下一步引入 jieba 预分词或 trigram tokenizer（已列入待办）。
- L2 深潜回填的结晶目前为 Grade E 置信 0.55（provisional），需人工/LLM 五元组仲裁确认后
  才升格——这是刻意保守设计，防止低质邮件污染 L1。

---

## 历史条目索引

- FDE 五级证据分级（Grade A~E）与引文锚定 → 见 `docs/REQUIREMENTS.md` 需求 R-2026-10-28。
