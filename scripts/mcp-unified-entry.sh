#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-info}"

case "$MODE" in
  server)
    exec node "$ROOT/scripts/mcp-unified-server.mjs"
    ;;
  stdio)
    exec node "$ROOT/scripts/mcp-unified-stdio.mjs"
    ;;
  info)
    cat <<INFO
atomic-kernel mcp unified entry
mode_support: http,stdio
http_start: npm run -s mcp:unified:server
http_smoke: npm run -s mcp:unified:smoke
stdio_start: npm run -s mcp:unified:stdio
stdio_smoke: npm run -s mcp:unified:stdio:smoke
capability_benchmark: npm run -s mcp:capability:benchmark
catalog: docs/control-plane.pages.v0.json
boundary: projection/advisory surfaces do not become authority
INFO
    ;;
  *)
    echo "unknown mode: $MODE (expected: server|stdio|info)" >&2
    exit 2
    ;;
esac
