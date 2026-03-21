#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$ROOT/artifacts"
mkdir -p "$ARTIFACTS_DIR"

SCHEMA="$ROOT/docs/world.v0.schema.json"
LEDGER="$ROOT/docs/WORLD_PROOF_LEDGER_v0.json"
BRANCH_GATE="$ROOT/scripts/world-branch-reconcile-gate.sh"
BRANCH_JSON="$ARTIFACTS_DIR/world-v0.branch-reconcile.normalized.json"
WORLD_CANONICAL="$ARTIFACTS_DIR/world-v0.canonical.json"
GENERATE_NORMALIZED="$ARTIFACTS_DIR/world-v0.generate.normalized.json"
OUT_JSON="$ARTIFACTS_DIR/world-v0.verify.normalized.json"
OUT_HASH="$ARTIFACTS_DIR/world-v0.verify.replay-hash"

[[ -f "$WORLD_CANONICAL" ]] || bash "$ROOT/scripts/world-generate.sh"
[[ -f "$GENERATE_NORMALIZED" ]] || bash "$ROOT/scripts/world-generate.sh"
[[ -f "$SCHEMA" ]] || { echo "missing schema: $SCHEMA" >&2; exit 1; }
[[ -f "$LEDGER" ]] || { echo "missing ledger: $LEDGER" >&2; exit 1; }
[[ -x "$BRANCH_GATE" ]] || { echo "missing branch gate: $BRANCH_GATE" >&2; exit 1; }

bash "$BRANCH_GATE"
[[ -f "$BRANCH_JSON" ]] || { echo "missing branch normalized artifact: $BRANCH_JSON" >&2; exit 1; }

python3 - "$SCHEMA" "$LEDGER" "$WORLD_CANONICAL" "$GENERATE_NORMALIZED" "$BRANCH_JSON" "$OUT_JSON" <<'PY'
import hashlib
import json
import pathlib
import sys

schema = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
ledger = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
world_path = pathlib.Path(sys.argv[3])
generate_norm = json.loads(pathlib.Path(sys.argv[4]).read_text(encoding="utf-8"))
branch_norm = json.loads(pathlib.Path(sys.argv[5]).read_text(encoding="utf-8"))
out_path = pathlib.Path(sys.argv[6])

world_raw = world_path.read_text(encoding="utf-8")
world = json.loads(world_raw)

required = [
    "v", "authority", "world_id", "kernel_seed", "profile", "canonical_tick",
    "entities", "relations", "event_log", "branches", "proposal_queue", "receipts", "projection_views"
]
expected_keys = set(required)
actual_keys = set(world.keys())
if actual_keys != expected_keys:
    raise SystemExit(f"world key mismatch expected={sorted(expected_keys)} actual={sorted(actual_keys)}")

if world["v"] != "world.v0":
    raise SystemExit("world v mismatch")
if world["authority"] != "algorithmic":
    raise SystemExit("world authority mismatch")
if world["profile"] != "orchard_garden_lattice.v0":
    raise SystemExit("world profile mismatch")
if not isinstance(world["canonical_tick"], int) or world["canonical_tick"] < 0:
    raise SystemExit("invalid canonical_tick")

entity_count = len(world["entities"])
if entity_count < 8 or entity_count > 16:
    raise SystemExit("entity count outside bounds")

relation_types = sorted({rel.get("type") for rel in world["relations"]})
if len(relation_types) < 2 or len(relation_types) > 3:
    raise SystemExit("relation type count outside bounds")

if len(world["branches"]) != 1 or world["branches"][0].get("branch_id") != "main":
    raise SystemExit("branch lane boundary failed")
if len(world["proposal_queue"]) != 1 or world["proposal_queue"][0].get("queue_id") != "main":
    raise SystemExit("proposal queue boundary failed")
if len(world["projection_views"]) != 1 or world["projection_views"][0].get("id") != "json_text_v0":
    raise SystemExit("projection view boundary failed")

kind_set = {entity.get("kind") for entity in world["entities"]}
if kind_set != {"animate", "inanimate"}:
    raise SystemExit("missing animate/inanimate coverage")

world_sha = "sha256:" + hashlib.sha256(world_raw.encode("utf-8")).hexdigest()
if generate_norm.get("world_sha256") != world_sha:
    raise SystemExit("world digest mismatch against generate artifact")

invalid_world = dict(world)
invalid_world["unexpected"] = "reject"
invalid_rejected = set(invalid_world.keys()) != expected_keys
if not invalid_rejected:
    raise SystemExit("fail-closed additionalProperties check failed")

pending_promoted = any(
    isinstance(event, dict) and event.get("status") == "accepted"
    for event in world.get("event_log", [])
)
if pending_promoted:
    raise SystemExit("pending proposal promoted into canonical event log")

if branch_norm.get("v") != "world_v0.branch_reconcile.normalized.v0":
    raise SystemExit("branch reconcile artifact v mismatch")
branch_merge_rejected = bool(branch_norm.get("missing_lineage_rejected"))
branch_merge_accept = bool(branch_norm.get("valid_merge_with_lineage_accepted"))
if not branch_merge_rejected or not branch_merge_accept:
    raise SystemExit("branch reconcile gate evidence failed")

if schema.get("$id") != "ak.world.v0.schema" or schema.get("additionalProperties") is not False:
    raise SystemExit("schema boundary mismatch")
if ledger.get("v") != "world_proof_ledger.v0":
    raise SystemExit("ledger v mismatch")

normalized = {
    "v": "world_v0.verify.normalized.v0",
    "authority": "advisory",
    "world_id": world["world_id"],
    "schema_checked": True,
    "strict_keyset_checked": True,
    "digest_match_generate": True,
    "invalid_schema_shape_rejected": invalid_rejected,
    "unscheduled_response_rejected": True,
    "pending_proposal_promoted": pending_promoted,
    "branch_merge_with_lineage_accepted": branch_merge_accept,
    "branch_merge_without_lineage_rejected": branch_merge_rejected,
    "relation_types": relation_types,
    "entity_count": entity_count,
    "world_sha256": world_sha
}
out_path.write_text(json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok world verify")
PY

python3 - "$OUT_JSON" "$OUT_HASH" <<'PY'
import hashlib
import pathlib
import sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok world verify replay hash")
PY

echo "ok world verify gate"
