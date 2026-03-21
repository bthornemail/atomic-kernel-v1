#!/usr/bin/env python3
"""Fail-closed validator for project-analysis-overlay.v0."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from runtime.atomic_kernel.workspace_ingest import validate_project_analysis_overlay


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--file", required=True)
  args = parser.parse_args()

  obj = json.loads(Path(args.file).read_text(encoding="utf-8"))
  validate_project_analysis_overlay(obj)
  print(f"ok project-analysis-overlay validate file={args.file}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
