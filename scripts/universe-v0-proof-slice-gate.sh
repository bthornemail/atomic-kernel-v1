#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPEC="$ROOT/docs/UNIVERSE_SPEC_v0.md"
SCHEMA="$ROOT/docs/universe.v0.schema.json"
LEDGER="$ROOT/docs/UNIVERSE_PROOF_LEDGER_v0.json"
A5_GATE="$ROOT/scripts/universe-a5-fano-gate.sh"
A5_HASH="$ROOT/artifacts/universe-a5-fano.replay-hash"
A5_JSON="$ROOT/artifacts/universe-a5-fano.normalized.json"
A14_GATE="$ROOT/scripts/universe-a14-incidence-scheduling-gate.sh"
A14_HASH="$ROOT/artifacts/universe-a14-incidence-scheduling.replay-hash"
A14_JSON="$ROOT/artifacts/universe-a14-incidence-scheduling.normalized.json"

OUT_JSON="$ROOT/artifacts/universe-v0-proof-slice.normalized.json"
OUT_HASH="$ROOT/artifacts/universe-v0-proof-slice.replay-hash"
RECEIPT="$ROOT/docs/proofs/universe-v0-proof-slice.latest.md"

mkdir -p "$ROOT/artifacts" "$ROOT/docs/proofs"

[[ -f "$SPEC" ]] || { echo "missing spec: $SPEC" >&2; exit 1; }
[[ -f "$SCHEMA" ]] || { echo "missing schema: $SCHEMA" >&2; exit 1; }
[[ -f "$LEDGER" ]] || { echo "missing ledger: $LEDGER" >&2; exit 1; }
[[ -x "$A5_GATE" ]] || { echo "missing executable A5 gate: $A5_GATE" >&2; exit 1; }
[[ -x "$A14_GATE" ]] || { echo "missing executable A14 gate: $A14_GATE" >&2; exit 1; }

bash "$A5_GATE"
[[ -f "$A5_HASH" ]] || { echo "missing A5 replay hash artifact: $A5_HASH" >&2; exit 1; }
[[ -f "$A5_JSON" ]] || { echo "missing A5 normalized artifact: $A5_JSON" >&2; exit 1; }
bash "$A14_GATE"
[[ -f "$A14_HASH" ]] || { echo "missing A14 replay hash artifact: $A14_HASH" >&2; exit 1; }
[[ -f "$A14_JSON" ]] || { echo "missing A14 normalized artifact: $A14_JSON" >&2; exit 1; }

python3 - "$A5_JSON" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))
if d.get("v") != "universe_a5_fano.normalized.v0":
    raise SystemExit("a5 normalized v mismatch")
for section, key in [
    ("constructive", "pass"),
    ("constructive", "replay_stable"),
    ("falsification", "pass"),
    ("falsification", "label_swap_invariant"),
    ("falsification", "ui_reorder_invariant"),
    ("falsification", "seed_variation_diverges"),
]:
    if d.get(section, {}).get(key) is not True:
        raise SystemExit(f"a5 invariant failed: {section}.{key}")
print("ok universe a5 invariants validated")
PY

python3 - "$A14_JSON" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))
if d.get("v") != "universe_a14_incidence_scheduling.normalized.v0":
    raise SystemExit("a14 normalized v mismatch")
for section, key in [
    ("constructive", "pass"),
    ("constructive", "replay_stable"),
    ("falsification", "pass"),
    ("falsification", "ui_reorder_semantic_invariant"),
    ("falsification", "unscheduled_action_rejected"),
]:
    if d.get(section, {}).get(key) is not True:
        raise SystemExit(f"a14 invariant failed: {section}.{key}")
print("ok universe a14 invariants validated")
PY

python3 - "$LEDGER" "$OUT_JSON" <<'PY'
import json, pathlib, sys
ledger_path = pathlib.Path(sys.argv[1])
out_path = pathlib.Path(sys.argv[2])

allowed_forms = {"constructive", "falsification"}
allowed_questions = {f"Q{i}" for i in range(1, 9)}
allowed_status = {"planned", "in_progress", "pass", "fail"}

