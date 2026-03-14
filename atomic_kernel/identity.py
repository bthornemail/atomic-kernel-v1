"""Public identity/occurrence surface."""

from __future__ import annotations

from typing import Any, Dict

from runtime.atomic_kernel.identity import (
  advance_clock as _advance_clock,
  compute_oid as _compute_oid,
  compute_sid as _compute_sid,
  compute_typed_sid as _compute_typed_sid,
)


def compute_sid(value: Any) -> str:
  return _compute_sid(value)


def compute_typed_sid(type_name: str, canonical_form: str) -> str:
  return _compute_typed_sid(type_name, canonical_form)


def advance_clock(clock: Dict[str, int]) -> Dict[str, int]:
  return _advance_clock(clock)


def compute_oid(clock: Dict[str, int], sid: str, prev_oid: str | None) -> str:
  return _compute_oid(clock, sid, prev_oid)

