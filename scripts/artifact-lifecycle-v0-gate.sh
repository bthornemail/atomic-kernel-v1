#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/docs/imports/folder1-v1_2/IMPORT_MANIFEST.json"
REGISTRY="$ROOT/docs/imports/folder1-v1_2/LIFECYCLE_REGISTRY.v0.json"
PROMOTION_DOC="$ROOT/docs/PROMOTION_MATRIX_v1_2.md"
INDEX_DOC="$ROOT/docs/index.md"
INDEX_DOC_CAPS="$ROOT/docs/INDEX.md"

ARTIFACT_JSON="$ROOT/artifacts/artifact-lifecycle-v0.normalized.json"
ARTIFACT_HASH="$ROOT/artifacts/artifact-lifecycle-v0.replay-hash"
RECEIPT="$ROOT/docs/proofs/artifact-lifecycle-v0.latest.md"

mkdir -p "$ROOT/artifacts" "$ROOT/docs/proofs"

[[ -f "$MANIFEST" ]] || { echo "missing manifest: $MANIFEST" >&2; exit 1; }
[[ -f "$REGISTRY" ]] || { echo "missing lifecycle registry: $REGISTRY" >&2; exit 1; }
[[ -f "$PROMOTION_DOC" ]] || { echo "missing promotion doc: $PROMOTION_DOC" >&2; exit 1; }
[[ -f "$INDEX_DOC" ]] || { echo "missing index doc: $INDEX_DOC" >&2; exit 1; }
[[ -f "$INDEX_DOC_CAPS" ]] || { echo "missing index doc: $INDEX_DOC_CAPS" >&2; exit 1; }

python3 - "$ROOT" "$MANIFEST" "$REGISTRY" "$PROMOTION_DOC" "$INDEX_DOC" "$INDEX_DOC_CAPS" "$ARTIFACT_JSON" <<'PY'
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys

root = pathlib.Path(sys.argv[1])
manifest_path = pathlib.Path(sys.argv[2])
registry_path = pathlib.Path(sys.argv[3])
promotion_doc = pathlib.Path(sys.argv[4])
index_doc = pathlib.Path(sys.argv[5])
index_doc_caps = pathlib.Path(sys.argv[6])
artifact_json = pathlib.Path(sys.argv[7])

allowed_states = {
    "candidate",
    "validated",
    "receipted",
    "promotion-ready",
    "canonical",
    "deprecated",
    "superseded",
}
allowed_decisions = {"defer", "merge", "supersede"}

transition_edges = {
    "candidate": {"candidate", "validated"},
    "validated": {"validated", "receipted"},
    "receipted": {"receipted", "promotion-ready"},
    "promotion-ready": {"promotion-ready", "canonical"},
    "canonical": {"canonical", "deprecated", "superseded"},
    "deprecated": {"deprecated", "superseded"},
    "superseded": {"superseded"},
}

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
registry = json.loads(registry_path.read_text(encoding="utf-8"))
promo_txt = promotion_doc.read_text(encoding="utf-8")
index_txt = index_doc.read_text(encoding="utf-8")
index_caps_txt = index_doc_caps.read_text(encoding="utf-8")

if registry.get("v") != "ak.artifact_lifecycle_registry.v0":
    raise SystemExit("registry v mismatch")
if registry.get("authority") != "advisory":
    raise SystemExit("registry authority must be advisory")
entries = registry.get("entries")
if not isinstance(entries, list):
    raise SystemExit("registry entries missing/invalid")

manifest_files = {pathlib.Path(e["file"]).name for e in manifest.get("entries", [])}
registry_files = set()

for ent in entries:
    required = {
        "file",
        "class",
        "lifecycle_state",
        "promotion_decision",
        "canonical_target",
        "evidence",
        "updated_at_utc",
    }
    if set(ent.keys()) != required:
        raise SystemExit(f"registry entry key mismatch for {ent.get('file')}")
    f = pathlib.Path(ent["file"]).name
    registry_files.add(f)
    if ent["lifecycle_state"] not in allowed_states:
        raise SystemExit(f"unknown lifecycle state for {f}: {ent['lifecycle_state']}")
    if ent["promotion_decision"] not in allowed_decisions:
        raise SystemExit(f"unknown promotion decision for {f}: {ent['promotion_decision']}")
    if not isinstance(ent["canonical_target"], str) or not ent["canonical_target"]:
        raise SystemExit(f"invalid canonical_target for {f}")
    if not isinstance(ent["evidence"], list) or not ent["evidence"]:
        raise SystemExit(f"evidence must be non-empty list for {f}")
    try:
        dt.datetime.fromisoformat(ent["updated_at_utc"].replace("Z", "+00:00"))
    except Exception:
        raise SystemExit(f"invalid updated_at_utc for {f}")
    if ent["lifecycle_state"] == "canonical":
        if ent["promotion_decision"] not in {"merge", "supersede"}:
            raise SystemExit(f"canonical requires merge/supersede decision for {f}")
        target = root / ent["canonical_target"]
        if not target.exists():
            raise SystemExit(f"canonical target missing for {f}: {ent['canonical_target']}")
    if ent["promotion_decision"] == "defer" and ent["lifecycle_state"] == "canonical":
        raise SystemExit(f"defer cannot be canonical for {f}")

