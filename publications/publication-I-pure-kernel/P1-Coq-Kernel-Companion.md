# Publication I — Coq Companion
Status: Normative
Authority: Kernel
Depends on: `kernel/coq/AtomicKernel.v`, `P1-Kernel.md`

Purpose: document the current enforced contract and usage boundaries for this layer.


## Purpose
This companion maps normative claims in Publication I to mechanized statements in Coq.

## What Is Proven Here
- Determinism of `delta` under equal inputs.
- Determinism of replay sequence under equal seeds.
- Idempotence of masking operation.

## Relationship to Runtime
- Python runtime (`atomic_kernel.core`) is the executable reference.
- Coq file is the formal contract source for the kernel law.
- If runtime and formal law diverge, runtime must be corrected.

## Claim Boundary
Only statements currently present and discharged in `AtomicKernel.v` are treated as formal proof claims.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
