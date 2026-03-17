#!/usr/bin/env python3
"""Direct-byte canonical package v2 for prototype lane.

Normative truth is canonical package bytes (canonical JSON UTF-8 bytes of this object).
Carrier formats (Aztec/Unicode projections) are advisory transport surfaces.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from canonical import DEFAULT_HASH_ALGO, SUPPORTED_HASH_ALGOS, canonical_json_bytes, digest_bytes

PACKAGE_V2 = "ak.canonical.package.v2"
SPEC_VERSION_V2 = "ak.spec.v2"
SECTION_ORDER = ["manifest", "algorithms", "control_plane", "identity", "payload_bytes"]

ALGORITHM_IDS_V2 = {
    "extract": "extract_control_stream.v1",
    "parse": "parse_orbit_channels.v1",
    "reduce": "reduce_orbit36.v1",
    "emit": "emit_propagation_artifact.v1",
}

CONTROL_PLANE_V2 = {
    "encoding": "utf-ebcdic-control-v1",
    "channels": {"FS": "0x1C", "GS": "0x1D", "RS": "0x1E", "US": "0x1F"},
    "reserved": ["0x3C", "0x3D", "0x3E", "0x3F"],
    "canonicalization": "stream-sign-value-v1",
}


def _ensure_object(payload: Any, keys: set[str], label: str) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError(f"{label}_NOT_OBJECT")
    actual = set(payload.keys())
    if actual != keys:
        extra = sorted(actual - keys)
        missing = sorted(keys - actual)
        detail = f"extra={extra};missing={missing}"
        raise ValueError(f"{label}_KEYSET_MISMATCH:{detail}")
    return payload


def _package_digest_seed(package: Dict[str, Any]) -> bytes:
    if not isinstance(package.get("identity"), dict):
        raise ValueError("PACKAGE_IDENTITY_NOT_OBJECT")
    seed = json.loads(json.dumps(package))
    seed["identity"]["package_digest"] = ""
    return canonical_json_bytes(seed)


def build_package_v2(
    payload: Dict[str, Any],
    *,
    law_version: str,
    hash_algo: str = DEFAULT_HASH_ALGO,
    algorithms: Dict[str, str] | None = None,
    control_plane: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if hash_algo not in SUPPORTED_HASH_ALGOS:
        raise ValueError("UNKNOWN_HASH_ALGO")
    if not isinstance(payload, dict):
        raise ValueError("PAYLOAD_NOT_OBJECT")

    payload_raw = canonical_json_bytes(payload)
    payload_bytes = list(payload_raw)

    manifest = {
        "type": PACKAGE_V2,
        "spec_version": SPEC_VERSION_V2,
        "law_version": str(law_version),
        "hash_algo": hash_algo,
        "section_order": SECTION_ORDER,
    }

    package = {
        "v": PACKAGE_V2,
        "authority": "advisory",
        "manifest": manifest,
        "algorithms": dict(algorithms or ALGORITHM_IDS_V2),
        "control_plane": dict(control_plane or CONTROL_PLANE_V2),
        "identity": {
            "hash_algo": hash_algo,
            "payload_digest": digest_bytes(payload_raw, hash_algo=hash_algo),
            "payload_length": len(payload_raw),
            "payload_encoding": "direct-bytes-v1",
            "source_result_hash": str(payload.get("digest", "")),
            "source_replay_hash": str(payload.get("replay_hash", "")),
            "source_math_id_v2": str(payload.get("math_id_v2", "")),
            "package_digest": "",
        },
        "payload_bytes": payload_bytes,
    }

    package_digest = digest_bytes(_package_digest_seed(package), hash_algo=hash_algo)
    package["identity"]["package_digest"] = package_digest
    validate_package_v2(package)
    return package


def validate_package_v2(package: Dict[str, Any]) -> Dict[str, Any]:
    top = _ensure_object(
        package,
        {"v", "authority", "manifest", "algorithms", "control_plane", "identity", "payload_bytes"},
        "PACKAGE_TOP",
    )
    if top["v"] != PACKAGE_V2:
        raise ValueError("PACKAGE_V_MISMATCH")
    if top["authority"] != "advisory":
        raise ValueError("PACKAGE_AUTHORITY_MISMATCH")

    manifest = _ensure_object(
        top["manifest"],
        {"type", "spec_version", "law_version", "hash_algo", "section_order"},
        "PACKAGE_MANIFEST",
    )
    if manifest["type"] != PACKAGE_V2:
        raise ValueError("PACKAGE_TYPE_MISMATCH")
    if manifest["spec_version"] != SPEC_VERSION_V2:
        raise ValueError("PACKAGE_SPEC_VERSION_MISMATCH")
    if not isinstance(manifest["law_version"], str) or not manifest["law_version"]:
        raise ValueError("PACKAGE_LAW_VERSION_INVALID")
    if manifest["hash_algo"] not in SUPPORTED_HASH_ALGOS:
        raise ValueError("UNKNOWN_HASH_ALGO")
    if manifest["section_order"] != SECTION_ORDER:
        raise ValueError("PACKAGE_SECTION_ORDER_MISMATCH")

    algorithms = top["algorithms"]
    if not isinstance(algorithms, dict) or not algorithms:
        raise ValueError("PACKAGE_ALGORITHMS_INVALID")
    for k, v in algorithms.items():
        if not isinstance(k, str) or not k:
            raise ValueError("PACKAGE_ALGORITHMS_KEY_INVALID")
        if not isinstance(v, str) or not v:
            raise ValueError("PACKAGE_ALGORITHMS_VALUE_INVALID")

    control_plane = _ensure_object(
        top["control_plane"],
        {"encoding", "channels", "reserved", "canonicalization"},
        "PACKAGE_CONTROL_PLANE",
    )
    if not isinstance(control_plane["encoding"], str) or not control_plane["encoding"]:
        raise ValueError("PACKAGE_CONTROL_PLANE_ENCODING_INVALID")
    channels = control_plane["channels"]
    if not isinstance(channels, dict) or set(channels.keys()) != {"FS", "GS", "RS", "US"}:
        raise ValueError("PACKAGE_CONTROL_PLANE_CHANNELS_INVALID")
    for val in channels.values():
        if not isinstance(val, str) or not val.startswith("0x"):
            raise ValueError("PACKAGE_CONTROL_PLANE_CHANNEL_VALUE_INVALID")
    reserved = control_plane["reserved"]
    if not isinstance(reserved, list) or any(not isinstance(x, str) or not x.startswith("0x") for x in reserved):
        raise ValueError("PACKAGE_CONTROL_PLANE_RESERVED_INVALID")
    if not isinstance(control_plane["canonicalization"], str) or not control_plane["canonicalization"]:
        raise ValueError("PACKAGE_CONTROL_PLANE_CANONICALIZATION_INVALID")

    identity = _ensure_object(
        top["identity"],
        {
            "hash_algo",
            "payload_digest",
            "payload_length",
            "payload_encoding",
            "source_result_hash",
            "source_replay_hash",
            "source_math_id_v2",
            "package_digest",
        },
        "PACKAGE_IDENTITY",
    )
    if identity["hash_algo"] not in SUPPORTED_HASH_ALGOS:
        raise ValueError("PACKAGE_IDENTITY_HASH_ALGO_INVALID")
    if identity["hash_algo"] != manifest["hash_algo"]:
        raise ValueError("PACKAGE_IDENTITY_HASH_ALGO_MISMATCH")
    if not isinstance(identity["payload_encoding"], str) or identity["payload_encoding"] != "direct-bytes-v1":
        raise ValueError("PACKAGE_PAYLOAD_ENCODING_INVALID")

    payload_bytes = top["payload_bytes"]
    if not isinstance(payload_bytes, list):
        raise ValueError("PACKAGE_PAYLOAD_BYTES_INVALID")
    if any((not isinstance(b, int) or b < 0 or b > 255) for b in payload_bytes):
        raise ValueError("PACKAGE_PAYLOAD_BYTES_RANGE_INVALID")
    payload_raw = bytes(payload_bytes)

    if identity["payload_length"] != len(payload_raw):
        raise ValueError("PACKAGE_PAYLOAD_LENGTH_MISMATCH")

    expected_payload_digest = digest_bytes(payload_raw, hash_algo=identity["hash_algo"])
    if identity["payload_digest"] != expected_payload_digest:
        raise ValueError("PACKAGE_PAYLOAD_DIGEST_MISMATCH")

    expected_package_digest = digest_bytes(_package_digest_seed(top), hash_algo=identity["hash_algo"])
    if identity["package_digest"] != expected_package_digest:
        raise ValueError("PACKAGE_DIGEST_MISMATCH")

    return top


def canonical_package_bytes_v2(package: Dict[str, Any]) -> bytes:
    validate_package_v2(package)
    return canonical_json_bytes(package)


def decode_payload_v2(package: Dict[str, Any]) -> Dict[str, Any]:
    validate_package_v2(package)
    raw = bytes(package["payload_bytes"])
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:  # pragma: no cover - explicit fail-closed path
        raise ValueError("PACKAGE_PAYLOAD_DECODE_FAILED") from exc
    if not isinstance(payload, dict):
        raise ValueError("PACKAGE_PAYLOAD_NOT_OBJECT")
    return payload
