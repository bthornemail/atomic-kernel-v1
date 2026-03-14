#!/usr/bin/env python3
"""Extract deterministic protocol flow from ASG and pattern outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def classify_path(path: str) -> str:
  p = path.lower()
  if any(tok in p for tok in ("/tests/", "tests/", "replay", "witness", "conformance", "verify", "determinism")):
    return "conformance"
  if "eabi" in p:
    return "eabi"
  if "abi" in p:
    return "abi"
  if any(tok in p for tok in ("wave32", "projection", "portal", "viewer", "obsidian", "/trees/")):
    return "projection"
  if any(tok in p for tok in ("waveform", "bridge")):
    return "bridge"
  if any(tok in p for tok in ("unicode", "carrier", "spherepack", "hw_canon", "hw_project", "validate_jsonl")):
    return "carrier"
  if "control" in p:
    return "control"
  if any(tok in p for tok in ("/ui/", "ui/")):
    return "ui"
  return "core"


def classify_target(name: str) -> str:
  n = name.lower()
  if "canbc" in n:
    return "abi"
  if any(tok in n for tok in ("canisa", "interpreter")):
    return "eabi"
  if any(tok in n for tok in ("control", "surface", "frame", "separator")):
    return "control"
  if any(tok in n for tok in ("waveform", "unicode", "carrier", "spherepack", "hw_canon", "hw_project", "validate_jsonl", "drift_scan")):
    return "carrier"
  if any(tok in n for tok in ("projection", "viewer", "portal", "obsidian", "esbuild")):
    return "projection"
  if any(tok in n for tok in ("runtime", "vm", "scheduler", "memory", "identity", "seed", "lane16")):
    return "runtime"
  if any(tok in n for tok in ("test", "verify", "witness", "conformance", "golden", "replay", "assert", "check", "run_all")):
    return "conformance"
  return "core"


def canonical_json(data: Any) -> str:
  return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(data: Any) -> str:
  return "sha256:" + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument("--asg", required=True, help="ASG directory with *.json frames")
  ap.add_argument("--patterns", required=True, help="Pattern output directory with *.json")
  ap.add_argument("--output", required=True, help="protocol flow output json")
  args = ap.parse_args()

  asg_dir = Path(args.asg)
  pat_dir = Path(args.patterns)
  out_path = Path(args.output)
  if not asg_dir.is_dir():
    raise SystemExit(f"missing asg dir: {asg_dir}")
  if not pat_dir.is_dir():
    raise SystemExit(f"missing patterns dir: {pat_dir}")

  state_counts: dict[str, int] = {}
  transitions: dict[tuple[str, str, str], dict[str, Any]] = {}
  frame_domain_by_hash: dict[str, str] = {}

  for fp in sorted(asg_dir.glob("*.json")):
    frame = json.loads(fp.read_text(encoding="utf-8"))
    src_path = str(frame.get("provenance", {}).get("source_path", ""))
    src_domain = classify_path(src_path)
    frame_hash = str(frame.get("graph_hash", "")).replace("sha256:", "")
    frame_domain_by_hash[frame_hash] = src_domain
    state_counts[src_domain] = state_counts.get(src_domain, 0) + 1

    node_by_id = {n["id"]: n for n in frame.get("nodes", [])}
    for e in frame.get("edges", []):
      kind = e.get("kind", "")
      if kind not in {"Imports", "Calls"}:
        continue
      tnode = node_by_id.get(e.get("to", ""), {})
      tname = str(tnode.get("attrs", {}).get("name", ""))
      dst_domain = classify_target(tname)
      key = (src_domain, dst_domain, kind)
      rec = transitions.get(key)
      if rec is None:
        rec = {
          "from": src_domain,
          "to": dst_domain,
          "kind": kind,
          "count": 0,
          "evidence_edges": [],
        }
        transitions[key] = rec
      rec["count"] += 1
      if len(rec["evidence_edges"]) < 6:
        rec["evidence_edges"].append(e["id"])

  for fp in sorted(pat_dir.glob("*.json")):
    data = json.loads(fp.read_text(encoding="utf-8"))
    for p in data.get("patterns", []):
      ptype = p.get("pattern_type", "")
      src_hash = p.get("source_frame_hash", "")
      src_domain = frame_domain_by_hash.get(src_hash, "core")
      if ptype == "BridgeLayer":
        rb = p.get("role_bindings", {})
        a = str(rb.get("domain_a", src_domain))
        b = str(rb.get("domain_b", "core"))
        key = (a, b, "PatternBridge")
      elif ptype == "ProjectionOnlySurface":
        key = (src_domain, "projection", "PatternProjection")
      elif ptype == "CarrierLayer":
        key = (src_domain, "carrier", "PatternCarrier")
      elif ptype == "ConformanceSurface":
        key = (src_domain, "conformance", "PatternConformance")
      elif ptype == "BoundarySplit":
        key = (src_domain, "core", "PatternBoundary")
      else:
        continue

      rec = transitions.get(key)
      if rec is None:
        rec = {
          "from": key[0],
          "to": key[1],
          "kind": key[2],
          "count": 0,
          "evidence_edges": [],
        }
        transitions[key] = rec
      rec["count"] += 1
      pe = p.get("evidence_edges", [])
      for edge_id in pe:
        if len(rec["evidence_edges"]) >= 6:
          break
        if edge_id not in rec["evidence_edges"]:
          rec["evidence_edges"].append(edge_id)

  states = [{"id": k, "count": state_counts[k]} for k in sorted(state_counts.keys())]
  trans = [transitions[k] for k in sorted(transitions.keys())]

  flow = {
    "v": "protocol-flow.v0",
    "authority": "advisory",
    "states": states,
    "transitions": trans,
    "state_digest": sha(states),
    "transition_digest": sha(trans),
    "flow_digest": "",
  }
  flow["flow_digest"] = sha({"states": flow["states"], "transitions": flow["transitions"]})

  out_path.parent.mkdir(parents=True, exist_ok=True)
  out_path.write_text(canonical_json(flow) + "\n", encoding="utf-8")
  print(f"ok protocol flow out={out_path}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
