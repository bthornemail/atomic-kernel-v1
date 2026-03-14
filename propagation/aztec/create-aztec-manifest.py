#!/usr/bin/env python3
"""Deterministic manifest generator (no wall-clock fields)."""
import hashlib
import json
from pathlib import Path
import yaml

OUT = Path(__file__).resolve().parent / "genesis-32-layer-manifest.yaml"

def main() -> int:
  manifest = {
    "v": "tetragrammatron.manifest.v1",
    "artifact": {
      "id": "tetragrammatron-genesis-32-layer-001",
      "type": "tetragrammatron-manifest",
    },
    "basis": {"unicode": "17.0", "utf_ebcdic": "root-2026-draft"},
    "layers": {
      "1-8": "Pure algorithms + Unicode/UTF-EBCDIC",
      "9-16": "Encoded runtime + lane extension",
      "17-25": "Distributed API + living XML",
      "26-31": "Advisory metaverse extension",
      "32": "Full manifest",
    },
  }
  digest = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
  manifest["artifact"]["hash"] = digest
  OUT.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
  print(f"ok manifest {OUT}")
  return 0

if __name__ == "__main__":
  raise SystemExit(main())
