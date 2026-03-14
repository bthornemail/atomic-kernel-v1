#!/usr/bin/env python3

import unittest

import atomic_kernel as ak


class PublicApiTests(unittest.TestCase):
  def test_version(self):
    self.assertEqual(ak.__version__, "0.1.0")

  def test_core_replay(self):
    seq = ak.replay(16, 0x0001, 4)
    self.assertEqual(len(seq), 4)
    self.assertEqual(seq[0], 0x0001)
    self.assertEqual(seq[1], ak.delta(16, 0x0001))

  def test_identity_surface(self):
    sid = ak.compute_typed_sid("living_xml", "0011100")
    self.assertTrue(sid.startswith("sha256:"))
    c1 = ak.advance_clock({"frame": 0, "tick": 1, "control": 0})
    self.assertEqual(c1, {"frame": 0, "tick": 2, "control": 0})
    oid = ak.compute_oid({"frame": 0, "tick": 1, "control": 0}, sid, None)
    self.assertTrue(oid.startswith("sha256:"))

  def test_seed_surface(self):
    header = ak.closure_fixpoint(0x1C)
    self.assertGreaterEqual(header, 0)
    p = ak.phase(0x1C)
    self.assertTrue(1 <= p <= 7)


if __name__ == "__main__":
  unittest.main()

