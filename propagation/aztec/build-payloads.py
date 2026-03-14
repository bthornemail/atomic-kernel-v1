#!/usr/bin/env python3
"""Build deterministic Aztec payload JSON artifacts from release files."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RELEASE = "0.1.0"

DOC_TARGETS: List[Tuple[str, str, str]] = [
    ("README", "README.md", "README.json"),
    (
        "P1-Kernel",
        "publications/publication-I-pure-kernel/P1-Kernel.md",
        "P1-Kernel.json",
    ),
    (
        "P3-Distributed-Runtime-API",
        "publications/publication-III-distributed-api/P3-Distributed-Runtime-API.md",
        "P3-Distributed-Runtime-API.json",
    ),
    (
        "P5-Adoption-Guide",
        "publications/publication-V-adoption/P5-Adoption-Guide.md",
        "P5-Adoption-Guide.json",
    ),
    (
        "RELEASE_NOTES",
        "releases/0.1.0/RELEASE_NOTES.md",
        "RELEASE_NOTES.json",
    ),
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_artifacts_index(path: Path) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"invalid ARTIFACTS.sha256 line: {raw!r}")
        digest, rel = parts
        mapping[rel] = digest
    return mapping


def build_doc_badges(release: str, artifacts: Dict[str, str], out_dir: Path) -> None:
    artifacts_ref = f"releases/{release}/ARTIFACTS.sha256"
    badge_dir = out_dir / "doc-badges"
    badge_dir.mkdir(parents=True, exist_ok=True)

    for doc_id, rel_path, filename in DOC_TARGETS:
        if rel_path not in artifacts:
            raise KeyError(f"{rel_path} missing from {artifacts_ref}")
        payload = {
            "schema": "atomic-kernel.doc.badge/1",
            "authority": "projection",
            "doc_id": doc_id,
            "doc_path": rel_path,
            "release": release,
            "version": 1,
            "hash_alg": "sha256",
            "doc_hash": f"sha256:{artifacts[rel_path]}",
            "artifacts_ref": artifacts_ref,
            "verify_mode": "hash-match",
        }
        (badge_dir / filename).write_text(
            json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )


def build_experience_manifest(release: str, out_dir: Path) -> None:
    payload = {
        "schema": "atomic-kernel.experience.manifest/1",
        "authority": "projection",
        "manifest_id": "atomic-kernel-genesis-experience-001",
        "release": release,
        "version": 1,
        "kernel": {
            "package": "atomic-kernel",
            "public_api": "atomic_kernel.*",
            "release_artifacts": f"releases/{release}/ARTIFACTS.sha256",
        },
        "entry_points": {
            "quick_start": "docs/guide/quick-start.md",
            "architecture": "docs/guide/architecture-overview.md",
            "kernel_publication": "publications/publication-I-pure-kernel/P1-Kernel.md",
            "distributed_api": "publications/publication-III-distributed-api/P3-Distributed-Runtime-API.md",
            "adoption": "publications/publication-V-adoption/P5-Adoption-Guide.md",
        },
        "render": {
            "xml_projection": "supported",
            "clipboard_profile": "supported",
            "aztec_profile": "supported",
        },
        "policy": {
            "verify_before_render": True,
            "projection_cannot_upgrade_authority": True,
            "fork_scope": ["extension", "projection"],
        },
    }
    (out_dir / "experience-manifest.json").write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", default=DEFAULT_RELEASE)
    parser.add_argument(
        "--output",
        default=str(ROOT / "propagation" / "aztec" / "payloads"),
        help="payload output directory",
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    artifacts_path = ROOT / "releases" / args.release / "ARTIFACTS.sha256"
    artifacts = parse_artifacts_index(artifacts_path)

    build_doc_badges(args.release, artifacts, output)
    build_experience_manifest(args.release, output)

    print(f"ok aztec payloads release={args.release} dir={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
