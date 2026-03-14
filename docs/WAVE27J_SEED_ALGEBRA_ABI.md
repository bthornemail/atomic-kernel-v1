# Wave 27J - Seed Algebra ABI
Status: Normative
Authority: Extension
Depends on: `runtime/atomic_kernel/seed_algebra.py`, `runtime/atomic_kernel/seed_companion.py`, `scripts/seed-algebra-gate.sh`

Purpose: freeze deterministic 7-bit seed closure algebra and canonical companion contract.

Version: `wave27J.seed_algebra.v0`  
Date: `2026-03-12`

## Domain
- seeds: integers in `0..127`
- cyclic 7-bit neighborhood topology

## Normative Operations
- `step_closure(seed)`
- `closure_fixpoint(seed)`
- `phase(seed)`
- `compose_xor(a,b)`
- `compose_and(a,b)`
- `shared_phase(a,b)`

All operations are deterministic and fail-closed for out-of-range values.

## Canonical Seed Entity
Required fields include:
- `seed`, `header`, `phase`, `type`, `canonical`, `sid`

Companion JSON is canonical truth for this layer; XML companion is projection-only.

## Gate
`scripts/seed-algebra-gate.sh` validates seed corpora, companion corpora, cross-wave continuity checks, and replay-hash lock.

## Boundary
Seed algebra ABI is extension contract derived from canonical artifacts.
It does not redefine kernel law and cannot upgrade authority.
