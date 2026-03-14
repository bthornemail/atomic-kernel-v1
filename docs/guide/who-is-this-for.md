# Who Atomic Kernel Is For
Status: Advisory
Authority: Extension
Depends on: `README.md`, `docs/STATUS.md`

Purpose: help teams decide quickly whether Atomic Kernel is a good fit.

## Good fit
- Deterministic distributed runtimes.
- Verifiable artifact pipelines and replay-centric workflows.
- Identity-safe coordination systems (content-addressed truth, fail-closed validation).
- Systems requiring auditability and cross-machine reproducibility.

## Usually not a good fit
- Simple CRUD apps without deterministic replay requirements.
- Small internal services where eventual consistency and logs are sufficient.
- UI-first projects that do not require canonical artifact verification.

## Decision test
Use Atomic Kernel when your team needs all three:
- Recompute-and-verify behavior (not trust-only runtime behavior)
- Strict authority boundaries
- Deterministic replay as an operational requirement

If you only need one of the above, a lighter stack is often better.

## Boundary
This page is guidance for adoption decisions. It cannot redefine kernel law or authority status.
