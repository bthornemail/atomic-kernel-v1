#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

TARGET=""
NAME=""
OUT_ROOT=""
LANGUAGES=""
INCLUDE_PROTOCOL_FLOW=1
INCLUDE_GLOBS=""
EXCLUDE_GLOBS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    --name)
      NAME="${2:-}"
      shift 2
      ;;
    --out-root)
      OUT_ROOT="${2:-}"
      shift 2
      ;;
    --languages)
      LANGUAGES="${2:-}"
      shift 2
      ;;
    --no-protocol-flow)
      INCLUDE_PROTOCOL_FLOW=0
      shift
      ;;
    --include-globs)
      INCLUDE_GLOBS="${2:-}"
      shift 2
      ;;
    --exclude-globs)
      EXCLUDE_GLOBS="${2:-}"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

[[ -n "$TARGET" ]] || { echo "missing --target" >&2; exit 2; }
[[ -n "$NAME" ]] || { echo "missing --name" >&2; exit 2; }
[[ -n "$OUT_ROOT" ]] || { echo "missing --out-root" >&2; exit 2; }
[[ -n "$LANGUAGES" ]] || { echo "missing --languages" >&2; exit 2; }

bash "$ROOT/scripts/run-applied-analysis.sh" \
  --target "$TARGET" \
  --name "$NAME" \
  --out-root "$OUT_ROOT" \
  --languages "$LANGUAGES" \
  --include-globs "$INCLUDE_GLOBS" \
  --exclude-globs "$EXCLUDE_GLOBS" \
  >/dev/null

OUT_DIR="$OUT_ROOT/$NAME"
REPORT_JSON="$OUT_DIR/report.json"
ASG_DIR="$OUT_DIR/asg"
PATTERN_DIR="$OUT_DIR/patterns"
FLOW_JSON="$OUT_DIR/protocol-flow.json"

if [[ "$INCLUDE_PROTOCOL_FLOW" -eq 1 ]]; then
  pattern_count="$(python3 - <<PY
import json
from pathlib import Path
r = json.loads(Path(r"$REPORT_JSON").read_text(encoding="utf-8"))
print(sum(r.get("summary", {}).get("patterns", {}).values()))
PY
)"
  if [[ "${pattern_count:-0}" -gt 0 ]]; then
    python3 "$ROOT/scripts/extract-protocol-flow.py" \
      --asg "$ASG_DIR" \
      --patterns "$PATTERN_DIR" \
      --output "$FLOW_JSON" \
      >/dev/null
  fi
fi

echo "ok project analysis out=$OUT_DIR"
