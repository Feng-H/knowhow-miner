"""
KnowhowCraft Open-Source Local MCP Server
=========================================
Author: John Huang & Hermes Agent
License: CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike 4.0)

A self-contained MCP (Model Context Protocol) Server for local agent workflows.
Runs on standard Python 3 (zero heavy frameworks), providing:
  1. SSE endpoint: GET /sse (for WorkBuddy, Cursor, Claude Desktop)
  2. JSON-RPC POST: POST /mcp and POST /mcp/messages?sessionId=...
  3. Physical ground-truth causal defect diagnosis and DFM rule verification.

Usage:
  python3 -m miner.mcp_server --port 8800
"""

import os
import sys
import json
import time
import uuid
import queue
import argparse
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from miner.sanitizer import sanitize_text, sanitize_crystal_record
from miner.knowledge_store import KnowledgeStore

MCP_TOOLS = [
    {
        "name": "fpd_diagnose_defect",
        "description": (
            "半导体显示/微纳制造（FPD Array / Photolithography / Track / Etch / Thin-Film）"
            "一线制程缺陷与工艺异常因果研判。\n"
            "输入缺陷现象、异常代码、膜层或站点，返回脱敏后的本质物理机理、跨工序推诿争议、"
            "分件实验验证探针、对策定案(PCA)及流片前可制造性设计红线(DFM Rules)。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "缺陷现象描述或异常代码，例如：'5.99寸 M2 过孔孔边发黑铝腐蚀'、'ITO2 CD偏大感度变慢'、'AZ99'、'17300显影光阻残留'、'M1坡度过陡' 等"
                },
                "layer": {
                    "type": "string",
                    "description": "可选：特定工艺膜层（如 M1_Gate, M2_SourceDrain, ITO, Poly, All Layers）"
                },
                "station": {
                    "type": "string",
                    "description": "可选：工序或站点（如 Photo, Track, DET, WET, CVD, PVD）"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "fpd_get_preset_cases",
        "description": "获取已收录的典型金标准半导体显示工艺异常案例清单（含现象、争议焦点、本质物理根因与治本对策）。",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "fpd_query_dfm_rules",
        "description": "查询流片前（Tape-out）可制造性设计红线（DFM Rules）及物理计算公式（如刻蚀坡度选择比、光阻感度容差、显影液电导率阈值等）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "可选：关键词或缺陷代码（如 'Taper', 'CD', 'Conductivity', 'AZ99'）"
                }
            }
        }
    }
]

