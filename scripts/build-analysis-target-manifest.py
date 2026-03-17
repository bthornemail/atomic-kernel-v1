#!/usr/bin/env python3
"""Build deterministic target manifest for applied semantic analysis."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def _git_commit(path: Path) -> str:
  proc = subprocess.run(
    ["git", "-C", str(path), "rev-parse", "HEAD"],
    check=False,
    capture_output=True,
    text=True,
  )
  if proc.returncode != 0:
    raise ValueError(f"target is not a git repo: {path}")
  return proc.stdout.strip()


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--target", required=True, help="Repository root to analyze")
  parser.add_argument("--language-profile", default="mjs", help="Analysis language profile")
  parser.add_argument(
    "--include",
    default="**/*.mjs",
    help="Comma-separated include globs (default: **/*.mjs)",
  )
  parser.add_argument(
    "--exclude",
    default="**/node_modules/**,**/.git/**,**/dist/**,**/build/**,**/site/**",
    help="Comma-separated exclude globs",
  )
  parser.add_argument("--out", required=True, help="Output manifest path")
  args = parser.parse_args()

  target = Path(args.target).resolve()
  if not target.is_dir():
    raise SystemExit(f"target is not a directory: {target}")

  manifest = {
    "v": "analysis-target-manifest.v0",
    "authority": "advisory",
    "repo_path": str(target),
    "commit": _git_commit(target),
    "include_globs": [x.strip() for x in args.include.split(",") if x.strip()],
    "exclude_globs": [x.strip() for x in args.exclude.split(",") if x.strip()],
    "language_profile": args.language_profile.strip() or "mjs",
  }

  out = Path(args.out)
  out.parent.mkdir(parents=True, exist_ok=True)
  out.write_text(json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
  print(f"ok target manifest out={out}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
