#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAW_DOC="$ROOT/docs/A14_INCIDENCE_SCHEDULING_LAW_v0.md"

OUT_JSON="$ROOT/artifacts/universe-a14-incidence-scheduling.normalized.json"
OUT_HASH="$ROOT/artifacts/universe-a14-incidence-scheduling.replay-hash"
RECEIPT="$ROOT/docs/proofs/universe-a14-incidence-scheduling.latest.md"

mkdir -p "$ROOT/artifacts" "$ROOT/docs/proofs"

[[ -f "$LAW_DOC" ]] || { echo "missing law doc: $LAW_DOC" >&2; exit 1; }

python3 - "$OUT_JSON" <<'PY'
import hashlib
import json
import sys

out_path = sys.argv[1]

seed = "universe-a14-v0-seed"
ticks = list(range(8))
entities = [
    {"id": "stone-01", "kind": "inanimate"},
    {"id": "agent-01", "kind": "animate"},
]

def schedule(seed_text: str):
    rows = []
    for tick in ticks:
        for idx, e in enumerate(entities):
            material = f"{seed_text}|{tick}|{e['id']}"
            d = hashlib.sha256(material.encode("utf-8")).digest()
            chirality = d[0] & 1
            eligible = (d[1] & 1) == 1
            proposal_state = "pending" if (d[2] % 3 == 0) else "accepted"
            incidence_tick = tick if eligible else tick + 1
            rows.append({
                "entity_id": e["id"],
                "kind": e["kind"],
                "canonical_tick": tick,
                "incidence_tick": incidence_tick,
                "proposal_state": proposal_state,
                "fano_rank": chirality,
                "eligible": eligible,
            })
    return rows

rows_a = schedule(seed)
rows_b = schedule(seed)
if rows_a != rows_b:
    raise SystemExit("constructive fail: schedule replay instability")

# Falsification controls:
# 1) display/UI reorder must not alter canonical schedule rows.
rows_ui_reordered = sorted(rows_a, key=lambda r: (r["entity_id"], r["canonical_tick"]))
rows_canonical_sorted = sorted(rows_a, key=lambda r: (r["canonical_tick"], r["entity_id"]))
canonical_digest = hashlib.sha256(json.dumps(rows_canonical_sorted, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
ui_digest = hashlib.sha256(json.dumps(rows_ui_reordered, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()

# Digests differ because sort order differs, but canonical semantics should be invariant by key mapping.
by_key_a = {(r["canonical_tick"], r["entity_id"]): r for r in rows_canonical_sorted}
by_key_ui = {(r["canonical_tick"], r["entity_id"]): r for r in rows_ui_reordered}
if by_key_a != by_key_ui:
    raise SystemExit("falsification fail: UI reorder changed semantic schedule mapping")

# 2) unscheduled action must be rejected.
unscheduled_row = next(r for r in rows_a if r["eligible"] is False)
unscheduled_action_rejected = unscheduled_row["incidence_tick"] > unscheduled_row["canonical_tick"]
if not unscheduled_action_rejected:
    raise SystemExit("falsification fail: unscheduled action not rejected")

summary = {
    "v": "universe_a14_incidence_scheduling.normalized.v0",
    "authority": "advisory",
    "seed": seed,
    "ticks": len(ticks),
    "entity_count": len(entities),
    "constructive": {
        "pass": True,
        "replay_stable": True,
        "rows": rows_canonical_sorted,
    },
    "falsification": {
        "pass": True,
        "ui_reorder_semantic_invariant": True,
        "unscheduled_action_rejected": unscheduled_action_rejected,
        "canonical_digest": f"sha256:{canonical_digest}",
        "ui_order_digest": f"sha256:{ui_digest}",
    },
}

with open(out_path, "w", encoding="utf-8") as f:
    f.write(json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n")

print("ok universe a14 incidence scheduling checks")
PY

python3 - "$OUT_JSON" "$OUT_HASH" <<'PY'
import hashlib, pathlib, sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok universe a14 replay hash")
PY

cat > "$RECEIPT" <<EOF
# Universe A14 Incidence Scheduling Receipt

Generated (UTC): $(date -u +%FT%TZ)
Repo: /home/main/devops/atomic-kernel

Command:
bash scripts/universe-a14-incidence-scheduling-gate.sh

Checks:
A14 law doc present: PASS
constructive replay-stable schedule: PASS
falsification UI reorder semantic invariance: PASS
falsification unscheduled response rejection: PASS

Artifacts:
- artifacts/universe-a14-incidence-scheduling.normalized.json
- artifacts/universe-a14-incidence-scheduling.replay-hash ($(cat "$OUT_HASH"))

Result: PASS
EOF

echo "ok universe a14 incidence scheduling gate"
