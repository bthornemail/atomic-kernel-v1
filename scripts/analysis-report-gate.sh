#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

ACCEPT_DIR="$ROOT/runtime/atomic_kernel/fixtures/analysis-report/accept"
REJECT_DIR="$ROOT/runtime/atomic_kernel/fixtures/analysis-report/must-reject"
TARGET="$ACCEPT_DIR/target-sample"
EXPECTED_JSON="$ACCEPT_DIR/expected-report.json"
EXPECTED_MD="$ACCEPT_DIR/expected-report.md"
REPORT_JSON="$ROOT/reports/phase27O-analysis-report.json"
REPORT_MD="$ROOT/reports/phase27O-analysis-report.md"
GOLDEN_HASH="$ROOT/golden/analysis-report/replay-hash"

[[ -d "$TARGET" ]] || { echo "missing analysis target: $TARGET" >&2; exit 2; }
[[ -f "$EXPECTED_JSON" ]] || { echo "missing expected report json: $EXPECTED_JSON" >&2; exit 2; }
[[ -f "$EXPECTED_MD" ]] || { echo "missing expected report md: $EXPECTED_MD" >&2; exit 2; }
[[ -f "$GOLDEN_HASH" ]] || { echo "missing golden hash: $GOLDEN_HASH" >&2; exit 2; }

mkdir -p "$(dirname "$REPORT_JSON")"
TMP_JSON="$(mktemp)"
TMP_MD="$(mktemp)"
TMP_JSON_NORM="$(mktemp)"
TMP_EXPECTED_NORM="$(mktemp)"
TMP_WRAP_NORM="$(mktemp)"
TMP_OUT="$(mktemp -d)"
trap 'rm -f "$TMP_JSON" "$TMP_MD" "$TMP_JSON_NORM" "$TMP_EXPECTED_NORM" "$TMP_WRAP_NORM"; rm -rf "$TMP_OUT"' EXIT

normalize_report_json() {
  local in_file="$1"
  local out_file="$2"
  python3 - <<PY > "$out_file"
import json
from pathlib import Path
p = Path(r"$in_file")
obj = json.loads(p.read_text(encoding="utf-8"))
if isinstance(obj, dict) and isinstance(obj.get("target"), dict):
  obj["target"]["path"] = "__TARGET__"
print(json.dumps(obj, sort_keys=True, separators=(",", ":")))
PY
}

python3 "$ROOT/scripts/semantic-analyze.py" \
  --target "$TARGET" \
  --out-json "$TMP_JSON" \
  --out-md "$TMP_MD" \
  >/dev/null

normalize_report_json "$TMP_JSON" "$TMP_JSON_NORM"
normalize_report_json "$EXPECTED_JSON" "$TMP_EXPECTED_NORM"

cmp -s "$TMP_JSON_NORM" "$TMP_EXPECTED_NORM" || { echo "analysis report json mismatch" >&2; exit 1; }
cmp -s "$TMP_MD" "$EXPECTED_MD" || { echo "analysis report md mismatch" >&2; exit 1; }

python3 "$ROOT/scripts/validate-analysis-report.py" --file "$TMP_JSON" >/dev/null

cp "$TMP_JSON_NORM" "$REPORT_JSON"
cp "$TMP_MD" "$REPORT_MD"

bash "$ROOT/scripts/run-applied-analysis.sh" \
  --target "$TARGET" \
  --name "fixture-sample" \
  --out-root "$TMP_OUT" \
  --languages "python,typescript" \
  >/dev/null

WRAP_JSON="$TMP_OUT/fixture-sample/report.json"
WRAP_MD="$TMP_OUT/fixture-sample/report.md"
WRAP_RECEIPT="$TMP_OUT/fixture-sample/receipt.json"
[[ -f "$WRAP_JSON" ]] || { echo "wrapper missing report json" >&2; exit 1; }
[[ -f "$WRAP_MD" ]] || { echo "wrapper missing report md" >&2; exit 1; }
[[ -f "$WRAP_RECEIPT" ]] || { echo "wrapper missing receipt" >&2; exit 1; }
normalize_report_json "$WRAP_JSON" "$TMP_WRAP_NORM"
cmp -s "$TMP_WRAP_NORM" "$TMP_EXPECTED_NORM" || { echo "wrapper report json mismatch" >&2; exit 1; }
cmp -s "$WRAP_MD" "$EXPECTED_MD" || { echo "wrapper report md mismatch" >&2; exit 1; }

python3 - <<PY >/dev/null
import json
from pathlib import Path

receipt = json.loads(Path(r"$WRAP_RECEIPT").read_text(encoding="utf-8"))
report = json.loads(Path(r"$WRAP_JSON").read_text(encoding="utf-8"))
required = {
  "v", "authority", "name", "target", "languages", "report_json_sha", "report_md_sha",
  "asg_count", "pattern_count", "inputs_digest", "evidence_digest", "outputs_digest",
  "asg_digest", "patterns_digest"
}
assert set(receipt.keys()) == required
assert receipt["v"] == "analysis-receipt.v0"
assert receipt["authority"] == "advisory"
assert receipt["name"] == "fixture-sample"
assert receipt["asg_count"] == 4
assert receipt["pattern_count"] == len(report["instances"])
for k in ("report_json_sha", "report_md_sha", "inputs_digest", "evidence_digest", "outputs_digest", "asg_digest", "patterns_digest"):
  assert isinstance(receipt[k], str) and receipt[k].startswith("sha256:")
PY

want="$(tr -d '\n' < "$GOLDEN_HASH")"
got="sha256:$(sha256sum "$REPORT_JSON" | awk '{print $1}')"
if [[ "$want" != "$got" ]]; then
  echo "analysis-report replay hash mismatch: expected $want got $got" >&2
  exit 1
fi

for f in "$REJECT_DIR"/bad-report-*.json; do
  [[ -f "$f" ]] || continue
  if python3 "$ROOT/scripts/validate-analysis-report.py" --file "$f" >/dev/null 2>&1; then
    echo "must-reject report accepted: $f" >&2
    exit 1
  fi
done

for d in "$REJECT_DIR"/target-*; do
  [[ -d "$d" ]] || continue
  if python3 "$ROOT/scripts/semantic-analyze.py" --target "$d" --out-json "$TMP_JSON" --out-md "$TMP_MD" >/dev/null 2>&1; then
    echo "must-reject target accepted: $d" >&2
    exit 1
  fi
done

echo "ok analysis-report gate"
