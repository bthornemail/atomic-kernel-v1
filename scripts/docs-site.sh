#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CMD="${1:-help}"

if ! command -v mkdocs >/dev/null 2>&1; then
  echo "mkdocs not installed. Install with: pip install mkdocs mkdocs-material" >&2
  exit 2
fi

case "$CMD" in
  serve)
    exec mkdocs serve -f "$ROOT/mkdocs.yml"
    ;;
  build)
    exec mkdocs build -f "$ROOT/mkdocs.yml"
    ;;
  check)
    exec mkdocs build --strict -f "$ROOT/mkdocs.yml" >/dev/null
    ;;
  *)
    echo "usage: $0 {serve|build|check}" >&2
    exit 1
    ;;
esac