GOLDEN_PRESETS = {
    "m2_al_corrosion": {
        "title": "M2 铝腐蚀与走线断线 (Al Corrosion)",
        "layer": "M2_SourceDrain",
        "station": "DET / Photo / PI",
        "defect_code": "AZ99",
        "symptom": "点亮测试报 Data 暗线/亮线，AOI 报 AZ99 M2 铝腐蚀超标，单板缺陷高达上千颗，集中分布在 Poly 左侧 ILD 过孔边缘。",
        "disputes": [
            {"dept": "整合/PI", "point": "要求刻蚀排查腔室水汽与机台清洗，要求光刻加厚光阻。"},
            {"dept": "光刻/Photo", "point": "排查机台涂布膜厚与烘烤温度受控无异常，光阻抗蚀刻裕量正常。"},
            {"dept": "刻蚀/DET", "point": "排查无明显 Chamber 差异，仅在两款大尺寸新产品上集中爆发。"}
        ],
        "probe": "对不同产品版图进行最恶劣公差链（Worst-case Budget）叠图对比，发现老产品有过孔保护，新产品标称 0 裕量。",
        "internal_root_cause": "设计规则（DRC）公差链断裂：ILD 刻蚀 CD 2.5±0.7μm，M2 PHT CD 2.5±0.6μm，叠加曝光机极限 Overlay ±0.8μm。最坏公差下 M2 无法包住 ILD 孔，孔壁铝层暴露于干刻含氯气体（Cl2/BCl3）正面轰击，微量 AlCl3 残留微孔接触湿气自催化电化学腐蚀烂穿走线。",
        "pca_solution": "修改版图，对 M2 过孔边缘强制实施单边 Sizing Out 1.5μm 包覆补偿；制程端严格卡死 M2 刻蚀出机台至后道湿法剥膜（Strip）的 Q-Time < 4 小时。",
        "dfm_rule": {
            "rule_id": "FPD-DFM-MET02-001",
            "name": "过孔耐腐蚀包覆裕量强校验 (Via Enclosure Rule)",
            "formula": "Enclosure_Margin >= (Tol_Via + Tol_Metal) / 2 + Max_Overlay",
            "action": "强制金属层单边包裹介质过孔 >= 1.5μm，从图纸根源杜绝腐蚀。"
        },
        "evidence_grade": "Grade A (技术定案与量产锁版)"
    },
    "ito2_cd_drift": {
        "title": "ITO2 CD 均值全线偏大阶跃 (CD Drift & Photospeed)",
        "layer": "ITO2_Common",
        "station": "Photo / Track",
        "defect_code": "CD_DRIFT",
        "symptom": "全线新产品 ITO2 CD 均值突然从 2.62μm 阶跃漂移至 2.69μm 以上超 OOC 规格持卡，但曝光 Dose、显影浓度与烘烤温度全线受控。",
        "disputes": [
            {"dept": "曝光科", "point": "曝光机照度计校准正常，Dose 能量参数绝对未做任何更改。"},
            {"dept": "Track科", "point": "显影液 TMAH 浓度、温度、流量及各热板温度完全正常。"}
        ],
        "probe": "将整线 CD 突变时间点与中央供胶系统（CCSS）换桶与光阻上料批次时间戳对齐，发现 100% 精确吻合。",
        "internal_root_cause": "光刻胶供应商为内部 CPK 考核擅改原料混合配比（Blend ratio），导致批次门槛曝光量（Eth / Photospeed）突降（感度变慢）。正胶感度变慢导致相同能量下光阻溶解不足，留存条宽变宽，表现为全线偶发性偏大。",
        "pca_solution": "立即紧急下线异常光刻胶桶，并对供应商建立进料 Eth 极窄窗口（必须控制在 +0.2% 以内）入厂硬卡控，全线 CD 均值恢复 2.62μm 基准。",
        "dfm_rule": {
            "rule_id": "FPD-DFM-PHT-003",
            "name": "高 PPI 微细电极光阻感度容差预算",
            "formula": "Max_Delta_CD = Photospeed_Slope x Delta_Eth <= 0.03μm",
            "action": "锁定正胶进料批次波动，高精细层禁止跨批次直接混跑。"
        },
        "evidence_grade": "Grade A (供应商定案与入库硬卡死)"
    },
    "m1_taper_rc": {
        "title": "M1 Taper 坡度过陡与爬坡断线 / RC 延迟",
        "layer": "M1_Gate",
        "station": "Photo / DET / CVD",
        "defect_code": "TAPER_OVERSTEEP",
        "symptom": "M1 金属层刻蚀后坡度角达 52°，过陡导致后续 CVD 绝缘层（IMD SiNx）台阶覆盖率不足，转接阶梯 RC 延迟超标并引发介质击穿漏电。",
        "disputes": [
            {"dept": "刻蚀/薄膜", "point": "要求黄光把光阻做缓，强行要求曝光 Focus 散焦 ±30μm 或后烘烤拉长到 200s。"},
            {"dept": "光刻/Photo", "point": "坚决拒绝！散焦会耗尽景深（DOF），摧毁全板 CD 均一性并引发严重 Mura；延长烘烤会导致 Takt Time 翻倍、产能腰斩！"}
        ],
        "probe": "通过分件表验证，光刻保持标准 POR 条件，由下游干法刻蚀进行多步骤氧气拉胶实验。",
        "internal_root_cause": "刻蚀纵向与横向选择比失衡。光刻坚守量产 POR 底线；量产治本方案由干法刻蚀（DET）吸收：优化 SF6/O2 气体比例，通过主刻蚀、过刻蚀（加大氧等离子体侧向灰化光阻）、界面微调的三步阶梯各向异性刻蚀，成功拉出 33° 黄金坡度。",
        "pca_solution": "光刻量产 POR 参数坚决不动；刻蚀端固化三步阶梯刻蚀 Recipe，PVD 调靶材功率微调结晶致密性，清洗站固化 HF 35s。",
        "dfm_rule": {
            "rule_id": "FPD-DFM-ETCH-002",
            "name": "厚金属台阶坡度与绝缘层厚度匹配红线",
            "formula": "tan(theta_metal) <= [ER_metal / ER_lateral_PR] x tan(theta_PR)",
            "action": "规定刻蚀 Taper 目标角 30°~40°，禁止向上游光刻强加非物理散焦需求。"
        },
        "evidence_grade": "Grade A (三步阶梯刻蚀定案)"
    },
    "pht03_pr_residue": {
        "title": "17300 显影出板 PHT03 光阻残留 (PR Residue)",
        "layer": "All Layers",
        "station": "17300 Track",
        "defect_code": "PHT03",
        "symptom": "ADI 检查发现 17300 站显影出板后 PHT03 光阻残留成批出现，集中在卡匣第 10-20 片位。",
        "disputes": [
            {"dept": "曝光科", "point": "曝光机照度计正常，曝光 Dose 能量未衰减。"},
            {"dept": "Track科", "point": "初期怀疑显影喷嘴堵塞，但清洗喷嘴后仍偶发报警。"}
        ],
        "probe": "排查混药柜（Chemical Mixing Cabinet）管路流量与浓度趋势曲线。",
        "internal_root_cause": "显影液浓度跌破下限：混药柜管路单向阀老化漏气，导致补液未按精准比例执行，显影不净残留。",
        "pca_solution": "紧急更换单向阀件，恢复正规混药柜自动监控配比，卡死进液电导率下限。",
        "dfm_rule": {
            "rule_id": "FPD-DFM-TRK-001",
            "name": "显影液电导率自动联锁停机准则",
            "formula": "Conductivity_Dev >= 2.38% ± 0.05%",
            "action": "显影液浓度偏离基准超过 0.05% 自动持卡停机，禁止未混匀直供。"
        },
        "evidence_grade": "Grade B (管路实测与阀件确认)"
    }
}

