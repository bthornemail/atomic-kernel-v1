#!/usr/bin/env python3
"""Classify TypeScript files as valid/invalid syntax using independent TS parser checks."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from runtime.atomic_kernel.asg import AsgError, _check_ts_syntax


CODE_RE = re.compile(r"error TS(\d+):")


def ts_parse_with_typescript(path: Path) -> tuple[str, list[str]]:
  proc = subprocess.run(
    ["npx", "-y", "tsc", "--pretty", "false", "--noEmit", str(path)],
    check=False,
    text=True,
    capture_output=True,
  )
  output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
  lines = [ln for ln in output.splitlines() if ln.strip()]
  if proc.returncode == 0:
    return ("valid_ts", [])
  # If tsc ran and diagnostics are non-syntax (outside TS1xxx), treat as syntax-valid.
  codes: list[int] = []
  for line in lines:
    m = CODE_RE.search(line)
    if m:
      codes.append(int(m.group(1)))
  if not codes:
    return ("tool_error", [ln for ln in lines[:10]] or ["tsc failed without diagnostics"])
  has_syntax = any(1000 <= c < 2000 for c in codes)
  if has_syntax:
    return ("invalid_ts", lines[:10])
  return ("valid_ts", lines[:10])


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--files", required=True, help="Comma-separated TS file paths")
  parser.add_argument("--out", required=True)
  args = parser.parse_args()

  files = [Path(x.strip()).resolve() for x in args.files.split(",") if x.strip()]
  results: list[dict[str, object]] = []
  for file in files:
    src = file.read_text(encoding="utf-8")
    current_err = None
    try:
      _check_ts_syntax(src)
    except AsgError as exc:
      current_err = str(exc)
    status, details = ts_parse_with_typescript(file)
    if status == "valid_ts":
      recommended = "parser_fix"
    elif status == "invalid_ts":
      recommended = "repo_hygiene"
    else:
      recommended = "manual_triage"
    results.append(
      {
        "file": str(file),
        "current_parser_error": current_err,
        "external_check": status,
        "external_details": details,
        "recommended_action": recommended,
      }
    )

  out = {
    "v": "ts-validity-classification.v0",
    "authority": "advisory",
    "results": results,
  }
  out_path = Path(args.out)
  out_path.parent.mkdir(parents=True, exist_ok=True)
  out_path.write_text(json.dumps(out, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
  print(f"ok ts validity classification out={out_path}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
