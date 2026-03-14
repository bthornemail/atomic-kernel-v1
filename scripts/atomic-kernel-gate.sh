#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

echo "[1/11] living-xml gate"
bash "$ROOT/scripts/living-xml-gate.sh" >/dev/null

echo "[2/11] identity gate"
bash "$ROOT/scripts/identity-gate.sh" >/dev/null

echo "[3/11] seed-algebra gate"
bash "$ROOT/scripts/seed-algebra-gate.sh" >/dev/null

echo "[4/11] lane16 gate"
bash "$ROOT/scripts/lane16-gate.sh" >/dev/null

echo "[5/11] semantic-contracts gate"
bash "$ROOT/scripts/semantic-contracts-gate.sh" >/dev/null

echo "[6/11] rdf-export gate"
bash "$ROOT/scripts/rdf-export-gate.sh" >/dev/null

echo "[7/11] asg-ingest gate"
bash "$ROOT/scripts/asg-ingest-gate.sh" >/dev/null

echo "[8/11] mjs-asg-ingest gate"
bash "$ROOT/scripts/mjs-asg-ingest-gate.sh" >/dev/null

echo "[9/11] pattern-extraction gate"
bash "$ROOT/scripts/pattern-extraction-gate.sh" >/dev/null

echo "[10/11] analysis-report gate"
bash "$ROOT/scripts/analysis-report-gate.sh" >/dev/null

echo "[11/11] protocol-flow gate"
bash "$ROOT/scripts/protocol-flow-gate.sh" >/dev/null

echo "ok atomic-kernel gate"
