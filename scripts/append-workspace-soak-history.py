#!/usr/bin/env python3
"""Append current soak-status to deterministic advisory history artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _canonical_json(data: Any) -> str:
  return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--status", required=True, help="Path to soak-status.json")
  parser.add_argument("--history-dir", default="reports/workspace/soak/history")
  parser.add_argument("--index", default="reports/workspace/soak/history/index.json")
  args = parser.parse_args()

  status_path = Path(args.status).resolve()
  status = json.loads(status_path.read_text(encoding="utf-8"))
  run_id = status.get("run_id")
  if not isinstance(run_id, str) or not run_id:
    raise SystemExit("invalid soak status: run_id missing")

  history_dir = Path(args.history_dir).resolve()
  history_dir.mkdir(parents=True, exist_ok=True)
  entry_path = history_dir / f"{run_id}.json"
  entry_path.write_text(_canonical_json(status) + "\n", encoding="utf-8")

  index_path = Path(args.index).resolve()
  index_path.parent.mkdir(parents=True, exist_ok=True)
  runs = sorted(
    p.stem
    for p in history_dir.glob("*.json")
    if p.is_file() and p.name != "index.json"
  )
  index = {
    "v": "workspace-soak-history-index.v0",
    "authority": "advisory",
    "history_dir": str(history_dir),
    "runs": runs,
    "latest_run_id": run_id,
  }
  index_path.write_text(_canonical_json(index) + "\n", encoding="utf-8")
  print(f"ok workspace soak-history append run={run_id} entry={entry_path} index={index_path}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
