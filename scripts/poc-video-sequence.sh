#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_ROOT="$(cd "$REPO_ROOT/.." && pwd)"

section() {
  printf '\n============================================================\n'
  printf '%s\n' "$1"
  printf '============================================================\n'
}

run_cmd() {
  printf '\n$ %s\n' "$*"
  "$@"
}

section "Atomic Kernel PoC: Deterministic + Governed + MCP Operability"
run_cmd pwd

section "1) MCP Entrypoint Info"
run_cmd npm run -s mcp:unified:info

section "2) MCP HTTP Smoke Proof"
run_cmd npm run -s mcp:unified:smoke

section "3) MCP STDIO Smoke Proof"
run_cmd npm run -s mcp:unified:stdio:smoke

section "4) Fork Import Integrity / Authority Boundary"
run_cmd ./scripts/fork-import-v1_2-gate.sh

section "5) Release Gate"
run_cmd ./scripts/release-gate.sh

section "6) Workspace Closure Spine"
run_cmd bash -lc "cd '$WORKSPACE_ROOT' && ./scripts/closure-spine-smoke.sh"

section "7) Message To Future Integrity Check"
run_cmd bash -lc "cd '$REPO_ROOT' && python3 - <<'PY'\nimport hashlib, pathlib\np = pathlib.Path('artifacts/message-to-future.v0.json')\nif not p.exists():\n    raise SystemExit('missing artifacts/message-to-future.v0.json')\nprint('sha256:' + hashlib.sha256(p.read_bytes()).hexdigest())\nPY"

section "PoC Sequence Complete"
echo "All primary proof surfaces executed."
