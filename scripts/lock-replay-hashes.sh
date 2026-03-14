#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

write_hash() {
  local report="$1"
  local out="$2"
  [[ -f "$report" ]] || { echo "missing report artifact: $report" >&2; exit 2; }
  mkdir -p "$(dirname "$out")"
  printf 'sha256:%s\n' "$(sha256sum "$report" | awk '{print $1}')" > "$out"
}

# Locks the hashes of already-generated phase reports.
# This script does not regenerate report artifacts.

write_hash "$ROOT/reports/phase27H-living-xml.json" "$ROOT/golden/living-xml/replay-hash"
write_hash "$ROOT/reports/phase27H-living-xml-hardening.json" "$ROOT/golden/living-xml/hardening-replay-hash"
write_hash "$ROOT/reports/phase27I-semantic-identity.json" "$ROOT/golden/identity/replay-hash"
write_hash "$ROOT/reports/phase27J-seed-algebra.json" "$ROOT/golden/seed-algebra/replay-hash"
write_hash "$ROOT/reports/phase27K-lane16.json" "$ROOT/golden/lane16/replay-hash"
write_hash "$ROOT/reports/phase27L-rdf-export.json" "$ROOT/golden/rdf-export/replay-hash"
write_hash "$ROOT/reports/phase27M-asg-ingest.json" "$ROOT/golden/asg-ingest/replay-hash"
write_hash "$ROOT/reports/phase27P-mjs-asg-ingest.json" "$ROOT/golden/mjs-asg-ingest/replay-hash"
write_hash "$ROOT/reports/phase27N-pattern-extraction.json" "$ROOT/golden/pattern-extraction/replay-hash"
write_hash "$ROOT/reports/phase27O-analysis-report.json" "$ROOT/golden/analysis-report/replay-hash"
write_hash "$ROOT/reports/phase27Q-protocol-flow.json" "$ROOT/golden/protocol-flow/replay-hash"

echo "ok replay hashes locked"
