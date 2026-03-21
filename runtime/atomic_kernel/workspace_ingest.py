"""Deterministic workspace-level discovery and orchestration helpers."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

SOURCE_SUFFIX_TO_LANG = {
  ".py": "python",
  ".ts": "typescript",
  ".mjs": "mjs",
}

DEFAULT_INCLUDE_GLOBS = ["**/*.py", "**/*.ts", "**/*.mjs"]
DEFAULT_EXCLUDE_GLOBS = [
  "**/.git/**",
  "**/node_modules/**",
  "**/.venv/**",
  "**/venv/**",
  "**/dist/**",
  "**/build/**",
  "**/.next/**",
  "**/coverage/**",
  "**/.cache/**",
  "**/site/**",
  "**/reports/**",
  "**/.obsidian/**",
  "**/fixtures/**",
  "**/must-reject/**",
  "**/accept/**",
  "**/vendor/**",
  "**/archive/**",
]

SKIP_DIRS = {
  ".git",
  "__pycache__",
  "node_modules",
  ".venv",
  "venv",
  "dist",
  "build",
  ".next",
  "coverage",
  ".cache",
  "site",
  "reports",
  ".obsidian",
}

PROJECT_MARKERS = {
  "package.json",
  "pyproject.toml",
  "requirements.txt",
  "Cargo.toml",
  "go.mod",
  "Makefile",
}

WORKSPACE_MANIFEST_KEYS = {
  "v",
  "authority",
  "workspace_root",
  "project_count",
  "projects",
  "discovery_rules",
  "scan_digest",
}

PROJECT_PROFILE_KEYS = {
  "v",
  "authority",
  "project_id",
  "name",
  "root_path",
  "git_root",
  "git_commit",
  "dirty",
  "markers",
  "languages",
  "project_kind",
  "include_globs",
  "exclude_globs",
  "analysis_profile",
  "analyzable",
}

PROJECT_ANALYSIS_OVERLAY_KEYS = {
  "v",
  "authority",
  "project_id",
  "root_path",
  "include_globs",
  "exclude_globs",
  "overlay_digest",
}

WORKSPACE_SUMMARY_KEYS = {
  "v",
  "authority",
  "workspace_id",
  "workspace_root",
  "projects_total",
  "projects_analyzed",
  "projects_skipped",
  "coverage",
  "project_reports",
  "aggregate_counts",
  "inputs_digest",
  "outputs_digest",
}

PROJECT_REPORT_KEYS = {
  "project_id",
  "root_path",
  "analyzed",
  "reason",
  "report_path",
  "report_digest",
  "summary",
}


class WorkspaceIngestError(ValueError):
  """Raised when workspace ingestion artifacts fail closed."""


def _canonical_json(data: Any) -> str:
  return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash_obj(data: Any) -> str:
  return "sha256:" + hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def compute_overlay_digest(overlay: dict[str, Any]) -> str:
  core = {
    "v": overlay["v"],
    "authority": overlay["authority"],
    "project_id": overlay["project_id"],
    "root_path": overlay["root_path"],
    "include_globs": overlay["include_globs"],
    "exclude_globs": overlay["exclude_globs"],
  }
  return hash_obj(core)


def _safe_git(path: Path, args: list[str]) -> tuple[bool, str]:
  proc = subprocess.run(
    ["git", "-C", str(path), *args],
    check=False,
    capture_output=True,
    text=True,
  )
  if proc.returncode != 0:
    return False, (proc.stderr or proc.stdout or "").strip()
  return True, proc.stdout.strip()


def _git_commit(path: Path) -> str | None:
  ok, out = _safe_git(path, ["rev-parse", "HEAD"])
  return out if ok and out else None


def _git_dirty(path: Path) -> bool | None:
  ok, out = _safe_git(path, ["status", "--porcelain"])
  if not ok:
    return None
  return bool(out.strip())


def _should_skip(path: Path) -> bool:
  return any(part in SKIP_DIRS for part in path.parts)


def detect_languages(project_root: Path) -> list[str]:
  seen: set[str] = set()
  for p in sorted(project_root.rglob("*")):
    if not p.is_file():
      continue
    if _should_skip(p):
      continue
    lang = SOURCE_SUFFIX_TO_LANG.get(p.suffix.lower())
    if lang:
      seen.add(lang)
  return sorted(seen)


def _project_kind(languages: list[str], markers: list[str]) -> str:
  if len(languages) > 1:
    return "mixed"
  if languages == ["python"]:
    return "python"
  if languages == ["typescript"]:
    return "typescript"
  if languages == ["mjs"]:
    return "mjs"
  if not languages and any(m in markers for m in ("package.json", "pyproject.toml", "requirements.txt")):
    return "scripts-only"
  if not languages:
    return "docs-only"
  return "core"


def _project_id(path: Path) -> str:
  return path.name.lower().replace(" ", "-")


def _include_globs_for_languages(languages: list[str]) -> list[str]:
  globs: list[str] = []
  if "python" in languages:
    globs.append("**/*.py")
  if "typescript" in languages:
    globs.append("**/*.ts")
  if "mjs" in languages:
    globs.append("**/*.mjs")
  return globs or list(DEFAULT_INCLUDE_GLOBS)


def build_project_profile(project_root: Path) -> dict[str, Any]:
  root = project_root.resolve()
  markers = sorted(m for m in PROJECT_MARKERS if (root / m).exists())
  git_root = (root / ".git").exists()
  commit = _git_commit(root) if git_root else None
  dirty = _git_dirty(root) if git_root else None
  languages = detect_languages(root)
  kind = _project_kind(languages, markers)
  analyzable = bool(git_root)
  return {
    "v": "project-profile.v0",
    "authority": "advisory",
    "project_id": _project_id(root),
    "name": root.name,
    "root_path": str(root),
    "git_root": git_root,
    "git_commit": commit,
    "dirty": dirty,
    "markers": markers,
    "languages": languages,
    "project_kind": kind,
    "include_globs": _include_globs_for_languages(languages),
    "exclude_globs": list(DEFAULT_EXCLUDE_GLOBS),
    "analysis_profile": "workspace-project.v0",
    "analyzable": analyzable,
  }


def validate_project_analysis_overlay(overlay: dict[str, Any]) -> None:
  if not isinstance(overlay, dict):
    raise WorkspaceIngestError("project overlay must be object")
  keys = set(overlay.keys())
  if keys != PROJECT_ANALYSIS_OVERLAY_KEYS:
    raise WorkspaceIngestError(
      f"project overlay key mismatch missing={sorted(PROJECT_ANALYSIS_OVERLAY_KEYS-keys)} extra={sorted(keys-PROJECT_ANALYSIS_OVERLAY_KEYS)}"
    )
  if overlay["v"] != "project-analysis-overlay.v0":
    raise WorkspaceIngestError("project overlay v invalid")
  if overlay["authority"] != "advisory":
    raise WorkspaceIngestError("project overlay authority invalid")
  for key in ("project_id", "root_path"):
    if not isinstance(overlay[key], str) or not overlay[key]:
      raise WorkspaceIngestError(f"project overlay {key} invalid")
  for key in ("include_globs", "exclude_globs"):
    if not isinstance(overlay[key], list):
      raise WorkspaceIngestError(f"project overlay {key} invalid")
    prev = None
    seen: set[str] = set()
    for idx, value in enumerate(overlay[key]):
      if not isinstance(value, str) or not value:
        raise WorkspaceIngestError(f"project overlay {key}[{idx}] invalid")
      if value in seen:
        raise WorkspaceIngestError(f"project overlay {key} duplicate: {value}")
      seen.add(value)
      if prev is not None and value < prev:
        raise WorkspaceIngestError(f"project overlay {key} not sorted")
      prev = value
  # W4 policy: overlays only narrow file sets; no include expansion.
  if overlay["include_globs"] != []:
    raise WorkspaceIngestError("project overlay include_globs must be empty in v0")
  got = overlay["overlay_digest"]
  if not isinstance(got, str) or not got.startswith("sha256:"):
    raise WorkspaceIngestError("project overlay overlay_digest invalid")
  want = compute_overlay_digest(overlay)
  if got != want:
    raise WorkspaceIngestError("project overlay digest mismatch")


def load_project_analysis_overlay(overlays_root: Path, project_id: str, project_root: Path) -> dict[str, Any] | None:
  overlay_path = overlays_root / f"{project_id}.overlay.json"
  if not overlay_path.is_file():
    return None
  overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
  validate_project_analysis_overlay(overlay)
  if overlay["project_id"] != project_id:
    raise WorkspaceIngestError("project overlay project_id mismatch")
  if Path(overlay["root_path"]).resolve() != project_root.resolve():
    raise WorkspaceIngestError("project overlay root_path mismatch")
  return overlay


def discover_projects(workspace_root: Path) -> list[dict[str, Any]]:
  root = workspace_root.resolve()
  if not root.is_dir():
    raise WorkspaceIngestError(f"workspace is not directory: {root}")
  projects: list[dict[str, Any]] = []
  for child in sorted(root.iterdir(), key=lambda p: p.name):
    if not child.is_dir():
      continue
    if child.name.startswith("."):
      continue
    marker_hits = [m for m in PROJECT_MARKERS if (child / m).exists()]
    has_git = (child / ".git").exists()
    if not has_git and not marker_hits:
      continue
    projects.append(build_project_profile(child))
  projects.sort(key=lambda p: (p["project_id"], p["root_path"]))
  return projects


def build_workspace_manifest(workspace_root: Path, projects: list[dict[str, Any]]) -> dict[str, Any]:
  root = workspace_root.resolve()
  manifest = {
    "v": "workspace-manifest.v0",
    "authority": "advisory",
    "workspace_root": str(root),
    "project_count": len(projects),
    "projects": projects,
    "discovery_rules": {
      "project_markers": sorted(PROJECT_MARKERS),
      "skip_dirs": sorted(SKIP_DIRS),
      "analyzable_requires_git_root": True,
      "deterministic_order": "project_id_then_root_path",
    },
    "scan_digest": "",
  }
  manifest["scan_digest"] = hash_obj(
    {
      "workspace_root": manifest["workspace_root"],
      "projects": [
        {
          "project_id": p["project_id"],
          "root_path": p["root_path"],
          "git_commit": p["git_commit"],
          "dirty": p["dirty"],
          "languages": p["languages"],
          "analyzable": p["analyzable"],
        }
        for p in projects
      ],
      "discovery_rules": manifest["discovery_rules"],
    }
  )
  return manifest


def validate_workspace_manifest(manifest: dict[str, Any]) -> None:
  if not isinstance(manifest, dict):
    raise WorkspaceIngestError("workspace manifest must be object")
  keys = set(manifest.keys())
  if keys != WORKSPACE_MANIFEST_KEYS:
    raise WorkspaceIngestError(
      f"workspace manifest key mismatch missing={sorted(WORKSPACE_MANIFEST_KEYS-keys)} extra={sorted(keys-WORKSPACE_MANIFEST_KEYS)}"
    )
  if manifest["v"] != "workspace-manifest.v0":
    raise WorkspaceIngestError("workspace manifest v invalid")
  if manifest["authority"] != "advisory":
    raise WorkspaceIngestError("workspace manifest authority invalid")
  if not isinstance(manifest["workspace_root"], str) or not manifest["workspace_root"]:
    raise WorkspaceIngestError("workspace_root invalid")
  if not isinstance(manifest["project_count"], int) or manifest["project_count"] < 0:
    raise WorkspaceIngestError("project_count invalid")
  if not isinstance(manifest["projects"], list):
    raise WorkspaceIngestError("projects invalid")
  if manifest["project_count"] != len(manifest["projects"]):
    raise WorkspaceIngestError("project_count mismatch")
  prev = None
  seen: set[str] = set()
  for idx, project in enumerate(manifest["projects"]):
    validate_project_profile(project)
    sort_key = (project["project_id"], project["root_path"])
    if prev is not None and sort_key < prev:
      raise WorkspaceIngestError(f"projects not deterministically sorted at index {idx}")
    prev = sort_key
    uniq = f"{project['project_id']}::{project['root_path']}"
    if uniq in seen:
      raise WorkspaceIngestError(f"duplicate project entry: {uniq}")
    seen.add(uniq)
  if not isinstance(manifest["discovery_rules"], dict):
    raise WorkspaceIngestError("discovery_rules invalid")
  if not isinstance(manifest["scan_digest"], str) or not manifest["scan_digest"].startswith("sha256:"):
    raise WorkspaceIngestError("scan_digest invalid")


def validate_project_profile(profile: dict[str, Any]) -> None:
  if not isinstance(profile, dict):
    raise WorkspaceIngestError("project profile must be object")
  keys = set(profile.keys())
  if keys != PROJECT_PROFILE_KEYS:
    raise WorkspaceIngestError(
      f"project profile key mismatch missing={sorted(PROJECT_PROFILE_KEYS-keys)} extra={sorted(keys-PROJECT_PROFILE_KEYS)}"
    )
  if profile["v"] != "project-profile.v0":
    raise WorkspaceIngestError("project profile v invalid")
  if profile["authority"] != "advisory":
    raise WorkspaceIngestError("project profile authority invalid")
  for k in ("project_id", "name", "root_path", "project_kind", "analysis_profile"):
    if not isinstance(profile[k], str) or not profile[k]:
      raise WorkspaceIngestError(f"project profile {k} invalid")
  if not isinstance(profile["git_root"], bool):
    raise WorkspaceIngestError("project profile git_root invalid")
  if profile["git_commit"] is not None and (not isinstance(profile["git_commit"], str) or not profile["git_commit"]):
    raise WorkspaceIngestError("project profile git_commit invalid")
  if profile["dirty"] is not None and not isinstance(profile["dirty"], bool):
    raise WorkspaceIngestError("project profile dirty invalid")
  for k in ("markers", "languages", "include_globs", "exclude_globs"):
    if not isinstance(profile[k], list):
      raise WorkspaceIngestError(f"project profile {k} invalid")
    for idx, value in enumerate(profile[k]):
      if not isinstance(value, str) or not value:
        raise WorkspaceIngestError(f"project profile {k}[{idx}] invalid")
  if not isinstance(profile["analyzable"], bool):
    raise WorkspaceIngestError("project profile analyzable invalid")


def render_workspace_summary_md(summary: dict[str, Any]) -> str:
  agg = summary["aggregate_counts"]
  cov = summary["coverage"]
  lines = [
    "# Workspace Summary",
    "",
    f"- workspace_id: `{summary['workspace_id']}`",
    f"- workspace_root: `{summary['workspace_root']}`",
    f"- projects_total: {summary['projects_total']}",
    f"- projects_analyzed: {summary['projects_analyzed']}",
    f"- projects_skipped: {summary['projects_skipped']}",
    "",
    "## Coverage Delta",
    f"- discovered: {cov['discovered']}",
    f"- analyzable: {cov['analyzable']}",
    f"- analyzed: {cov['analyzed']}",
    f"- analyzed_with_conformance: {cov['analyzed_with_conformance']}",
    f"- analyzed_with_protocol_flow: {cov['analyzed_with_protocol_flow']}",
    "",
    "## Aggregate Counts",
    f"- files: {agg['files']}",
    f"- asg_nodes: {agg['asg_nodes']}",
    f"- asg_edges: {agg['asg_edges']}",
    "- language_counts:",
  ]
  for k, v in agg["language_counts"].items():
    lines.append(f"  - {k}: {v}")
  lines.append("- domain_counts:")
  for k, v in agg["domain_counts"].items():
    lines.append(f"  - {k}: {v}")
  lines.append("- patterns:")
  for k, v in agg["patterns"].items():
    lines.append(f"  - {k}: {v}")
  lines.extend(
    [
      "",
      "## Digests",
      f"- inputs_digest: `{summary['inputs_digest']}`",
      f"- outputs_digest: `{summary['outputs_digest']}`",
      "",
    ]
  )
  return "\n".join(lines)


def validate_workspace_summary(summary: dict[str, Any]) -> None:
  if not isinstance(summary, dict):
    raise WorkspaceIngestError("workspace summary must be object")
  keys = set(summary.keys())
  if keys != WORKSPACE_SUMMARY_KEYS:
    raise WorkspaceIngestError(
      f"workspace summary key mismatch missing={sorted(WORKSPACE_SUMMARY_KEYS-keys)} extra={sorted(keys-WORKSPACE_SUMMARY_KEYS)}"
    )
  if summary["v"] != "workspace-summary.v0":
    raise WorkspaceIngestError("workspace summary v invalid")
  if summary["authority"] != "advisory":
    raise WorkspaceIngestError("workspace summary authority invalid")
  if not isinstance(summary["workspace_id"], str) or not summary["workspace_id"]:
    raise WorkspaceIngestError("workspace_id invalid")
  if not isinstance(summary["workspace_root"], str) or not summary["workspace_root"]:
    raise WorkspaceIngestError("workspace_root invalid")
  for k in ("projects_total", "projects_analyzed", "projects_skipped"):
    if not isinstance(summary[k], int) or summary[k] < 0:
      raise WorkspaceIngestError(f"{k} invalid")
  if summary["projects_total"] != summary["projects_analyzed"] + summary["projects_skipped"]:
    raise WorkspaceIngestError("project totals do not balance")
  cov = summary["coverage"]
  if not isinstance(cov, dict):
    raise WorkspaceIngestError("coverage invalid")
  cov_keys = {
    "discovered",
    "analyzable",
    "analyzed",
    "analyzed_with_conformance",
    "analyzed_with_protocol_flow",
  }
  got_cov = set(cov.keys())
  if got_cov != cov_keys:
    raise WorkspaceIngestError(
      f"coverage key mismatch missing={sorted(cov_keys-got_cov)} extra={sorted(got_cov-cov_keys)}"
    )
  for k in cov_keys:
    if not isinstance(cov[k], int) or cov[k] < 0:
      raise WorkspaceIngestError(f"coverage.{k} invalid")
  if cov["discovered"] != summary["projects_total"]:
    raise WorkspaceIngestError("coverage.discovered mismatch")
  if cov["analyzed"] != summary["projects_analyzed"]:
    raise WorkspaceIngestError("coverage.analyzed mismatch")
  if cov["analyzed_with_conformance"] > cov["analyzed"]:
    raise WorkspaceIngestError("coverage.analyzed_with_conformance exceeds analyzed")
  if cov["analyzed_with_protocol_flow"] > cov["analyzed"]:
    raise WorkspaceIngestError("coverage.analyzed_with_protocol_flow exceeds analyzed")
  if not isinstance(summary["project_reports"], list):
    raise WorkspaceIngestError("project_reports invalid")
  if summary["projects_total"] != len(summary["project_reports"]):
    raise WorkspaceIngestError("project_reports count mismatch")
  prev = None
  for idx, row in enumerate(summary["project_reports"]):
    if not isinstance(row, dict):
      raise WorkspaceIngestError(f"project_reports[{idx}] invalid")
    row_keys = set(row.keys())
    if row_keys != PROJECT_REPORT_KEYS:
      raise WorkspaceIngestError(
        f"project_reports[{idx}] key mismatch missing={sorted(PROJECT_REPORT_KEYS-row_keys)} extra={sorted(row_keys-PROJECT_REPORT_KEYS)}"
      )
    if not isinstance(row["project_id"], str) or not row["project_id"]:
      raise WorkspaceIngestError(f"project_reports[{idx}].project_id invalid")
    if not isinstance(row["root_path"], str) or not row["root_path"]:
      raise WorkspaceIngestError(f"project_reports[{idx}].root_path invalid")
    if not isinstance(row["analyzed"], bool):
      raise WorkspaceIngestError(f"project_reports[{idx}].analyzed invalid")
    if row["reason"] is not None and not isinstance(row["reason"], str):
      raise WorkspaceIngestError(f"project_reports[{idx}].reason invalid")
    if row["report_path"] is not None and not isinstance(row["report_path"], str):
      raise WorkspaceIngestError(f"project_reports[{idx}].report_path invalid")
    if row["report_digest"] is not None and (
      not isinstance(row["report_digest"], str) or not row["report_digest"].startswith("sha256:")
    ):
      raise WorkspaceIngestError(f"project_reports[{idx}].report_digest invalid")
    if not isinstance(row["summary"], dict):
      raise WorkspaceIngestError(f"project_reports[{idx}].summary invalid")
    sort_key = (row["project_id"], row["root_path"])
    if prev is not None and sort_key < prev:
      raise WorkspaceIngestError(f"project_reports not deterministically sorted at index {idx}")
    prev = sort_key

  agg = summary["aggregate_counts"]
  if not isinstance(agg, dict):
    raise WorkspaceIngestError("aggregate_counts invalid")
  for k in ("files", "asg_nodes", "asg_edges"):
    if not isinstance(agg.get(k), int) or agg[k] < 0:
      raise WorkspaceIngestError(f"aggregate_counts.{k} invalid")
  for k in ("language_counts", "domain_counts", "patterns"):
    if not isinstance(agg.get(k), dict):
      raise WorkspaceIngestError(f"aggregate_counts.{k} invalid")
    for key, value in agg[k].items():
      if not isinstance(key, str) or not key:
        raise WorkspaceIngestError(f"aggregate_counts.{k} key invalid")
      if not isinstance(value, int) or value < 0:
        raise WorkspaceIngestError(f"aggregate_counts.{k}[{key}] invalid")

  for k in ("inputs_digest", "outputs_digest"):
    if not isinstance(summary[k], str) or not summary[k].startswith("sha256:"):
      raise WorkspaceIngestError(f"{k} invalid")

  expected_outputs = hash_obj(
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
  if summary["outputs_digest"] != expected_outputs:
    raise WorkspaceIngestError("outputs_digest mismatch")
