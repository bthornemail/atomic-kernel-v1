#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

echo "[1/5] living-xml gate"
bash "$ROOT/scripts/living-xml-gate.sh" >/dev/null

echo "[2/5] identity gate"
bash "$ROOT/scripts/identity-gate.sh" >/dev/null

echo "[3/5] seed-algebra gate"
bash "$ROOT/scripts/seed-algebra-gate.sh" >/dev/null

echo "[4/5] lane16 gate"
bash "$ROOT/scripts/lane16-gate.sh" >/dev/null

echo "[5/5] semantic-contracts gate"
bash "$ROOT/scripts/semantic-contracts-gate.sh" >/dev/null

echo "ok atomic-kernel gate"
