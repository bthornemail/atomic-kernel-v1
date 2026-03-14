#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAYLOAD_DIR="$ROOT/propagation/aztec/payloads"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

python3 "$ROOT/propagation/aztec/build-payloads.py" --release 0.1.0 --output "$TMP_DIR" >/dev/null

diff -ru "$PAYLOAD_DIR" "$TMP_DIR" >/dev/null || {
  echo "aztec payload drift: run propagation/aztec/build-payloads.py" >&2
  exit 1
}

python3 "$ROOT/propagation/aztec/validate-payloads.py" --payload-dir "$PAYLOAD_DIR" >/dev/null

echo "ok aztec payload gate"
