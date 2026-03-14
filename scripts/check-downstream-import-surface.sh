#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Downstream repos that may consume atomic-kernel.
TARGETS=(
  "$ROOT/metaverse"
  "$ROOT/metaverse-kit"
  "$ROOT/metaverse-build"
  "$ROOT/scripts"
)

hits=0
for t in "${TARGETS[@]}"; do
  [[ -d "$t" ]] || continue
  if rg -n \
    --glob '*.py' \
    --glob '*.ts' \
    --glob '*.tsx' \
    --glob '*.js' \
    --glob '*.mjs' \
    --glob '*.cjs' \
    "runtime\.atomic_kernel\.|from runtime\.atomic_kernel|import runtime\.atomic_kernel" \
    -S "$t" >/tmp/atomic-kernel-import-hits.txt 2>/dev/null; then
    echo "forbidden internal import surface detected in: $t" >&2
    cat /tmp/atomic-kernel-import-hits.txt >&2
    hits=1
  fi
done

if [[ "$hits" -ne 0 ]]; then
  exit 1
fi

echo "ok downstream import surface"
