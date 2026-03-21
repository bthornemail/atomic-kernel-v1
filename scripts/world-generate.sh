#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$ROOT/artifacts"
mkdir -p "$ARTIFACTS_DIR"

WORLD_CANONICAL="$ARTIFACTS_DIR/world-v0.canonical.json"
OUT_JSON="$ARTIFACTS_DIR/world-v0.generate.normalized.json"
OUT_HASH="$ARTIFACTS_DIR/world-v0.generate.replay-hash"

python3 - "$WORLD_CANONICAL" "$OUT_JSON" <<'PY'
import hashlib
import json
import pathlib
import sys

world_path = pathlib.Path(sys.argv[1])
out_path = pathlib.Path(sys.argv[2])

entities = [
    {"id": "stone-01", "kind": "inanimate", "class": "stone", "state": "rest"},
    {"id": "stone-02", "kind": "inanimate", "class": "stone", "state": "rest"},
    {"id": "gate-01", "kind": "inanimate", "class": "gate", "state": "closed"},
    {"id": "light-01", "kind": "inanimate", "class": "light", "state": "dim"},
    {"id": "tree-01", "kind": "inanimate", "class": "tree", "state": "stable"},
    {"id": "tree-02", "kind": "inanimate", "class": "tree", "state": "stable"},
    {"id": "water-01", "kind": "inanimate", "class": "stream", "state": "flow"},
    {"id": "hive-01", "kind": "animate", "class": "hive", "state": "active"},
    {"id": "observer-01", "kind": "animate", "class": "observer", "state": "watch"},
    {"id": "gardener-01", "kind": "animate", "class": "caretaker", "state": "ready"}
]

relations = [
    {"type": "adjacent", "from": "stone-01", "to": "gate-01"},
    {"type": "adjacent", "from": "gate-01", "to": "light-01"},
    {"type": "adjacent", "from": "tree-01", "to": "water-01"},
    {"type": "nurtures", "from": "water-01", "to": "tree-01"},
    {"type": "nurtures", "from": "water-01", "to": "tree-02"},
    {"type": "observes", "from": "observer-01", "to": "gate-01"},
    {"type": "observes", "from": "observer-01", "to": "hive-01"},
    {"type": "observes", "from": "gardener-01", "to": "tree-01"}
]

world = {
    "v": "world.v0",
    "authority": "algorithmic",
    "world_id": "world0-orchard-garden-lattice",
    "kernel_seed": "ak.seed.world0.orchard_garden_lattice.v0",
    "profile": "orchard_garden_lattice.v0",
    "canonical_tick": 0,
    "entities": entities,
    "relations": relations,
    "event_log": [],
    "branches": [{"branch_id": "main", "parent": None, "status": "active"}],
    "proposal_queue": [{"queue_id": "main", "pending": []}],
    "receipts": [],
    "projection_views": [{"id": "json_text_v0", "format": "application/json", "authority": "advisory"}]
}

world_serialized = json.dumps(world, sort_keys=True, separators=(",", ":")) + "\n"
world_path.write_text(world_serialized, encoding="utf-8")
world_sha = "sha256:" + hashlib.sha256(world_serialized.encode("utf-8")).hexdigest()

kind_counts = {
    "animate": sum(1 for e in entities if e["kind"] == "animate"),
    "inanimate": sum(1 for e in entities if e["kind"] == "inanimate")
}
relation_types = sorted({r["type"] for r in relations})

normalized = {
    "v": "world_v0.generate.normalized.v0",
    "authority": "advisory",
    "world_id": world["world_id"],
    "profile": world["profile"],
    "canonical_tick": world["canonical_tick"],
    "entity_count": len(entities),
    "kind_counts": kind_counts,
    "relation_type_count": len(relation_types),
    "relation_types": relation_types,
    "branch_count": len(world["branches"]),
    "proposal_queue_count": len(world["proposal_queue"]),
    "projection_view_count": len(world["projection_views"]),
    "world_artifact": "artifacts/world-v0.canonical.json",
    "world_sha256": world_sha
}
out_path.write_text(json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok world generate")
PY

python3 - "$OUT_JSON" "$OUT_HASH" <<'PY'
import hashlib
import pathlib
import sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok world generate replay hash")
PY

echo "ok world generate gate"
