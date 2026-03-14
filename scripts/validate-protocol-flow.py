#!/usr/bin/env python3
"""Validate protocol-flow.v0 artifact fail-closed."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

TOP_KEYS = {"v", "authority", "states", "transitions", "state_digest", "transition_digest", "flow_digest"}
STATE_KEYS = {"id", "count"}
TRANS_KEYS = {"from", "to", "kind", "count", "evidence_edges"}


def canonical_json(data: Any) -> str:
  return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(data: Any) -> str:
  return "sha256:" + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def validate(obj: dict[str, Any]) -> None:
  if not isinstance(obj, dict):
    raise ValueError("flow must be object")
  keys = set(obj.keys())
  if keys != TOP_KEYS:
    raise ValueError(f"flow key mismatch missing={sorted(TOP_KEYS-keys)} extra={sorted(keys-TOP_KEYS)}")
  if obj["v"] != "protocol-flow.v0":
    raise ValueError("v invalid")
  if obj["authority"] != "advisory":
    raise ValueError("authority invalid")
  if not isinstance(obj["states"], list):
    raise ValueError("states invalid")
  if not isinstance(obj["transitions"], list):
    raise ValueError("transitions invalid")

  for i, s in enumerate(obj["states"]):
    if not isinstance(s, dict) or set(s.keys()) != STATE_KEYS:
      raise ValueError(f"states[{i}] invalid")
    if not isinstance(s["id"], str) or not s["id"]:
      raise ValueError(f"states[{i}].id invalid")
    if not isinstance(s["count"], int) or s["count"] < 0:
      raise ValueError(f"states[{i}].count invalid")

  for i, t in enumerate(obj["transitions"]):
    if not isinstance(t, dict) or set(t.keys()) != TRANS_KEYS:
      raise ValueError(f"transitions[{i}] invalid")
    for k in ("from", "to", "kind"):
      if not isinstance(t[k], str) or not t[k]:
        raise ValueError(f"transitions[{i}].{k} invalid")
    if not isinstance(t["count"], int) or t["count"] < 0:
      raise ValueError(f"transitions[{i}].count invalid")
    if not isinstance(t["evidence_edges"], list):
      raise ValueError(f"transitions[{i}].evidence_edges invalid")
    for j, ev in enumerate(t["evidence_edges"]):
      if not isinstance(ev, str) or not ev:
        raise ValueError(f"transitions[{i}].evidence_edges[{j}] invalid")

  expected_state = sha(obj["states"])
  if obj["state_digest"] != expected_state:
    raise ValueError("state_digest mismatch")
  expected_trans = sha(obj["transitions"])
  if obj["transition_digest"] != expected_trans:
    raise ValueError("transition_digest mismatch")
  expected_flow = sha({"states": obj["states"], "transitions": obj["transitions"]})
  if obj["flow_digest"] != expected_flow:
    raise ValueError("flow_digest mismatch")


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument("--file", required=True)
  args = ap.parse_args()

  p = Path(args.file)
  obj = json.loads(p.read_text(encoding="utf-8"))
  validate(obj)
  print(f"ok protocol-flow validate file={p}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
