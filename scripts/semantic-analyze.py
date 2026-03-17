#!/usr/bin/env python3
"""Analyze a repository and emit deterministic semantic report artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime.atomic_kernel.repo_analysis import analyze_repo, normalize_languages, render_markdown, validate_analysis_report


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--target", required=True)
  parser.add_argument("--languages", default="")
  parser.add_argument("--include-globs", default="")
  parser.add_argument("--exclude-globs", default="")
  parser.add_argument("--out-json", required=True)
  parser.add_argument("--out-md", required=False)
  args = parser.parse_args()

  language_values = [x for x in args.languages.split(",") if x.strip()]
  languages = normalize_languages(language_values)
  include_globs = [x.strip() for x in args.include_globs.split(",") if x.strip()]
  exclude_globs = [x.strip() for x in args.exclude_globs.split(",") if x.strip()]
  report = analyze_repo(
    Path(args.target),
    languages=languages,
    include_globs=include_globs or None,
    exclude_globs=exclude_globs or None,
  )
  validate_analysis_report(report)
  Path(args.out_json).write_text(
    json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
    encoding="utf-8",
  )
  if args.out_md:
    Path(args.out_md).write_text(render_markdown(report), encoding="utf-8")
  print(f"ok semantic analyze json={args.out_json}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
