#!/usr/bin/env python3
"""Unicode/control-plane reversible projection for canonical package v2."""

from __future__ import annotations

import json
from typing import Any, Dict

from canonical import DEFAULT_HASH_ALGO, SUPPORTED_HASH_ALGOS, canonical_json_bytes, digest_bytes
from canonical_package_v2 import PACKAGE_V2, canonical_package_bytes_v2, validate_package_v2

PROJECTION_TYPE_V2 = "ak.unicode.projection.v2"
SPEC_VERSION_V2 = "ak.spec.v2"



def _bytes_to_unicode_plane(data: bytes) -> str:
    # Reversible 1:1 mapping for byte values 0..255 via U+0000..U+00FF.
    return "".join(chr(b) for b in data)



def _unicode_plane_to_bytes(text: str) -> bytes:
    out = bytearray()
    for ch in text:
        cp = ord(ch)
        if cp < 0 or cp > 255:
            raise ValueError("UNICODE_PROJECTION_CODEPOINT_OUT_OF_RANGE")
        out.append(cp)
    return bytes(out)



def build_projection_v2(package: Dict[str, Any], *, hash_algo: str = DEFAULT_HASH_ALGO) -> Dict[str, Any]:
    if hash_algo not in SUPPORTED_HASH_ALGOS:
        raise ValueError("UNKNOWN_HASH_ALGO")
    validate_package_v2(package)

    package_bytes = canonical_package_bytes_v2(package)
    projection = {
        "type": PROJECTION_TYPE_V2,
        "v": SPEC_VERSION_V2,
        "authority": "advisory",
        "package_type": PACKAGE_V2,
        "projection_encoding": "u0000-u00ff-byte-plane-v1",
        "hash_algo": hash_algo,
        "package_digest": package["identity"]["package_digest"],
        "package_bytes": len(package_bytes),
        "unicode_payload": _bytes_to_unicode_plane(package_bytes),
    }
    projection["projection_digest"] = digest_bytes(canonical_json_bytes(projection), hash_algo=hash_algo)
    return projection



def recover_projection_v2(projection: Dict[str, Any]) -> Dict[str, Any]:
    required = {
        "type",
        "v",
        "authority",
        "package_type",
        "projection_encoding",
        "hash_algo",
        "package_digest",
        "package_bytes",
        "unicode_payload",
        "projection_digest",
    }
    if not isinstance(projection, dict) or set(projection.keys()) != required:
        raise ValueError("UNICODE_PROJECTION_KEYSET_MISMATCH")
    if projection["type"] != PROJECTION_TYPE_V2:
        raise ValueError("UNICODE_PROJECTION_TYPE_MISMATCH")
    if projection["v"] != SPEC_VERSION_V2:
        raise ValueError("UNICODE_PROJECTION_VERSION_MISMATCH")
    if projection["authority"] != "advisory":
        raise ValueError("UNICODE_PROJECTION_AUTHORITY_MISMATCH")
    if projection["package_type"] != PACKAGE_V2:
        raise ValueError("UNICODE_PROJECTION_PACKAGE_TYPE_MISMATCH")
    if projection["projection_encoding"] != "u0000-u00ff-byte-plane-v1":
        raise ValueError("UNICODE_PROJECTION_ENCODING_MISMATCH")

    hash_algo = str(projection["hash_algo"])
    if hash_algo not in SUPPORTED_HASH_ALGOS:
        raise ValueError("UNKNOWN_HASH_ALGO")

    p = dict(projection)
    got = p.pop("projection_digest")
    want = digest_bytes(canonical_json_bytes(p), hash_algo=hash_algo)
    if got != want:
        raise ValueError("UNICODE_PROJECTION_DIGEST_MISMATCH")

    if not isinstance(projection["unicode_payload"], str):
        raise ValueError("UNICODE_PROJECTION_PAYLOAD_INVALID")

    package_bytes = _unicode_plane_to_bytes(projection["unicode_payload"])
    if len(package_bytes) != int(projection["package_bytes"]):
        raise ValueError("UNICODE_PROJECTION_SIZE_MISMATCH")

    package = json.loads(package_bytes.decode("utf-8"))
    validate_package_v2(package)
    if package["identity"]["package_digest"] != projection["package_digest"]:
        raise ValueError("UNICODE_PROJECTION_PACKAGE_DIGEST_MISMATCH")
    return package
