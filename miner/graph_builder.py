import json
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field

@dataclass
class GraphNode:
    id: str
    label: str
    group: str
    title: str
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GraphEdge:
    source: str
    target: str
    label: str
    arrows: str = "to"

class ManufacturingKnowledgeGraph:
    """
    Constructs a domain knowledge graph and exports interactive HTML / JSON graph representations.
    """

    GROUP_COLORS = {
        "Incident": "#e74c3c",       # Crimson Red
        "Layer": "#3498db",          # Blue
        "Station": "#9b59b6",        # Purple
        "Defect": "#e67e22",         # Orange
        "RootCause": "#f1c40f",      # Yellow
        "Countermeasure": "#2ecc71", # Emerald Green
        "DFMRule": "#1abc9c",        # Turquoise
        "Material": "#95a5a6"        # Slate Gray
    }

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    def add_node(self, node_id: str, label: str, group: str, title: str = "", properties: Optional[Dict[str, Any]] = None):
        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(
                id=node_id,
                label=label,
                group=group,
                title=title or label,
                properties=properties or {}
            )

    def add_edge(self, source: str, target: str, label: str):
        # Prevent duplicates
        for e in self.edges:
            if e.source == source and e.target == target and e.label == label:
                return
        self.edges.append(GraphEdge(source=source, target=target, label=label))

    def build_from_causal_records(self, causal_records: List[Dict[str, Any]], annotations_map: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Populates graph nodes and edges from structured causal incidents.
        """
        for r in causal_records:
            inc_id = r["incident_id"]
            inc_title = r.get("title", inc_id)
            defect_id = None
            rc_id = None
            
            # 1. Incident Node
            self.add_node(
                node_id=inc_id,
                label=f"{inc_id}\n{inc_title[:16]}...",
                group="Incident",
                title=f"Incident: {inc_title}\nStage: {r.get('lifecycle_stage')}\nDuration: {r.get('duration_days')} days",
                properties=r
            )

            # 2. Defect Node
            symptom = r.get("symptom")
            if symptom:
                defect_id = f"DEFECT_{inc_id}"
                self.add_node(
                    node_id=defect_id,
                    label=symptom[:24] + "...",
                    group="Defect",
                    title=f"Symptom: {symptom}"
                )
                self.add_edge(inc_id, defect_id, "OBSERVED")

            # 3. Root Cause Node
            rc = r.get("root_cause_internal")
            if rc and rc != "待深入工程复盘":
                rc_id = f"RC_{inc_id}"
                self.add_node(
                    node_id=rc_id,
                    label=rc[:24] + "...",
                    group="RootCause",
                    title=f"Internal Ground Truth: {rc}"
                )
                if defect_id:
                    self.add_edge(defect_id, rc_id, "PHYSICAL_CAUSE")
                else:
                    self.add_edge(inc_id, rc_id, "ROOTED_IN")

            # 4. Countermeasure Node
            pca = r.get("pca_countermeasure")
            if pca and pca != "优化工艺窗口":
                pca_id = f"PCA_{inc_id}"
                self.add_node(
                    node_id=pca_id,
                    label=pca[:24] + "...",
                    group="Countermeasure",
                    title=f"Permanent Corrective Action: {pca}\nVerification: {r.get('verification_evidence')}"
                )
                self.add_edge(inc_id, pca_id, "RESOLVED_BY")

            # 5. DFM Rule Node
            dfm = r.get("design_redline_derived")
            if dfm and isinstance(dfm, dict):
                rule_id = dfm.get("rule_id", f"DFM_{inc_id}")
                self.add_node(
                    node_id=rule_id,
                    label=f"Rule: {rule_id}",
                    group="DFMRule",
                    title=f"{dfm.get('requirement')}\nAction: {dfm.get('derived_action')}"
                )
                if rc_id:
                    self.add_edge(rc_id, rule_id, "DERIVES_RULE")

            # 6. Station & Layer connections from Annotations
            if annotations_map and inc_id in annotations_map:
                ann = annotations_map[inc_id]
                for st in ann.get("stations", []):
                    st_id = f"STATION_{st}"
                    self.add_node(st_id, st, "Station", f"Process Station: {st}")
                    self.add_edge(inc_id, st_id, "INVOLVED_STATION")

                for layer in ann.get("layers", []):
                    ly_id = f"LAYER_{layer}"
                    self.add_node(ly_id, layer, "Layer", f"Film Layer: {layer}")
                    self.add_edge(inc_id, ly_id, "AFFECTED_LAYER")

    def export_json(self, output_path: str):
        nodes_list = []
        for n in self.nodes.values():
            nodes_list.append({
                "id": n.id,
                "label": n.label,
                "group": n.group,
                "title": n.title,
                "color": self.GROUP_COLORS.get(n.group, "#7f8c8d"),
                "properties": n.properties
            })

        edges_list = [
            {"from": e.source, "to": e.target, "label": e.label, "arrows": e.arrows}
            for e in self.edges
        ]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"nodes": nodes_list, "edges": edges_list}, f, ensure_ascii=False, indent=2)

    def export_interactive_html(self, output_path: str, title: str = "Industrial Manufacturing Know-How Causal Graph"):
        nodes_json = []
        for n in self.nodes.values():
            color = self.GROUP_COLORS.get(n.group, "#7f8c8d")
            nodes_json.append({
                "id": n.id,
                "label": n.label,
                "group": n.group,
                "title": n.title.replace("\n", "<br/>"),
                "color": {"background": color, "border": "#ffffff", "highlight": {"background": "#ffffff", "border": color}},
                "font": {"color": "#ffffff", "size": 13, "face": "Inter, system-ui, sans-serif"},
                "shape": "box" if n.group in ["Incident", "DFMRule"] else "ellipse"
            })

        edges_json = [
            {
                "from": e.source,
                "to": e.target,
                "label": e.label,
                "arrows": e.arrows,
                "font": {"color": "#94a3b8", "size": 10, "align": "middle"},
                "color": {"color": "#475569", "highlight": "#38bdf8"}
            }
            for e in self.edges
        ]

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #0f172a;
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      overflow: hidden;
    }}
    #header {{
      position: absolute;
      top: 16px;
      left: 20px;
      z-index: 10;
      background: rgba(30, 41, 59, 0.85);
      backdrop-filter: blur(8px);
      padding: 12px 20px;
      border-radius: 8px;
      border: 1px solid #334155;
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }}
    h1 {{
      margin: 0 0 6px 0;
      font-size: 18px;
      font-weight: 600;
      letter-spacing: -0.02em;
    }}
    .legend {{
      display: flex;
      gap: 12px;
      font-size: 11px;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 5px;
    }}
    .legend-color {{
      width: 10px;
      height: 10px;
      border-radius: 2px;
    }}
    #network {{
      width: 100vw;
      height: 100vh;
    }}
    #details {{
      position: absolute;
      top: 16px;
      right: 20px;
      width: 320px;
      max-height: 80vh;
      overflow-y: auto;
      z-index: 10;
      background: rgba(30, 41, 59, 0.9);
      backdrop-filter: blur(8px);
      padding: 16px;
      border-radius: 8px;
      border: 1px solid #334155;
      display: none;
      font-size: 13px;
      line-height: 1.5;
    }}
    #details h3 {{
      margin-top: 0;
      font-size: 15px;
      color: #38bdf8;
      border-bottom: 1px solid #475569;
      padding-bottom: 6px;
    }}
  </style>
</head>
<body>
  <div id="header">
    <h1>{title}</h1>
    <div class="legend">
      <div class="legend-item"><div class="legend-color" style="background:#e74c3c;"></div>事件 (Incident)</div>
      <div class="legend-item"><div class="legend-color" style="background:#e67e22;"></div>不良现象 (Defect)</div>
      <div class="legend-item"><div class="legend-color" style="background:#f1c40f;"></div>物理真因 (Root Cause)</div>
      <div class="legend-item"><div class="legend-color" style="background:#2ecc71;"></div>治本对策 (PCA)</div>
      <div class="legend-item"><div class="legend-color" style="background:#1abc9c;"></div>设计红线 (DFM Rule)</div>
      <div class="legend-item"><div class="legend-color" style="background:#9b59b6;"></div>制程工序 (Station)</div>
    </div>
  </div>

  <div id="details">
    <h3 id="detail-title">节点详情</h3>
    <div id="detail-content">点击图谱中任意节点查看完整工艺机理...</div>
  </div>

  <div id="network"></div>

  <script type="text/javascript">
    const nodes = new vis.DataSet({json.dumps(nodes_json, ensure_ascii=False)});
    const edges = new vis.DataSet({json.dumps(edges_json, ensure_ascii=False)});

    const container = document.getElementById('network');
    const data = {{ nodes: nodes, edges: edges }};
    const options = {{
      physics: {{
        barnesHut: {{
          gravitationalConstant: -3500,
          centralGravity: 0.3,
          springLength: 95,
          springConstant: 0.04
        }},
        maxVelocity: 50,
        solver: 'barnesHut',
        timestep: 0.5
      }},
      interaction: {{
        hover: true,
        tooltipDelay: 100
      }}
    }};

    const network = new vis.Network(container, data, options);

    network.on("click", function (params) {{
      if (params.nodes.length > 0) {{
        const nodeId = params.nodes[0];
        const node = nodes.get(nodeId);
        document.getElementById('details').style.display = 'block';
        document.getElementById('detail-title').innerText = node.group + ': ' + node.id;
        document.getElementById('detail-content').innerHTML = node.title || node.label;
      }}
    }});
  </script>
</body>
</html>
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
