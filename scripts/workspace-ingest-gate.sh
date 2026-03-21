#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

WS="$TMP/workspace"
CANON_OUT="$TMP/canonical"
MIRROR_OUT="$TMP/mirror"
mkdir -p "$WS" "$CANON_OUT" "$MIRROR_OUT"

mk_git_repo() {
  local dir="$1"
  shift
  mkdir -p "$dir"
  git -C "$dir" init -q
  git -C "$dir" config user.email "gate@example.com"
  git -C "$dir" config user.name "workspace-gate"
  while [[ $# -gt 0 ]]; do
    local path="$1"
    local body="$2"
    shift 2
    mkdir -p "$(dirname "$dir/$path")"
    printf '%s' "$body" > "$dir/$path"
  done
  git -C "$dir" add .
  git -C "$dir" commit -q -m "init"
}

# alpha: python + excluded dirs
mk_git_repo "$WS/alpha-proj" \
  "src/main.py" $'class ServiceFacade:\n  def run(self):\n    return 1\n' \
  "node_modules/pkg/nope.ts" $'export const ignored = 1;\n' \
  "fixtures/bad.ts" $'function broken( {\n'

# beta: typescript
mk_git_repo "$WS/beta-proj" \
  "src/mod.ts" $'export class AdapterImpl extends AdapterBase {}\n'

# gamma: mjs
mk_git_repo "$WS/gamma-proj" \
  "src/bridge.mjs" $'export class BridgeLayer extends AdapterBase { map(x){ return x; } }\n'

# marker-only discovery, non-analyzable
mkdir -p "$WS/docs-only"
printf '{}' > "$WS/docs-only/package.json"

MANIFEST="$TMP/workspace-manifest.json"
RUN1="workspace-gate-run-1"
RUN2="workspace-gate-run-2"

OVERLAY_DIR="$ROOT/runtime/atomic_kernel/overlays/project-analysis"
if [[ -d "$OVERLAY_DIR" ]]; then
  for f in "$OVERLAY_DIR"/*.overlay.json; do
    [[ -f "$f" ]] || continue
    python3 "$ROOT/scripts/validate-project-analysis-overlay.py" --file "$f" >/dev/null
  done
fi

python3 "$ROOT/scripts/build-workspace-manifest.py" --workspace "$WS" --out "$MANIFEST" >/dev/null
python3 "$ROOT/scripts/validate-workspace-manifest.py" --manifest "$MANIFEST" >/dev/null

bash "$ROOT/scripts/run-workspace-ingest.sh" \
  --workspace "$WS" \
  --manifest "$MANIFEST" \
  --out-root "$CANON_OUT" \
  --run-id "$RUN1" \
  --allowlist "alpha-proj,beta-proj,gamma-proj" \
  --mirror-root "$MIRROR_OUT" \
  >/dev/null

bash "$ROOT/scripts/run-workspace-ingest.sh" \
  --workspace "$WS" \
  --manifest "$MANIFEST" \
  --out-root "$CANON_OUT" \
  --run-id "$RUN2" \
  --allowlist "alpha-proj,beta-proj,gamma-proj" \
  --mirror-root "$MIRROR_OUT" \
  >/dev/null

SUM1="$CANON_OUT/$RUN1/workspace-summary.json"
SUM2="$CANON_OUT/$RUN2/workspace-summary.json"
IDX1="$CANON_OUT/$RUN1/project-index.json"
IDX2="$CANON_OUT/$RUN2/project-index.json"

python3 "$ROOT/scripts/validate-workspace-summary.py" --summary "$SUM1" >/dev/null
python3 "$ROOT/scripts/validate-workspace-summary.py" --summary "$SUM2" >/dev/null

python3 - <<PY >/dev/null
import json
from pathlib import Path

manifest = json.loads(Path(r"$MANIFEST").read_text(encoding="utf-8"))
for p in manifest["projects"]:
  assert p["authority"] == "advisory"

summary = json.loads(Path(r"$SUM1").read_text(encoding="utf-8"))
assert summary["authority"] == "advisory"
cov = summary["coverage"]
assert cov["discovered"] == summary["projects_total"]
assert cov["analyzed"] == summary["projects_analyzed"]

# allowlist behavior + discovery-visible non-analyzable
rows = {r["project_id"]: r for r in summary["project_reports"]}
assert rows["alpha-proj"]["analyzed"] is True
assert rows["beta-proj"]["analyzed"] is True
assert rows["gamma-proj"]["analyzed"] is True
assert rows["docs-only"]["analyzed"] is False

# path confinement + disallowed directories
run_dir = Path(r"$CANON_OUT") / r"$RUN1"
for pid in ("alpha-proj", "beta-proj", "gamma-proj"):
  root_path = Path(rows[pid]["root_path"]).resolve()
  asg_dir = run_dir / "projects" / pid / "asg"
  for frame_path in sorted(asg_dir.glob("*.json")):
    frame = json.loads(frame_path.read_text(encoding="utf-8"))
    provenance = frame.get("provenance", {})
    if not isinstance(provenance, dict):
      raise AssertionError("frame provenance invalid")
    rel = provenance.get("source_path")
    if not isinstance(rel, str) or not rel:
      raise AssertionError("frame provenance.source_path invalid")
    assert "node_modules/" not in rel
    assert "/fixtures/" not in f"/{rel}"
    src = (root_path / rel).resolve()
    assert str(src).startswith(str(root_path) + "/") or str(src) == str(root_path)

# deterministic semantics across run ids (ignore run-id-bearing fields)
sum1 = json.loads(Path(r"$SUM1").read_text(encoding="utf-8"))
sum2 = json.loads(Path(r"$SUM2").read_text(encoding="utf-8"))
def stable_view(s):
  return {
    "workspace_root": s["workspace_root"],
    "projects_total": s["projects_total"],
    "projects_analyzed": s["projects_analyzed"],
    "projects_skipped": s["projects_skipped"],
    "coverage": s["coverage"],
    "project_reports": s["project_reports"],
    "aggregate_counts": s["aggregate_counts"],
    "inputs_digest": s["inputs_digest"],
  }
assert stable_view(sum1) == stable_view(sum2)

idx1 = json.loads(Path(r"$IDX1").read_text(encoding="utf-8"))
idx2 = json.loads(Path(r"$IDX2").read_text(encoding="utf-8"))
assert idx1["projects"] == idx2["projects"]

# mirrored summary/index present
for rid in (r"$RUN1", r"$RUN2"):
  base = Path(r"$MIRROR_OUT") / rid
  assert (base / "workspace-summary.json").is_file()
  assert (base / "workspace-summary.md").is_file()
  assert (base / "project-index.json").is_file()
PY

echo "ok workspace-ingest gate"
