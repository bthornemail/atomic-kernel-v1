# Wave27L vNext Algorithmic Identity ABI
Status: Normative
Authority: Extension
Depends on: `runtime/atomic_kernel/vnext.py`, `scripts/vnext-replay-parity-gate.sh`, `scripts/vnext-api-compat-gate.sh`, `scripts/vnext-coq-parity-gate.sh`

Purpose: define the parallel vNext lane for algorithmic-first identity and replay artifacts during migration soak.

## Scope
- vNext lane is the promoted normative lane by explicit policy action.
- Compatibility adapters remain available during one major-cycle migration window.
- Policy artifact remains the authority switch surface for rollback if needed.

## Normative Target (post-promotion)
- Replay artifacts include explicit `law_version`.
- Canonical identity fields are algorithmic (`math_v2:*`) and hash-free.
- Hash IDs (`sha256:*`, `sha3_256:*`) remain compat adapters during one major-cycle window.

## Promotion Bar
Promotion is permitted only after soak evidence remains continuously green for:
1. `scripts/vnext-replay-parity-gate.sh`
2. `scripts/vnext-api-compat-gate.sh`
3. `scripts/vnext-coq-parity-gate.sh`

## Boundary
Promotion and rollback are policy actions only. Projection/advisory layers cannot upgrade authority.
