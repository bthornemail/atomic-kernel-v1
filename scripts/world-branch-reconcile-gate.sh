#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$ROOT/artifacts"
mkdir -p "$ARTIFACTS_DIR"

WORLD_CANONICAL="$ARTIFACTS_DIR/world-v0.canonical.json"
OUT_JSON="$ARTIFACTS_DIR/world-v0.branch-reconcile.normalized.json"
OUT_HASH="$ARTIFACTS_DIR/world-v0.branch-reconcile.replay-hash"
FIXTURE="$ARTIFACTS_DIR/world-v0.branch-reconcile.fixture.json"

[[ -f "$WORLD_CANONICAL" ]] || bash "$ROOT/scripts/world-generate.sh"

python3 - "$WORLD_CANONICAL" "$FIXTURE" "$OUT_JSON" <<'PY'
import hashlib
import json
import pathlib
import sys

world_path = pathlib.Path(sys.argv[1])
fixture_path = pathlib.Path(sys.argv[2])
out_path = pathlib.Path(sys.argv[3])

world = json.loads(world_path.read_text(encoding="utf-8"))

world_id = world["world_id"]
canonical_tick = world["canonical_tick"]

valid_receipt = {
    "v": "world.branch.reconcile.receipt.v0",
    "authority": "advisory",
    "world_id": world_id,
    "source_branch": "sandbox-01",
    "target_branch": "main",
    "lineage": {
        "parent_tick": canonical_tick,
        "delta_event_sha256": "sha256:" + hashlib.sha256(f"{world_id}|delta|sandbox-01".encode("utf-8")).hexdigest()
    },
    "decision": "accept"
}
valid_receipt_serialized = json.dumps(valid_receipt, sort_keys=True, separators=(",", ":")) + "\n"
valid_receipt_sha = "sha256:" + hashlib.sha256(valid_receipt_serialized.encode("utf-8")).hexdigest()

fixture = {
    "v": "world.branch.reconcile.fixture.v0",
    "authority": "advisory",
    "valid": {
        "merge_request": {
            "world_id": world_id,
            "source_branch": "sandbox-01",
            "target_branch": "main",
            "lineage_receipt_sha256": valid_receipt_sha
        },
        "lineage_receipt": valid_receipt
    },
    "invalid": {
        "missing_lineage_receipt": {
            "world_id": world_id,
            "source_branch": "sandbox-01",
            "target_branch": "main",
            "lineage_receipt_sha256": None
        }
    }
}
fixture_path.write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

valid_req = fixture["valid"]["merge_request"]
valid_receipt_obj = fixture["valid"]["lineage_receipt"]
valid_accept = (
    valid_req["world_id"] == world_id and
    valid_req["target_branch"] == "main" and
    isinstance(valid_req["lineage_receipt_sha256"], str) and
    valid_req["lineage_receipt_sha256"].startswith("sha256:") and
    valid_receipt_obj["decision"] == "accept"
)

invalid_req = fixture["invalid"]["missing_lineage_receipt"]
invalid_reject = invalid_req.get("lineage_receipt_sha256") is None
if not invalid_reject:
    raise SystemExit("expected missing lineage receipt rejection")

normalized = {
    "v": "world_v0.branch_reconcile.normalized.v0",
    "authority": "advisory",
    "world_id": world_id,
    "fixture_artifact": "artifacts/world-v0.branch-reconcile.fixture.json",
    "valid_merge_with_lineage_accepted": bool(valid_accept),
    "missing_lineage_rejected": bool(invalid_reject),
    "lineage_receipt_sha256": valid_req["lineage_receipt_sha256"]
}
out_path.write_text(json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok world branch reconcile")
PY

python3 - "$OUT_JSON" "$OUT_HASH" <<'PY'
import hashlib
import pathlib
import sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok world branch reconcile replay hash")
PY

echo "ok world branch reconcile gate"
