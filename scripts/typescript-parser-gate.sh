#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

ACC_DIR="$ROOT/runtime/atomic_kernel/fixtures/typescript-parser/accept"
REJ_DIR="$ROOT/runtime/atomic_kernel/fixtures/typescript-parser/must-reject"

[[ -d "$ACC_DIR" ]] || { echo "missing accept dir: $ACC_DIR" >&2; exit 2; }
[[ -d "$REJ_DIR" ]] || { echo "missing must-reject dir: $REJ_DIR" >&2; exit 2; }
command -v npx >/dev/null 2>&1 || { echo "typescript-parser gate requires npx on PATH" >&2; exit 2; }
npx -y tsc --version >/dev/null 2>&1 || { echo "typescript-parser gate requires TypeScript compiler via npx tsc" >&2; exit 2; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

for f in "$ACC_DIR"/*.ts; do
  [[ -f "$f" ]] || continue
  out="$TMP/$(basename "$f").json"
  python3 "$ROOT/scripts/ingest-typescript-asg.py" \
    --input "$f" \
    --source-path "$(basename "$f")" \
    --namespace "ts.parser.accept.$(basename "$f" .ts)" \
    --out "$out" \
    >/dev/null
  python3 "$ROOT/scripts/validate-asg.py" --file "$out" >/dev/null
done

for f in "$REJ_DIR"/*.ts; do
  [[ -f "$f" ]] || continue
  out="$TMP/$(basename "$f").json"
  if python3 "$ROOT/scripts/ingest-typescript-asg.py" \
    --input "$f" \
    --source-path "$(basename "$f")" \
    --namespace "ts.parser.reject.$(basename "$f" .ts)" \
    --out "$out" \
    >/dev/null 2>&1; then
    echo "must-reject typescript fixture accepted: $f" >&2
    exit 1
  fi
done

echo "ok typescript-parser gate"
