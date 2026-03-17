#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 tests/test_v2.py
python3 scripts/package_v2.py parity --mode 16d --width 32 --seed 0x0B7406AC --steps 64 --law-version gate-v2

echo "ok v2 package gate"
