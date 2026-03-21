#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$ROOT/artifacts"
mkdir -p "$ARTIFACTS_DIR"

WORLD_CANONICAL="$ARTIFACTS_DIR/world-v0.canonical.json"
OUT_JSON="$ARTIFACTS_DIR/world-v0.step.normalized.json"
OUT_HASH="$ARTIFACTS_DIR/world-v0.step.replay-hash"
PROPOSAL_JSON="$ARTIFACTS_DIR/world-v0.step.proposal.json"
RECEIPT_JSON="$ARTIFACTS_DIR/world-v0.step.receipt.json"

[[ -f "$WORLD_CANONICAL" ]] || bash "$ROOT/scripts/world-generate.sh"

python3 - "$WORLD_CANONICAL" "$PROPOSAL_JSON" "$RECEIPT_JSON" "$OUT_JSON" <<'PY'
import hashlib
import json
import pathlib
import sys

world_path = pathlib.Path(sys.argv[1])
proposal_path = pathlib.Path(sys.argv[2])
receipt_path = pathlib.Path(sys.argv[3])
out_path = pathlib.Path(sys.argv[4])

world_raw = world_path.read_text(encoding="utf-8")
world = json.loads(world_raw)

if world.get("canonical_tick") != 0:
    raise SystemExit("unexpected canonical_tick for world.v0 baseline")

entities = sorted(world["entities"], key=lambda e: e["id"])
next_tick = world["canonical_tick"] + 1

rows = []
for entity in entities:
    material = f"a14|{next_tick}|{entity['id']}"
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    eligible = (digest[1] & 1) == 1
    chirality = digest[0] & 1
    rows.append({
        "entity_id": entity["id"],
        "kind": entity["kind"],
        "eligible": eligible,
        "fano_rank": chirality,
        "schedule_digest": "sha256:" + hashlib.sha256(material.encode("utf-8")).hexdigest()
    })

eligible_ids = [r["entity_id"] for r in rows if r["eligible"]]
if not eligible_ids:
    raise SystemExit("no eligible entities at next tick")

actor_id = eligible_ids[0]
proposal_payload = {
    "target": "gate-01",
    "requested_state": "open",
    "reason": "scheduled_world_step"
}
proposal_material = f"{world['world_id']}|{next_tick}|{actor_id}|set_state|gate-01|open"
proposal_id = "proposal-" + hashlib.sha256(proposal_material.encode("utf-8")).hexdigest()[:16]

proposal = {
    "v": "world.step.proposal.v0",
    "authority": "advisory",
    "world_id": world["world_id"],
    "proposal_id": proposal_id,
    "canonical_tick": world["canonical_tick"],
    "target_tick": next_tick,
    "actor_id": actor_id,
    "action": "set_state",
    "payload": proposal_payload,
    "status": "pending",
    "eligibility_law": "A14_INCIDENCE_SCHEDULING_LAW_v0",
    "chirality_law": "CHIRALITY_SELECTION_LAW_v0"
}
proposal_serialized = json.dumps(proposal, sort_keys=True, separators=(",", ":")) + "\n"
proposal_sha = "sha256:" + hashlib.sha256(proposal_serialized.encode("utf-8")).hexdigest()
proposal_path.write_text(proposal_serialized, encoding="utf-8")

receipt = {
    "v": "world.step.receipt.v0",
    "authority": "advisory",
    "world_id": world["world_id"],
    "proposal_id": proposal_id,
    "status": "queued",
    "receipt_ref": f"receipts/{proposal_id}",
    "proposal_sha256": proposal_sha,
    "committed": False
}
receipt_serialized = json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n"
receipt_sha = "sha256:" + hashlib.sha256(receipt_serialized.encode("utf-8")).hexdigest()
receipt_path.write_text(receipt_serialized, encoding="utf-8")

ineligible = [r["entity_id"] for r in rows if not r["eligible"]]
if not ineligible:
    raise SystemExit("expected at least one ineligible entity for fail-closed test")

unscheduled_actor = ineligible[0]
unscheduled_reject = unscheduled_actor not in eligible_ids
canonical_mutated = world.get("canonical_tick") != 0 or len(world.get("event_log", [])) != 0
pending_promoted = any(evt.get("status") == "accepted" for evt in world.get("event_log", []) if isinstance(evt, dict))

if canonical_mutated:
    raise SystemExit("canonical world mutated during proposal-only step")
if pending_promoted:
    raise SystemExit("pending proposal promoted into canonical event log")
if not unscheduled_reject:
    raise SystemExit("unscheduled actor was not rejected")

schedule_snapshot = [
    {
        "entity_id": row["entity_id"],
        "eligible": row["eligible"],
        "fano_rank": row["fano_rank"],
        "kind": row["kind"]
    }
    for row in rows
]
schedule_sha = "sha256:" + hashlib.sha256(
    json.dumps(schedule_snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()

normalized = {
    "v": "world_v0.step.normalized.v0",
    "authority": "advisory",
    "world_id": world["world_id"],
    "canonical_tick": world["canonical_tick"],
    "target_tick": next_tick,
    "proposal_only": True,
    "proposal_id": proposal_id,
    "proposal_artifact": "artifacts/world-v0.step.proposal.json",
    "proposal_sha256": proposal_sha,
    "receipt_artifact": "artifacts/world-v0.step.receipt.json",
    "receipt_sha256": receipt_sha,
    "eligible_actor_count": len(eligible_ids),
    "selected_actor_id": actor_id,
    "unscheduled_actor_tested": unscheduled_actor,
    "unscheduled_rejected": unscheduled_reject,
    "canonical_world_mutated": canonical_mutated,
    "pending_proposal_promoted": pending_promoted,
    "schedule_sha256": schedule_sha
}
out_path.write_text(json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok world step")
PY

python3 - "$OUT_JSON" "$OUT_HASH" <<'PY'
import hashlib
import pathlib
import sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok world step replay hash")
PY

echo "ok world step gate"
