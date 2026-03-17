#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

ACCEPT_DIR="$ROOT/runtime/atomic_kernel/fixtures/pattern-extraction/accept"
REJECT_DIR="$ROOT/runtime/atomic_kernel/fixtures/pattern-extraction/must-reject"
REPORT="$ROOT/reports/phase27N-pattern-extraction.json"
GOLDEN_HASH="$ROOT/golden/pattern-extraction/replay-hash"

[[ -d "$ACCEPT_DIR" ]] || { echo "missing accept fixtures: $ACCEPT_DIR" >&2; exit 2; }
[[ -d "$REJECT_DIR" ]] || { echo "missing reject fixtures: $REJECT_DIR" >&2; exit 2; }
[[ -f "$GOLDEN_HASH" ]] || { echo "missing golden hash: $GOLDEN_HASH" >&2; exit 2; }

mkdir -p "$(dirname "$REPORT")"
TMP_JSON="$(mktemp)"
CASES_FILE="$(mktemp)"
trap 'rm -f "$TMP_JSON" "$CASES_FILE"' EXIT

accept_count=0
while IFS= read -r asg; do
  base="$(basename "$asg")"
  name="${base#asg-}"
  name="${name%.json}"
  expected="$ACCEPT_DIR/expected-${name}.json"
  [[ -f "$expected" ]] || { echo "missing expected fixture: $expected" >&2; exit 2; }

  python3 "$ROOT/scripts/extract-patterns.py" --asg "$asg" --out "$TMP_JSON" >/dev/null
  cmp -s "$TMP_JSON" "$expected" || {
    echo "pattern extraction mismatch for $base" >&2
    exit 1
  }

  pattern_count="$(python3 - <<PY
import json
from pathlib import Path
d = json.loads(Path(r"$TMP_JSON").read_text(encoding="utf-8"))
print(len(d["patterns"]))
PY
)"
  types_csv="$(python3 - <<PY
import json
from pathlib import Path
d = json.loads(Path(r"$TMP_JSON").read_text(encoding="utf-8"))
types = sorted({p["pattern_type"] for p in d["patterns"]})
print(",".join(types))
PY
)"
  json_sha="sha256:$(sha256sum "$TMP_JSON" | awk '{print $1}')"
  printf '%s\t%s\t%s\t%s\n' "$name" "$pattern_count" "$types_csv" "$json_sha" >> "$CASES_FILE"
  accept_count=$((accept_count + 1))
done < <(find "$ACCEPT_DIR" -maxdepth 1 -type f -name 'asg-*.json' | sort)

[[ "$accept_count" -gt 0 ]] || { echo "no accept ASG fixtures found" >&2; exit 2; }

reject_count=0
for f in "$REJECT_DIR"/bad-asg-*.json; do
  [[ -f "$f" ]] || continue
  if python3 "$ROOT/scripts/extract-patterns.py" --asg "$f" --out "$TMP_JSON" >/dev/null 2>&1; then
    echo "must-reject ASG accepted: $f" >&2
    exit 1
  fi
  reject_count=$((reject_count + 1))
done

python3 - <<PY > "$REPORT"
import hashlib
import json
from pathlib import Path

cases = []
for line in Path(r"$CASES_FILE").read_text(encoding="utf-8").splitlines():
  name, pattern_count, types_csv, json_sha = line.split("\t")
  cases.append({
    "name": name,
    "pattern_count": int(pattern_count),
    "pattern_types": [t for t in types_csv.split(",") if t],
    "json_sha": json_sha,
  })
cases.sort(key=lambda c: c["name"])
types_digest = hashlib.sha256(
  json.dumps([c["pattern_types"] for c in cases], sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()
report = {
  "v": "phase27N.pattern_extraction_gate.v0",
  "authority": "advisory",
  "summary": {
    "accept": len(cases),
    "must_reject": int($reject_count),
  },
  "types_digest": f"sha256:{types_digest}",
  "cases": cases,
}
print(json.dumps(report, sort_keys=True, separators=(",", ":")))
PY

want="$(tr -d '\n' < "$GOLDEN_HASH")"
got="sha256:$(sha256sum "$REPORT" | awk '{print $1}')"
if [[ "$want" != "$got" ]]; then
  echo "pattern-extraction replay hash mismatch: expected $want got $got" >&2
  exit 1
fi

echo "ok pattern-extraction gate"

