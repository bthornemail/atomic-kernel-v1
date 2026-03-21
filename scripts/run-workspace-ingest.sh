#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"

WORKSPACE=""
MANIFEST=""
OUT_ROOT="$ROOT/reports/workspace"
RUN_ID=""
ALLOWLIST="atomic-kernel,metaverse-kit,tetragrammatron-os,automaton,autonomous-ai,waveform-core,universal-life-protocol"
MIRROR_ROOT="/home/main/devops/reports/workspace"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      WORKSPACE="${2:-}"
      shift 2
      ;;
    --manifest)
      MANIFEST="${2:-}"
      shift 2
      ;;
    --out-root)
      OUT_ROOT="${2:-}"
      shift 2
      ;;
    --run-id)
      RUN_ID="${2:-}"
      shift 2
      ;;
    --allowlist)
      ALLOWLIST="${2:-}"
      shift 2
      ;;
    --mirror-root)
      MIRROR_ROOT="${2:-}"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

[[ -n "$WORKSPACE" ]] || { echo "missing --workspace" >&2; exit 2; }
[[ -n "$MANIFEST" ]] || { echo "missing --manifest" >&2; exit 2; }
[[ -n "$RUN_ID" ]] || { echo "missing --run-id" >&2; exit 2; }

python3 "$ROOT/scripts/workspace-ingest.py" \
  --workspace "$WORKSPACE" \
  --manifest "$MANIFEST" \
  --out-root "$OUT_ROOT" \
  --run-id "$RUN_ID" \
  --allowlist "$ALLOWLIST" \
  --mirror-root "$MIRROR_ROOT"
