#!/usr/bin/env python3
"""Fail-closed validator for ASG v0 frames."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime.atomic_kernel.asg import validate_asg_frame


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--file", required=True)
  args = parser.parse_args()

  frame = json.loads(Path(args.file).read_text(encoding="utf-8"))
  validate_asg_frame(frame)
  print(f"ok asg validate file={args.file}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

