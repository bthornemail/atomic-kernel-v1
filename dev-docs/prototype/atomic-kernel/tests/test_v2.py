import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aztec_bundle_v2 import build_bundle_v2, recover_bundle_v2
from canonical import canonical_json_bytes
from canonical_package_v2 import (
    build_package_v2,
    canonical_package_bytes_v2,
    decode_payload_v2,
    validate_package_v2,
)
from replay_engine import replay_artifact
from unicode_projection_v2 import build_projection_v2, recover_projection_v2


class V2Tests(unittest.TestCase):
    def _source(self):
        return replay_artifact("16d", 32, 0x0B7406AC, 16, hash_algo="sha3_256").as_dict()

    def test_package_v2_deterministic_bytes(self):
        src = self._source()
        p1 = build_package_v2(src, law_version="test-v2", hash_algo="sha3_256")
        p2 = build_package_v2(src, law_version="test-v2", hash_algo="sha3_256")
        self.assertEqual(canonical_package_bytes_v2(p1), canonical_package_bytes_v2(p2))
        self.assertEqual(p1["identity"]["package_digest"], p2["identity"]["package_digest"])

    def test_aztec_roundtrip_byte_equal(self):
        src = self._source()
        p = build_package_v2(src, law_version="test-v2", hash_algo="sha3_256")
        manifest, chunks = build_bundle_v2(p, hash_algo="sha3_256", chunk_bytes=400)
        recovered = recover_bundle_v2(manifest, chunks)
        self.assertEqual(canonical_package_bytes_v2(p), canonical_package_bytes_v2(recovered))

    def test_unicode_roundtrip_byte_equal(self):
        src = self._source()
        p = build_package_v2(src, law_version="test-v2", hash_algo="sha3_256")
        projection = build_projection_v2(p, hash_algo="sha3_256")
        recovered = recover_projection_v2(projection)
        self.assertEqual(canonical_package_bytes_v2(p), canonical_package_bytes_v2(recovered))

    def test_fail_closed_unknown_top_key(self):
        src = self._source()
        p = build_package_v2(src, law_version="test-v2", hash_algo="sha3_256")
        bad = json.loads(json.dumps(p))
        bad["extra"] = True
        with self.assertRaises(ValueError):
            validate_package_v2(bad)

    def test_fail_closed_missing_top_key(self):
        src = self._source()
        p = build_package_v2(src, law_version="test-v2", hash_algo="sha3_256")
        bad = json.loads(json.dumps(p))
        del bad["payload_bytes"]
        with self.assertRaises(ValueError):
            validate_package_v2(bad)

    def test_fail_closed_bad_digest(self):
        src = self._source()
        p = build_package_v2(src, law_version="test-v2", hash_algo="sha3_256")
        bad = json.loads(json.dumps(p))
        bad["identity"]["package_digest"] = "sha3_256:" + ("0" * 64)
        with self.assertRaises(ValueError):
            validate_package_v2(bad)

    def test_fail_closed_section_order_violation(self):
        src = self._source()
        p = build_package_v2(src, law_version="test-v2", hash_algo="sha3_256")
        bad = json.loads(json.dumps(p))
        bad["manifest"]["section_order"] = [
            "manifest",
            "algorithms",
            "control_plane",
            "payload_bytes",
            "identity",
        ]
        with self.assertRaises(ValueError):
            validate_package_v2(bad)

    def test_fail_closed_bad_chunk_index(self):
        src = self._source()
        p = build_package_v2(src, law_version="test-v2", hash_algo="sha3_256")
        manifest, chunks = build_bundle_v2(p, hash_algo="sha3_256", chunk_bytes=400)
        bad_chunks = json.loads(json.dumps(chunks))
        bad_chunks[0]["index"] = 1
        with self.assertRaises(ValueError):
            recover_bundle_v2(manifest, bad_chunks)

    def test_fail_closed_projection_digest(self):
        src = self._source()
        p = build_package_v2(src, law_version="test-v2", hash_algo="sha3_256")
        projection = build_projection_v2(p, hash_algo="sha3_256")
        bad = json.loads(json.dumps(projection))
        bad["projection_digest"] = "sha3_256:" + ("0" * 64)
        with self.assertRaises(ValueError):
            recover_projection_v2(bad)

    def test_payload_parity_replay_hash(self):
        src = self._source()
        p = build_package_v2(src, law_version="test-v2", hash_algo="sha3_256")
        payload = decode_payload_v2(p)
        self.assertEqual(payload["replay_hash"], src["replay_hash"])

    def test_carrier_metadata_does_not_affect_package_digest(self):
        src = self._source()
        p = build_package_v2(src, law_version="test-v2", hash_algo="sha3_256")
        package_digest = p["identity"]["package_digest"]

        m1, c1 = build_bundle_v2(p, hash_algo="sha3_256", chunk_bytes=320)
        m2, c2 = build_bundle_v2(p, hash_algo="sha3_256", chunk_bytes=1200)
        self.assertNotEqual(m1["manifest_digest"], m2["manifest_digest"])
        self.assertNotEqual(m1["total_chunks"], m2["total_chunks"])

        p1 = recover_bundle_v2(m1, c1)
        p2 = recover_bundle_v2(m2, c2)
        self.assertEqual(p1["identity"]["package_digest"], package_digest)
        self.assertEqual(p2["identity"]["package_digest"], package_digest)
        self.assertEqual(canonical_package_bytes_v2(p1), canonical_package_bytes_v2(p2))

    def test_v2_cli_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            out = Path(td)
            package = out / "package.json"
            aztec_dir = out / "aztec"
            unicode_path = out / "projection.json"
            from_aztec = out / "from-aztec.json"
            from_unicode = out / "from-unicode.json"

            cmds = [
                [sys.executable, "scripts/package_v2.py", "build", "--mode", "16d", "--width", "32", "--seed", "0x0B7406AC", "--steps", "16", "--law-version", "test-v2", "--output", str(package)],
                [sys.executable, "scripts/package_v2.py", "verify", "--package", str(package)],
                [sys.executable, "scripts/package_v2.py", "aztec-pack", "--package", str(package), "--outdir", str(aztec_dir)],
                [sys.executable, "scripts/package_v2.py", "aztec-unpack", "--indir", str(aztec_dir), "--output", str(from_aztec)],
                [sys.executable, "scripts/package_v2.py", "unicode-pack", "--package", str(package), "--output", str(unicode_path)],
                [sys.executable, "scripts/package_v2.py", "unicode-unpack", "--projection", str(unicode_path), "--output", str(from_unicode)],
                [sys.executable, "scripts/package_v2.py", "parity", "--mode", "16d", "--width", "32", "--seed", "0x0B7406AC", "--steps", "16", "--law-version", "test-v2"],
            ]
            for cmd in cmds:
                rc = subprocess.run(cmd, cwd=root, check=False)
                self.assertEqual(rc.returncode, 0)

            p = json.loads(package.read_text(encoding="utf-8"))
            pa = json.loads(from_aztec.read_text(encoding="utf-8"))
            pu = json.loads(from_unicode.read_text(encoding="utf-8"))
            self.assertEqual(canonical_json_bytes(p), canonical_json_bytes(pa))
            self.assertEqual(canonical_json_bytes(p), canonical_json_bytes(pu))


if __name__ == "__main__":
    unittest.main()
