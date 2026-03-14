# atomic-kernel v0.1.0
Status: Normative
Authority: Extension
Depends on: `pyproject.toml`, `scripts/release-gate.sh`, `releases/0.1.0/ARTIFACTS.sha256`

Purpose: capture release classification and externally consumable contract for v0.1.0.

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

## Boundary
Release notes report enforced release state and do not redefine kernel law.
