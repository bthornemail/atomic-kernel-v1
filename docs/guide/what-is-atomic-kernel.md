# What Is Atomic Kernel?
Status: Advisory
Authority: Extension
Depends on: `README.md`, `ARCHITECTURE.md`, `docs/STATUS.md`

Purpose: explain Atomic Kernel in plain language for new developers and evaluators.

Atomic Kernel is a deterministic runtime substrate for replayable computation and verifiable identity.

Instead of trusting environment-specific behavior, Atomic Kernel uses canonical artifacts plus deterministic replay so independent implementations can recompute and verify the same outcomes.

## Why people use it
- reproducible computation across machines
- verifiable identity chains (`SID`/`OID`)
- fail-closed validation for malformed artifacts
- explicit authority boundaries between kernel truth and projection surfaces

## What to read next
- `docs/guide/quick-start.md`
- `docs/guide/architecture-overview.md`
- `publications/publication-I-pure-kernel/P1-Kernel.md`

## Boundary
This guide is explanatory and derived from canonical artifacts. It does not redefine kernel law or upgrade authority.
