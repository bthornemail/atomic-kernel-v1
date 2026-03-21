#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROOFS_DIR="$ROOT/docs/proofs"
ARTIFACTS_DIR="$ROOT/artifacts"
mkdir -p "$PROOFS_DIR" "$ARTIFACTS_DIR"

NOW_UTC="$(date -u +%FT%TZ)"
ID="future-demo-$(date -u +%Y%m%d%H%M%S)"
INTENDED="2000-01-01T00:00:00Z"
MSG="${1:-Hello future, this message survived as a verified artifact.}"
OUT_JSON="$ARTIFACTS_DIR/mcp-future-message-demo.normalized.json"
OUT_HASH="$ARTIFACTS_DIR/mcp-future-message-demo.replay-hash"
RECEIPT="$PROOFS_DIR/mcp-future-message-demo.latest.md"

python3 - "$ROOT" "$ID" "$INTENDED" "$MSG" "$OUT_JSON" <<'PY'
import json, subprocess, sys, pathlib, hashlib
root, mid, intended, msg, out_json = sys.argv[1:6]

reqs = [
  {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"future-demo","version":"0.1.0"}}},
  {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"send_message_to_future","arguments":{"id":mid,"message":msg,"intended_read_after_utc":intended}}},
  {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_future_message","arguments":{"id":mid}}}
]
payload = "\n".join(json.dumps(r, separators=(",", ":")) for r in reqs) + "\n"
p = subprocess.run(
  ["node", str(pathlib.Path(root) / "scripts" / "mcp-unified-stdio.mjs")],
  input=payload.encode(),
  stdout=subprocess.PIPE,
  stderr=subprocess.PIPE,
  check=True
)
lines = [x for x in p.stdout.decode().splitlines() if x.strip()]
resps = [json.loads(x) for x in lines]
by_id = {r.get("id"): r for r in resps}

send = json.loads(by_id[2]["result"]["content"][0]["text"])
getv = json.loads(by_id[3]["result"]["content"][0]["text"])
if not send.get("written"):
  raise RuntimeError("send_message_to_future failed")
if not getv.get("found"):
  raise RuntimeError("get_future_message failed")
if not getv.get("released"):
  raise RuntimeError("message not released")
if not getv.get("digest_match"):
  raise RuntimeError("digest mismatch")

norm = {
  "v": "ak.mcp.future_message_demo.normalized.v0",
  "authority": "advisory",
  "id": mid,
  "send": send,
  "get": getv
}
pathlib.Path(out_json).write_text(json.dumps(norm, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
PY

python3 - "$OUT_JSON" "$OUT_HASH" <<'PY'
import hashlib, pathlib, sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
PY

cat > "$RECEIPT" <<EOF
# MCP Future Message Demo Proof

Generated (UTC): $NOW_UTC
Repo: /home/main/devops/atomic-kernel

Command:
bash scripts/mcp-future-message-demo.sh

Checks:
send_message_to_future: PASS
get_future_message: PASS
released=true: PASS
digest_match=true: PASS

Artifacts:
- artifacts/mcp-future-message-demo.normalized.json
- artifacts/mcp-future-message-demo.replay-hash ($(cat "$OUT_HASH"))

Message ID:
$ID

Result: PASS
EOF

echo "ok mcp future message demo id=$ID receipt=$RECEIPT"
