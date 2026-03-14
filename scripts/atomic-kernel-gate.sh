#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

echo "[1/4] living-xml gate"
bash "$ROOT/scripts/living-xml-gate.sh" >/dev/null

echo "[2/4] identity gate"
bash "$ROOT/scripts/identity-gate.sh" >/dev/null

echo "[3/4] seed-algebra gate"
bash "$ROOT/scripts/seed-algebra-gate.sh" >/dev/null

echo "[4/4] lane16 gate"
bash "$ROOT/scripts/lane16-gate.sh" >/dev/null

echo "ok atomic-kernel gate"