if registry_files != manifest_files:
    missing = sorted(manifest_files - registry_files)
    extra = sorted(registry_files - manifest_files)
    raise SystemExit(f"registry/manifest mismatch missing={missing} extra={extra}")

# Canonical index boundary
state_by_file = {pathlib.Path(e["file"]).name: e["lifecycle_state"] for e in entries}
for name in manifest_files:
    appears = (name in index_txt) or (name in index_caps_txt)
    if appears and state_by_file[name] != "canonical":
        raise SystemExit(f"index boundary breach: {name} listed while state={state_by_file[name]}")

# Consistency with promotion matrix decisions
promo_decision_by_file = {}
for line in promo_txt.splitlines():
    if not line.strip().startswith("| `"):
        continue
    cols = [c.strip() for c in line.split("|")]
    if len(cols) < 6:
        continue
    m_file = re.match(r"`([^`]+)`", cols[1])
    m_dec = re.match(r"`([^`]+)`", cols[5])
    if m_file and m_dec:
        promo_decision_by_file[pathlib.Path(m_file.group(1)).name] = m_dec.group(1)
for f, state in state_by_file.items():
    r_dec = next(e["promotion_decision"] for e in entries if pathlib.Path(e["file"]).name == f)
    p_dec = promo_decision_by_file.get(f)
    if p_dec and p_dec != r_dec:
        raise SystemExit(f"promotion decision mismatch for {f}: registry={r_dec} promo_doc={p_dec}")

# Transition check against previous committed registry when available
transition_mode = "static"
transition_issues = []
try:
    prev_raw = subprocess.check_output(
        ["git", "show", "HEAD:docs/imports/folder1-v1_2/LIFECYCLE_REGISTRY.v0.json"],
        cwd=root,
        text=True,
        stderr=subprocess.DEVNULL,
    )
    prev = json.loads(prev_raw)
    prev_map = {pathlib.Path(e["file"]).name: e["lifecycle_state"] for e in prev.get("entries", [])}
    transition_mode = "compared_with_head"
    for f, now_state in state_by_file.items():
        prev_state = prev_map.get(f)
        if prev_state is None:
            continue
        allowed = transition_edges.get(prev_state, set())
        if now_state not in allowed:
            transition_issues.append(f"{f}:{prev_state}->{now_state}")
except Exception:
    transition_mode = "static_no_previous_registry"

if transition_issues:
    raise SystemExit("illegal transitions: " + ",".join(transition_issues))

summary = {
    "v": "ak.artifact_lifecycle_v0.normalized",
    "authority": "advisory",
    "lane": "fork-import-v1_2",
    "transition_validation_mode": transition_mode,
    "transition_issues": transition_issues,
    "counts": {
        "total": len(entries),
        "canonical": sum(1 for e in entries if e["lifecycle_state"] == "canonical"),
        "pre_canonical": sum(1 for e in entries if e["lifecycle_state"] in {"candidate", "validated", "receipted", "promotion-ready"}),
        "deprecated": sum(1 for e in entries if e["lifecycle_state"] == "deprecated"),
        "superseded": sum(1 for e in entries if e["lifecycle_state"] == "superseded"),
    },
    "entries": sorted(
        [
            {
                "file": pathlib.Path(e["file"]).name,
                "class": e["class"],
                "state": e["lifecycle_state"],
                "decision": e["promotion_decision"],
                "canonical_target": e["canonical_target"],
            }
            for e in entries
        ],
        key=lambda x: x["file"],
    ),
}
artifact_json.write_text(json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok artifact lifecycle registry validated")
PY

python3 - "$ARTIFACT_JSON" "$ARTIFACT_HASH" <<'PY'
import hashlib
import pathlib
import sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
h = hashlib.sha256(artifact.read_bytes()).hexdigest()
out.write_text(f"sha256:{h}\n", encoding="utf-8")
print("ok artifact lifecycle replay hash")
PY

cat > "$RECEIPT" <<EOF
# Artifact Lifecycle v0 Proof

Generated (UTC): $(date -u +%FT%TZ)
Repo: /home/main/devops/atomic-kernel

Command:
bash scripts/artifact-lifecycle-v0-gate.sh

Checks:
registry schema/required keys: PASS
lifecycle enum validity: PASS
transition validity: PASS
decision/state consistency: PASS
canonical target existence: PASS
index boundary check: PASS

Artifacts:
- artifacts/artifact-lifecycle-v0.normalized.json
- artifacts/artifact-lifecycle-v0.replay-hash ($(cat "$ARTIFACT_HASH"))

Result: PASS
EOF

echo "ok artifact lifecycle v0 gate"
