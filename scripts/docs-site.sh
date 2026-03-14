#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CMD="${1:-help}"

case "$CMD" in
  serve)
    if ! command -v mkdocs >/dev/null 2>&1; then
      echo "mkdocs not installed. Install with: pip install mkdocs mkdocs-material" >&2
      exit 2
    fi
    exec mkdocs serve -f "$ROOT/mkdocs.yml"
    ;;
  build)
    if ! command -v mkdocs >/dev/null 2>&1; then
      echo "mkdocs not installed. Install with: pip install mkdocs mkdocs-material" >&2
      exit 2
    fi
    exec mkdocs build -f "$ROOT/mkdocs.yml"
    ;;
  check)
    if ! command -v mkdocs >/dev/null 2>&1; then
      echo "mkdocs not installed. Install with: pip install mkdocs mkdocs-material" >&2
      exit 2
    fi
    exec mkdocs build --strict -f "$ROOT/mkdocs.yml" >/dev/null
    ;;
  publish)
    shift || true
    exec "$ROOT/scripts/docs-publish.sh" "$@"
    ;;
  *)
    echo "usage: $0 {serve|build|check|publish}" >&2
    exit 1
    ;;
esac
