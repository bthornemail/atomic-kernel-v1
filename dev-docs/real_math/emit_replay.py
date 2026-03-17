#!/usr/bin/env python3
"""Emit canonical clock replay artifacts from kernel law."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from kernel import B, C, WIDTH, replay


def emit(seed: int, steps: int) -> dict:
    trace = replay(seed, steps)
    return {
        "v": "clock-replay.v0",
        "seed": int(seed),
        "width": int(WIDTH),
        "constant": f"0x{C:04X}",
        "block": list(B),
        "steps": int(steps),
        "trace": trace,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--steps", type=int, default=4096)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = emit(args.seed, args.steps)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"ok emit replay out={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

