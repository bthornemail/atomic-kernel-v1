# vNext API Migration Matrix
Status: Draft
Authority: Advisory
Depends on: `atomic_kernel/identity.py`, `runtime/atomic_kernel/vnext.py`, `docs/WAVE27L_VNEXT_ALGORITHMIC_ID_ABI.md`

Purpose: map hash-first consumer calls to algorithmic-first vNext calls during the compatibility window.

| Legacy call | vNext call | Compat note |
| --- | --- | --- |
| `compute_typed_sid(type, canonical)` | `compute_algorithmic_sid(type, canonical)` | Legacy call remains operational but emits deprecation warning. |
| `compute_oid(clock, sid, prev_oid)` | `compute_algorithmic_oid(clock, sid, prev_oid)` | Legacy OID remains hash-based compat adapter. |
| `compute_sid(value)` | `compute_algorithmic_sid(type, canonical)` | Prefer typed canonical forms. |
| _(new)_ | `compute_hash_sid_adapter(type, canonical, hash_algo)` | Use only for consumers that still require tagged hash IDs. |

## Compatibility Window
- One major-cycle window.
- Hash adapters remain deterministic but advisory.
- Default normative target after promotion: algorithmic identity fields only.

## Boundary
This matrix is advisory migration guidance; it does not itself flip authority.
