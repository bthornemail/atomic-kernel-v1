#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$ROOT/artifacts"
PROOFS_DIR="$ROOT/docs/proofs"
mkdir -p "$ARTIFACTS_DIR" "$PROOFS_DIR"

OUT_JSON="$ARTIFACTS_DIR/world-v0.normalized.json"
OUT_HASH="$ARTIFACTS_DIR/world-v0.replay-hash"
RECEIPT="$PROOFS_DIR/world-v0.latest.md"

bash "$ROOT/scripts/world-generate.sh"
bash "$ROOT/scripts/world-step-gate.sh"
bash "$ROOT/scripts/world-project-gate.sh"
bash "$ROOT/scripts/world-verify-gate.sh"

python3 - "$ARTIFACTS_DIR" "$OUT_JSON" <<'PY'
import json
import pathlib
import sys

artifacts = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])

def load(name):
    return json.loads((artifacts / name).read_text(encoding="utf-8"))

generate = load("world-v0.generate.normalized.json")
step = load("world-v0.step.normalized.json")
project = load("world-v0.project.normalized.json")
verify = load("world-v0.verify.normalized.json")

if not step.get("proposal_only"):
    raise SystemExit("step gate must remain proposal-only")
if step.get("canonical_world_mutated"):
    raise SystemExit("step gate reported canonical mutation")
if not step.get("unscheduled_rejected"):
    raise SystemExit("step gate unscheduled reject missing")
if not project.get("deterministic_rerun"):
    raise SystemExit("projection rerun determinism failed")
if not verify.get("branch_merge_without_lineage_rejected"):
    raise SystemExit("verify gate branch-merge reject missing")

normalized = {
    "v": "world_v0.gate.normalized.v0",
    "authority": "advisory",
    "world_id": generate["world_id"],
    "profile": generate["profile"],
    "operations": {
        "world_generate": {"pass": True, "hash": (artifacts / "world-v0.generate.replay-hash").read_text(encoding="utf-8").strip()},
        "world_step": {"pass": True, "hash": (artifacts / "world-v0.step.replay-hash").read_text(encoding="utf-8").strip()},
        "world_project": {"pass": True, "hash": (artifacts / "world-v0.project.replay-hash").read_text(encoding="utf-8").strip()},
        "world_branch_reconcile": {"pass": True, "hash": (artifacts / "world-v0.branch-reconcile.replay-hash").read_text(encoding="utf-8").strip()},
        "world_verify": {"pass": True, "hash": (artifacts / "world-v0.verify.replay-hash").read_text(encoding="utf-8").strip()}
    },
    "proposal_only_boundary": step["proposal_only"],
    "deterministic_projection": project["deterministic_rerun"],
    "fail_closed_verify": verify["invalid_schema_shape_rejected"] and verify["branch_merge_without_lineage_rejected"]
}
out.write_text(json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok world v0 aggregate")
PY

python3 - "$OUT_JSON" "$OUT_HASH" <<'PY'
import hashlib
import pathlib
import sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok world v0 replay hash")
PY

cat > "$RECEIPT" <<EOF2
# World v0 Proof Receipt

Generated (UTC): $(date -u +%FT%TZ)
Repo: /home/main/devops/atomic-kernel

Command:
bash scripts/world-v0-gate.sh

Checks:
world_generate deterministic canonical artifact: PASS
world_step proposal-only boundary and eligibility checks: PASS
world_project deterministic JSON text projection: PASS
world_branch_reconcile lineage fixture/reject checks: PASS
world_verify schema/digest/replay and fail-closed checks: PASS

Artifacts:
- artifacts/world-v0.generate.normalized.json
- artifacts/world-v0.step.normalized.json
- artifacts/world-v0.project.normalized.json
- artifacts/world-v0.branch-reconcile.normalized.json
- artifacts/world-v0.verify.normalized.json
- artifacts/world-v0.normalized.json
- artifacts/world-v0.replay-hash ($(cat "$OUT_HASH"))

Result: PASS
EOF2

echo "ok world v0 gate"
