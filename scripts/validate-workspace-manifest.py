#!/usr/bin/env python3
"""Fail-closed validator for workspace-manifest.v0."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from runtime.atomic_kernel.workspace_ingest import validate_workspace_manifest


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--manifest", required=True)
  args = parser.parse_args()

  manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
  validate_workspace_manifest(manifest)
  print(f"ok workspace manifest validate file={args.manifest}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