data = json.loads(ledger_path.read_text(encoding="utf-8"))
required_top = {"v", "authority", "universe_artifact", "matrix_target", "phase1_slice_target", "algorithms", "entries"}
if set(data.keys()) != required_top:
    raise SystemExit("ledger top-level keys mismatch")
if data["v"] != "universe_proof_ledger.v0":
    raise SystemExit("ledger v mismatch")
if data["authority"] != "advisory":
    raise SystemExit("ledger authority must be advisory")
if data["phase1_slice_target"] != 16:
    raise SystemExit("phase1_slice_target must be 16")
if data["matrix_target"] != "8x7x2":
    raise SystemExit("matrix_target mismatch")
if not isinstance(data["algorithms"], list) or len(data["algorithms"]) != 7:
    raise SystemExit("algorithms must be list of 7")

entries = data["entries"]
if not isinstance(entries, list) or len(entries) != 16:
    raise SystemExit("entries must be list of 16")

seen_ids = set()
by_q = {q: set() for q in allowed_questions}
for e in entries:
    req = {"id", "question", "form", "algorithm_focus", "status", "evidence"}
    if set(e.keys()) != req:
        raise SystemExit(f"entry keys mismatch: {e}")
    if e["id"] in seen_ids:
        raise SystemExit(f"duplicate entry id: {e['id']}")
    seen_ids.add(e["id"])
    if e["question"] not in allowed_questions:
        raise SystemExit(f"invalid question: {e['question']}")
    if e["form"] not in allowed_forms:
        raise SystemExit(f"invalid form: {e['form']}")
    if e["status"] not in allowed_status:
        raise SystemExit(f"invalid status: {e['status']}")
    if e["algorithm_focus"] not in data["algorithms"]:
        raise SystemExit(f"unknown algorithm_focus: {e['algorithm_focus']}")
    if not isinstance(e["evidence"], str) or not e["evidence"]:
        raise SystemExit("evidence must be non-empty string")
    by_q[e["question"]].add(e["form"])

for q, forms in by_q.items():
    if forms != allowed_forms:
        raise SystemExit(f"question {q} must include both constructive and falsification forms")

summary = {
    "v": "universe_v0.proof_slice.normalized.v0",
    "authority": "advisory",
    "phase1_slice_target": 16,
    "entry_count": len(entries),
    "question_count": len(by_q),
    "forms_per_question_valid": True,
    "status_counts": {
        "planned": sum(1 for e in entries if e["status"] == "planned"),
        "in_progress": sum(1 for e in entries if e["status"] == "in_progress"),
        "pass": sum(1 for e in entries if e["status"] == "pass"),
        "fail": sum(1 for e in entries if e["status"] == "fail"),
    }
}
out_path.write_text(json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok universe proof slice validated")
PY

python3 - "$OUT_JSON" "$OUT_HASH" <<'PY'
import hashlib, pathlib, sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok universe proof slice replay hash")
PY

cat > "$RECEIPT" <<EOF
# Universe v0 Proof Slice Receipt

Generated (UTC): $(date -u +%FT%TZ)
Repo: /home/main/devops/atomic-kernel

Command:
bash scripts/universe-v0-proof-slice-gate.sh

Checks:
A5 Fano selection gate: PASS
A5 chirality invariants (label/ui/seed/replay): PASS
A14 incidence scheduling gate: PASS
A14 eligibility invariants (replay/ui/unscheduled): PASS
ledger schema and required keys: PASS
phase1 entry count (16): PASS
Q1-Q8 constructive/falsification pairing: PASS
algorithm focus allowlist (7): PASS

Artifacts:
- artifacts/universe-a5-fano.replay-hash ($(cat "$A5_HASH"))
- artifacts/universe-a14-incidence-scheduling.replay-hash ($(cat "$A14_HASH"))
- artifacts/universe-v0-proof-slice.normalized.json
- artifacts/universe-v0-proof-slice.replay-hash ($(cat "$OUT_HASH"))

Result: PASS
EOF

echo "ok universe v0 proof slice gate"
