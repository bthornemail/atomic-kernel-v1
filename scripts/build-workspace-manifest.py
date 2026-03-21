#!/usr/bin/env python3
"""Build deterministic workspace-manifest.v0 from a workspace root."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from runtime.atomic_kernel.workspace_ingest import build_workspace_manifest, discover_projects, validate_workspace_manifest


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--workspace", required=True)
  parser.add_argument("--out", required=True)
  args = parser.parse_args()

  workspace = Path(args.workspace).resolve()
  projects = discover_projects(workspace)
  manifest = build_workspace_manifest(workspace, projects)
  validate_workspace_manifest(manifest)

  out = Path(args.out)
  out.parent.mkdir(parents=True, exist_ok=True)
  out.write_text(json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
  print(f"ok workspace manifest out={out}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
