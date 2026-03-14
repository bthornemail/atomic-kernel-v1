# Atomic Kernel Foundation
Status: Normative
Authority: Kernel
Depends on: `kernel/coq/AtomicKernel.v`

Purpose: document the current enforced contract and usage boundaries for this layer.


Define kernel tuple:
`K = (S, δ, π, Σ)`

- `S`: bounded state space.
- `δ`: deterministic transition.
- `π`: deterministic witness/projection.
- `Σ`: canonical seed derivation.

## Constitutional Claims
- Same law + same seed + same steps => same replay sequence.
- State transitions stay inside declared width bounds.
- Runtime surfaces may encode/transport state but do not redefine kernel law.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
