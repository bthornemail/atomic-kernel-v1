#!/usr/bin/env python3
"""Discover candidate projects in a workspace deterministically."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from runtime.atomic_kernel.workspace_ingest import build_workspace_manifest, discover_projects


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--workspace", required=True)
  parser.add_argument("--out")
  args = parser.parse_args()

  workspace = Path(args.workspace).resolve()
  projects = discover_projects(workspace)
  manifest = build_workspace_manifest(workspace, projects)
  payload = {
    "v": "workspace-discovery.v0",
    "authority": "advisory",
    "workspace_manifest": manifest,
  }
  text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
  if args.out:
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"ok workspace discovery out={out}")
  else:
    print(text, end="")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
