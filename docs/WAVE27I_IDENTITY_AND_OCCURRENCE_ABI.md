# Wave 27I - Identity and Occurrence ABI
Status: Normative
Authority: Extension
Depends on: `runtime/atomic_kernel/identity/*.py`, `scripts/identity-gate.sh`

Purpose: freeze deterministic SID/OID/CLOCK split for append-only occurrence semantics.

Version: `wave27I.identity_occurrence_chain.v0`  
Date: `2026-03-12`

## Constitutional Split
- `SID`: semantic identity (`what`) from canonical form.
- `CLOCK`: deterministic traversal position (`when/where`).
- `OID`: occurrence identity (`sid @ clock` + chain predecessor).

## Formulas
- `SID = sha256(type || ":" || canonical_form)`
- `OID = sha256(clock_position || ":" || sid || ":" || prev_oid_or_null)`

## Clock Law
`CLOCK = (frame, tick, control)` with strict bounds:
- `frame in [0,239]`
- `tick in [1,7]`
- `control in [0,59]`

Advance:
- increment `tick`
- on wrap (`tick -> 1`), increment `frame` mod 240 and `control` mod 60

## Chain Law
Occurrence chain is append-only with immutable `oid` and `prev_oid` once written.

## Gate
`scripts/identity-gate.sh` validates SID/CLOCK/OID corpora, cross-wave continuity fixtures, and replay-hash lock.

## Boundary
Identity/occurrence ABI is extension-level contract derived from canonical artifacts.
It does not redefine kernel transition law and cannot upgrade authority.
