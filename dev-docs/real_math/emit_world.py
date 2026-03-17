#!/usr/bin/env python3
"""Emit deterministic world artifact from crystal + observer law."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from world import emit_world


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=4096)
    parser.add_argument("--count", type=int, default=16)
    parser.add_argument("--seed-start", type=int, default=1)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = emit_world(steps=args.steps, count=args.count, seed_start=args.seed_start)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"ok emit world out={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

