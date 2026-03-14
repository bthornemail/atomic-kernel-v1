# Publication III — Distributed Runtime API
Status: Normative
Authority: Extension
Depends on: `docs/WAVE27I_IDENTITY_AND_OCCURRENCE_ABI.md`, `atomic_kernel/identity.py`

Purpose: document the current enforced contract and usage boundaries for this layer.


## Purpose
Define the deterministic exchange boundary for identity-bearing artifacts across nodes.

## Runtime Semantics
- Semantic identity: `SID = sha256(type + canonical_form)`.
- Occurrence identity: `OID = sha256(clock_position + sid + prev_oid)`.
- Clock law is deterministic and bounded (`frame 0..239`, `tick 1..7`, `control 0..59`).

## Interop Contract
Distributed peers must exchange:
- canonical forms for SID derivation,
- clock position for occurrence derivation,
- append-only link references (`prev_oid`, optional materialized `next_oid`).

## Verification Boundary
- Reject unknown keys/malformed identities/broken links.
- Recompute SID/OID locally to verify claims.
- Replay hash on chains must match for the same chain content.

## Explicit Boundary
This publication defines runtime extension semantics over the kernel. It does not redefine kernel transition law.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
