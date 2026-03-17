#!/usr/bin/env python3

import unittest
from unittest import mock
import subprocess

from runtime.atomic_kernel.asg import AsgError, ingest_mjs_to_asg, ingest_python_to_asg, ingest_typescript_to_asg, validate_asg_frame


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


class AsgTests(unittest.TestCase):
  def test_ingest_deterministic(self):
    src = "class A:\n  def f(self):\n    return 1\n"
    a = ingest_python_to_asg(src, "x.py", "demo")
    b = ingest_python_to_asg(src, "x.py", "demo")
    self.assertEqual(a, b)
    validate_asg_frame(a)

  def test_validate_fails_on_bad_hash(self):
    src = "def f():\n  return 1\n"
    frame = ingest_python_to_asg(src, "x.py", "demo")
    frame["graph_hash"] = "sha256:" + "0" * 64
    with self.assertRaises(AsgError):
      validate_asg_frame(frame)

  def test_typescript_ingest_deterministic(self):
    src = "class A { f() { return 1; } }\nexport function mk() { return new A(); }\n"
    a = ingest_typescript_to_asg(src, "x.ts", "demo.ts")
    b = ingest_typescript_to_asg(src, "x.ts", "demo.ts")
    self.assertEqual(a, b)
    validate_asg_frame(a)

  def test_typescript_bad_syntax_rejects(self):
    src = "class A { f() { return 1; }\n"
    with self.assertRaises(AsgError):
      ingest_typescript_to_asg(src, "x.ts", "reject.ts")

  def test_typescript_syntax_ignores_comment_and_string_tokens(self):
    src = (
      "// unmatched tokens in comments should not count: } )\n"
      "const a = \"text with ) and }\";\n"
      "const b = `tmpl ${a} with } )`;\n"
      "export function ok() { return a + b; }\n"
    )
    frame = ingest_typescript_to_asg(src, "ok.ts", "demo.ts.strict")
    validate_asg_frame(frame)

  def test_typescript_fallback_tsc_accepts_when_local_check_fails(self):
    src = "export function ok() { return 1; }\n"
    with mock.patch("runtime.atomic_kernel.asg._check_ts_syntax", side_effect=AsgError("lexical check failed")):
      with mock.patch("runtime.atomic_kernel.asg._ts_source_valid_via_tsc", return_value=True):
        frame = ingest_typescript_to_asg(src, "ok.ts", "demo.ts.fallback")
    validate_asg_frame(frame)

  def test_typescript_fallback_tsc_rejects_when_invalid(self):
    src = "export function bad() { return 1; }\n"
    with mock.patch("runtime.atomic_kernel.asg._check_ts_syntax", side_effect=AsgError("lexical check failed")):
      with mock.patch("runtime.atomic_kernel.asg._ts_source_valid_via_tsc", return_value=False):
        with self.assertRaises(AsgError):
          ingest_typescript_to_asg(src, "bad.ts", "demo.ts.fallback.reject")

  @unittest.skipUnless(_has_mjs_parser(), "acorn parser unavailable")
  def test_mjs_ingest_deterministic(self):
    src = (
      "import { parse } from './surface.mjs';\n"
      "export class BridgeLayer extends AdapterBase {\n"
      "  map(input) { return parse(input); }\n"
      "}\n"
      "export function emitEnvelope(payload) { return BridgeLayer(payload); }\n"
    )
    a = ingest_mjs_to_asg(src, "x.mjs", "demo.mjs")
    b = ingest_mjs_to_asg(src, "x.mjs", "demo.mjs")
    self.assertEqual(a, b)
    validate_asg_frame(a)

  @unittest.skipUnless(_has_mjs_parser(), "acorn parser unavailable")
  def test_mjs_bad_syntax_rejects(self):
    src = "export function f( { return 1; }\n"
    with self.assertRaises(AsgError):
      ingest_mjs_to_asg(src, "x.mjs", "reject.mjs")


if __name__ == "__main__":
  unittest.main()
