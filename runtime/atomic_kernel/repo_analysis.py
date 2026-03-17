"""Deterministic applied semantic analysis over a repository path."""

from __future__ import annotations

import hashlib
import json
import fnmatch
from pathlib import Path
from typing import Any

from .asg import AsgError, ingest_mjs_to_asg, ingest_python_to_asg, ingest_typescript_to_asg, validate_asg_frame
from .pattern_extract import PatternExtractError, extract_patterns_from_asg


class RepoAnalysisError(ValueError):
  """Raised when repository analysis fails closed."""


ALLOWED_EXT = {".py": "python", ".ts": "typescript", ".mjs": "mjs"}
IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "site", "dist", "build"}
TOP_KEYS = {"v", "authority", "target", "summary", "instances", "warnings", "inputs_digest", "evidence_digest", "outputs_digest"}


def _canonical_json(data: Any) -> str:
  return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash_obj(data: Any) -> str:
  return "sha256:" + hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _should_skip(path: Path) -> bool:
  return any(part in IGNORE_DIRS for part in path.parts)


def _collect_source_files(
  target: Path,
  languages: set[str] | None = None,
  include_globs: list[str] | None = None,
  exclude_globs: list[str] | None = None,
) -> list[Path]:
  if not target.is_dir():
    raise RepoAnalysisError(f"target is not directory: {target}")
  out: list[Path] = []
  includes = [g for g in (include_globs or []) if g]
  excludes = [g for g in (exclude_globs or []) if g]
  for p in sorted(target.rglob("*")):
    if not p.is_file():
      continue
    if _should_skip(p):
      continue
    rel = p.relative_to(target).as_posix()
    if includes and not any(_glob_match(rel, pattern) for pattern in includes):
      continue
    if excludes and any(_glob_match(rel, pattern) for pattern in excludes):
      continue
    if p.suffix in ALLOWED_EXT:
      lang = ALLOWED_EXT[p.suffix]
      if languages is not None and lang not in languages:
        continue
      out.append(p)
  return out


def _glob_match(rel_path: str, pattern: str) -> bool:
  if fnmatch.fnmatch(rel_path, pattern):
    return True
  if pattern.startswith("**/") and fnmatch.fnmatch(rel_path, pattern[3:]):
    return True
  return False


def classify_domain(rel_path: str) -> str:
  p = rel_path.lower()
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


def normalize_languages(values: list[str] | None) -> set[str] | None:
  if values is None:
    return None
  allowed = set(ALLOWED_EXT.values())
  cleaned = {v.strip().lower() for v in values if v.strip()}
  if not cleaned:
    return None
  unknown = cleaned - allowed
  if unknown:
    raise RepoAnalysisError(f"unsupported languages: {sorted(unknown)}")
  return cleaned


def list_repo_sources(
  target: Path,
  languages: set[str] | None = None,
  include_globs: list[str] | None = None,
  exclude_globs: list[str] | None = None,
) -> list[Path]:
  return _collect_source_files(
    target.resolve(),
    languages=languages,
    include_globs=include_globs,
    exclude_globs=exclude_globs,
  )


