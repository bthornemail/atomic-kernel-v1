#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

write_hash() {
  local report="$1"
  local out="$2"
  mkdir -p "$(dirname "$out")"
  printf 'sha256:%s\n' "$(sha256sum "$report" | awk '{print $1}')" > "$out"
}

write_hash "$ROOT/reports/phase27H-living-xml.json" "$ROOT/golden/living-xml/replay-hash"
write_hash "$ROOT/reports/phase27H-living-xml-hardening.json" "$ROOT/golden/living-xml/hardening-replay-hash"
write_hash "$ROOT/reports/phase27I-semantic-identity.json" "$ROOT/golden/identity/replay-hash"
write_hash "$ROOT/reports/phase27J-seed-algebra.json" "$ROOT/golden/seed-algebra/replay-hash"
write_hash "$ROOT/reports/phase27K-lane16.json" "$ROOT/golden/lane16/replay-hash"

echo "ok replay hashes locked"
