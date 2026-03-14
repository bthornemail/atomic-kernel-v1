# Witness Format
Status: Normative
Authority: Kernel
Depends on: `conformance/replay-witness-packs/replay-256.json`, `scripts/atomic-kernel-gate.sh`

Purpose: define deterministic witness packaging and verification obligations.

Canonical witness package includes:
- payload hash
- seed
- orbit/projection signature
- basis/runtime version

Verification recomputes hash, seed, and replay signature and rejects on mismatch.

## Boundary
Witness artifacts are derived from canonical replay truth and cannot upgrade authority.
