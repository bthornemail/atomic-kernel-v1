"""Public API for atomic-kernel."""

from .core import C16, C32, C64, C128, C256, delta, replay
from .identity import (
  advance_clock,
  compute_algorithmic_oid,
  compute_algorithmic_sid,
  compute_hash_sid_adapter,
  compute_oid,
  compute_sid,
  compute_typed_sid,
)
from .seed import closure_fixpoint, phase

__version__ = "0.1.0"

__all__ = [
  "__version__",
  "C16",
  "C32",
  "C64",
  "C128",
  "C256",
  "delta",
  "replay",
  "compute_sid",
  "compute_typed_sid",
  "advance_clock",
  "compute_oid",
  "compute_algorithmic_sid",
  "compute_algorithmic_oid",
  "compute_hash_sid_adapter",
  "closure_fixpoint",
  "phase",
]
