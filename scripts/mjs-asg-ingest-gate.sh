#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

ACCEPT_DIR="$ROOT/runtime/atomic_kernel/fixtures/mjs-asg-ingest/accept"
REJECT_DIR="$ROOT/runtime/atomic_kernel/fixtures/mjs-asg-ingest/must-reject"
REPORT="$ROOT/reports/phase27P-mjs-asg-ingest.json"
GOLDEN_HASH="$ROOT/golden/mjs-asg-ingest/replay-hash"

[[ -d "$ACCEPT_DIR" ]] || { echo "missing accept fixtures: $ACCEPT_DIR" >&2; exit 2; }
[[ -d "$REJECT_DIR" ]] || { echo "missing reject fixtures: $REJECT_DIR" >&2; exit 2; }
[[ -f "$GOLDEN_HASH" ]] || { echo "missing golden hash: $GOLDEN_HASH" >&2; exit 2; }

if ! node -e "require('acorn')" >/dev/null 2>&1; then
  [[ -f "$ROOT/package.json" ]] || { echo "missing package.json for mjs parser bootstrap" >&2; exit 2; }
  [[ -f "$ROOT/package-lock.json" ]] || { echo "missing package-lock.json for mjs parser bootstrap" >&2; exit 2; }
  npm ci --silent >/dev/null
  node -e "require('acorn')" >/dev/null 2>&1 || { echo "acorn unavailable after bootstrap" >&2; exit 2; }
fi

mkdir -p "$(dirname "$REPORT")"
TMP_JSON="$(mktemp)"
CASES_FILE="$(mktemp)"
trap 'rm -f "$TMP_JSON" "$CASES_FILE"' EXIT

accept_count=0
while IFS= read -r src; do
  base="$(basename "$src")"
  stem="${base#source-}"
  name="${stem%.*}"
  expected="$ACCEPT_DIR/expected-${name}.json"
  [[ -f "$expected" ]] || { echo "missing expected fixture: $expected" >&2; exit 2; }

  python3 "$ROOT/scripts/ingest-mjs-asg.py" \
    --input "$src" \
    --source-path "fixtures/mjs-asg-ingest/accept/$base" \
    --namespace "demo.${name}" \
    --out "$TMP_JSON" \
    >/dev/null

  cmp -s "$TMP_JSON" "$expected" || {
    echo "mjs asg ingest mismatch for $base" >&2
    exit 1
  }

  python3 "$ROOT/scripts/validate-asg.py" --file "$TMP_JSON" >/dev/null

  frame_hash="$(python3 - <<PY
import json
from pathlib import Path
p = Path(r"$TMP_JSON")
print(json.loads(p.read_text(encoding='utf-8'))['graph_hash'])
PY
)"
  json_sha="sha256:$(sha256sum "$TMP_JSON" | awk '{print $1}')"
  printf '%s\t%s\t%s\n' "$name" "$frame_hash" "$json_sha" >> "$CASES_FILE"
  accept_count=$((accept_count + 1))
done < <(find "$ACCEPT_DIR" -maxdepth 1 -type f -name 'source-*.mjs' | sort)

[[ "$accept_count" -gt 0 ]] || { echo "no accept source fixtures found" >&2; exit 2; }

reject_count=0
for f in "$REJECT_DIR"/bad-source-*.mjs; do
  [[ -f "$f" ]] || continue
  if python3 "$ROOT/scripts/ingest-mjs-asg.py" \
    --input "$f" \
    --source-path "fixtures/mjs-asg-ingest/must-reject/$(basename "$f")" \
    --namespace "reject" \
    --out "$TMP_JSON" \
    >/dev/null 2>&1; then
    echo "must-reject source accepted: $f" >&2
    exit 1
  fi
  reject_count=$((reject_count + 1))
done

python3 - <<PY > "$REPORT"
import json
from pathlib import Path

cases = []
for line in Path(r"$CASES_FILE").read_text(encoding="utf-8").splitlines():
  name, graph_hash, json_sha = line.split("\t")
  cases.append({"name": name, "graph_hash": graph_hash, "json_sha": json_sha})
cases.sort(key=lambda c: c["name"])
report = {
  "v": "phase27P.mjs_asg_ingest_gate.v0",
  "authority": "advisory",
  "language": "mjs",
  "summary": {
    "accept": len(cases),
    "must_reject": int($reject_count)
  },
  "cases": cases,
}
print(json.dumps(report, sort_keys=True, separators=(",", ":")))
PY

want="$(tr -d '\n' < "$GOLDEN_HASH")"
got="sha256:$(sha256sum "$REPORT" | awk '{print $1}')"
if [[ "$want" != "$got" ]]; then
  echo "mjs-asg-ingest replay hash mismatch: expected $want got $got" >&2
  exit 1
fi

echo "ok mjs-asg-ingest gate"
