#!/usr/bin/env python3
"""Extract deterministic pattern instances from ASG frame."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime.atomic_kernel.pattern_extract import extract_patterns_from_asg


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--asg", required=True)
  parser.add_argument("--out", required=True)
  args = parser.parse_args()

  frame = json.loads(Path(args.asg).read_text(encoding="utf-8"))
  patterns = extract_patterns_from_asg(frame)
  report = {
    "v": "ak.pattern_extraction.v0",
    "authority": "advisory",
    "source_graph_hash": frame["graph_hash"],
    "patterns": patterns,
  }
  Path(args.out).write_text(
    json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
    encoding="utf-8",
  )
  print(f"ok pattern extraction out={args.out}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

