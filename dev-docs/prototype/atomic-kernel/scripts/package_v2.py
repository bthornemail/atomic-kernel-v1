#!/usr/bin/env python3
"""Prototype v2 lane CLI: direct-byte canonical package + carrier projections."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aztec_bundle_v2 import build_bundle_v2, recover_bundle_v2, write_bundle_v2
from canonical import DEFAULT_HASH_ALGO, SUPPORTED_HASH_ALGOS
from canonical_package_v2 import build_package_v2, decode_payload_v2, validate_package_v2
from replay_engine import replay_artifact
from unicode_projection_v2 import build_projection_v2, recover_projection_v2



def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")



def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))



def _load_payload(args: argparse.Namespace) -> Dict[str, Any]:
    if args.payload:
        return _read_json(Path(args.payload))
    artifact = replay_artifact(args.mode, args.width, int(str(args.seed), 0), args.steps, hash_algo=args.hash_algo)
    return artifact.as_dict()



def cmd_build(args: argparse.Namespace) -> int:
    payload = _load_payload(args)
    package = build_package_v2(payload, law_version=args.law_version, hash_algo=args.hash_algo)
    _write_json(Path(args.output), package)
    print(json.dumps({"ok": True, "output": args.output, "package_digest": package["identity"]["package_digest"]}, separators=(",", ":")))
    return 0



def cmd_verify(args: argparse.Namespace) -> int:
    package = _read_json(Path(args.package))
    validate_package_v2(package)
    payload = decode_payload_v2(package)
    print(
        json.dumps(
            {
                "ok": True,
                "package": args.package,
                "package_digest": package["identity"]["package_digest"],
                "payload_digest": package["identity"]["payload_digest"],
                "payload_replay_hash": payload.get("replay_hash", ""),
                "source_replay_hash": package["identity"].get("source_replay_hash", ""),
            },
            separators=(",", ":"),
        )
    )
    return 0



def cmd_aztec_pack(args: argparse.Namespace) -> int:
    package = _read_json(Path(args.package))
    manifest, chunks = build_bundle_v2(package, hash_algo=args.hash_algo, chunk_bytes=args.chunk_bytes)
    write_bundle_v2(Path(args.outdir), manifest, chunks)
    print(json.dumps({"ok": True, "outdir": args.outdir, "chunks": len(chunks), "bundle_id": manifest["bundle_id"]}, separators=(",", ":")))
    return 0



def cmd_aztec_unpack(args: argparse.Namespace) -> int:
    indir = Path(args.indir)
    manifest = _read_json(indir / "manifest.json")
    chunks: List[Dict[str, Any]] = []
    for p in sorted((indir / "chunks").glob("chunk-*.json")):
        chunks.append(_read_json(p))
    package = recover_bundle_v2(manifest, chunks)
    _write_json(Path(args.output), package)
    print(json.dumps({"ok": True, "output": args.output, "package_digest": package["identity"]["package_digest"]}, separators=(",", ":")))
    return 0



def cmd_unicode_pack(args: argparse.Namespace) -> int:
    package = _read_json(Path(args.package))
    projection = build_projection_v2(package, hash_algo=args.hash_algo)
    _write_json(Path(args.output), projection)
    print(json.dumps({"ok": True, "output": args.output, "projection_digest": projection["projection_digest"]}, separators=(",", ":")))
    return 0



def cmd_unicode_unpack(args: argparse.Namespace) -> int:
    projection = _read_json(Path(args.projection))
    package = recover_projection_v2(projection)
    _write_json(Path(args.output), package)
    print(json.dumps({"ok": True, "output": args.output, "package_digest": package["identity"]["package_digest"]}, separators=(",", ":")))
    return 0



def cmd_parity(args: argparse.Namespace) -> int:
    payload = _load_payload(args)
    package = build_package_v2(payload, law_version=args.law_version, hash_algo=args.hash_algo)

    m, c = build_bundle_v2(package, hash_algo=args.hash_algo, chunk_bytes=args.chunk_bytes)
    package_from_aztec = recover_bundle_v2(m, c)

    projection = build_projection_v2(package, hash_algo=args.hash_algo)
    package_from_unicode = recover_projection_v2(projection)

    src_replay_hash = str(payload.get("replay_hash", ""))
    p1 = decode_payload_v2(package_from_aztec)
    p2 = decode_payload_v2(package_from_unicode)
    if src_replay_hash and (p1.get("replay_hash") != src_replay_hash or p2.get("replay_hash") != src_replay_hash):
        raise ValueError("PACKAGE_V2_PARITY_REPLAY_HASH_MISMATCH")

    print(
        json.dumps(
            {
                "ok": True,
                "law_version": args.law_version,
                "package_digest": package["identity"]["package_digest"],
                "source_replay_hash": src_replay_hash,
                "aztec_roundtrip_replay_hash": p1.get("replay_hash", ""),
                "unicode_roundtrip_replay_hash": p2.get("replay_hash", ""),
            },
            separators=(",", ":"),
        )
    )
    return 0



def main() -> int:
    p = argparse.ArgumentParser(description="Direct-byte canonical package v2 lane")
    sp = p.add_subparsers(dest="command", required=True)

    def add_source_args(cp: argparse.ArgumentParser) -> None:
        cp.add_argument("--payload", default="", help="Existing payload artifact JSON. If omitted, derive from replay params")
        cp.add_argument("--mode", default="16d", choices=["kernel", "16d"])
        cp.add_argument("--width", type=int, default=32)
        cp.add_argument("--seed", default="0x0B7406AC")
        cp.add_argument("--steps", type=int, default=64)
        cp.add_argument("--hash-algo", dest="hash_algo", default=DEFAULT_HASH_ALGO, choices=sorted(SUPPORTED_HASH_ALGOS))
        cp.add_argument("--law-version", default="package-v2-draft")

    b = sp.add_parser("build")
    add_source_args(b)
    b.add_argument("--output", default="package-v2/package.json")

    v = sp.add_parser("verify")
    v.add_argument("--package", required=True)

    ap = sp.add_parser("aztec-pack")
    ap.add_argument("--package", required=True)
    ap.add_argument("--hash-algo", dest="hash_algo", default=DEFAULT_HASH_ALGO, choices=sorted(SUPPORTED_HASH_ALGOS))
    ap.add_argument("--chunk-bytes", type=int, default=1200)
    ap.add_argument("--outdir", default="package-v2/aztec")

    au = sp.add_parser("aztec-unpack")
    au.add_argument("--indir", default="package-v2/aztec")
    au.add_argument("--output", default="package-v2/recovered-from-aztec.json")

    up = sp.add_parser("unicode-pack")
    up.add_argument("--package", required=True)
    up.add_argument("--hash-algo", dest="hash_algo", default=DEFAULT_HASH_ALGO, choices=sorted(SUPPORTED_HASH_ALGOS))
    up.add_argument("--output", default="package-v2/unicode-projection.json")

    uu = sp.add_parser("unicode-unpack")
    uu.add_argument("--projection", default="package-v2/unicode-projection.json")
    uu.add_argument("--output", default="package-v2/recovered-from-unicode.json")

    pa = sp.add_parser("parity")
    add_source_args(pa)
    pa.add_argument("--chunk-bytes", type=int, default=1200)

    args = p.parse_args()

    if args.command == "build":
        return cmd_build(args)
    if args.command == "verify":
        return cmd_verify(args)
    if args.command == "aztec-pack":
        return cmd_aztec_pack(args)
    if args.command == "aztec-unpack":
        return cmd_aztec_unpack(args)
    if args.command == "unicode-pack":
        return cmd_unicode_pack(args)
    if args.command == "unicode-unpack":
        return cmd_unicode_unpack(args)
    if args.command == "parity":
        return cmd_parity(args)

    raise ValueError("UNKNOWN_COMMAND")


if __name__ == "__main__":
    raise SystemExit(main())
