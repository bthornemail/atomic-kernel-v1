#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

echo "[1/16] living-xml gate"
bash "$ROOT/scripts/living-xml-gate.sh" >/dev/null

echo "[2/16] identity gate"
bash "$ROOT/scripts/identity-gate.sh" >/dev/null

echo "[3/16] seed-algebra gate"
bash "$ROOT/scripts/seed-algebra-gate.sh" >/dev/null

echo "[4/16] lane16 gate"
bash "$ROOT/scripts/lane16-gate.sh" >/dev/null

echo "[5/16] semantic-contracts gate"
bash "$ROOT/scripts/semantic-contracts-gate.sh" >/dev/null

echo "[6/16] rdf-export gate"
bash "$ROOT/scripts/rdf-export-gate.sh" >/dev/null

echo "[7/16] asg-ingest gate"
bash "$ROOT/scripts/asg-ingest-gate.sh" >/dev/null

echo "[8/16] mjs-asg-ingest gate"
bash "$ROOT/scripts/mjs-asg-ingest-gate.sh" >/dev/null

echo "[9/16] typescript-parser gate"
bash "$ROOT/scripts/typescript-parser-gate.sh" >/dev/null

echo "[10/16] pattern-extraction gate"
bash "$ROOT/scripts/pattern-extraction-gate.sh" >/dev/null

echo "[11/16] analysis-report gate"
bash "$ROOT/scripts/analysis-report-gate.sh" >/dev/null

echo "[12/16] protocol-flow gate"
bash "$ROOT/scripts/protocol-flow-gate.sh" >/dev/null

echo "[13/16] workspace-ingest gate"
bash "$ROOT/scripts/workspace-ingest-gate.sh" >/dev/null

echo "[14/16] vnext replay parity gate"
bash "$ROOT/scripts/vnext-replay-parity-gate.sh" >/dev/null

echo "[15/16] vnext api compat gate"
bash "$ROOT/scripts/vnext-api-compat-gate.sh" >/dev/null

echo "[16/16] vnext coq parity gate"
bash "$ROOT/scripts/vnext-coq-parity-gate.sh" >/dev/null

echo "ok atomic-kernel gate"
