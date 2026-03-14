"""Atomic-kernel IO/runtime surface."""
from .living_xml import (
  LivingXmlError,
  advance_living_xml,
  circulation_role,
  circulation_trace,
  next_fano_tick,
  parse_living_xml,
)
from .seed_algebra import (
  SCHEMA_V as SEED_ALGEBRA_SCHEMA_V,
  SeedAlgebraError,
  build_seed_entity,
  closure_fixpoint,
  compose_and,
  compose_xor,
  invariant_digest,
  phase,
  phase_from_header,
  popcount7,
  shared_phase,
  step_closure,
  validate_seed_entity,
)
from .seed_companion import (
  COMPANION_NS,
  COMPANION_V,
  SeedCompanionError,
  build_companion,
  companion_from_xml,
  companion_reference,
  companion_to_xml,
  derive_seed_from_wave27h_report,
  to_projection_metadata,
  validate_companion,
  validate_companion_wave27h_continuity,
)
from .lane16 import (
  SCHEMA_V as LANE16_SCHEMA_V,
  ALLOWED_STATES as LANE16_ALLOWED_STATES,
  CHANNELS as LANE16_CHANNELS,
  Lane16Error,
  Lane16System,
  control_code,
  encode_lane_state,
  fano_pcg_check,
  lane_pair_digest,
  lane_phase,
  lane_sid,
  lane_step,
  system_sid,
)

__all__ = [k for k in globals().keys() if not k.startswith("_")]
