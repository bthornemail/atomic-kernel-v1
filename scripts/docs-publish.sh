#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RELEASE="0.1.0"
BUILD_DOCS=1
EMIT_AZTEC=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --release)
      RELEASE="$2"
      shift 2
      ;;
    --no-build)
      BUILD_DOCS=0
      shift
      ;;
    --emit-aztec)
      EMIT_AZTEC=1
      shift
      ;;
    *)
      echo "usage: $0 [--release X.Y.Z] [--no-build] [--emit-aztec]" >&2
      exit 1
      ;;
  esac
done

PAYLOAD_SRC="$ROOT/propagation/aztec/payloads"
BADGE_DST="$ROOT/docs/badges/payloads"
AZTEC_DST="$ROOT/docs/badges/aztec"

echo "[1/5] build deterministic payloads"
python3 "$ROOT/propagation/aztec/build-payloads.py" --release "$RELEASE" >/dev/null

echo "[2/5] validate payload contracts"
python3 "$ROOT/propagation/aztec/validate-payloads.py" --payload-dir "$PAYLOAD_SRC" >/dev/null

echo "[3/5] sync docs badge payloads"
mkdir -p "$BADGE_DST/doc-badges"
cp "$PAYLOAD_SRC/experience-manifest.json" "$BADGE_DST/experience-manifest.json"
cp "$PAYLOAD_SRC/doc-badges/"*.json "$BADGE_DST/doc-badges/"

if [[ "$EMIT_AZTEC" -eq 1 ]]; then
  echo "[4/5] emit Aztec images"
  if command -v python3 >/dev/null 2>&1 && python3 - <<'PY' >/dev/null 2>&1
import importlib.util
raise SystemExit(0 if importlib.util.find_spec('segno') else 1)
PY
  then
    mkdir -p "$AZTEC_DST"
    for f in "$BADGE_DST"/doc-badges/*.json "$BADGE_DST"/experience-manifest.json; do
      base="$(basename "$f" .json)"
      python3 - <<PY
import segno
from pathlib import Path
p = Path(r"$f")
out = Path(r"$AZTEC_DST") / f"{p.stem}.svg"
segno.make(p.read_text(encoding='utf-8'), error='m').save(out, scale=4)
PY
    done
  else
    echo "segno not installed; skipping Aztec image emission" >&2
  fi
else
  echo "[4/5] emit Aztec images (skipped)"
fi

if [[ "$BUILD_DOCS" -eq 1 ]]; then
  echo "[5/5] build docs site"
  "$ROOT/scripts/docs-site.sh" check
else
  echo "[5/5] build docs site (skipped)"
fi

echo "ok docs publish release=$RELEASE"
