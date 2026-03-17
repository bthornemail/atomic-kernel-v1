#!/usr/bin/env python3
"""Ingest MJS source into deterministic ASG v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime.atomic_kernel.asg import ingest_mjs_to_asg, validate_asg_frame


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--input", required=True)
  parser.add_argument("--source-path", required=True)
  parser.add_argument("--namespace", required=True)
  parser.add_argument("--out", required=True)
  args = parser.parse_args()

  src = Path(args.input).read_text(encoding="utf-8")
  frame = ingest_mjs_to_asg(src, source_path=args.source_path, namespace=args.namespace)
  validate_asg_frame(frame)
  Path(args.out).write_text(
    json.dumps(frame, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
    encoding="utf-8",
  )
  print(f"ok asg ingest mjs out={args.out}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
