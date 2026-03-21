#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${1:-/opt/atomic-kernel}"
DOMAIN="${2:-}"

if [[ ! -d "$REPO_DIR" ]]; then
  echo "repo dir not found: $REPO_DIR" >&2
  exit 1
fi

echo "[1/9] service status"
systemctl is-active --quiet atomic-kernel-mcp.service
systemctl is-enabled --quiet atomic-kernel-mcp.service

echo "[2/9] timer status"
systemctl is-enabled --quiet atomic-kernel-gates-smoke.timer
systemctl is-enabled --quiet atomic-kernel-gates-snapshot.timer
systemctl is-enabled --quiet atomic-kernel-gates-parity.timer

echo "[3/9] localhost MCP health probe"
curl -fsS -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"node-verify","version":"0.1.0"}}}' \
  http://127.0.0.1:18787/mcp >/dev/null

echo "[4/9] world gate"
( cd "$REPO_DIR" && npm run -s world:v0:gate >/dev/null )

echo "[5/9] snapshot gate"
( cd "$REPO_DIR" && npm run -s workspace:snapshot:v0:gate >/dev/null )

echo "[6/9] parity gate"
( cd "$REPO_DIR" && npm run -s source:capability:parity:gate >/dev/null )

echo "[7/9] HTTP smoke"
( cd "$REPO_DIR" && npm run -s mcp:unified:smoke >/dev/null )

echo "[8/9] STDIO smoke"
( cd "$REPO_DIR" && npm run -s mcp:unified:stdio:smoke >/dev/null )

if [[ -n "$DOMAIN" ]]; then
  echo "[9/9] TLS endpoint probe"
  curl -fsS -H 'content-type: application/json' \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"node-verify","version":"0.1.0"}}}' \
    "https://${DOMAIN}/mcp" >/dev/null
else
  echo "[9/9] TLS endpoint probe skipped (no domain arg)"
fi

echo "ok live governed node verify"
