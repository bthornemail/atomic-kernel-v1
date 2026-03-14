# P2 Control Surface
Status: Normative
Authority: Extension
Depends on: `atomic_kernel/core.py`, `runtime/atomic_kernel/living_xml.py`

Purpose: document the current enforced contract and usage boundaries for this layer.


## Purpose
Define how runtime state is encoded/projected over control hierarchies without upgrading authority.

## Implemented Surface
- Living XML hierarchy: `fs -> gs -> rs -> us`.
- Strict validation and fail-closed rejects.
- Deterministic tick progression (7-cycle).

## Boundary
- Encoded control surface is derived representation.
- Canonical truth remains deterministic runtime + fixtures + replay-hash locks.
