#!/usr/bin/env python3
"""Validate Aztec payload JSON files against strict in-repo contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]

DOC_BADGE_KEYS = {
    "schema",
    "authority",
    "doc_id",
    "doc_path",
    "release",
    "version",
    "hash_alg",
    "doc_hash",
    "artifacts_ref",
    "verify_mode",
}

EXPERIENCE_KEYS = {
    "schema",
    "authority",
    "manifest_id",
    "release",
    "version",
    "kernel",
    "entry_points",
    "render",
    "policy",
}


def fail(msg: str) -> None:
    raise SystemExit(msg)


def parse_artifacts_index(path: Path) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        digest, rel = line.split()
        mapping[rel] = digest
    return mapping


def ensure_str_keys(obj: Mapping[str, object], keys: Iterable[str], name: str) -> None:
    got = set(obj.keys())
    want = set(keys)
    if got != want:
        missing = sorted(want - got)
        extra = sorted(got - want)
        fail(f"{name}: key mismatch missing={missing} extra={extra}")


def validate_doc_badge(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail(f"{path}: payload must be object")
    ensure_str_keys(payload, DOC_BADGE_KEYS, str(path))

    if payload["schema"] != "atomic-kernel.doc.badge/1":
        fail(f"{path}: invalid schema")
    if payload["authority"] != "projection":
        fail(f"{path}: authority must be projection")
    if payload["version"] != 1:
        fail(f"{path}: version must be 1")
    if payload["hash_alg"] != "sha256":
        fail(f"{path}: hash_alg must be sha256")
    if payload["verify_mode"] != "hash-match":
        fail(f"{path}: verify_mode must be hash-match")

    release = payload["release"]
    if not isinstance(release, str) or release.count(".") != 2:
        fail(f"{path}: invalid release format")

    doc_path = payload["doc_path"]
    if not isinstance(doc_path, str) or not doc_path:
        fail(f"{path}: invalid doc_path")

    artifacts_ref = payload["artifacts_ref"]
    expected_ref = f"releases/{release}/ARTIFACTS.sha256"
    if artifacts_ref != expected_ref:
        fail(f"{path}: artifacts_ref mismatch")

    artifacts = parse_artifacts_index(ROOT / artifacts_ref)
    if doc_path not in artifacts:
        fail(f"{path}: doc path missing from artifacts index")

    expected_doc_hash = f"sha256:{artifacts[doc_path]}"
    if payload["doc_hash"] != expected_doc_hash:
        fail(f"{path}: doc_hash mismatch")

    actual_path = ROOT / doc_path
    actual = hashlib.sha256(actual_path.read_bytes()).hexdigest()
    if actual != artifacts[doc_path]:
        fail(f"{path}: doc file digest does not match artifact index")



def validate_experience(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        fail(f"{path}: payload must be object")
    ensure_str_keys(payload, EXPERIENCE_KEYS, str(path))

    if payload["schema"] != "atomic-kernel.experience.manifest/1":
        fail(f"{path}: invalid schema")
    if payload["authority"] != "projection":
        fail(f"{path}: authority must be projection")
    if payload["version"] != 1:
        fail(f"{path}: version must be 1")

    release = payload["release"]
    kernel = payload["kernel"]
    if not isinstance(kernel, dict):
        fail(f"{path}: kernel must be object")
    if kernel.get("package") != "atomic-kernel":
        fail(f"{path}: kernel.package mismatch")
    if kernel.get("public_api") != "atomic_kernel.*":
        fail(f"{path}: kernel.public_api mismatch")

    expected_artifacts = f"releases/{release}/ARTIFACTS.sha256"
    if kernel.get("release_artifacts") != expected_artifacts:
        fail(f"{path}: kernel.release_artifacts mismatch")

    artifacts = parse_artifacts_index(ROOT / expected_artifacts)
    for key, rel_path in payload["entry_points"].items():
        if not isinstance(rel_path, str) or not rel_path:
            fail(f"{path}: entry point {key} invalid")
        if not (ROOT / rel_path).exists():
            fail(f"{path}: entry point missing {rel_path}")
        # If release index has digest for this path, verify current file still matches it.
        if rel_path in artifacts:
            actual = hashlib.sha256((ROOT / rel_path).read_bytes()).hexdigest()
            if actual != artifacts[rel_path]:
                fail(f"{path}: entry point digest drift for {rel_path}")

    render = payload["render"]
    if render != {
        "xml_projection": "supported",
        "clipboard_profile": "supported",
        "aztec_profile": "supported",
    }:
        fail(f"{path}: unexpected render block")

    policy = payload["policy"]
    if policy != {
        "verify_before_render": True,
        "projection_cannot_upgrade_authority": True,
        "fork_scope": ["extension", "projection"],
    }:
        fail(f"{path}: unexpected policy block")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--payload-dir",
        default=str(ROOT / "propagation" / "aztec" / "payloads"),
        help="directory containing payload JSON files",
    )
    args = parser.parse_args()

    payload_dir = Path(args.payload_dir)
    badge_dir = payload_dir / "doc-badges"
    badge_files = sorted(badge_dir.glob("*.json"))
    if not badge_files:
        fail(f"no doc badge files found under {badge_dir}")
    for path in badge_files:
        validate_doc_badge(path)

    experience = payload_dir / "experience-manifest.json"
    if not experience.exists():
        fail(f"missing {experience}")
    validate_experience(experience)

    print(f"ok aztec payload validation badges={len(badge_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
