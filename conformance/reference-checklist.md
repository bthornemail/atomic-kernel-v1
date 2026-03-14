# Conformance Checklist
Status: Normative
Authority: Extension
Depends on: `conformance/run-tests.sh`, `scripts/atomic-kernel-gate.sh`, `scripts/release-gate.sh`

Purpose: define the minimum reproducibility checks required before release decisions.

## Checklist
- Runtime unit tests pass.
- Gate reports reproduce expected replay hashes.
- Canonical outputs are byte-stable across reruns.

## Boundary
This checklist validates implementation conformance and release readiness; it does not redefine kernel law.
