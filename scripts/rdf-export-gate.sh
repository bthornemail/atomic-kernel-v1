#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACCEPT_DIR="$ROOT/runtime/atomic_kernel/fixtures/rdf-export/accept"
REJECT_DIR="$ROOT/runtime/atomic_kernel/fixtures/rdf-export/must-reject"
REPORT="$ROOT/reports/phase27L-rdf-export.json"
GOLDEN_HASH="$ROOT/golden/rdf-export/replay-hash"

[[ -d "$ACCEPT_DIR" ]] || { echo "missing accept directory: $ACCEPT_DIR" >&2; exit 2; }
[[ -d "$REJECT_DIR" ]] || { echo "missing must-reject directory: $REJECT_DIR" >&2; exit 2; }
[[ -f "$GOLDEN_HASH" ]] || { echo "missing golden hash: $GOLDEN_HASH" >&2; exit 2; }

mkdir -p "$(dirname "$REPORT")"

TMP_JSON="$(mktemp)"
TMP_TTL="$(mktemp)"
CASES_FILE="$(mktemp)"
trap 'rm -f "$TMP_JSON" "$TMP_TTL" "$CASES_FILE"' EXIT

accept_count=0
while IFS= read -r src; do
  base="$(basename "$src")"
  name="${base#source-}"
  name="${name%.json}"
  expected_json="$ACCEPT_DIR/expected-${name}.json"
  expected_ttl="$ACCEPT_DIR/expected-${name}.ttl"

  [[ -f "$expected_json" ]] || { echo "missing expected json: $expected_json" >&2; exit 2; }
  [[ -f "$expected_ttl" ]] || { echo "missing expected ttl: $expected_ttl" >&2; exit 2; }

  python3 "$ROOT/scripts/export-rdf.py" \
    --input "$src" \
    --json-out "$TMP_JSON" \
    --ttl-out "$TMP_TTL" \
    >/dev/null

  cmp -s "$TMP_JSON" "$expected_json" || {
    echo "rdf-export json mismatch for $base" >&2
    exit 1
  }
  cmp -s "$TMP_TTL" "$expected_ttl" || {
    echo "rdf-export ttl mismatch for $base" >&2
    exit 1
  }

  python3 "$ROOT/scripts/validate-rdf-export.py" --file "$TMP_JSON" >/dev/null

  json_sha="sha256:$(sha256sum "$TMP_JSON" | awk '{print $1}')"
  ttl_sha="sha256:$(sha256sum "$TMP_TTL" | awk '{print $1}')"
  printf '%s\t%s\t%s\n' "$name" "$json_sha" "$ttl_sha" >> "$CASES_FILE"
  accept_count=$((accept_count + 1))
done < <(find "$ACCEPT_DIR" -maxdepth 1 -type f -name 'source-*.json' | sort)

[[ "$accept_count" -gt 0 ]] || { echo "no accept source fixtures found" >&2; exit 2; }

reject_count=0
for f in "$REJECT_DIR"/bad-envelope-*.json; do
  [[ -f "$f" ]] || continue
  if python3 "$ROOT/scripts/validate-rdf-export.py" --file "$f" >/dev/null 2>&1; then
    echo "must-reject envelope accepted: $f" >&2
    exit 1
  fi
  reject_count=$((reject_count + 1))
done

for f in "$REJECT_DIR"/bad-source-*.json; do
  [[ -f "$f" ]] || continue
  if python3 "$ROOT/scripts/export-rdf.py" \
    --input "$f" \
    --json-out "$TMP_JSON" \
    --ttl-out "$TMP_TTL" \
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
    name, json_sha, ttl_sha = line.split("\t")
    cases.append({"name": name, "json_sha": json_sha, "ttl_sha": ttl_sha})
cases.sort(key=lambda c: c["name"])
report = {
    "v": "phase27L.rdf_export_gate.v0",
    "authority": "advisory",
    "summary": {
        "accept": len(cases),
        "must_reject": int($reject_count),
    },
    "cases": cases,
}
print(json.dumps(report, sort_keys=True, separators=(",", ":")))
PY

want="$(tr -d '\n' < "$GOLDEN_HASH")"
got="sha256:$(sha256sum "$REPORT" | awk '{print $1}')"
if [[ "$want" != "$got" ]]; then
  echo "rdf-export replay hash mismatch: expected $want got $got" >&2
  exit 1
fi

echo "ok rdf-export gate"
