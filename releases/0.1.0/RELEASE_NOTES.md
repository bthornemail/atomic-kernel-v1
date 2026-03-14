# atomic-kernel v0.1.0

## Classification
- implementation-complete
- verification-complete
- release-normalized

## Public API
- `atomic_kernel.delta`
- `atomic_kernel.replay`
- `atomic_kernel.compute_sid`
- `atomic_kernel.compute_typed_sid`
- `atomic_kernel.advance_clock`
- `atomic_kernel.compute_oid`
- `atomic_kernel.closure_fixpoint`
- `atomic_kernel.phase`

## Determinism and gates
- `scripts/atomic-kernel-gate.sh` passes.
- `scripts/release-gate.sh` passes.
- Replay hash locks enforced for Wave27H/27I/27J/27K.

## Contract boundaries
- Normative: kernel law + Wave27H/27I/27J runtime contracts.
- Draft extension: Wave27K lane16.
- Advisory/projection: aztec/clipboard/xml surfaces.

## Release artifact index
See `releases/0.1.0/ARTIFACTS.sha256`.
