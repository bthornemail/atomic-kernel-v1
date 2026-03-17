#!/usr/bin/env python3
"""Aztec carrier bundle v2 for direct-byte canonical package v2."""

from __future__ import annotations

import base64
import json
import zlib
from pathlib import Path
from typing import Any, Dict, List, Tuple

from canonical import DEFAULT_HASH_ALGO, SUPPORTED_HASH_ALGOS, canonical_json_bytes, digest_bytes
from canonical_package_v2 import PACKAGE_V2, canonical_package_bytes_v2, validate_package_v2

BUNDLE_TYPE_V2 = "ak.aztec.bundle.v2"
CHUNK_TYPE_V2 = "ak.aztec.chunk.v2"
SPEC_VERSION_V2 = "ak.spec.v2"
DEFAULT_CHUNK_BYTES_V2 = 1200


def _b64u_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64u_decode(text: str) -> bytes:
    padding = "=" * ((4 - (len(text) % 4)) % 4)
    return base64.urlsafe_b64decode((text + padding).encode("ascii"))


def _split_chunks(text: str, chunk_bytes: int) -> List[str]:
    raw = text.encode("utf-8")
    return [raw[i : i + chunk_bytes].decode("utf-8") for i in range(0, len(raw), chunk_bytes)] or [""]


