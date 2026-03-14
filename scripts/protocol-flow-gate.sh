#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

TARGET="$ROOT/runtime/atomic_kernel/fixtures/analysis-report/accept/target-sample"
EXPECT="$ROOT/runtime/atomic_kernel/fixtures/protocol-flow/accept/expected-flow.json"
REJECT_DIR="$ROOT/runtime/atomic_kernel/fixtures/protocol-flow/must-reject"
REPORT="$ROOT/reports/phase27Q-protocol-flow.json"
GOLDEN="$ROOT/golden/protocol-flow/replay-hash"

[[ -d "$TARGET" ]] || { echo "missing target: $TARGET" >&2; exit 2; }
[[ -f "$EXPECT" ]] || { echo "missing expected flow: $EXPECT" >&2; exit 2; }
[[ -f "$GOLDEN" ]] || { echo "missing replay hash: $GOLDEN" >&2; exit 2; }

TMP_OUT="$(mktemp -d)"
TMP_FLOW="$(mktemp)"
trap 'rm -rf "$TMP_OUT"; rm -f "$TMP_FLOW"' EXIT

bash "$ROOT/scripts/run-applied-analysis.sh" \
  --target "$TARGET" \
  --name "fixture-protocol-flow" \
  --out-root "$TMP_OUT" \
  --languages "python,typescript" \
  >/dev/null

python3 "$ROOT/scripts/extract-protocol-flow.py" \
  --asg "$TMP_OUT/fixture-protocol-flow/asg" \
  --patterns "$TMP_OUT/fixture-protocol-flow/patterns" \
  --output "$TMP_FLOW" \
  >/dev/null

cmp -s "$TMP_FLOW" "$EXPECT" || { echo "protocol-flow mismatch" >&2; exit 1; }
python3 "$ROOT/scripts/validate-protocol-flow.py" --file "$TMP_FLOW" >/dev/null

mkdir -p "$(dirname "$REPORT")"
cp "$TMP_FLOW" "$REPORT"

want="$(tr -d '\n' < "$GOLDEN")"
got="sha256:$(sha256sum "$REPORT" | awk '{print $1}')"
if [[ "$want" != "$got" ]]; then
  echo "protocol-flow replay hash mismatch: expected $want got $got" >&2
  exit 1
fi

for f in "$REJECT_DIR"/bad-*.json; do
  [[ -f "$f" ]] || continue
  if python3 "$ROOT/scripts/validate-protocol-flow.py" --file "$f" >/dev/null 2>&1; then
    echo "must-reject protocol-flow accepted: $f" >&2
    exit 1
  fi
done

echo "ok protocol-flow gate"
