#!/usr/bin/env python3
"""Fail-closed verifier for clock-world.v0 artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from kernel import B, C, W, WIDTH
from world import frame_at

TOP_KEYS = {"v", "crystal", "observer_count", "seeds", "steps", "frames"}
CRYSTAL_KEYS = {"width", "constant", "block", "weight"}
FRAME_KEYS = {"t", "position", "orbit", "offset", "objects"}
OBJ_KEYS = {"id", "seed", "state", "position", "orbit", "offset", "phase", "diff", "x", "y", "color", "symbol", "band"}


def fail(msg: str) -> None:
    raise SystemExit(f"verify failed: {msg}")


def verify(payload: dict) -> None:
    if set(payload.keys()) != TOP_KEYS:
        fail("top-level keys mismatch")
    if payload["v"] != "clock-world.v0":
        fail("version mismatch")
    if set(payload["crystal"].keys()) != CRYSTAL_KEYS:
        fail("crystal keys mismatch")
    if payload["crystal"]["width"] != WIDTH:
        fail("crystal width mismatch")
    if payload["crystal"]["constant"] != f"0x{C:04X}":
        fail("crystal constant mismatch")
    if payload["crystal"]["block"] != list(B):
        fail("crystal block mismatch")
    if payload["crystal"]["weight"] != W:
        fail("crystal weight mismatch")
    if not isinstance(payload["seeds"], list) or not payload["seeds"]:
        fail("seeds invalid")
    if payload["observer_count"] != len(payload["seeds"]):
        fail("observer count mismatch")
    if not isinstance(payload["steps"], int) or payload["steps"] < 0:
        fail("steps invalid")
    if not isinstance(payload["frames"], list) or len(payload["frames"]) != payload["steps"]:
        fail("frames length mismatch")

    seeds = [int(s) for s in payload["seeds"]]
    for n, frame in enumerate(payload["frames"]):
        if set(frame.keys()) != FRAME_KEYS:
            fail(f"frame keys mismatch at t={n}")
        expected = frame_at(n, seeds)
        if frame != expected:
            fail(f"frame mismatch at t={n}")
        for i, obj in enumerate(frame["objects"]):
            if set(obj.keys()) != OBJ_KEYS:
                fail(f"object keys mismatch at t={n} idx={i}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    verify(payload)
    print(f"ok verify world file={args.file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

