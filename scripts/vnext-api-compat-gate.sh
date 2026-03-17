#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

POLICY="$ROOT/runtime/atomic_kernel/vnext_policy.json"

python3 "$ROOT/scripts/validate-vnext-policy.py" --file "$POLICY" >/dev/null

python3 - <<PY >/dev/null
import warnings
import atomic_kernel as ak

with warnings.catch_warnings(record=True) as rec:
  warnings.simplefilter("always")
  sid = ak.compute_typed_sid("living_xml", "0011100")
  oid = ak.compute_oid({"frame": 0, "tick": 1, "control": 0}, sid, None)
  assert sid.startswith("sha256:")
  assert oid.startswith("sha256:")
  assert any(r.category is DeprecationWarning for r in rec)

asid = ak.compute_algorithmic_sid("living_xml", "0011100")
aoid = ak.compute_algorithmic_oid({"frame": 0, "tick": 1, "control": 0}, asid, None)
assert asid.startswith("math_v2:")
assert aoid.startswith("math_v2:")
assert ak.compute_hash_sid_adapter("living_xml", "0011100", "sha256").startswith("sha256:")
assert ak.compute_hash_sid_adapter("living_xml", "0011100", "sha3_256").startswith("sha3_256:")
PY

python3 -m unittest \
  atomic_kernel.tests.test_public_api \
  runtime.atomic_kernel.tests.test_vnext_lane >/dev/null

echo "ok vnext-api-compat gate"
