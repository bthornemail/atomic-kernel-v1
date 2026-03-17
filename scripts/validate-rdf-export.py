#!/usr/bin/env python3
"""Fail-closed validator for ak.rdf_export.v0 envelopes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
TOP_KEYS = {"v", "authority", "export_profile", "source_frame_hash", "namespaces", "triples"}
TRIPLE_KEYS = {"s", "p", "o", "o_kind"}


def fail(msg: str) -> None:
    raise ValueError(msg)


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("envelope must be object")
    return data


def validate(path: Path) -> None:
    d = load_json(path)
    keys = set(d.keys())
    if keys != TOP_KEYS:
        fail(f"top-level key mismatch missing={sorted(TOP_KEYS-keys)} extra={sorted(keys-TOP_KEYS)}")
    if d["v"] != "ak.rdf_export.v0":
        fail("v invalid")
    if d["authority"] != "advisory":
        fail("authority invalid")
    if d["export_profile"] != "core-minimal":
        fail("export_profile invalid")
    if not isinstance(d["source_frame_hash"], str) or not HEX64_RE.fullmatch(d["source_frame_hash"]):
        fail("source_frame_hash invalid")

    ns = d["namespaces"]
    if not isinstance(ns, dict) or set(ns.keys()) != {"ak", "rdf", "rdfs"}:
        fail("namespaces invalid")
    for k in ("ak", "rdf", "rdfs"):
        if not isinstance(ns[k], str) or not ns[k]:
            fail(f"namespace {k} invalid")

    triples = d["triples"]
    if not isinstance(triples, list):
        fail("triples must be list")
    prev = None
    for i, t in enumerate(triples):
        if not isinstance(t, dict):
            fail(f"triples[{i}] must be object")
        tk = set(t.keys())
        if tk != TRIPLE_KEYS:
            fail(f"triples[{i}] key mismatch")
        for key in ("s", "p", "o", "o_kind"):
            if not isinstance(t[key], str) or not t[key]:
                fail(f"triples[{i}].{key} invalid")
        if t["o_kind"] not in {"iri", "literal"}:
            fail(f"triples[{i}].o_kind invalid")
        cur = (t["s"], t["p"], t["o"], t["o_kind"])
        if prev is not None and cur < prev:
            fail("triples not deterministically sorted")
        prev = cur


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    validate(Path(args.file))
    print(f"ok rdf-export validate file={args.file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
