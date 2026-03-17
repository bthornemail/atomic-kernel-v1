#!/usr/bin/env python3
"""Parallel vNext kernel lane (draft extension, non-authoritative).

This module provides side-by-side replay + identity surfaces so gates can
compare legacy normative behavior against the algorithmic-first lane.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

from runtime.atomic_kernel.identity.clock import clock_to_text, validate_clock
from runtime.atomic_kernel.identity.sid import SemanticIdentityError, validate_sid_type

LAW_VERSION = "ak.vnext.algorithmic.v1"
ID_LAW_VERSION = "ak.vnext.algorithmic-id.v1"
SUPPORTED_WIDTHS = {16, 32, 64, 128, 256}
SUPPORTED_HASH_ADAPTERS = {"sha256", "sha3_256"}


def _repeat_1d_constant(width: int) -> int:
  value = 0
  for _ in range(width // 8):
    value = (value << 8) | 0x1D
  return value


def _rotl(width: int, x: int, k: int) -> int:
  m = (1 << width) - 1
  x = x & m
  k %= width
  return ((x << k) | (x >> (width - k))) & m


def _rotr(width: int, x: int, k: int) -> int:
  m = (1 << width) - 1
  x = x & m
  k %= width
  return ((x >> k) | (x << (width - k))) & m


def _delta(width: int, x: int) -> int:
  m = (1 << width) - 1
  c = _repeat_1d_constant(width)
  return (_rotl(width, x, 1) ^ _rotl(width, x, 3) ^ _rotr(width, x, 2) ^ c) & m


def _to_base36(n: int) -> str:
  if n == 0:
    return "0"
  chars = "0123456789abcdefghijklmnopqrstuvwxyz"
  out = []
  x = n
  while x > 0:
    x, r = divmod(x, 36)
    out.append(chars[r])
  return "".join(reversed(out))


def _math_id_bytes(data: bytes) -> str:
  """Hash-free deterministic identifier encoding."""
  acc = 0
  mult = 1
  for b in data:
    acc += (int(b) + 1) * mult
    mult *= 257
  return f"math_v2:{len(data)}:{_to_base36(acc)}"


def _math_id_text(text: str) -> str:
  return _math_id_bytes(text.encode("utf-8"))


def compute_algorithmic_sid(type_name: str, canonical_form: str) -> str:
  validate_sid_type(type_name)
  if not isinstance(canonical_form, str) or canonical_form == "":
    raise SemanticIdentityError("canonical form must be non-empty string")
  return _math_id_text(f"{type_name}:{canonical_form}")


def compute_algorithmic_oid(clock: Dict[str, int], sid: str, prev_oid: str | None) -> str:
  validate_clock(clock)
  if not isinstance(sid, str) or not sid.startswith("math_v2:"):
    raise SemanticIdentityError("sid invalid")
  if prev_oid is not None and (not isinstance(prev_oid, str) or not prev_oid.startswith("math_v2:")):
    raise SemanticIdentityError("prev_oid invalid")
  payload = f"{clock_to_text(clock)}:{sid}:{prev_oid or 'null'}"
  return _math_id_text(payload)


def compute_hash_sid_adapter(type_name: str, canonical_form: str, hash_algo: str = "sha256") -> str:
  """Compatibility adapter for consumers still needing tagged hash IDs."""
  import hashlib

  validate_sid_type(type_name)
  if not isinstance(canonical_form, str) or canonical_form == "":
    raise SemanticIdentityError("canonical form must be non-empty string")
  if hash_algo not in SUPPORTED_HASH_ADAPTERS:
    raise SemanticIdentityError("unsupported hash algorithm")
  payload = f"{type_name}:{canonical_form}".encode("utf-8")
  if hash_algo == "sha256":
    dig = hashlib.sha256(payload).hexdigest()
  else:
    dig = hashlib.sha3_256(payload).hexdigest()
  return f"{hash_algo}:{dig}"


@dataclass(frozen=True)
class ReplayArtifact:
  v: str
  authority: str
  lane: str
  law_version: str
  width: int
  seed_hex: str
  steps: int
  states: List[Dict[str, Any]]
  algorithmic_replay_id: str

  def as_dict(self) -> Dict[str, Any]:
    return {
      "v": self.v,
      "authority": self.authority,
      "lane": self.lane,
      "law_version": self.law_version,
      "width": self.width,
      "seed_hex": self.seed_hex,
      "steps": self.steps,
      "states": self.states,
      "algorithmic_replay_id": self.algorithmic_replay_id,
    }


def _require_width(width: int) -> None:
  if width not in SUPPORTED_WIDTHS:
    raise ValueError("width must be one of 16,32,64,128,256")


def _legacy_states(width: int, seed: int, steps: int) -> List[int]:
  _require_width(width)
  if not isinstance(steps, int) or steps < 0:
    raise ValueError("steps must be int >= 0")
  m = (1 << width) - 1
  x = seed & m
  out: List[int] = []
  for _ in range(steps):
    out.append(x)
    x = _delta(width, x)
  return out


def _vnext_states(width: int, seed: int, steps: int) -> List[int]:
  _require_width(width)
  if not isinstance(steps, int) or steps < 0:
    raise ValueError("steps must be int >= 0")
  m = (1 << width) - 1
  x = seed & m
  out: List[int] = []
  for _ in range(steps):
    out.append(x)
    x = _delta(width, x)
  return out


def _encode_states(states: List[int], width: int) -> List[Dict[str, Any]]:
  hex_width = width // 4
  out: List[Dict[str, Any]] = []
  for i, s in enumerate(states):
    out.append({"step": i, "state_hex": f"0x{s:0{hex_width}X}"})
  return out


def replay_artifact(width: int, seed: int, steps: int, *, lane: str = "vnext") -> ReplayArtifact:
  if lane not in {"legacy", "vnext"}:
    raise ValueError("lane must be legacy or vnext")
  states_raw = _legacy_states(width, seed, steps) if lane == "legacy" else _vnext_states(width, seed, steps)
  states = _encode_states(states_raw, width)
  payload = {
    "lane": lane,
    "law_version": LAW_VERSION if lane == "vnext" else "ak.legacy.v1",
    "width": width,
    "seed_hex": f"0x{(seed & ((1 << width) - 1)):0{width // 4}X}",
    "steps": steps,
    "states": states,
  }
  canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
  replay_id = _math_id_text(canonical)
  return ReplayArtifact(
    v="ak.replay.vnext.v0",
    authority="advisory",
    lane=lane,
    law_version=payload["law_version"],
    width=width,
    seed_hex=payload["seed_hex"],
    steps=steps,
    states=states,
    algorithmic_replay_id=replay_id,
  )


def lane_parity(width: int, seed: int, steps: int) -> Dict[str, Any]:
  legacy = replay_artifact(width, seed, steps, lane="legacy")
  vnext = replay_artifact(width, seed, steps, lane="vnext")
  return {
    "width": width,
    "seed_hex": legacy.seed_hex,
    "steps": steps,
    "law_version_legacy": legacy.law_version,
    "law_version_vnext": vnext.law_version,
    "states_equal": legacy.states == vnext.states,
    "legacy_algorithmic_replay_id": legacy.algorithmic_replay_id,
    "vnext_algorithmic_replay_id": vnext.algorithmic_replay_id,
  }