class MCPSessionManager:
    def __init__(self):
        self._sessions: Dict[str, queue.Queue] = {}

    def create_session(self) -> str:
        session_id = uuid.uuid4().hex
        self._sessions[session_id] = queue.Queue()
        return session_id

    def get_queue(self, session_id: str) -> Optional[queue.Queue]:
        return self._sessions.get(session_id)

    def remove_session(self, session_id: str):
        self._sessions.pop(session_id, None)

_sessions = MCPSessionManager()

def format_diagnosis(diag: dict) -> str:
    title = diag.get("title", "工序异常因果研判")
    layer = diag.get("layer", "Array Layer")
    station = diag.get("station", "Station")
    grade = diag.get("evidence_grade", "Grade A")
    symptom = diag.get("symptom", "暂无描述")
    root_cause = diag.get("internal_root_cause", "物理机理分析中")
    pca = diag.get("pca_solution", "暂无量产对策")
    probe = diag.get("probe", "查验分件表与工艺监控曲线")

    lines = [
        f"### 🛠️ 工艺异常因果研判：{title}",
        f"- **膜层/工序**: `{layer}` / `{station}`",
        f"- **证据评级**: `{grade}`",
        "",
        "#### 1. 现象特征 (Symptom)",
        symptom,
        ""
    ]

    disputes = diag.get("disputes", [])
    if disputes:
        lines.append("#### 2. 跨工序推诿争议 (Disputes)")
        for d in disputes:
            lines.append(f"- **{d.get('dept')}**：{d.get('point')}")
        lines.append("")

    lines.extend([
        "#### 3. 现场验证探针 (Validation Probe)",
        probe,
        "",
        "#### 4. 本质物理机理 (Ground Truth Physics)",
        f"> {root_cause}",
        "",
        "#### 5. 量产治本对策 (PCA Solution)",
        pca,
        ""
    ])

    dfm = diag.get("dfm_rule")
    if dfm:
        rule_id = dfm.get("rule_id", "DFM-RULE")
        rule_name = dfm.get("name", "设计红线")
        formula = dfm.get("formula", "")
        action = dfm.get("action", "")
        lines.extend([
            f"#### 6. 派生 DFM 设计红线 ({rule_id}: {rule_name})",
            f"- **物理公式**: `{formula}`",
            f"- **设计/制程动作**: {action}",
            ""
        ])

    lines.append("---")
    lines.append("*来源: KnowhowCraft L1 认知结晶库 • CC BY-NC-SA 4.0*")
    return "\n".join(lines)

