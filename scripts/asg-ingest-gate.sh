#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

ACCEPT_DIR="$ROOT/runtime/atomic_kernel/fixtures/asg-ingest/accept"
REJECT_DIR="$ROOT/runtime/atomic_kernel/fixtures/asg-ingest/must-reject"
REPORT="$ROOT/reports/phase27M-asg-ingest.json"
GOLDEN_HASH="$ROOT/golden/asg-ingest/replay-hash"

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
  ext="${base##*.}"
  name="${stem%.*}"
  expected="$ACCEPT_DIR/expected-${name}.json"
  [[ -f "$expected" ]] || { echo "missing expected fixture: $expected" >&2; exit 2; }

  if [[ "$ext" == "py" ]]; then
    ingester="$ROOT/scripts/ingest-python-asg.py"
    ns="demo.${name}"
  elif [[ "$ext" == "ts" ]]; then
    ingester="$ROOT/scripts/ingest-typescript-asg.py"
    ns="demo.${name}"
  elif [[ "$ext" == "mjs" ]]; then
    ingester="$ROOT/scripts/ingest-mjs-asg.py"
    ns="demo.${name}"
  else
    echo "unsupported accept fixture extension: $base" >&2
    exit 2
  fi

  python3 "$ingester" \
    --input "$src" \
    --source-path "fixtures/asg-ingest/accept/$base" \
    --namespace "$ns" \
    --out "$TMP_JSON" \
    >/dev/null

  cmp -s "$TMP_JSON" "$expected" || {
    echo "asg ingest mismatch for $base" >&2
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
  language="$(python3 - <<PY
import json
from pathlib import Path
p = Path(r"$TMP_JSON")
print(json.loads(p.read_text(encoding='utf-8'))['language'])
PY
)"
  json_sha="sha256:$(sha256sum "$TMP_JSON" | awk '{print $1}')"
  printf '%s\t%s\t%s\t%s\n' "$name" "$language" "$frame_hash" "$json_sha" >> "$CASES_FILE"
  accept_count=$((accept_count + 1))
done < <(find "$ACCEPT_DIR" -maxdepth 1 -type f \( -name 'source-*.py' -o -name 'source-*.ts' -o -name 'source-*.mjs' \) | sort)

[[ "$accept_count" -gt 0 ]] || { echo "no accept source fixtures found" >&2; exit 2; }

reject_count=0
for f in "$REJECT_DIR"/bad-frame-*.json; do
  [[ -f "$f" ]] || continue
  if python3 "$ROOT/scripts/validate-asg.py" --file "$f" >/dev/null 2>&1; then
    echo "must-reject frame accepted: $f" >&2
    exit 1
  fi
  reject_count=$((reject_count + 1))
done

for f in "$REJECT_DIR"/bad-source-*.py; do
  [[ -f "$f" ]] || continue
  if python3 "$ROOT/scripts/ingest-python-asg.py" \
    --input "$f" \
    --source-path "fixtures/asg-ingest/must-reject/$(basename "$f")" \
    --namespace "reject" \
    --out "$TMP_JSON" \
    >/dev/null 2>&1; then
    echo "must-reject source accepted: $f" >&2
    exit 1
  fi
  reject_count=$((reject_count + 1))
done

for f in "$REJECT_DIR"/bad-source-*.ts; do
  [[ -f "$f" ]] || continue
  if python3 "$ROOT/scripts/ingest-typescript-asg.py" \
    --input "$f" \
    --source-path "fixtures/asg-ingest/must-reject/$(basename "$f")" \
    --namespace "reject" \
    --out "$TMP_JSON" \
    >/dev/null 2>&1; then
    echo "must-reject source accepted: $f" >&2
    exit 1
  fi
  reject_count=$((reject_count + 1))
done

for f in "$REJECT_DIR"/bad-source-*.mjs; do
  [[ -f "$f" ]] || continue
  if python3 "$ROOT/scripts/ingest-mjs-asg.py" \
    --input "$f" \
    --source-path "fixtures/asg-ingest/must-reject/$(basename "$f")" \
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
  name, language, graph_hash, json_sha = line.split("\t")
  cases.append({"name": name, "language": language, "graph_hash": graph_hash, "json_sha": json_sha})
cases.sort(key=lambda c: c["name"])
report = {
  "v": "phase27M.asg_ingest_gate.v0",
  "authority": "advisory",
  "languages": ["mjs", "python", "typescript"],
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
  echo "asg-ingest replay hash mismatch: expected $want got $got" >&2
  exit 1
fi

echo "ok asg-ingest gate"