def build_bundle_v2(
    package: Dict[str, Any],
    *,
    hash_algo: str = DEFAULT_HASH_ALGO,
    chunk_bytes: int = DEFAULT_CHUNK_BYTES_V2,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    if hash_algo not in SUPPORTED_HASH_ALGOS:
        raise ValueError("UNKNOWN_HASH_ALGO")
    if chunk_bytes < 256:
        raise ValueError("INVALID_CHUNK_BYTES")

    validate_package_v2(package)
    package_bytes = canonical_package_bytes_v2(package)
    package_digest = package["identity"]["package_digest"]

    compressed = zlib.compress(package_bytes, level=9)
    encoded = _b64u_encode(compressed)
    compressed_digest = digest_bytes(compressed, hash_algo=hash_algo)

    parts = _split_chunks(encoded, chunk_bytes)
    bundle_id = digest_bytes(
        canonical_json_bytes(
            {
                "package_digest": package_digest,
                "compressed_digest": compressed_digest,
                "parts": len(parts),
                "chunk_bytes": chunk_bytes,
                "hash_algo": hash_algo,
            }
        ),
        hash_algo=hash_algo,
    )

    chunks: List[Dict[str, Any]] = []
    for idx, part in enumerate(parts):
        c = {
            "type": CHUNK_TYPE_V2,
            "authority": "advisory",
            "bundle_id": bundle_id,
            "index": idx,
            "total": len(parts),
            "hash_algo": hash_algo,
            "data": part,
        }
        c["chunk_digest"] = digest_bytes(canonical_json_bytes(c), hash_algo=hash_algo)
        chunks.append(c)

    manifest = {
        "type": BUNDLE_TYPE_V2,
        "v": SPEC_VERSION_V2,
        "authority": "advisory",
        "hash_algo": hash_algo,
        "package_type": PACKAGE_V2,
        "payload_encoding": "zlib+base64url+package-bytes-v2",
        "bundle_id": bundle_id,
        "chunk_bytes": chunk_bytes,
        "total_chunks": len(chunks),
        "package_digest": package_digest,
        "compressed_digest": compressed_digest,
        "package_bytes": len(package_bytes),
    }
    manifest["manifest_digest"] = digest_bytes(canonical_json_bytes(manifest), hash_algo=hash_algo)
    return manifest, chunks


def recover_bundle_v2(manifest: Dict[str, Any], chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    required_manifest_keys = {
        "type",
        "v",
        "authority",
        "hash_algo",
        "package_type",
        "payload_encoding",
        "bundle_id",
        "chunk_bytes",
        "total_chunks",
        "package_digest",
        "compressed_digest",
        "package_bytes",
        "manifest_digest",
    }
    if not isinstance(manifest, dict) or set(manifest.keys()) != required_manifest_keys:
        raise ValueError("BUNDLE_V2_MANIFEST_KEYSET_MISMATCH")
    if manifest["type"] != BUNDLE_TYPE_V2:
        raise ValueError("BUNDLE_V2_TYPE_MISMATCH")
    if manifest["v"] != SPEC_VERSION_V2:
        raise ValueError("BUNDLE_V2_VERSION_MISMATCH")
    if manifest["authority"] != "advisory":
        raise ValueError("BUNDLE_V2_AUTHORITY_MISMATCH")
    if manifest["payload_encoding"] != "zlib+base64url+package-bytes-v2":
        raise ValueError("BUNDLE_V2_ENCODING_MISMATCH")

    hash_algo = str(manifest["hash_algo"])
    if hash_algo not in SUPPORTED_HASH_ALGOS:
        raise ValueError("UNKNOWN_HASH_ALGO")

    m = dict(manifest)
    got_manifest_digest = m.pop("manifest_digest")
    want_manifest_digest = digest_bytes(canonical_json_bytes(m), hash_algo=hash_algo)
    if got_manifest_digest != want_manifest_digest:
        raise ValueError("BUNDLE_V2_MANIFEST_DIGEST_MISMATCH")

    total_chunks = int(manifest["total_chunks"])
    if total_chunks < 1:
        raise ValueError("BUNDLE_V2_CHUNK_COUNT_INVALID")

    by_index: Dict[int, Dict[str, Any]] = {}
    for c in chunks:
        if not isinstance(c, dict):
            raise ValueError("BUNDLE_V2_CHUNK_NOT_OBJECT")
        required_chunk_keys = {
            "type",
            "authority",
            "bundle_id",
            "index",
            "total",
            "hash_algo",
            "data",
            "chunk_digest",
        }
        if set(c.keys()) != required_chunk_keys:
            raise ValueError("BUNDLE_V2_CHUNK_KEYSET_MISMATCH")
        if c["type"] != CHUNK_TYPE_V2:
            raise ValueError("BUNDLE_V2_CHUNK_TYPE_MISMATCH")
        if c["authority"] != "advisory":
            raise ValueError("BUNDLE_V2_CHUNK_AUTHORITY_MISMATCH")
        if c["bundle_id"] != manifest["bundle_id"]:
            raise ValueError("BUNDLE_V2_CHUNK_BUNDLE_ID_MISMATCH")
        if int(c["total"]) != total_chunks:
            raise ValueError("BUNDLE_V2_CHUNK_TOTAL_MISMATCH")
        if c["hash_algo"] != hash_algo:
            raise ValueError("BUNDLE_V2_CHUNK_HASH_ALGO_MISMATCH")

        d = dict(c)
        got = d.pop("chunk_digest")
        want = digest_bytes(canonical_json_bytes(d), hash_algo=hash_algo)
        if got != want:
            raise ValueError("BUNDLE_V2_CHUNK_DIGEST_MISMATCH")

        idx = int(c["index"])
        if idx in by_index:
            raise ValueError("BUNDLE_V2_DUPLICATE_CHUNK_INDEX")
        by_index[idx] = c

    if set(by_index.keys()) != set(range(total_chunks)):
        raise ValueError("BUNDLE_V2_MISSING_CHUNKS")

    encoded = "".join(str(by_index[i]["data"]) for i in range(total_chunks))
    compressed = _b64u_decode(encoded)
    if digest_bytes(compressed, hash_algo=hash_algo) != manifest["compressed_digest"]:
        raise ValueError("BUNDLE_V2_COMPRESSED_DIGEST_MISMATCH")

    package_bytes = zlib.decompress(compressed)
    if len(package_bytes) != int(manifest["package_bytes"]):
        raise ValueError("BUNDLE_V2_PACKAGE_SIZE_MISMATCH")

    package = json.loads(package_bytes.decode("utf-8"))
    validate_package_v2(package)
    if package["identity"]["package_digest"] != manifest["package_digest"]:
        raise ValueError("BUNDLE_V2_PACKAGE_DIGEST_MISMATCH")
    return package


def write_bundle_v2(outdir: Path, manifest: Dict[str, Any], chunks: List[Dict[str, Any]]) -> None:
    (outdir / "chunks").mkdir(parents=True, exist_ok=True)
    (outdir / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for c in chunks:
        (outdir / "chunks" / f"chunk-{int(c['index']):04d}.json").write_text(
            json.dumps(c, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    nd = "\n".join(json.dumps(c, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for c in chunks)
    (outdir / "chunks.ndjson").write_text(nd + ("\n" if nd else ""), encoding="utf-8")
