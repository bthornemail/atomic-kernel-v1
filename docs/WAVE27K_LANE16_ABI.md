# Wave 27K - Lane16 Parallel ABI
Status: Draft
Authority: Extension
Depends on: `runtime/atomic_kernel/lane16.py`, `scripts/lane16-gate.sh`, `docs/WAVE27J_SEED_ALGEBRA_ABI.md`

Purpose: define the implemented-but-draft 16-lane deterministic extension surface.

Version: `wave27K.lane16.v0`  
Date: `2026-03-13`

## Lane Model
- lane indices: `0..15`
- groups: 4 groups of 4 lanes
- valid states only: `0x0,0x8,0xC,0xD,0xE,0xF`

Any other 4-bit value rejects.

## Deterministic Operations
- lane stepping, phase, SID, system SID
- control-code projection encode
- group sync checks
- pair digest over lane relations

## Gate
`scripts/lane16-gate.sh` validates accept/must-reject corpora, emits deterministic report, and verifies replay-hash lock.

## Boundary
Wave27K remains draft extension scope in `0.1.0`.
It does not redefine kernel law and cannot upgrade authority.
