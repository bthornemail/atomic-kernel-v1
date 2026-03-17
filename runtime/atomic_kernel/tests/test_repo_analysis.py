#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path
import subprocess

from runtime.atomic_kernel.repo_analysis import RepoAnalysisError, analyze_repo


def _has_mjs_parser() -> bool:
  try:
    subprocess.run(
      ["node", "-e", "require('acorn')"],
      check=True,
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
    )
    return True
  except Exception:
    return False


class RepoAnalysisTests(unittest.TestCase):
  def test_analyze_repo_deterministic(self):
    with tempfile.TemporaryDirectory() as td:
      root = Path(td)
      (root / "a.py").write_text(
        "class PaymentAdapter(Entity):\n"
        "  def pay(self, amount):\n"
        "    return gateway.process(amount)\n",
        encoding="utf-8",
      )
      (root / "b.py").write_text(
        "import subsystem_a\nimport subsystem_b\n"
        "class ServiceFacade:\n"
        "  def run(self):\n"
        "    return subsystem_a.start()\n"
        "  def stop(self):\n"
        "    return subsystem_b.stop()\n",
        encoding="utf-8",
      )
      has_mjs = _has_mjs_parser()
      if has_mjs:
        (root / "c.mjs").write_text(
          "import { parse } from './surface.mjs';\n"
          "export class BridgeLayer extends AdapterBase {\n"
          "  map(input) { return parse(input); }\n"
          "}\n",
          encoding="utf-8",
        )
      r1 = analyze_repo(root)
      r2 = analyze_repo(root)
      self.assertEqual(r1, r2)
      if has_mjs:
        self.assertEqual(r1["summary"]["language_counts"]["mjs"], 1)
      self.assertGreaterEqual(r1["summary"]["patterns"]["Adapter"], 1)
      self.assertGreaterEqual(r1["summary"]["patterns"]["Facade"], 1)

  def test_rejects_invalid_target(self):
    with self.assertRaises(RepoAnalysisError):
      analyze_repo(Path("/definitely/not/a/real/path"))

  def test_include_exclude_globs(self):
    with tempfile.TemporaryDirectory() as td:
      root = Path(td)
      (root / "src").mkdir()
      (root / "fixtures").mkdir()
      (root / "src" / "ok.py").write_text("class A:\n  pass\n", encoding="utf-8")
      (root / "fixtures" / "bad.ts").write_text("function broken( {\n", encoding="utf-8")

      report = analyze_repo(
        root,
        include_globs=["**/*.py", "**/*.ts"],
        exclude_globs=["**/fixtures/**"],
      )
      self.assertEqual(report["summary"]["files"], 1)
      self.assertEqual(report["summary"]["language_counts"], {"python": 1})


if __name__ == "__main__":
  unittest.main()
