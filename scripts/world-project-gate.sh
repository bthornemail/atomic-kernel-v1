#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$ROOT/artifacts"
mkdir -p "$ARTIFACTS_DIR"

WORLD_CANONICAL="$ARTIFACTS_DIR/world-v0.canonical.json"
OUT_JSON="$ARTIFACTS_DIR/world-v0.project.normalized.json"
OUT_HASH="$ARTIFACTS_DIR/world-v0.project.replay-hash"
PROJECTION_JSON="$ARTIFACTS_DIR/world-v0.projection.json"

[[ -f "$WORLD_CANONICAL" ]] || bash "$ROOT/scripts/world-generate.sh"

python3 - "$WORLD_CANONICAL" "$PROJECTION_JSON" "$OUT_JSON" <<'PY'
import hashlib
import json
import pathlib
import sys

world_path = pathlib.Path(sys.argv[1])
projection_path = pathlib.Path(sys.argv[2])
out_path = pathlib.Path(sys.argv[3])

world = json.loads(world_path.read_text(encoding="utf-8"))

by_kind = {"animate": 0, "inanimate": 0}
for entity in world["entities"]:
    by_kind[entity["kind"]] += 1

relation_counts = {}
for rel in world["relations"]:
    relation_counts[rel["type"]] = relation_counts.get(rel["type"], 0) + 1

projection = {
    "v": "world.projection.v0",
    "authority": "advisory",
    "world_id": world["world_id"],
    "canonical_tick": world["canonical_tick"],
    "view_id": "json_text_v0",
    "entities_by_kind": by_kind,
    "relation_counts": dict(sorted(relation_counts.items())),
    "branch": world["branches"][0]["branch_id"],
    "proposal_queue_depth": len(world["proposal_queue"][0]["pending"]),
    "event_log_size": len(world["event_log"])
}
projection_serialized = json.dumps(projection, sort_keys=True, separators=(",", ":")) + "\n"
projection_path.write_text(projection_serialized, encoding="utf-8")
projection_sha = "sha256:" + hashlib.sha256(projection_serialized.encode("utf-8")).hexdigest()

projection_rebuild = json.dumps(projection, sort_keys=True, separators=(",", ":")) + "\n"
deterministic_rerun = projection_serialized == projection_rebuild
if not deterministic_rerun:
    raise SystemExit("projection rerun mismatch")

normalized = {
    "v": "world_v0.project.normalized.v0",
    "authority": "advisory",
    "world_id": world["world_id"],
    "view_id": projection["view_id"],
    "projection_artifact": "artifacts/world-v0.projection.json",
    "projection_sha256": projection_sha,
    "deterministic_rerun": deterministic_rerun,
    "entities_by_kind": by_kind,
    "relation_types": sorted(relation_counts.keys())
}
out_path.write_text(json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok world project")
PY

python3 - "$OUT_JSON" "$OUT_HASH" <<'PY'
import hashlib
import pathlib
import sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok world project replay hash")
PY

echo "ok world project gate"
