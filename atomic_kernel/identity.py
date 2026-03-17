"""Public identity/occurrence surface."""

from __future__ import annotations

import warnings
from typing import Any, Dict

from runtime.atomic_kernel.identity import (
  advance_clock as _advance_clock,
  compute_oid as _compute_oid,
  compute_sid as _compute_sid,
  compute_typed_sid as _compute_typed_sid,
)
from runtime.atomic_kernel.vnext import (
  compute_algorithmic_oid as _compute_algorithmic_oid,
  compute_algorithmic_sid as _compute_algorithmic_sid,
  compute_hash_sid_adapter as _compute_hash_sid_adapter,
)


def compute_sid(value: Any) -> str:
  warnings.warn(
    "compute_sid() is hash-default compat surface; prefer compute_algorithmic_sid().",
    DeprecationWarning,
    stacklevel=2,
  )
  return _compute_sid(value)


def compute_typed_sid(type_name: str, canonical_form: str) -> str:
  warnings.warn(
    "compute_typed_sid() is hash-default compat surface; prefer compute_algorithmic_sid().",
    DeprecationWarning,
    stacklevel=2,
  )
  return _compute_typed_sid(type_name, canonical_form)


def advance_clock(clock: Dict[str, int]) -> Dict[str, int]:
  return _advance_clock(clock)


def compute_oid(clock: Dict[str, int], sid: str, prev_oid: str | None) -> str:
  warnings.warn(
    "compute_oid() is hash-default compat surface; prefer compute_algorithmic_oid().",
    DeprecationWarning,
    stacklevel=2,
  )
  return _compute_oid(clock, sid, prev_oid)


def compute_algorithmic_sid(type_name: str, canonical_form: str) -> str:
  return _compute_algorithmic_sid(type_name, canonical_form)


def compute_algorithmic_oid(clock: Dict[str, int], sid: str, prev_oid: str | None) -> str:
  return _compute_algorithmic_oid(clock, sid, prev_oid)


def compute_hash_sid_adapter(type_name: str, canonical_form: str, hash_algo: str = "sha256") -> str:
  return _compute_hash_sid_adapter(type_name, canonical_form, hash_algo)
