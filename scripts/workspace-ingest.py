#!/usr/bin/env python3
"""Run deterministic workspace-level orchestration over project analyses."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from runtime.atomic_kernel.workspace_ingest import (
  validate_workspace_manifest,
  validate_workspace_summary,
  hash_obj,
  render_workspace_summary_md,
  load_project_analysis_overlay,
)


DEFAULT_ALLOWLIST = [
  "atomic-kernel",
  "metaverse-kit",
  "tetragrammatron-os",
  "automaton",
  "autonomous-ai",
  "waveform-core",
  "universal-life-protocol",
]


def _canonical_json(data: Any) -> str:
  return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest_file(path: Path) -> str:
  return hash_obj(path.read_text(encoding="utf-8"))


def _aggregate_counts(project_rows: list[dict[str, Any]]) -> dict[str, Any]:
  agg = {
    "files": 0,
    "asg_nodes": 0,
    "asg_edges": 0,
    "language_counts": {},
    "domain_counts": {},
    "patterns": {},
  }
  for row in project_rows:
    if not row["analyzed"]:
      continue
    summary = row["summary"]
    agg["files"] += int(summary.get("files", 0))
    agg["asg_nodes"] += int(summary.get("asg_nodes", 0))
    agg["asg_edges"] += int(summary.get("asg_edges", 0))
    for k, v in summary.get("language_counts", {}).items():
      agg["language_counts"][k] = agg["language_counts"].get(k, 0) + int(v)
    for k, v in summary.get("domain_counts", {}).items():
      agg["domain_counts"][k] = agg["domain_counts"].get(k, 0) + int(v)
    for k, v in summary.get("patterns", {}).items():
      agg["patterns"][k] = agg["patterns"].get(k, 0) + int(v)
  agg["language_counts"] = {k: agg["language_counts"][k] for k in sorted(agg["language_counts"].keys())}
  agg["domain_counts"] = {k: agg["domain_counts"][k] for k in sorted(agg["domain_counts"].keys())}
  agg["patterns"] = {k: agg["patterns"][k] for k in sorted(agg["patterns"].keys())}
  return agg


def _pick_languages(project: dict[str, Any]) -> str:
  langs = [x for x in project.get("languages", []) if x in {"python", "typescript", "mjs"}]
  if not langs:
    return "python,typescript,mjs"
  return ",".join(langs)


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--workspace", required=True)
  parser.add_argument("--manifest", required=True)
  parser.add_argument("--out-root", required=True)
  parser.add_argument("--run-id", required=True)
  parser.add_argument("--allowlist", default=",".join(DEFAULT_ALLOWLIST))
  parser.add_argument("--mirror-root", default="")
  args = parser.parse_args()

  workspace = Path(args.workspace).resolve()
  manifest_path = Path(args.manifest).resolve()
  out_root = Path(args.out_root).resolve()
  run_id = args.run_id.strip()
  allowlist = {x.strip().lower() for x in args.allowlist.split(",") if x.strip()}
  mirror_root = Path(args.mirror_root).resolve() if args.mirror_root else None

  if not run_id:
    raise SystemExit("run-id must be non-empty")
  manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
  validate_workspace_manifest(manifest)
  if Path(manifest["workspace_root"]).resolve() != workspace:
    raise SystemExit("workspace root mismatch with manifest")

  run_dir = out_root / run_id
  projects_dir = run_dir / "projects"
  overlays_root = Path(__file__).resolve().parents[1] / "runtime" / "atomic_kernel" / "overlays" / "project-analysis"
  run_dir.mkdir(parents=True, exist_ok=True)
  projects_dir.mkdir(parents=True, exist_ok=True)

  # Re-emit canonical workspace manifest under run directory.
  (run_dir / "workspace-manifest.json").write_text(
    _canonical_json(manifest) + "\n",
    encoding="utf-8",
  )

  rows: list[dict[str, Any]] = []
  for project in manifest["projects"]:
    project_id = project["project_id"]
    project_root = Path(project["root_path"]).resolve()
    target_manifest = {
      "v": "analysis-target-manifest.v0",
      "authority": "advisory",
      "repo_path": str(project_root),
      "commit": project["git_commit"],
      "dirty": project["dirty"],
      "include_globs": project["include_globs"],
      "exclude_globs": project["exclude_globs"],
      "language_profile": project["project_kind"],
      "analysis_profile": project["analysis_profile"],
      "workspace_project_id": project_id,
      "overlay_applied": False,
      "overlay_exclude_globs": [],
    }
    proj_out = projects_dir / project_id
    proj_out.mkdir(parents=True, exist_ok=True)
    (proj_out / "target-manifest.json").write_text(
      _canonical_json(target_manifest) + "\n",
      encoding="utf-8",
    )

    selected = project_id.lower() in allowlist
    if not selected:
      rows.append(
        {
          "project_id": project_id,
          "root_path": str(project_root),
          "analyzed": False,
          "reason": "not_allowlisted",
          "report_path": None,
          "report_digest": None,
          "summary": {},
        }
      )
      continue
    if not project["analyzable"]:
      rows.append(
        {
          "project_id": project_id,
          "root_path": str(project_root),
          "analyzed": False,
          "reason": "not_analyzable",
          "report_path": None,
          "report_digest": None,
          "summary": {},
        }
      )
      continue

    merged_excludes = list(project.get("exclude_globs", []))
    overlay = None
    try:
      overlay = load_project_analysis_overlay(overlays_root, project_id, project_root)
    except Exception:
      rows.append(
        {
          "project_id": project_id,
          "root_path": str(project_root),
          "analyzed": False,
          "reason": "analysis_failed:overlay_invalid",
          "report_path": None,
          "report_digest": None,
          "summary": {},
        }
      )
      continue
    if overlay is not None:
      target_manifest["overlay_applied"] = True
      target_manifest["overlay_exclude_globs"] = list(overlay["exclude_globs"])
      merged_excludes.extend(overlay["exclude_globs"])
    merged_excludes = sorted(set(merged_excludes))
    # Rewrite target manifest after overlay application.
    (proj_out / "target-manifest.json").write_text(
      _canonical_json(target_manifest) + "\n",
      encoding="utf-8",
    )

    langs = _pick_languages(project)
    try:
      subprocess.run(
        [
          "bash",
          str((Path(__file__).resolve().parents[1] / "scripts" / "run-project-analysis.sh")),
          "--target",
          str(project_root),
          "--name",
          project_id,
          "--out-root",
          str(projects_dir),
          "--languages",
          langs,
          "--include-globs",
          ",".join(project.get("include_globs", [])),
          "--exclude-globs",
          ",".join(merged_excludes),
        ],
        check=True,
        capture_output=True,
        text=True,
      )
    except subprocess.CalledProcessError as exc:
      (projects_dir / project_id / "analysis-error.log").write_text(
        (exc.stdout or "") + "\n" + (exc.stderr or ""),
        encoding="utf-8",
      )
      rows.append(
        {
          "project_id": project_id,
          "root_path": str(project_root),
          "analyzed": False,
          "reason": f"analysis_failed:{exc.returncode}",
          "report_path": None,
          "report_digest": None,
          "summary": {},
        }
      )
      continue
    report_path = projects_dir / project_id / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    rows.append(
      {
        "project_id": project_id,
        "root_path": str(project_root),
        "analyzed": True,
        "reason": None,
        "report_path": str(report_path.relative_to(run_dir)),
        "report_digest": _digest_file(report_path),
        "summary": report["summary"],
      }
    )

  rows.sort(key=lambda r: (r["project_id"], r["root_path"]))
  analyzed = sum(1 for r in rows if r["analyzed"])
  skipped = len(rows) - analyzed
  analyzable = sum(1 for p in manifest["projects"] if p.get("analyzable") is True)
  analyzed_with_conformance = sum(
    1
    for r in rows
    if r["analyzed"] and int(r["summary"].get("domain_counts", {}).get("conformance", 0)) > 0
  )
  analyzed_with_protocol_flow = sum(
    1 for r in rows if r["analyzed"] and (projects_dir / r["project_id"] / "protocol-flow.json").is_file()
  )
  coverage = {
    "discovered": len(rows),
    "analyzable": analyzable,
    "analyzed": analyzed,
    "analyzed_with_conformance": analyzed_with_conformance,
    "analyzed_with_protocol_flow": analyzed_with_protocol_flow,
  }
  aggregate = _aggregate_counts(rows)
  inputs_digest = hash_obj(
    {
      "workspace_manifest_digest": _digest_file(run_dir / "workspace-manifest.json"),
      "projects": [
        {
          "project_id": r["project_id"],
          "analyzed": r["analyzed"],
          "report_digest": r["report_digest"],
          "reason": r["reason"],
        }
        for r in rows
      ],
    }
  )
  summary = {
    "v": "workspace-summary.v0",
    "authority": "advisory",
    "workspace_id": run_id,
    "workspace_root": str(workspace),
    "projects_total": len(rows),
    "projects_analyzed": analyzed,
    "projects_skipped": skipped,
    "coverage": coverage,
    "project_reports": rows,
    "aggregate_counts": aggregate,
    "inputs_digest": inputs_digest,
    "outputs_digest": "",
  }
  summary["outputs_digest"] = hash_obj(
    {
      "workspace_id": summary["workspace_id"],
      "projects_total": summary["projects_total"],
      "projects_analyzed": summary["projects_analyzed"],
      "projects_skipped": summary["projects_skipped"],
      "coverage": summary["coverage"],
      "aggregate_counts": summary["aggregate_counts"],
      "project_reports": summary["project_reports"],
      "inputs_digest": summary["inputs_digest"],
    }
  )
  validate_workspace_summary(summary)

  project_index = {
    "v": "workspace-project-index.v0",
    "authority": "advisory",
    "workspace_id": run_id,
    "projects": [
      {
        "project_id": r["project_id"],
        "analyzed": r["analyzed"],
        "report_path": r["report_path"],
      }
      for r in rows
    ],
  }

  summary_json = run_dir / "workspace-summary.json"
  summary_md = run_dir / "workspace-summary.md"
  index_json = run_dir / "project-index.json"
  summary_json.write_text(_canonical_json(summary) + "\n", encoding="utf-8")
  summary_md.write_text(render_workspace_summary_md(summary), encoding="utf-8")
  index_json.write_text(_canonical_json(project_index) + "\n", encoding="utf-8")

  if mirror_root is not None:
    mirror_dir = mirror_root / run_id
    mirror_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(summary_json, mirror_dir / "workspace-summary.json")
    shutil.copy2(summary_md, mirror_dir / "workspace-summary.md")
    shutil.copy2(index_json, mirror_dir / "project-index.json")

  print(f"ok workspace ingest out={run_dir}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