def run_diagnose(query: str, layer: str = "", station: str = "", kstore: Optional[KnowledgeStore] = None) -> str:
    query = (query or "").strip()
    layer = (layer or "").strip()
    station = (station or "").strip()

    if not query:
        return "错误：查询关键词不能为空。"

    # Check L1 KnowledgeStore first if loaded
    if kstore:
        crystals = kstore.lookup(layer=layer or None, station=station or None)
        for c in crystals:
            c_code = c.get("defect_code", "")
            if c_code and c_code.lower() in query.lower():
                return format_diagnosis({
                    "title": f"工序结晶：{c.get('layer', '')} {c_code}",
                    "layer": c.get("layer", ""),
                    "station": c.get("station", ""),
                    "evidence_grade": f"Grade {c.get('evidence_grade', 'B')}",
                    "symptom": c.get("symptom", ""),
                    "internal_root_cause": c.get("ground_truth_mechanism", ""),
                    "pca_solution": c.get("pca_action", ""),
                    "dfm_rule": c.get("dfm_rule", {}),
                    "probe": "查验分件对策表"
                })

    # Golden presets fallback
    q_lower = (query + " " + layer + " " + station).lower()
    matched = None
    if any(k in q_lower for k in ["铝腐", "m2", "腐蚀", "过孔", "az99"]):
        matched = GOLDEN_PRESETS["m2_al_corrosion"]
    elif any(k in q_lower for k in ["ito2", "cd偏大", "cd 偏大", "光阻感度", "eth"]):
        matched = GOLDEN_PRESETS["ito2_cd_drift"]
    elif any(k in q_lower for k in ["taper", "m1", "rc", "坡度", "倒角"]):
        matched = GOLDEN_PRESETS["m1_taper_rc"]
    elif any(k in q_lower for k in ["17300", "pht03", "光阻残", "显影不净"]):
        matched = GOLDEN_PRESETS["pht03_pr_residue"]

    if matched:
        return format_diagnosis(sanitize_crystal_record(matched))

    return (
        f"⚠️ 【未匹配到已定案物理因果】\n\n"
        f"- 查询关键词: `{query}`\n"
        f"- 提示: 可尝试查询已收录的典型工况，如 'M2铝腐蚀'、'ITO2 CD偏大'、'M1坡度RC' 或 '17300显影残留'。"
    )

