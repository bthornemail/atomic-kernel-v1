#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CMD="${1:-help}"
IMAGE="squidfunk/mkdocs-material:9"

run_mkdocs() {
  if command -v mkdocs >/dev/null 2>&1; then
    mkdocs "$@"
    return
  fi

  if command -v docker >/dev/null 2>&1; then
    docker run --rm \
      -v "$ROOT:/docs" \
      -w /docs \
      "$IMAGE" \
      "$@"
    return
  fi

  echo "mkdocs not installed and docker unavailable." >&2
  echo "Use one of:" >&2
  echo "  - pip install mkdocs mkdocs-material" >&2
  echo "  - docker run --rm -v \"$ROOT:/docs\" -w /docs $IMAGE mkdocs build -f mkdocs.yml" >&2
  exit 2
}

case "$CMD" in
  serve)
    if command -v mkdocs >/dev/null 2>&1; then
      exec mkdocs serve -f "$ROOT/mkdocs.yml"
    fi
    if command -v docker >/dev/null 2>&1; then
      exec docker run --rm -p 8000:8000 \
        -v "$ROOT:/docs" \
        -w /docs \
        "$IMAGE" \
        serve -a 0.0.0.0:8000 -f mkdocs.yml
    fi
    echo "mkdocs not installed and docker unavailable." >&2
    exit 2
    ;;
  build)
    run_mkdocs build -f mkdocs.yml
    ;;
  check)
    run_mkdocs build --strict -f mkdocs.yml >/dev/null
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
