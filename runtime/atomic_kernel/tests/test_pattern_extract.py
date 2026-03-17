#!/usr/bin/env python3

import unittest

from runtime.atomic_kernel.asg import ingest_python_to_asg
from runtime.atomic_kernel.pattern_extract import PatternExtractError, extract_patterns_from_asg


class PatternExtractTests(unittest.TestCase):
  def test_adapter_detected(self):
    src = (
      "class PaymentAdapter(Entity):\n"
      "  def pay(self, amount):\n"
      "    return gateway.process(amount)\n"
    )
    frame = ingest_python_to_asg(src, "x.py", "demo")
    patterns = extract_patterns_from_asg(frame)
    self.assertEqual([p["pattern_type"] for p in patterns], ["Adapter"])

  def test_facade_detected(self):
    src = (
      "import subsystem_a\n"
      "import subsystem_b\n"
      "class ServiceFacade:\n"
      "  def run(self):\n"
      "    return subsystem_a.start()\n"
      "  def stop(self):\n"
      "    return subsystem_b.stop()\n"
    )
    frame = ingest_python_to_asg(src, "x.py", "demo")
    patterns = extract_patterns_from_asg(frame)
    self.assertEqual([p["pattern_type"] for p in patterns], ["Facade"])

  def test_invalid_frame_rejects(self):
    with self.assertRaises(PatternExtractError):
      extract_patterns_from_asg({"v": "ak.asg.v0"})

  def test_observer_detected(self):
    src = (
      "class Subject:\n"
      "  def register(self, listener):\n"
      "    return listener\n"
      "  def notify(self, listener):\n"
      "    return listener.update()\n"
    )
    frame = ingest_python_to_asg(src, "x.py", "demo")
    patterns = extract_patterns_from_asg(frame)
    self.assertEqual([p["pattern_type"] for p in patterns], ["Observer"])

  def test_strategy_detected(self):
    src = (
      "class Context:\n"
      "  def run(self):\n"
      "    return self.strategy.execute()\n"
    )
    frame = ingest_python_to_asg(src, "x.py", "demo")
    patterns = extract_patterns_from_asg(frame)
    self.assertEqual([p["pattern_type"] for p in patterns], ["Strategy"])

  def test_builder_detected(self):
    src = (
      "class ReportBuilder:\n"
      "  def set_title(self, title):\n"
      "    return title\n"
      "  def build(self):\n"
      "    return renderer.build()\n"
    )
    frame = ingest_python_to_asg(src, "x.py", "demo")
    patterns = extract_patterns_from_asg(frame)
    self.assertEqual([p["pattern_type"] for p in patterns], ["Builder"])

  def test_multi_pattern_output_ordered(self):
    src = (
      "import subsystem_a\n"
      "import subsystem_b\n"
      "class ServiceFacade:\n"
      "  def run(self):\n"
      "    return subsystem_a.start()\n"
      "  def stop(self):\n"
      "    return subsystem_b.stop()\n"
      "class ReportBuilder:\n"
      "  def with_title(self, title):\n"
      "    return title\n"
      "  def build(self):\n"
      "    return renderer.build()\n"
    )
    frame = ingest_python_to_asg(src, "x.py", "demo")
    patterns = extract_patterns_from_asg(frame)
    self.assertEqual([p["pattern_type"] for p in patterns], ["Builder", "Facade"])


if __name__ == "__main__":
  unittest.main()
