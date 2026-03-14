# Publication I — Kernel Law
Status: Normative
Authority: Kernel
Depends on: `kernel/coq/AtomicKernel.v`, `conformance/run-tests.sh`

Purpose: document the current enforced contract and usage boundaries for this layer.


## Scope
This publication freezes the deterministic kernel core used by `atomic_kernel.core`.

## Normative Law
For supported widths `n in {16,32,64,128,256}`:
- `delta_n(x) = mask_n(rotl_n(x,1) xor rotl_n(x,3) xor rotr_n(x,2) xor C_n)`
- `replay(seed, k)` is iterative application of `delta_n`.
- `C_n` is byte pattern `0x1D` repeated to width.

## Conformance Obligations
A conforming implementation must:
1. Produce the same replay sequence for same `(n, seed, k)`.
2. Keep states masked to width.
3. Preserve byte-stable canonical report outputs for fixture corpus.

## Deterministic Invariants
1. Transition law is deterministic for all supported widths.
2. Replay from identical seed/width/step yields identical sequence.
3. Canonical artifacts for fixed corpus produce identical replay hashes.
4. Identity surfaces derive from canonical forms.
5. Projection surfaces cannot alter canonical artifacts.

## Verification Basis in Repo
- Machine-checked core theorems: `kernel/coq/AtomicKernel.v`
- Executable reference API: `atomic_kernel/core.py`
- Runtime/gate evidence: `conformance/run-tests.sh`, `scripts/atomic-kernel-gate.sh`

## Non-Goals
- This publication does not assign authority to transport/projection media.
- This publication does not elevate draft extensions to constitutional law.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
