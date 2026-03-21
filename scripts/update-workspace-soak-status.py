#!/usr/bin/env python3
"""Build an advisory W5 soak-status artifact from workspace manifest+summary."""

from __future__ import annotations

import argparse
import json
import hashlib
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from runtime.atomic_kernel.asg import AsgError, _check_ts_syntax, _ts_source_valid_via_tsc


DEFAULT_PROBE_FILES = [
  "/home/main/devops/automaton/meta-log-db/src/rdf/sparql-parser.ts",
  "/home/main/devops/autonomous-ai/packages/hyperbolic-geometric-neural-network/src/generation/intelligent-code-generator.ts",
]


def _canonical_json(data: Any) -> str:
  return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _stable_summary_view(summary: dict[str, Any]) -> dict[str, Any]:
  return {
    "workspace_root": summary["workspace_root"],
    "projects_total": summary["projects_total"],
    "projects_analyzed": summary["projects_analyzed"],
    "projects_skipped": summary["projects_skipped"],
    "coverage": summary["coverage"],
    "project_reports": summary["project_reports"],
    "aggregate_counts": summary["aggregate_counts"],
    "inputs_digest": summary["inputs_digest"],
  }


def _sha256(data: Any) -> str:
  return "sha256:" + hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _overlay_files() -> list[Path]:
  overlay_dir = ROOT / "runtime" / "atomic_kernel" / "overlays" / "project-analysis"
  if not overlay_dir.is_dir():
    return []
  return [p for p in sorted(overlay_dir.glob("*.overlay.json")) if p.is_file()]


def _overlay_policy_state() -> dict[str, Any]:
  files = _overlay_files()
  include_nonempty = 0
  exclude_total = 0
  for file in files:
    obj = json.loads(file.read_text(encoding="utf-8"))
    includes = obj.get("include_globs", [])
    excludes = obj.get("exclude_globs", [])
    if isinstance(includes, list) and len(includes) > 0:
      include_nonempty += 1
    if isinstance(excludes, list):
      exclude_total += len(excludes)
  return {
    "overlay_count": len(files),
    "overlay_include_nonempty_count": include_nonempty,
    "overlay_exclude_glob_total": exclude_total,
  }


def _shape_view(manifest: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
  sample_profile_keys: list[str] = []
  sample_report_keys: list[str] = []
  if isinstance(manifest.get("projects"), list) and manifest["projects"]:
    first = manifest["projects"][0]
    if isinstance(first, dict):
      sample_profile_keys = sorted(first.keys())
  if isinstance(summary.get("project_reports"), list) and summary["project_reports"]:
    first = summary["project_reports"][0]
    if isinstance(first, dict):
      sample_report_keys = sorted(first.keys())
  return {
    "manifest_top_keys": sorted(manifest.keys()),
    "summary_top_keys": sorted(summary.keys()),
    "manifest_project_profile_keys": sample_profile_keys,
    "summary_project_report_keys": sample_report_keys,
  }


def _fallback_probe(files: list[Path]) -> tuple[bool, list[str]]:
  exercised_on: list[str] = []
  for path in files:
    if not path.is_file():
      continue
    source = path.read_text(encoding="utf-8")
    try:
      _check_ts_syntax(source)
    except AsgError:
      if _ts_source_valid_via_tsc(source):
        exercised_on.append(str(path))
  return (len(exercised_on) > 0, exercised_on)


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--manifest", required=False, help="workspace-manifest.json; defaults to sibling of summary")
  parser.add_argument("--summary", required=True)
  parser.add_argument("--run-id", required=True)
  parser.add_argument("--out", required=True)
  parser.add_argument("--parser-gate-status", choices=("pass", "fail"), required=True)
  parser.add_argument("--workspace-gate-status", choices=("pass", "fail"), required=True)
  parser.add_argument("--probe-files", default=",".join(DEFAULT_PROBE_FILES))
  args = parser.parse_args()

  summary_path = Path(args.summary).resolve()
  manifest_path = Path(args.manifest).resolve() if args.manifest else (summary_path.parent / "workspace-manifest.json").resolve()
  manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
  summary = json.loads(summary_path.read_text(encoding="utf-8"))
  stable_view = _stable_summary_view(summary)
  shape_view = _shape_view(manifest, summary)
  analyzed = sorted([r["project_id"] for r in summary["project_reports"] if r["analyzed"]])
  probe_files = [Path(p.strip()) for p in args.probe_files.split(",") if p.strip()]
  fallback_exercised, fallback_paths = _fallback_probe(probe_files)
  overlay_state = _overlay_policy_state()

  payload = {
    "v": "workspace-soak-status.v0",
    "authority": "advisory",
    "run_id": args.run_id,
    "manifest_path": str(manifest_path),
    "summary_path": str(summary_path),
    "summary_stable_digest": _sha256(stable_view),
    "manifest_shape_digest": _sha256({
      "manifest_top_keys": shape_view["manifest_top_keys"],
      "manifest_project_profile_keys": shape_view["manifest_project_profile_keys"],
    }),
    "summary_shape_digest": _sha256({
      "summary_top_keys": shape_view["summary_top_keys"],
      "summary_project_report_keys": shape_view["summary_project_report_keys"],
    }),
    "shape_keys": shape_view,
    "run_id_noise_signals": {
      "manifest_has_run_id_key": "run_id" in manifest,
      "summary_has_run_id_key": "run_id" in summary,
    },
    "coverage": summary["coverage"],
    "analyzed_projects": analyzed,
    "analyzed_with_conformance": summary["coverage"]["analyzed_with_conformance"],
    "analyzed_with_protocol_flow": summary["coverage"]["analyzed_with_protocol_flow"],
    **overlay_state,
    "gates": {
      "typescript_parser": args.parser_gate_status,
      "workspace_ingest": args.workspace_gate_status,
    },
    "ts_fallback_exercised": fallback_exercised,
    "ts_fallback_probe_paths": fallback_paths,
  }

  out_path = Path(args.out)
  out_path.parent.mkdir(parents=True, exist_ok=True)
  out_path.write_text(_canonical_json(payload) + "\n", encoding="utf-8")
  print(f"ok workspace soak-status out={out_path}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