def analyze_repo(
  target: Path,
  languages: set[str] | None = None,
  include_globs: list[str] | None = None,
  exclude_globs: list[str] | None = None,
) -> dict[str, Any]:
  target = target.resolve()
  files = _collect_source_files(
    target,
    languages=languages,
    include_globs=include_globs,
    exclude_globs=exclude_globs,
  )
  if not files:
    raise RepoAnalysisError("no supported source files found")

  languages_seen: dict[str, int] = {}
  asg_frames: list[dict[str, Any]] = []
  instances: list[dict[str, Any]] = []
  inputs_for_digest: list[dict[str, Any]] = []
  warnings: list[str] = []
  domain_counts: dict[str, int] = {}

  for path in files:
    rel = path.relative_to(target).as_posix()
    domain = classify_domain(rel)
    domain_counts[domain] = domain_counts.get(domain, 0) + 1
    source = path.read_text(encoding="utf-8")
    ext = path.suffix
    lang = ALLOWED_EXT[ext]
    languages_seen[lang] = languages_seen.get(lang, 0) + 1
    inputs_for_digest.append({"path": rel, "sha256": _hash_obj(source)})

    namespace = f"analysis.{lang}.{rel.replace('/', '.')}"
    try:
      if lang == "python":
        frame = ingest_python_to_asg(source, rel, namespace)
      elif lang == "typescript":
        frame = ingest_typescript_to_asg(source, rel, namespace)
      elif lang == "mjs":
        frame = ingest_mjs_to_asg(source, rel, namespace)
      else:
        raise RepoAnalysisError(f"unsupported language: {lang}")
      validate_asg_frame(frame)
      asg_frames.append(frame)
      patterns = extract_patterns_from_asg(frame)
      for p in patterns:
        instances.append(
          {
            "file": rel,
            "language": lang,
            "pattern_type": p["pattern_type"],
            "pattern_id": p["pattern_id"],
            "confidence": p["confidence"],
            "subject_nodes": p["subject_nodes"],
            "evidence_edges": p["evidence_edges"],
            "source_frame_hash": p["source_frame_hash"],
          }
        )
    except (AsgError, PatternExtractError, SyntaxError, UnicodeDecodeError) as exc:
      raise RepoAnalysisError(f"failed analyzing {rel}: {exc}") from exc

  instances.sort(key=lambda i: (i["pattern_type"], i["pattern_id"], i["file"]))
  pattern_counts: dict[str, int] = {}
  for inst in instances:
    pt = inst["pattern_type"]
    pattern_counts[pt] = pattern_counts.get(pt, 0) + 1

  summary = {
    "files": len(files),
    "language_counts": {k: languages_seen[k] for k in sorted(languages_seen.keys())},
    "domain_counts": {k: domain_counts[k] for k in sorted(domain_counts.keys())},
    "asg_nodes": sum(len(f["nodes"]) for f in asg_frames),
    "asg_edges": sum(len(f["edges"]) for f in asg_frames),
    "patterns": {k: pattern_counts[k] for k in sorted(pattern_counts.keys())},
  }
  target_obj = {
    "path": str(target),
    "languages": sorted(languages_seen.keys()),
  }
  evidence_digest = _hash_obj([{"id": i["pattern_id"], "evidence": i["evidence_edges"]} for i in instances])
  inputs_digest = _hash_obj(inputs_for_digest)
  report = {
    "v": "analysis-report.v0",
    "authority": "advisory",
    "target": target_obj,
    "summary": summary,
    "instances": instances,
    "warnings": warnings,
    "inputs_digest": inputs_digest,
    "evidence_digest": evidence_digest,
    "outputs_digest": "",
  }
  report["outputs_digest"] = _hash_obj(
    {
      "summary": report["summary"],
      "instances": report["instances"],
      "inputs_digest": report["inputs_digest"],
      "evidence_digest": report["evidence_digest"],
    }
  )
  return report


def render_markdown(report: dict[str, Any]) -> str:
  lines = [
    "# Applied Analysis Report",
    "",
    f"- v: `{report['v']}`",
    f"- authority: `{report['authority']}`",
    f"- target: `{report['target']['path']}`",
    f"- languages: `{', '.join(report['target']['languages'])}`",
    "",
    "## Summary",
    f"- files: {report['summary']['files']}",
    f"- asg_nodes: {report['summary']['asg_nodes']}",
    f"- asg_edges: {report['summary']['asg_edges']}",
    "- domain counts:",
  ]
  for k, v in report["summary"].get("domain_counts", {}).items():
    lines.append(f"  - {k}: {v}")
  lines.extend(
    [
    "- pattern counts:",
    ]
  )
  for k, v in report["summary"]["patterns"].items():
    lines.append(f"  - {k}: {v}")
  lines.extend(
    [
      "",
      "## Instances",
    ]
  )
  if not report["instances"]:
    lines.append("- none")
  else:
    for inst in report["instances"]:
      lines.append(
        f"- {inst['pattern_type']} `{inst['pattern_id']}` in `{inst['file']}` confidence={inst['confidence']}"
      )
  lines.extend(
    [
      "",
      "## Digests",
      f"- inputs_digest: `{report['inputs_digest']}`",
      f"- evidence_digest: `{report['evidence_digest']}`",
      f"- outputs_digest: `{report['outputs_digest']}`",
      "",
    ]
  )
  return "\n".join(lines)


def validate_analysis_report(report: dict[str, Any]) -> None:
  if not isinstance(report, dict):
    raise RepoAnalysisError("report must be object")
  keys = set(report.keys())
  if keys != TOP_KEYS:
    raise RepoAnalysisError(f"report key mismatch missing={sorted(TOP_KEYS-keys)} extra={sorted(keys-TOP_KEYS)}")
  if report["v"] != "analysis-report.v0":
    raise RepoAnalysisError("v invalid")
  if report["authority"] != "advisory":
    raise RepoAnalysisError("authority invalid")
  for k in ("inputs_digest", "evidence_digest", "outputs_digest"):
    if not isinstance(report[k], str) or not report[k].startswith("sha256:"):
      raise RepoAnalysisError(f"{k} invalid")
  if not isinstance(report["instances"], list):
    raise RepoAnalysisError("instances invalid")
  if not isinstance(report["warnings"], list):
    raise RepoAnalysisError("warnings invalid")