def handle_jsonrpc(req: dict, kstore: Optional[KnowledgeStore] = None) -> Optional[dict]:
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {}) or {}

    if method == "notifications/initialized":
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "knowhowcraft-fpd-local", "version": "1.0.0"}
            }
        }

    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": MCP_TOOLS}}

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {}) or {}

        if tool_name == "fpd_diagnose_defect":
            text_out = run_diagnose(args.get("query", ""), args.get("layer", ""), args.get("station", ""), kstore)
        elif tool_name == "fpd_get_preset_cases":
            items = [f"- **[{k}] {v['title']}** ({v['layer']} / {v['station']})" for k, v in GOLDEN_PRESETS.items()]
            text_out = "### 📚 已收录工序实战案例清单\n\n" + "\n".join(items)
        elif tool_name == "fpd_query_dfm_rules":
            kw = args.get("keyword", "").lower()
            rules = [f"### 📐 {v['dfm_rule']['rule_id']}: {v['dfm_rule']['name']}\n- 公式: `{v['dfm_rule']['formula']}`\n- 动作: {v['dfm_rule']['action']}" for v in GOLDEN_PRESETS.values() if not kw or kw in json.dumps(v['dfm_rule']).lower()]
            text_out = "\n\n".join(rules) if rules else "未找到匹配规则。"
        else:
            text_out = f"未知工具: {tool_name}"

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"content": [{"type": "text", "text": text_out}]}
        }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

class LocalMCPHandler(BaseHTTPRequestHandler):
    kstore: Optional[KnowledgeStore] = None

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        if url.path in ("/sse", "/mcp/sse"):
            session_id = _sessions.create_session()
            q = _sessions.get_queue(session_id)
            if not q:
                self.send_error(500, "Failed to create session")
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            self.wfile.write(f"event: endpoint\r\ndata: /mcp/messages?sessionId={session_id}\r\n\r\n".encode("utf-8"))
            self.wfile.flush()

            try:
                while True:
                    try:
                        msg = q.get(timeout=15)
                        if msg is None: break
                        self.wfile.write(f"event: message\r\ndata: {json.dumps(msg, ensure_ascii=False)}\r\n\r\n".encode("utf-8"))
                        self.wfile.flush()
                    except queue.Empty:
                        self.wfile.write(b": keep-alive\r\n\r\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                _sessions.remove_session(session_id)
            return

        elif url.path == "/health":
            body = json.dumps({"status": "ok", "service": "knowhow-miner-local-mcp"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404, "Not found")

    def do_POST(self):
        url = urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len)
        try:
            req_json = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            req_json = {}

        if url.path in ("/mcp/messages", "/messages"):
            session_ids = parse_qs(url.query).get("sessionId", [])
            session_id = session_ids[0] if session_ids else None
            q = _sessions.get_queue(session_id) if session_id else None
            if not session_id or not q:
                self.send_error(400, "Invalid sessionId")
                return
            self.send_response(202)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"Accepted")

            res = handle_jsonrpc(req_json, self.kstore)
            if res is not None:
                q.put(res)
            return

        elif url.path in ("/mcp", "/api/mcp"):
            res = handle_jsonrpc(req_json, self.kstore)
            if res is not None:
                body_bytes = json.dumps(res, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body_bytes)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body_bytes)
            else:
                self.send_response(204)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
            return

        self.send_error(404, "Not found")

def main():
    parser = argparse.ArgumentParser(description="KnowhowCraft Local MCP Server")
    parser.add_argument("--port", type=int, default=8800, help="Server port (default: 8800)")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--db", default=None, help="Optional SQLite knowledge_store.db path")
    args = parser.parse_args()

    kstore = KnowledgeStore(args.db) if args.db and os.path.exists(args.db) else None
    LocalMCPHandler.kstore = kstore

    server = ThreadingHTTPServer((args.host, args.port), LocalMCPHandler)
    server.daemon_threads = True
    print(f"🚀 KnowhowCraft Local MCP Server started at http://{args.host}:{args.port}")
    print(f"   SSE Endpoint: http://localhost:{args.port}/sse")
    print(f"   JSON-RPC POST: http://localhost:{args.port}/mcp")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()

if __name__ == "__main__":
    main()
