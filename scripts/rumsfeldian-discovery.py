#!/usr/bin/env python3
"""Generate a deterministic manifest-granular Rumsfeldian workspace analysis."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

MARKER_FILES = (
  "package.json",
  "pyproject.toml",
  "requirements.txt",
  "Cargo.toml",
  "go.mod",
  "Makefile",
)

SKIP_DIRS = {
  ".git",
  "node_modules",
  ".venv",
  "venv",
  "__pycache__",
  "dist",
  "build",
  ".next",
  ".cache",
  "coverage",
}

ARCHIVE_TOKENS = {
  "archive",
  "backup",
  "corrupt",
  "deprecated",
  "depreciated",
  "legacy",
  "old",
}

MIRROR_TOKENS = {
  "fixture",
  "fixtures",
  "vendor",
  "mirror",
  "test-repo",
  "test-repos",
  "third_party",
  "third-party",
  "examples",
}

PRIMARY_CODE_EXTENSIONS = {
  ".py",
  ".ts",
  ".tsx",
  ".js",
  ".jsx",
  ".mjs",
  ".cjs",
  ".rs",
  ".go",
  ".java",
  ".kt",
  ".rb",
  ".php",
  ".c",
  ".cc",
  ".cpp",
  ".h",
  ".hpp",
  ".cs",
  ".scala",
  ".sh",
  ".ps1",
}

LANG_BY_EXT = {
  ".py": "python",
  ".ts": "typescript",
  ".tsx": "typescript",
  ".js": "javascript",
  ".jsx": "javascript",
  ".mjs": "javascript",
  ".cjs": "javascript",
  ".rs": "rust",
  ".go": "go",
}

ABS_WORKSPACE_PATH_RE = re.compile(r"/home/main/devops/[A-Za-z0-9._\- /]+")
REL_PATH_RE = re.compile(r"(?<![A-Za-z0-9_.-])\.\./[A-Za-z0-9._/\-]+")


def canonical_json(data: Any) -> str:
  return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(payload: str) -> str:
  import hashlib

  return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_token(s: str) -> str:
  return s.strip().lower().replace("\\", "/")


def classify_stratum(path: Path, workspace_root: Path) -> str:
  rel = str(path.resolve().relative_to(workspace_root)).lower()
  parts = re.split(r"[/ _\-.]+", rel)
  if any(tok in ARCHIVE_TOKENS for tok in parts) or any(tok in rel for tok in ARCHIVE_TOKENS):
    return "archive/backup/corrupt"
  if any(tok in MIRROR_TOKENS for tok in parts) or any(tok in rel for tok in MIRROR_TOKENS):
    return "mirror/vendor/fixture"
  return "active"


@dataclass
class Component:
  root: Path
  markers: set[str] = field(default_factory=set)
  stratum: str = "active"
  file_count: int = 0
  size_bytes: int = 0
  last_mtime: float = 0.0
  ext_counts: Counter[str] = field(default_factory=Counter)
  path_signals: set[str] = field(default_factory=set)
  dependencies: set[Path] = field(default_factory=set)
  language: str = "other"
  detected_patterns: list[str] = field(default_factory=list)
  readiness: str = "low"
  readiness_category: str = "needs_major_work"
  readiness_rationale: str = ""
  capabilities: dict[str, bool] = field(default_factory=dict)
  description: str = ""

  def stable_id(self, workspace_root: Path) -> str:
    rel = self.root.resolve().relative_to(workspace_root.resolve())
    return str(rel).replace("\\", "/")

  def top_project(self, workspace_root: Path) -> str:
    rel = self.stable_id(workspace_root)
    return rel.split("/", 1)[0]


def discover_components(workspace_root: Path) -> dict[Path, Component]:
  components: dict[Path, Component] = {}
  for dirpath, dirnames, filenames in os.walk(workspace_root, topdown=True, followlinks=False):
    dirnames[:] = [d for d in sorted(dirnames) if d not in SKIP_DIRS]
    marker_hits = sorted(set(f for f in filenames if f in MARKER_FILES))
    if not marker_hits:
      continue
    root = Path(dirpath).resolve()
    if root == workspace_root.resolve():
      continue
    comp = components.get(root)
    if comp is None:
      comp = Component(root=root)
      components[root] = comp
    comp.markers.update(marker_hits)
  for comp in components.values():
    comp.stratum = classify_stratum(comp.root, workspace_root)
  return components


def nearest_component_parent(path: Path, component_roots: set[Path], workspace_root: Path) -> Path | None:
  cur = path.resolve()
  while True:
    if cur in component_roots:
      return cur
    if cur == workspace_root or cur.parent == cur:
      return None
    cur = cur.parent


def update_component_metrics(workspace_root: Path, components: dict[Path, Component]) -> dict[str, int]:
  component_roots = set(components.keys())
  by_language = {"python": 0, "typescript": 0, "javascript": 0, "rust": 0, "go": 0, "other": 0}

  for dirpath, dirnames, filenames in os.walk(workspace_root, topdown=True, followlinks=False):
    dirnames[:] = [d for d in sorted(dirnames) if d not in SKIP_DIRS]
    base = Path(dirpath)
    for filename in sorted(filenames):
      path = (base / filename).resolve()
      parent = nearest_component_parent(path.parent, component_roots, workspace_root)
      if parent is None:
        continue
      comp = components[parent]
      try:
        st = path.stat()
      except OSError:
        continue
      comp.file_count += 1
      comp.size_bytes += int(st.st_size)
      comp.last_mtime = max(comp.last_mtime, float(st.st_mtime))
      ext = path.suffix.lower()
      comp.ext_counts[ext] += 1

      if ext in LANG_BY_EXT:
        by_language[LANG_BY_EXT[ext]] += 1
      elif ext in PRIMARY_CODE_EXTENSIONS:
        by_language["other"] += 1

      lp = str(path).lower()
      for tok in (
        "control",
        "runtime",
        "kernel",
        "bridge",
        "adapter",
        "gateway",
        "proxy",
        "carrier",
        "transport",
        "bundle",
        "packet",
        "schema",
        "abi",
        "protocol",
        "conformance",
        "validate",
        "validator",
        "must-reject",
        "golden",
        "replay",
        "deterministic",
        "portal",
        "projection",
        "render",
        "viewer",
        "ui",
        "diagram",
        "docs",
      ):
        if tok in lp:
          comp.path_signals.add(tok)
  return by_language


def assign_primary_language(comp: Component) -> str:
  score = {
    "python": comp.ext_counts[".py"],
    "typescript": comp.ext_counts[".ts"] + comp.ext_counts[".tsx"],
    "javascript": comp.ext_counts[".js"] + comp.ext_counts[".jsx"] + comp.ext_counts[".mjs"] + comp.ext_counts[".cjs"],
    "rust": comp.ext_counts[".rs"],
    "go": comp.ext_counts[".go"],
  }
  best_lang, best_count = "other", 0
  for lang in ("python", "typescript", "javascript", "rust", "go"):
    if score[lang] > best_count:
      best_lang, best_count = lang, score[lang]
  if best_count == 0:
    return "other"
  return best_lang


def resolve_dep_target(candidate: Path, components: dict[Path, Component], workspace_root: Path) -> Path | None:
  cand = candidate.resolve()
  if not str(cand).startswith(str(workspace_root.resolve())):
    return None
  cur = cand
  while True:
    if cur in components:
      return cur
    if cur == workspace_root or cur.parent == cur:
      return None
    cur = cur.parent


def extract_dependencies(workspace_root: Path, components: dict[Path, Component]) -> None:
  roots = sorted(components.keys(), key=lambda p: str(p))
  for root in roots:
    comp = components[root]
    for marker in sorted(comp.markers):
      marker_path = root / marker
      try:
        text = marker_path.read_text(encoding="utf-8", errors="ignore")
      except OSError:
        continue

      if marker == "package.json":
        try:
          pkg = json.loads(text)
        except json.JSONDecodeError:
          pkg = {}
        workspaces = pkg.get("workspaces", [])
        patterns: list[str] = []
        if isinstance(workspaces, list):
          patterns = [str(x) for x in workspaces if isinstance(x, str)]
        elif isinstance(workspaces, dict):
          patterns = [str(x) for x in workspaces.get("packages", []) if isinstance(x, str)]
        for pattern in sorted(set(patterns)):
          for path in sorted(root.glob(pattern)):
            if not path.is_dir():
              continue
            target = resolve_dep_target(path, components, workspace_root)
            if target is not None and target != root:
              comp.dependencies.add(target)

      for match in sorted(set(ABS_WORKSPACE_PATH_RE.findall(text))):
        target = resolve_dep_target(Path(match), components, workspace_root)
        if target is not None and target != root:
          comp.dependencies.add(target)

      for rel in sorted(set(REL_PATH_RE.findall(text))):
        candidate = (root / rel).resolve()
        target = resolve_dep_target(candidate, components, workspace_root)
        if target is not None and target != root:
          comp.dependencies.add(target)


def map_capabilities(comp: Component) -> tuple[dict[str, bool], list[str], str, str, str]:
  s = comp.path_signals
  has_control = bool({"control", "runtime", "kernel"} & s)
  has_bridge = bool({"bridge", "adapter", "gateway", "proxy"} & s)
  has_carrier = bool({"carrier", "transport", "bundle", "packet", "schema", "abi", "protocol"} & s)
  has_conformance = bool({"conformance", "validate", "validator", "must-reject", "golden"} & s)
  has_projection = bool({"portal", "projection", "render", "viewer", "ui", "diagram"} & s)

  patterns: list[str] = []
  if has_control:
    patterns.append("ControlSurface")
  if has_bridge:
    patterns.append("BridgeLayer")
  if has_carrier:
    patterns.append("CarrierLayer")
  if has_conformance:
    patterns.append("ConformanceSurface")
  if has_projection:
    patterns.append("ProjectionSurface")

  score = 0
  score += 2 if has_conformance else 0
  score += 2 if has_carrier else 0
  score += 1 if has_control else 0
  score += 1 if has_bridge else 0
  score += 1 if any(m in comp.markers for m in ("package.json", "pyproject.toml", "Cargo.toml", "go.mod")) else 0
  score += 1 if {"replay", "deterministic", "schema", "abi", "validator"} & s else 0
  score -= 2 if comp.stratum != "active" else 0
  score -= 1 if not has_conformance else 0

  if score >= 5:
    readiness = "high"
  elif score >= 3:
    readiness = "medium"
  else:
    readiness = "low"

  if comp.stratum != "active":
    category = "not_encodable"
  elif readiness == "high" and has_conformance:
    category = "immediately_encodable"
  elif readiness == "medium":
    category = "needs_minor_work"
  else:
    category = "needs_major_work"

  rationale = (
    f"signals={','.join(sorted(patterns)) or 'none'}; "
    f"stratum={comp.stratum}; markers={','.join(sorted(comp.markers)) or 'none'}; score={score}"
  )

  if has_conformance and has_carrier:
    desc = "Protocol or runtime component with validation surface."
  elif has_projection:
    desc = "Projection/UI-oriented component."
  elif comp.language in {"python", "typescript", "javascript"}:
    desc = "Executable software component with partial protocol signals."
  else:
    desc = "Support or documentation-oriented component."

  return (
    {
      "has_control_surface": has_control,
      "has_bridge_layer": has_bridge,
      "has_carrier_layer": has_carrier,
      "has_conformance": has_conformance,
      "has_projection": has_projection,
      "detected_patterns": patterns,
      "encoding_readiness": readiness,
      "rationale": rationale,
    },
    patterns,
    readiness,
    category,
    desc,
  )


def compute_critical_path(components: dict[Path, Component], workspace_root: Path) -> list[str]:
  indegree: Counter[Path] = Counter()
  for comp in components.values():
    for dep in comp.dependencies:
      indegree[dep] += 1
  ranked = sorted(
    components.values(),
    key=lambda c: (
      0 if c.stratum == "active" else 1,
      {"high": 0, "medium": 1, "low": 2}.get(c.readiness, 2),
      -indegree[c.root],
      c.stable_id(workspace_root),
    ),
  )
  return [c.stable_id(workspace_root) for c in ranked[:3]]


def make_timeline(today: date) -> dict[str, Any]:
  optimistic = today + timedelta(days=120)
  realistic = today + timedelta(days=210)
  pessimistic = today + timedelta(days=330)
  return {
    "full_metaverse_expression": {
      "optimistic": optimistic.isoformat(),
      "realistic": realistic.isoformat(),
      "pessimistic": pessimistic.isoformat(),
    }
  }


def component_last_modified_iso(comp: Component) -> str:
  if comp.last_mtime <= 0:
    return "1970-01-01"
  return datetime.fromtimestamp(comp.last_mtime, tz=timezone.utc).date().isoformat()


def build_report(workspace_root: Path) -> dict[str, Any]:
  components = discover_components(workspace_root)
  by_language = update_component_metrics(workspace_root, components)
  extract_dependencies(workspace_root, components)

  ready_groups = {
    "immediately_encodable": [],
    "needs_minor_work": [],
    "needs_major_work": [],
    "not_encodable": [],
  }

  strata_counts: Counter[str] = Counter()
  projects_json: list[dict[str, Any]] = []
  capability_map: list[dict[str, Any]] = []
  dep_edges: list[dict[str, str]] = []

  for root in sorted(components.keys(), key=lambda p: str(p)):
    comp = components[root]
    comp.language = assign_primary_language(comp)
    (
      comp.capabilities,
      comp.detected_patterns,
      comp.readiness,
      comp.readiness_category,
      comp.description,
    ) = map_capabilities(comp)
    ready_groups[comp.readiness_category].append(comp.stable_id(workspace_root))
    strata_counts[comp.stratum] += 1

    deps = sorted({components[d].stable_id(workspace_root) for d in comp.dependencies if d in components})
    projects_json.append(
      {
        "name": comp.stable_id(workspace_root),
        "path": str(comp.root),
        "language": comp.language,
        "size_bytes": comp.size_bytes,
        "file_count": comp.file_count,
        "last_modified": component_last_modified_iso(comp),
        "description": comp.description,
        "dependencies": deps,
      }
    )
    capability_map.append(
      {
        "project": comp.stable_id(workspace_root),
        "capabilities": comp.capabilities,
      }
    )
    for dep in deps:
      dep_edges.append({"from": comp.stable_id(workspace_root), "to": dep, "type": "depends"})

  nodes = [c.stable_id(workspace_root) for c in sorted(components.values(), key=lambda c: c.stable_id(workspace_root))]
  dep_edges = sorted(dep_edges, key=lambda e: (e["from"], e["to"], e["type"]))

  indegree = Counter(e["to"] for e in dep_edges)
  outdegree = Counter(e["from"] for e in dep_edges)
  recommendations: list[dict[str, Any]] = []
  ranked = sorted(
    components.values(),
    key=lambda c: (
      0 if c.stratum == "active" else 1,
      {"high": 0, "medium": 1, "low": 2}.get(c.readiness, 2),
      -(indegree[c.stable_id(workspace_root)] + outdegree[c.stable_id(workspace_root)]),
      c.stable_id(workspace_root),
    ),
  )

  priority = 1
  for comp in ranked:
    if comp.stratum != "active":
      continue
    recommendations.append(
      {
        "project": comp.stable_id(workspace_root),
        "priority": priority,
        "rationale": (
          f"readiness={comp.readiness}; "
          f"centrality={indegree[comp.stable_id(workspace_root)] + outdegree[comp.stable_id(workspace_root)]}; "
          f"patterns={','.join(comp.detected_patterns) or 'none'}"
        ),
        "estimated_effort_days": 7 if comp.readiness == "high" else (14 if comp.readiness == "medium" else 30),
        "expected_capabilities": sorted(comp.detected_patterns),
      }
    )
    priority += 1
    if priority > 5:
      break

  high_risks: list[str] = []
  medium_risks: list[str] = []
  low_risks: list[str] = []

  id_to_component = {c.stable_id(workspace_root): c for c in components.values()}
  non_active_refs = [e for e in dep_edges if id_to_component[e["to"]].stratum != "active"] if dep_edges else []
  if non_active_refs:
    high_risks.append(
      f"{len(non_active_refs)} dependency edges point from active components into archive/mirror strata."
    )

  low_conf = [c for c in components.values() if c.stratum == "active" and not c.capabilities.get("has_conformance", False)]
  if low_conf:
    high_risks.append(f"{len(low_conf)} active components lack explicit conformance signals (validate/must-reject/golden).")

  backup_count = strata_counts.get("archive/backup/corrupt", 0)
  mirror_count = strata_counts.get("mirror/vendor/fixture", 0)
  if backup_count:
    medium_risks.append(f"{backup_count} components are in archive/backup/corrupt strata and may drift from canonical intent.")
  if mirror_count:
    medium_risks.append(f"{mirror_count} components are mirror/vendor/fixture strata and can distort readiness or dependency centrality.")

  docs_or_other = [c for c in components.values() if c.language == "other"]
  if docs_or_other:
    low_risks.append(f"{len(docs_or_other)} components are non-code dominant; encoding value may be primarily metadata/provenance.")

  critical_path = compute_critical_path(components, workspace_root)

  report = {
    "rumsfeldian_analysis": {
      "known_knowns": [
        "Atomic kernel and deterministic replay gates are present and exercised.",
        "Manifest-discovery and workspace-level deterministic ingestion already exist.",
        "Projection-only and advisory authority boundaries are explicitly documented.",
      ],
      "known_unknowns": [
        "Manifest-level readiness varies widely across active and archival strata.",
        "Cross-component dependency graph includes both live and mirrored ecosystems.",
        "Conformance coverage is inconsistent outside core protocol surfaces.",
      ],
      "unknown_unknowns": [
        "Undeclared runtime coupling hidden in scripts/docs may bypass manifest dependency edges.",
        "Mirror/archive trees may contain latent regressions that appear as viable dependencies.",
        "Some components may embed protocol semantics without explicit ABI/schema declarations.",
      ],
      "complete_inventory": {
        "total_projects": len(projects_json),
        "by_language": by_language,
        "strata": {
          "active": strata_counts.get("active", 0),
          "archive_backup_corrupt": strata_counts.get("archive/backup/corrupt", 0),
          "mirror_vendor_fixture": strata_counts.get("mirror/vendor/fixture", 0),
        },
        "projects": sorted(projects_json, key=lambda p: p["name"]),
      },
      "capability_map": sorted(capability_map, key=lambda c: c["project"]),
      "readiness_assessment": {
        "immediately_encodable": sorted(ready_groups["immediately_encodable"]),
        "needs_minor_work": sorted(ready_groups["needs_minor_work"]),
        "needs_major_work": sorted(ready_groups["needs_major_work"]),
        "not_encodable": sorted(ready_groups["not_encodable"]),
      },
      "dependency_graph": {
        "nodes": nodes,
        "edges": dep_edges,
        "critical_path": critical_path,
      },
      "risk_analysis": {
        "high": sorted(high_risks),
        "medium": sorted(medium_risks),
        "low": sorted(low_risks),
      },
      "top_5_recommendations": recommendations,
      "timeline_estimate": make_timeline(date(2026, 3, 14)),
    }
  }
  return report


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--workspace", default="/home/main/devops")
  parser.add_argument("--out", default="/home/main/devops/atomic-kernel/reports/workspace/devops-rumsfeldian-analysis.json")
  args = parser.parse_args()

  workspace = Path(args.workspace).resolve()
  report = build_report(workspace)
  text = canonical_json(report) + "\n"
  out = Path(args.out).resolve()
  out.parent.mkdir(parents=True, exist_ok=True)
  out.write_text(text, encoding="utf-8")
  print(f"ok rumsfeldian discovery out={out} digest={sha256_hex(text)}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
