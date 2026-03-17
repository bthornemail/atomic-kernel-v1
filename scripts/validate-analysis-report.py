#!/usr/bin/env python3
"""Fail-closed validator for analysis-report.v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime.atomic_kernel.repo_analysis import validate_analysis_report


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--file", required=True)
  args = parser.parse_args()
  report = json.loads(Path(args.file).read_text(encoding="utf-8"))
  validate_analysis_report(report)
  print(f"ok analysis-report validate file={args.file}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

