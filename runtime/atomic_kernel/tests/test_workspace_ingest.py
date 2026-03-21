from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runtime.atomic_kernel.workspace_ingest import (
  build_workspace_manifest,
  compute_overlay_digest,
  discover_projects,
  hash_obj,
  load_project_analysis_overlay,
  validate_project_analysis_overlay,
  validate_workspace_manifest,
  validate_workspace_summary,
  WorkspaceIngestError,
)


class WorkspaceIngestTests(unittest.TestCase):
  def test_discover_projects_is_deterministic(self) -> None:
    with tempfile.TemporaryDirectory() as td:
      root = Path(td)
      p1 = root / "beta-proj"
      p2 = root / "alpha-proj"
      p1.mkdir()
      p2.mkdir()
      (p1 / ".git").mkdir()
      (p2 / ".git").mkdir()
      (p1 / "a.py").write_text("print('x')\n", encoding="utf-8")
      (p2 / "b.ts").write_text("export const x = 1;\n", encoding="utf-8")

      d1 = discover_projects(root)
      d2 = discover_projects(root)
      self.assertEqual(d1, d2)
      self.assertEqual([p["project_id"] for p in d1], ["alpha-proj", "beta-proj"])

      manifest = build_workspace_manifest(root, d1)
      validate_workspace_manifest(manifest)
      self.assertEqual(manifest["project_count"], 2)

  def test_workspace_summary_digest_and_validation(self) -> None:
    summary = {
      "v": "workspace-summary.v0",
      "authority": "advisory",
      "workspace_id": "devops-scan-001",
      "workspace_root": "/tmp/devops",
      "projects_total": 2,
      "projects_analyzed": 1,
      "projects_skipped": 1,
      "coverage": {
        "discovered": 2,
        "analyzable": 1,
        "analyzed": 1,
        "analyzed_with_conformance": 0,
        "analyzed_with_protocol_flow": 0,
      },
      "project_reports": [
        {
          "project_id": "alpha",
          "root_path": "/tmp/devops/alpha",
          "analyzed": True,
          "reason": None,
          "report_path": "projects/alpha/report.json",
          "report_digest": "sha256:" + ("a" * 64),
          "summary": {
            "files": 1,
            "language_counts": {"python": 1},
            "domain_counts": {"core": 1},
            "asg_nodes": 3,
            "asg_edges": 2,
            "patterns": {"Facade": 1},
          },
        },
        {
          "project_id": "beta",
          "root_path": "/tmp/devops/beta",
          "analyzed": False,
          "reason": "not_allowlisted",
          "report_path": None,
          "report_digest": None,
          "summary": {},
        },
      ],
      "aggregate_counts": {
        "files": 1,
        "asg_nodes": 3,
        "asg_edges": 2,
        "language_counts": {"python": 1},
        "domain_counts": {"core": 1},
        "patterns": {"Facade": 1},
      },
      "inputs_digest": "sha256:" + ("b" * 64),
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

    summary_bad = dict(summary)
    summary_bad["outputs_digest"] = "sha256:" + ("0" * 64)
    with self.assertRaises(WorkspaceIngestError):
      validate_workspace_summary(summary_bad)

  def test_project_overlay_validation_and_load(self) -> None:
    with tempfile.TemporaryDirectory() as td:
      root = Path(td)
      proj = root / "demo-proj"
      proj.mkdir()
      overlays = root / "overlays"
      overlays.mkdir()
      overlay = {
        "v": "project-analysis-overlay.v0",
        "authority": "advisory",
        "project_id": "demo-proj",
        "root_path": str(proj.resolve()),
        "include_globs": [],
        "exclude_globs": sorted(["**/dist/**", "**/vendor/**"]),
        "overlay_digest": "",
      }
      overlay["overlay_digest"] = compute_overlay_digest(overlay)
      (overlays / "demo-proj.overlay.json").write_text(
        json.dumps(overlay, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
      )
      loaded = load_project_analysis_overlay(overlays, "demo-proj", proj)
      self.assertIsNotNone(loaded)
      assert loaded is not None
      self.assertEqual(loaded["exclude_globs"], ["**/dist/**", "**/vendor/**"])

  def test_project_overlay_rejects_include_expansion(self) -> None:
    overlay = {
      "v": "project-analysis-overlay.v0",
      "authority": "advisory",
      "project_id": "x",
      "root_path": "/tmp/x",
      "include_globs": ["**/*.ts"],
      "exclude_globs": [],
      "overlay_digest": "sha256:" + ("0" * 64),
    }
    with self.assertRaises(WorkspaceIngestError):
      validate_project_analysis_overlay(overlay)


if __name__ == "__main__":
  unittest.main()
