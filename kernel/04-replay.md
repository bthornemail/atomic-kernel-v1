# Replay
Status: Normative
Authority: Kernel
Depends on: `atomic_kernel/core.py`, `kernel/coq/AtomicKernel.v`

Purpose: define deterministic replay semantics from a seed under fixed kernel law.

Given seed `x0`:
- `x1 = δ(x0)`
- `xk = δ^k(x0)`

Replay is deterministic: same law + same seed + same step count yields identical sequence.

## Boundary
Replay semantics are kernel authority and do not depend on projection-layer interpretations.
