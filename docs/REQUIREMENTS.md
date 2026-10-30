# REQUIREMENTS — 需求·结果·验证 追溯表

> 用户与开发者（AI）协商确定的需求，逐条对照落地模块与实测验证结果。
> 任何一条与实现矛盾时，必须在此表中标注并说明。

| ID | 日期 | 需求（用户口径） | 落地模块 | 验证方式 | 验证结果 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | 2026-10-26 | 缺陷代码/机台/站点等私有暗号必须先打捞，不得当无意义词清洗 | `miner/codebook.py`, `miner/cleaner.py` | `eval_runner` Level 1 | Critical Tech Preservation 100%，0 误删 | ✅ 完成 |
| R-002 | 2026-10-26 | 技术负责人识别不得按发件量统计；以 NPI Kick-off/DOE 名单为金标准 + 语气指令动态识别 | `miner/authority.py` | Level 2 + 人工核对金标准名单 | 产线各模块 Lead 全对齐（Track=[LEAD] 等） | ✅ 完成 |
| R-003 | 2026-10-28 | 借鉴 FDE 数据治理：证据分级、冲突仲裁、原句锚定 | `miner/evidence.py`, `miner/causal_extractor.py` | Level 5 | Citation Anchoring 100%，Grade Validity 100% | ✅ 完成 |
| R-004 | 2026-10-29 | 需要全文检索，但初期全量挖掘后沉淀 knowhow；日常先查结晶缓存，仅置信度不足才深入全文；系统不得随数据增长变慢 | `miner/fulltext_engine.py`, `miner/knowledge_store.py`, `miner/distill.py`, `miner/hybrid_router.py` | Level 6 + CLI 双路由实测 | 路由准确率 100%，L1 精度 100%，L2 Recall@K 100%，认知进化 100% | ✅ 完成（mock 语料）|
| R-005 | 2026-10-29 | 评测必须端到端：不得"把答案喂到嘴边"式自嗨打分 | `miner/eval_runner.py` Level 6, `benchmarks/retrieval_cases.json` | 真实执行 SQL 检索 + 召回核对 | Level 6 全指标 100，总评 97.8 PASS | ✅ 完成 |
| R-006 | 2026-10-29 | 开发 log、需求、结果、验证结果落成文件并传 GitHub，供追溯与前后矛盾校准 | `docs/DEVLOG.md`, `docs/REQUIREMENTS.md` | git push | 本文件随代码同仓版本化 | ✅ 完成 |
| R-007 | 2026-10-26 | 商业保密：真实邮件数据/公司名/PII 绝不出库；GitHub 仅匿名 mock 数据与连接指导 | 仓库 .gitignore + mock_generator | push 前内容审查 | 仓库仅含 mock_emails.db 生成器，无私有数据 | ✅ 持续执行 |
| R-008 | 2026-10-26 | 术语校准：Cassette=卡匣，Slot=卡匣内片位（非实验槽位） | `industrial-knowhow-mining` skill + 文档 | 人工校对 | 全库无"玻璃盒/实验槽"误译 | ✅ 完成 |
| R-009 | 2026-10-29 | 明确运行期模型依赖：代码库与评测套件必须 100% 离线确定性（0 外部 LLM API 依赖），杜绝数据泄露与评分随机性 | 全仓原生 Python 3 + SQLite3 FTS5 + 符号验证器 | 静态依赖检查 + 离线 15ms 评测运行 | 运行期 0 大模型依赖，开发期由 Hermes Agent (gemini-3.8-flash-high) 辅助编写 | ✅ 完成 |
| R-010 | 2026-10-29 | 公网主页 fpd.knowhowcraft.com 重构与安全隔离：只允许打 L1 结晶库，严禁查原邮件；动态脱敏敏感信息（工厂/人名/联系方式）；全面采用 Docker 容器化隔离部署 | `fpd-server/server.py`, `sanitizer.py`, `Dockerfile`, `docker-compose.yml` | HTTPS 接口实测 + 物理隔离挂载 (`knowledge_store.db:ro`) | 成功切换至 Docker 非特权运行，未收录工况优雅拦截，域名平滑接管 | ✅ 完成 |
| R-011 | 2026-10-29 | 支持开放标准 MCP（Model Context Protocol）协议，对接到 WorkBuddy 与外部 Agent | `fpd-server/mcp_handler.py`, `server.py`, `miner/mcp_bridge.py` | SSE /sse 与 JSON-RPC /mcp 握手及工具调用 | WorkBuddy/Cursor 兼容，3 项工具全通 | ✅ 完成 |

## 待办（未完成，不冒充完成）

| ID | 需求 | 状态 |
|---|---|---|
| T-001 | 真实全量语料上的 Level 6 检索复测（后台数据完整接入后执行） | ⏳ 等待数据 |
| T-002 | 中文分词优化（jieba 预分词或 trigram）以提升长中文短语召回 | ⏳ 已识别边界 |
| T-003 | L2 深潜回填结晶的 LLM 五元组仲裁升格（E→A/B）闭环 | ⏳ 计划中 |
| T-004 | `fpd.knowhowcraft.com` 前端接入 HybridRouter 作为查询引擎 | ⏳ 计划中 |
