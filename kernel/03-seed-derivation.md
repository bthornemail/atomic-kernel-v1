# Seed Derivation
Status: Normative
Authority: Kernel
Depends on: `atomic_kernel/seed.py`, `runtime/atomic_kernel/seed_algebra.py`

Purpose: define deterministic seed derivation and seed-domain constraints.

Canonical seed derives from canonical payload bytes:
`seed = sha256(canonical_payload) truncated to width`

For Wave27J seed algebra, 7-bit domain is strict `0..127` and canonical header is closure-fixpoint.

## Boundary
Seed derivation is canonical input law; transport/projection media cannot redefine derived seeds.
