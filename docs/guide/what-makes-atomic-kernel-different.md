# What Makes Atomic Kernel Different
Status: Advisory
Authority: Extension
Depends on: `README.md`, `docs/STATUS.md`, `docs/WAVE27I_IDENTITY_AND_OCCURRENCE_ABI.md`

Purpose: position Atomic Kernel against adjacent architectures without overstating scope.

## Short answer
Atomic Kernel is a deterministic replay substrate with strict authority boundaries and content-derived identity. It is not a consensus chain, not a conflict-free merge algorithm, and not a generic app framework.

## Comparison
### Versus event sourcing
- Event sourcing records history and derives state.
- Atomic Kernel adds deterministic replay contracts, replay-hash locks, and fail-closed gates as first-class release requirements.

### Versus CRDT systems
- CRDTs prioritize convergence under concurrent edits.
- Atomic Kernel prioritizes canonicalization + replay determinism + explicit authority classes.
- They can be combined, but they solve different primary problems.

### Versus blockchains
- Blockchains solve open-network consensus and Byzantine trust.
- Atomic Kernel solves deterministic recomputation and identity-safe verification for governed systems.
- No token/economic consensus is required by kernel law.

### Versus deterministic simulators
- Deterministic simulators typically focus on simulation state updates.
- Atomic Kernel adds protocol/gate/release discipline across artifacts, identities (SID/OID/CLOCK), and projection boundaries.

## Choose Atomic Kernel when
- You need cross-machine replay reproducibility.
- You need strict authority boundaries (projection cannot become truth).
- You need content-derived identity and append-only occurrence chains.

## Do not choose Atomic Kernel when
- You only need basic CRUD with standard persistence.
- You do not require deterministic replay verification.
- You need open, adversarial consensus as the primary problem.

## Boundary
This page is an adoption aid. It cannot redefine kernel law or authority classes.
