"""Deterministic transition and replay core."""

from __future__ import annotations

from typing import List


def _require_width(width: int) -> None:
  if width not in (16, 32, 64, 128, 256):
    raise ValueError("width must be one of 16,32,64,128,256")


def _mask(width: int) -> int:
  return (1 << width) - 1


def _normalize(width: int, x: int) -> int:
  return x & _mask(width)


def _rotl(width: int, x: int, k: int) -> int:
  x = _normalize(width, x)
  k %= width
  return _normalize(width, (x << k) | (x >> (width - k)))


def _rotr(width: int, x: int, k: int) -> int:
  x = _normalize(width, x)
  k %= width
  return _normalize(width, (x >> k) | (x << (width - k)))


def _repeat_1d_constant(width: int) -> int:
  value = 0
  for _ in range(width // 8):
    value = (value << 8) | 0x1D
  return value


C16 = _repeat_1d_constant(16)
C32 = _repeat_1d_constant(32)
C64 = _repeat_1d_constant(64)
C128 = _repeat_1d_constant(128)
C256 = _repeat_1d_constant(256)


def delta(width: int, x: int) -> int:
  """One deterministic kernel transition for width."""
  _require_width(width)
  c = _repeat_1d_constant(width)
  return _normalize(width, _rotl(width, x, 1) ^ _rotl(width, x, 3) ^ _rotr(width, x, 2) ^ c)


def replay(width: int, seed: int, steps: int) -> List[int]:
  """Replay deterministic orbit from seed."""
  _require_width(width)
  if not isinstance(steps, int) or steps < 0:
    raise ValueError("steps must be int >= 0")
  out: List[int] = []
  x = _normalize(width, seed)
  for _ in range(steps):
    out.append(x)
    x = delta(width, x)
  return out

