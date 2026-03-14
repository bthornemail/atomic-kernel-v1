#!/usr/bin/env python3
"""Deterministic projection-manifest generator from canonical payloads."""
import json
import subprocess
from pathlib import Path
import yaml

OUT = Path(__file__).resolve().parent / "genesis-32-layer-manifest.yaml"
ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / "propagation" / "aztec" / "payloads" / "experience-manifest.json"
BUILD = ROOT / "propagation" / "aztec" / "build-payloads.py"

def main() -> int:
  subprocess.run(["python3", str(BUILD), "--release", "0.1.0"], check=True, cwd=ROOT)
  manifest = json.loads(PAYLOAD.read_text(encoding="utf-8"))
  OUT.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
  print(f"ok manifest {OUT}")
  return 0

if __name__ == "__main__":
  raise SystemExit(main())
