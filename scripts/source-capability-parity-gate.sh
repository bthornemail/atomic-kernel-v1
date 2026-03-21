#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$ROOT/artifacts"
PROOFS_DIR="$ROOT/docs/proofs"
mkdir -p "$ARTIFACTS_DIR" "$PROOFS_DIR"

NORMALIZED="$ARTIFACTS_DIR/source-capability-parity.normalized.json"
REPLAY_HASH="$ARTIFACTS_DIR/source-capability-parity.replay-hash"
RECEIPT="$PROOFS_DIR/source-capability-parity.latest.md"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
RESTORE_REPO="$TMP/restore-repo"
BASELINE_REPO="$TMP/baseline-repo"
BASELINE_DIR="$TMP/baseline"
RESTORED_DIR="$TMP/restored"
mkdir -p "$BASELINE_DIR" "$RESTORED_DIR"

# Ensure snapshot lane is fresh and restorable before parity checks.
bash "$ROOT/scripts/workspace-snapshot-v0-gate.sh" >/dev/null

SNAPSHOT_JSON="$ROOT/artifacts/workspace-snapshot-v0.normalized.json"
BUNDLE="$ROOT/artifacts/workspace-snapshot-v0.bundle"
HEAD_COMMIT="$(python3 - "$SNAPSHOT_JSON" <<'PY'
import json, pathlib, sys
obj = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print(obj["head_commit"])
PY
)"

SURFACES_FILE="$TMP/surfaces.txt"
HASH_FILES="$TMP/hash-files.txt"

cat > "$SURFACES_FILE" <<'EOF'
world:v0:gate
capability:virtual:graph
universe:v0:gate
mcp:unified:smoke
mcp:unified:stdio:smoke
EOF

surface_hashes_for() {
  local surface="$1"
  case "$surface" in
    world:v0:gate)
      cat <<'EOF'
artifacts/world-v0.generate.replay-hash
artifacts/world-v0.step.replay-hash
artifacts/world-v0.project.replay-hash
artifacts/world-v0.branch-reconcile.replay-hash
artifacts/world-v0.verify.replay-hash
artifacts/world-v0.replay-hash
EOF
      ;;
    capability:virtual:graph)
      echo "artifacts/capability-kernel-virtual-graph.replay-hash"
      ;;
    universe:v0:gate)
      cat <<'EOF'
artifacts/universe-a5-fano.replay-hash
artifacts/universe-a14-incidence-scheduling.replay-hash
artifacts/universe-v0-proof-slice.replay-hash
EOF
      ;;
    mcp:unified:smoke)
      echo "artifacts/mcp-unified-smoke.replay-hash"
      ;;
    mcp:unified:stdio:smoke)
      echo "artifacts/mcp-unified-stdio-smoke.replay-hash"
      ;;
    *)
      return 1
      ;;
  esac
}

run_core_surface() {
  local repo="$1"
  : > "$HASH_FILES"
  (
    cd "$repo"
    if [[ ! -f package.json ]]; then
      : > "$HASH_FILES"
      exit 0
    fi
    while IFS= read -r surface; do
      [[ -n "$surface" ]] || continue
      if jq -e --arg s "$surface" '.scripts[$s] != null' package.json >/dev/null 2>&1; then
        case "$surface" in
          mcp:unified:smoke)
            HOST=127.0.0.1 PORT=18887 npm run -s "$surface" >/dev/null
            ;;
          *)
            npm run -s "$surface" >/dev/null
            ;;
        esac
        surface_hashes_for "$surface" >> "$HASH_FILES"
      fi
    done < "$SURFACES_FILE"
  )
  sort -u "$HASH_FILES" -o "$HASH_FILES"
}

collect_hashes() {
  local repo="$1"
  local out_dir="$2"
  while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    src="$repo/$rel"
    [[ -f "$src" ]] || { echo "missing replay hash: $src" >&2; exit 1; }
    cp "$src" "$out_dir/$(basename "$rel")"
  done < "$HASH_FILES"
}

git clone "$BUNDLE" "$BASELINE_REPO" >/dev/null 2>&1
git -C "$BASELINE_REPO" checkout -q "$HEAD_COMMIT"
git clone "$BUNDLE" "$RESTORE_REPO" >/dev/null 2>&1
git -C "$RESTORE_REPO" checkout -q "$HEAD_COMMIT"

run_core_surface "$BASELINE_REPO"
collect_hashes "$BASELINE_REPO" "$BASELINE_DIR"
run_core_surface "$RESTORE_REPO"
collect_hashes "$RESTORE_REPO" "$RESTORED_DIR"

python3 - "$BASELINE_DIR" "$RESTORED_DIR" "$HEAD_COMMIT" "$NORMALIZED" "$HASH_FILES" <<'PY'
import json
import pathlib
import sys

baseline = pathlib.Path(sys.argv[1])
restored = pathlib.Path(sys.argv[2])
head_commit = sys.argv[3]
out = pathlib.Path(sys.argv[4])
hash_files = pathlib.Path(sys.argv[5])

rows = []
for p in sorted(baseline.glob("*.replay-hash")):
  q = restored / p.name
  if not q.exists():
    raise SystemExit(f"missing restored hash: {q}")
  b = p.read_text(encoding="utf-8").strip()
  r = q.read_text(encoding="utf-8").strip()
  rows.append({
    "artifact": p.name,
    "baseline": b,
    "restored": r,
    "match": b == r,
  })

if not all(x["match"] for x in rows):
  raise SystemExit("source-capability parity mismatch")

obj = {
  "v": "source_capability_parity.normalized.v0",
  "authority": "advisory",
  "head_commit": head_commit,
  "surface_hash_files": [x for x in hash_files.read_text(encoding="utf-8").splitlines() if x.strip()],
  "checked_hashes": len(rows),
  "rows": rows,
  "valid": True,
}
out.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok source capability parity normalized")
PY

python3 - "$NORMALIZED" "$REPLAY_HASH" <<'PY'
import hashlib
import pathlib
import sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok source capability parity replay hash")
PY

CHECKED="$(python3 - "$NORMALIZED" <<'PY'
import json, pathlib, sys
d = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print(d["checked_hashes"])
PY
)"
SHA="$(cat "$REPLAY_HASH")"

cat > "$RECEIPT" <<EOF
# Source Capability Parity v0 Proof

Generated (UTC): $(date -u +%FT%TZ)
Repo: /home/main/devops/atomic-kernel

Command:
bash scripts/source-capability-parity-gate.sh

Scope:
- restore source from workspace snapshot bundle
- rerun core world/capability/universe/MCP surfaces
- verify replay-hash parity against baseline

Head Commit: $HEAD_COMMIT
Checked Replay Hashes: $CHECKED

Artifacts:
- artifacts/source-capability-parity.normalized.json
- artifacts/source-capability-parity.replay-hash ($SHA)

Result: PASS
EOF

echo "ok source capability parity gate receipt=$RECEIPT"
