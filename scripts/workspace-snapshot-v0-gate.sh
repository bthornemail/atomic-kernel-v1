#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$ROOT/artifacts"
PROOFS_DIR="$ROOT/docs/proofs"
mkdir -p "$ARTIFACTS_DIR" "$PROOFS_DIR"

TARGET_REPO="${1:-$ROOT}"
TARGET_REPO="$(cd "$TARGET_REPO" && pwd)"

if [[ ! -d "$TARGET_REPO/.git" ]]; then
  echo "workspace snapshot gate requires a git repository: $TARGET_REPO" >&2
  exit 1
fi

NORMALIZED="$ARTIFACTS_DIR/workspace-snapshot-v0.normalized.json"
RESTORE_NORMALIZED="$ARTIFACTS_DIR/workspace-snapshot-v0.restore.normalized.json"
REPLAY_HASH="$ARTIFACTS_DIR/workspace-snapshot-v0.replay-hash"
RESTORE_HASH="$ARTIFACTS_DIR/workspace-snapshot-v0.restore.replay-hash"
BUNDLE="$ARTIFACTS_DIR/workspace-snapshot-v0.bundle"
RECEIPT="$PROOFS_DIR/workspace-snapshot-v0.latest.md"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
norm1="$tmp/norm1.json"
norm2="$tmp/norm2.json"
restore_tmp="$tmp/restore"

git -C "$TARGET_REPO" bundle create "$BUNDLE" HEAD >/dev/null

emit_normalized() {
  local out="$1"
  python3 - "$TARGET_REPO" "$BUNDLE" "$out" <<'PY'
import hashlib
import json
import pathlib
import subprocess
import sys

repo = pathlib.Path(sys.argv[1])
bundle = pathlib.Path(sys.argv[2])
out = pathlib.Path(sys.argv[3])

def run(*args: str) -> str:
  return subprocess.check_output(args, cwd=repo, text=True).strip()

head = run("git", "rev-parse", "HEAD")
tree_lines = subprocess.check_output(
  ["git", "ls-tree", "-r", "--full-tree", head],
  cwd=repo,
  text=True,
).splitlines()

files = []
for line in tree_lines:
  left, path = line.split("\t", 1)
  mode, obj_type, blob_oid = left.split()
  if obj_type != "blob":
    continue
  content = subprocess.check_output(["git", "cat-file", "-p", blob_oid], cwd=repo)
  entry = {
    "path": path,
    "sha256": "sha256:" + hashlib.sha256(content).hexdigest(),
    "bytes": len(content),
    "mode": mode,
    "blob_oid": blob_oid,
  }
  files.append(entry)

files_rollup = hashlib.sha256("\n".join(f"{f['path']}:{f['sha256']}" for f in files).encode("utf-8")).hexdigest()
bundle_sha = hashlib.sha256(bundle.read_bytes()).hexdigest()

obj = {
  "v": "workspace_snapshot.v0",
  "authority": "advisory",
  "scope": "git_tracked_files",
  "repo_root": str(repo),
  "head_commit": head,
  "file_count": len(files),
  "files_rollup_sha256": "sha256:" + files_rollup,
  "bundle": {
    "path": "artifacts/workspace-snapshot-v0.bundle",
    "sha256": "sha256:" + bundle_sha,
  },
  "files": files,
}
out.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok workspace snapshot normalized")
PY
}

emit_normalized "$norm1"
emit_normalized "$norm2"
cmp -s "$norm1" "$norm2" || {
  echo "workspace snapshot determinism check failed: normalized outputs differ" >&2
  exit 1
}
cp "$norm1" "$NORMALIZED"

python3 - "$NORMALIZED" "$BUNDLE" "$restore_tmp" "$RESTORE_NORMALIZED" <<'PY'
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

normalized = pathlib.Path(sys.argv[1])
bundle = pathlib.Path(sys.argv[2])
restore_tmp = pathlib.Path(sys.argv[3])
out = pathlib.Path(sys.argv[4])

if restore_tmp.exists():
  shutil.rmtree(restore_tmp)
restore_tmp.mkdir(parents=True, exist_ok=True)

snap = json.loads(normalized.read_text(encoding="utf-8"))
repo = restore_tmp / "repo"
subprocess.check_call(["git", "clone", str(bundle), str(repo)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.check_call(["git", "checkout", "-q", snap["head_commit"]], cwd=repo)

tree_lines = subprocess.check_output(
  ["git", "ls-tree", "-r", "--full-tree", snap["head_commit"]],
  cwd=repo,
  text=True,
).splitlines()
actual = {}
for line in tree_lines:
  left, path = line.split("\t", 1)
  mode, obj_type, blob_oid = left.split()
  if obj_type != "blob":
    continue
  actual[path] = {"mode": mode, "blob_oid": blob_oid}

expected = {f["path"]: {"mode": f["mode"], "blob_oid": f["blob_oid"]} for f in snap["files"]}
if set(actual.keys()) != set(expected.keys()):
  raise SystemExit("restore path set mismatch")

for path, expect in expected.items():
  got = actual[path]
  if got["mode"] != expect["mode"] or got["blob_oid"] != expect["blob_oid"]:
    raise SystemExit(f"restore blob mismatch: {path}")

obj = {
  "v": "workspace_snapshot_restore.v0",
  "authority": "advisory",
  "head_commit": snap["head_commit"],
  "restored_file_count": len(expected),
  "path_set_match": True,
  "blob_parity_match": True,
  "valid": True,
}
out.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok workspace snapshot restore check")
PY

python3 - "$NORMALIZED" "$REPLAY_HASH" <<'PY'
import hashlib
import pathlib
import sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok workspace snapshot replay hash")
PY

python3 - "$RESTORE_NORMALIZED" "$RESTORE_HASH" <<'PY'
import hashlib
import pathlib
import sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok workspace snapshot restore replay hash")
PY

SNAP_HASH="$(cat "$REPLAY_HASH")"
RESTORE_HASH_VAL="$(cat "$RESTORE_HASH")"
FILE_COUNT="$(python3 - "$NORMALIZED" <<'PY'
import json
import pathlib
import sys
d = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print(d["file_count"])
PY
)"
HEAD_COMMIT="$(python3 - "$NORMALIZED" <<'PY'
import json
import pathlib
import sys
d = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print(d["head_commit"])
PY
)"

cat > "$RECEIPT" <<EOF
# Workspace Snapshot v0 Proof

Generated (UTC): $(date -u +%FT%TZ)
Repo: /home/main/devops/atomic-kernel

Command:
bash scripts/workspace-snapshot-v0-gate.sh

Scope:
- git tracked files snapshot (full tracked codebase in target repo)
- deterministic normalized artifact emission
- restorable proof from snapshot bundle

Checks:
snapshot normalized deterministic rerun: PASS
bundle created from HEAD: PASS
restore clone from bundle: PASS
restore digest parity against snapshot manifest: PASS

Head Commit: $HEAD_COMMIT
Tracked File Count: $FILE_COUNT

Artifacts:
- artifacts/workspace-snapshot-v0.normalized.json
- artifacts/workspace-snapshot-v0.replay-hash ($SNAP_HASH)
- artifacts/workspace-snapshot-v0.restore.normalized.json
- artifacts/workspace-snapshot-v0.restore.replay-hash ($RESTORE_HASH_VAL)
- artifacts/workspace-snapshot-v0.bundle

Result: PASS
EOF

echo "ok workspace snapshot v0 gate receipt=$RECEIPT"
