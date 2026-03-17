#!/usr/bin/env python3
"""Verify replay artifact rows against kernel replay law."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from kernel import B, C, WIDTH, replay

TOP_KEYS = {"v", "seed", "width", "constant", "block", "steps", "trace"}
ROW_KEYS = {"t", "state", "state_hex", "position", "orbit", "offset", "phase", "diff", "band"}


def fail(msg: str) -> None:
    raise SystemExit(f"verify failed: {msg}")


def verify(payload: dict) -> None:
    if set(payload.keys()) != TOP_KEYS:
        fail("top-level keys mismatch")
    if payload["v"] != "clock-replay.v0":
        fail("unsupported replay version")
    if payload["width"] != WIDTH:
        fail("width mismatch")
    if payload["constant"] != f"0x{C:04X}":
        fail("constant mismatch")
    if payload["block"] != list(B):
        fail("block mismatch")
    if not isinstance(payload["steps"], int) or payload["steps"] < 0:
        fail("steps invalid")
    if not isinstance(payload["seed"], int):
        fail("seed invalid")
    if not isinstance(payload["trace"], list):
        fail("trace invalid")
    if len(payload["trace"]) != payload["steps"]:
        fail("trace length mismatch")

    expected = replay(payload["seed"], payload["steps"])
    for i, (got, want) in enumerate(zip(payload["trace"], expected)):
        if set(got.keys()) != ROW_KEYS:
            fail(f"trace row keys mismatch at t={i}")
        if isinstance(got.get("band"), list):
            got["band"] = tuple(got["band"])
        if got != want:
            fail(f"trace mismatch at t={i}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    verify(payload)
    print(f"ok verify replay file={args.file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

