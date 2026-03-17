#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

CASES="$ROOT/runtime/atomic_kernel/fixtures/vnext/replay-parity/accept/cases.json"
REPORT="$ROOT/reports/phase27R-vnext-replay-parity.json"
GOLDEN="$ROOT/golden/vnext-replay-parity/replay-hash"

[[ -f "$CASES" ]] || { echo "missing cases fixture: $CASES" >&2; exit 2; }
[[ -f "$GOLDEN" ]] || { echo "missing golden hash: $GOLDEN" >&2; exit 2; }

mkdir -p "$(dirname "$REPORT")"

python3 - <<PY > "$REPORT"
import json
from pathlib import Path
from runtime.atomic_kernel.vnext import LAW_VERSION, lane_parity

cases = json.loads(Path(r"$CASES").read_text(encoding="utf-8"))
if not isinstance(cases, list) or not cases:
  raise SystemExit("cases must be non-empty list")

results = []
for c in cases:
  if set(c.keys()) != {"width", "seed", "steps"}:
    raise SystemExit("case keyset mismatch")
  width = int(c["width"])
  seed = int(str(c["seed"]), 0)
  steps = int(c["steps"])
  p = lane_parity(width, seed, steps)
  if not p["states_equal"]:
    raise SystemExit(f"lane parity mismatch width={width} seed={hex(seed)} steps={steps}")
  results.append(p)

results.sort(key=lambda r: (r["width"], r["seed_hex"], r["steps"]))
report = {
  "v": "phase27R.vnext_replay_parity_gate.v0",
  "authority": "advisory",
  "law_version": LAW_VERSION,
  "summary": {
    "cases": len(results),
    "mismatches": 0,
  },
  "results": results,
}
print(json.dumps(report, sort_keys=True, separators=(",", ":")))
PY

want="$(tr -d '\n' < "$GOLDEN")"
got="sha256:$(sha256sum "$REPORT" | awk '{print $1}')"
if [[ "$want" != "$got" ]]; then
  echo "vnext replay parity replay hash mismatch: expected $want got $got" >&2
  exit 1
fi

echo "ok vnext-replay-parity gate"
