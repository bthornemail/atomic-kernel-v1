#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

python3 "$ROOT/scripts/validate-semantic-contracts.py" --kind all >/dev/null

echo "ok semantic-contracts gate"
