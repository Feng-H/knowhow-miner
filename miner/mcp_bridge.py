"""
KnowhowCraft MCP Stdio Bridge
==============================
Author: John Huang & Hermes Agent
License: CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike 4.0)

A lightweight stdio-to-remote MCP bridge.
Allows any local agent (WorkBuddy, Claude Desktop, Cursor, Codex, OpenCode) that
only supports stdio transport to query the remote KnowhowCraft L1 Brain directly.

Usage in mcp.json:
{
  "mcpServers": {
    "fpd-knowhowcraft": {
      "command": "python3",
      "args": ["/path/to/knowhow-miner/miner/mcp_bridge.py"]
    }
  }
}
"""

import sys
import json
import urllib.request

REMOTE_MCP_URL = "https://fpd.knowhowcraft.com/mcp"

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue

        try:
            post_data = json.dumps(req, ensure_ascii=False).encode("utf-8")
            http_req = urllib.request.Request(
                REMOTE_MCP_URL,
                data=post_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "KnowhowCraft-StdioBridge/1.0"
                }
            )
            with urllib.request.urlopen(http_req, timeout=15) as resp:
                resp_bytes = resp.read()
                if resp_bytes:
                    sys.stdout.write(resp_bytes.decode("utf-8") + "\n")
                    sys.stdout.flush()
        except Exception as e:
            req_id = req.get("id")
            if req_id is not None:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32000,
                        "message": f"Bridge error contacting remote brain: {str(e)}"
                    }
                }
                sys.stdout.write(json.dumps(err_resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    main()
