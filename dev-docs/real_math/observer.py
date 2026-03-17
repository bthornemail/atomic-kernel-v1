#!/usr/bin/env python3
"""Observer projection over crystal kernel."""

from __future__ import annotations

from kernel import B, T, classify, position_at, recover, state_at

_SYMBOLS = (
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "!@#$%^&*()"
    "+-=<>?/|~"
)


def _to_color(state: int) -> str:
    r = (state >> 8) & 0xFF
    g = ((state >> 4) & 0x0F) * 17
    b = (state & 0x0F) * 17
    return f"#{r:02X}{g:02X}{b:02X}"


def _to_symbol(seed: int, orbit: int, phase: int) -> str:
    return _SYMBOLS[(seed + orbit + phase) % len(_SYMBOLS)]


def observe(seed: int, n: int) -> dict:
    state = state_at(seed, n)
    position = position_at(n)
    orbit, offset = recover(position)
    width, density, texture = classify(state)
    phase = n % T
    diff = B[phase]
    return {
        "state": state,
        "position": position,
        "orbit": orbit,
        "offset": offset,
        "phase": phase,
        "diff": diff,
        "x": offset,
        "y": density,
        "color": _to_color(state),
        "symbol": _to_symbol(seed, orbit, phase),
        "band": [width, density, texture],
    }

