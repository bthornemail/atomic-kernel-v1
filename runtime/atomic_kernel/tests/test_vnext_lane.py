#!/usr/bin/env python3

import unittest

from runtime.atomic_kernel.vnext import (
  ID_LAW_VERSION,
  LAW_VERSION,
  SemanticIdentityError,
  compute_algorithmic_oid,
  compute_algorithmic_sid,
  compute_hash_sid_adapter,
  lane_parity,
  replay_artifact,
)


class VNextLaneTests(unittest.TestCase):
  def test_replay_artifact_shape(self):
    art = replay_artifact(16, 0x0001, 8, lane="vnext").as_dict()
    self.assertEqual(art["v"], "ak.replay.vnext.v0")
    self.assertEqual(art["authority"], "advisory")
    self.assertEqual(art["law_version"], LAW_VERSION)
    self.assertTrue(art["algorithmic_replay_id"].startswith("math_v2:"))
    self.assertEqual(len(art["states"]), 8)

  def test_lane_parity(self):
    p = lane_parity(16, 0x0001, 16)
    self.assertTrue(p["states_equal"])
    self.assertEqual(p["law_version_vnext"], LAW_VERSION)

  def test_algorithmic_identity(self):
    sid = compute_algorithmic_sid("living_xml", "0011100")
    self.assertTrue(sid.startswith("math_v2:"))
    oid = compute_algorithmic_oid({"frame": 0, "tick": 1, "control": 0}, sid, None)
    self.assertTrue(oid.startswith("math_v2:"))
    self.assertEqual(ID_LAW_VERSION, "ak.vnext.algorithmic-id.v1")

  def test_hash_adapters(self):
    sha256_sid = compute_hash_sid_adapter("living_xml", "0011100", "sha256")
    sha3_sid = compute_hash_sid_adapter("living_xml", "0011100", "sha3_256")
    self.assertTrue(sha256_sid.startswith("sha256:"))
    self.assertTrue(sha3_sid.startswith("sha3_256:"))

  def test_identity_fail_closed(self):
    with self.assertRaises(SemanticIdentityError):
      compute_hash_sid_adapter("living_xml", "0011100", "blake3")
    with self.assertRaises(SemanticIdentityError):
      compute_algorithmic_oid({"frame": 0, "tick": 1, "control": 0}, "sha256:bad", None)


if __name__ == "__main__":
  unittest.main()
