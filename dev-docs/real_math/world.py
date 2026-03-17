#!/usr/bin/env python3
"""Deterministic world frames: many observers, one crystal."""

from __future__ import annotations

from kernel import B, C, MASK, W, WIDTH, position_at, recover
from observer import observe


def default_seeds(count: int = 16, seed_start: int = 1, stride: int = 73) -> list[int]:
    seeds: list[int] = []
    for i in range(count):
        s = (seed_start + i * stride) & MASK
        if s == 0:
            s = 1
        seeds.append(s)
    return seeds


def frame_at(n: int, seeds: list[int]) -> dict:
    position = position_at(n)
    orbit, offset = recover(position)
    objs = []
    for idx, seed in enumerate(seeds):
        obs = observe(seed, n)
        obs["id"] = f"obj-{idx:02d}"
        obs["seed"] = seed
        objs.append(obs)
    return {
        "t": n,
        "position": position,
        "orbit": orbit,
        "offset": offset,
        "objects": objs,
    }


def frames(steps: int, seeds: list[int]) -> list[dict]:
    return [frame_at(n, seeds) for n in range(steps)]


def emit_world(steps: int = 4096, count: int = 16, seed_start: int = 1) -> dict:
    seeds = default_seeds(count=count, seed_start=seed_start)
    return {
        "v": "clock-world.v0",
        "crystal": {
            "width": WIDTH,
            "constant": f"0x{C:04X}",
            "block": list(B),
            "weight": W,
        },
        "observer_count": count,
        "seeds": seeds,
        "steps": steps,
        "frames": frames(steps, seeds),
    }

