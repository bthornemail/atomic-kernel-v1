#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

VECTORS="$ROOT/runtime/atomic_kernel/fixtures/vnext/coq-parity/accept/parity-vectors.json"
COQ_COMPANION="$ROOT/kernel/coq/AtomicKernelVNext.v"

[[ -f "$VECTORS" ]] || { echo "missing vectors fixture: $VECTORS" >&2; exit 2; }
[[ -f "$COQ_COMPANION" ]] || { echo "missing Coq companion: $COQ_COMPANION" >&2; exit 2; }

python3 - <<PY
import json
from pathlib import Path
from runtime.atomic_kernel.vnext import lane_parity

vectors = json.loads(Path(r"$VECTORS").read_text(encoding="utf-8"))
if not isinstance(vectors, list) or not vectors:
  raise SystemExit("coq vectors must be non-empty list")

for c in vectors:
  if set(c.keys()) != {"width", "seed", "steps"}:
    raise SystemExit("coq vector keyset mismatch")
  p = lane_parity(int(c["width"]), int(str(c["seed"]), 0), int(c["steps"]))
  if not p["states_equal"]:
    raise SystemExit("coq parity mismatch")
PY

if command -v coqc >/dev/null 2>&1; then
  coqc "$COQ_COMPANION" >/dev/null
fi

echo "ok vnext-coq-parity gate"
