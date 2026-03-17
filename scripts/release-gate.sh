#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

echo "[1/6] conformance tests"
bash "$ROOT/conformance/run-tests.sh" >/dev/null

echo "[2/6] atomic-kernel gate"
bash "$ROOT/scripts/atomic-kernel-gate.sh" >/dev/null

echo "[3/6] replay-hash files present and valid"
for f in \
  "$ROOT/golden/living-xml/replay-hash" \
  "$ROOT/golden/living-xml/hardening-replay-hash" \
  "$ROOT/golden/identity/replay-hash" \
  "$ROOT/golden/seed-algebra/replay-hash" \
  "$ROOT/golden/lane16/replay-hash" \
  "$ROOT/golden/rdf-export/replay-hash" \
  "$ROOT/golden/asg-ingest/replay-hash" \
  "$ROOT/golden/mjs-asg-ingest/replay-hash" \
  "$ROOT/golden/pattern-extraction/replay-hash" \
  "$ROOT/golden/analysis-report/replay-hash" \
  "$ROOT/golden/protocol-flow/replay-hash" \
  "$ROOT/golden/vnext-replay-parity/replay-hash"
do
  [[ -f "$f" ]] || { echo "missing replay hash: $f" >&2; exit 1; }
  grep -Eq '^sha256:[0-9a-f]{64}$' "$f" || { echo "invalid replay hash format: $f" >&2; exit 1; }
done

echo "[4/6] package metadata sanity"
python3 - <<PY >/dev/null
from pathlib import Path
import tomllib
root = Path(r"$ROOT")
data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
project = data["project"]
assert project["name"] == "atomic-kernel"
assert project["version"] == "0.1.0"
PY

echo "[5/6] downstream public import boundary"
bash "$ROOT/scripts/check-downstream-import-surface.sh" >/dev/null

echo "[6/6] aztec payload contracts"
bash "$ROOT/scripts/aztec-payload-gate.sh" >/dev/null

echo "ok release gate"
