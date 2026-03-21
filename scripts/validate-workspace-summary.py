#!/usr/bin/env python3
"""Fail-closed validator for workspace-summary.v0."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from runtime.atomic_kernel.workspace_ingest import validate_workspace_summary


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--summary", required=True)
  args = parser.parse_args()

  summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
  validate_workspace_summary(summary)
  print(f"ok workspace summary validate file={args.summary}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
