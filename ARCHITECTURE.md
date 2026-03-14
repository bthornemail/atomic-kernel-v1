# Atomic Kernel Architecture
Status: Normative
Authority: Kernel
Depends on: `README.md`, `docs/STATUS.md`, `kernel/coq/AtomicKernel.v`

Purpose: document the current enforced contract and usage boundaries for this layer.


## Constitutional Layers
1. Kernel law (`delta`, `replay`, bounded widths).
2. Identity/occurrence law (SID/OID/CLOCK split).
3. Seed closure algebra (7-bit closure/phase).
4. Draft lane16 parallel extension.
5. Projection/propagation profiles (advisory).

## Authority Ladder
```text
Publication I  - Kernel Law
    ->
Publication II - Encoded Runtime
    ->
Publication III - Distributed Identity
    ->
Publication IV - Extension Structures
    ->
Publication V - Adoption Rules
    ->
Propagation Profiles - Transport / Projection
```

## Dataflow
`canonical payload -> seed -> replay -> witness -> validation gate -> replay hash lock`

## Enforcement Plane
- Unit conformance: `conformance/run-tests.sh`
- Wave gate suite: `scripts/atomic-kernel-gate.sh`
- Release gate: `scripts/release-gate.sh`
- Hash lock update (explicit only): `scripts/lock-replay-hashes.sh`

## Verification Triad
- Proofs: mathematical contract (`kernel/coq/AtomicKernel.v`).
- Gates: runtime enforcement (`scripts/*-gate.sh`).
- Replay locks: artifact reproducibility (`golden/**/replay-hash`).

## Drift Prevention
- Unknown keys and invalid bounds reject fail-closed.
- Canonical outputs are byte-stable for fixed input corpus.
- Downstream import boundary rejects internal path usage (`runtime.atomic_kernel.*`).

## Authority Separation
- Kernel/runtime/fixtures/golden are normative.
- Publication-IV/V and propagation profiles are extension/advisory unless promoted by normative gate and ABI update.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
