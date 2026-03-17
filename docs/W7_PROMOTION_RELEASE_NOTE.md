# W7 Promotion Release Note
Status: Normative
Authority: Kernel Policy
Depends on: `runtime/atomic_kernel/vnext_policy.json`, `docs/VNEXT_MIGRATION_NOTICE_W7.md`, `docs/VNEXT_AUTHORITY_PROMOTION_DECISION.md`

## Statement
- Legacy lane remained normative through W6.
- vNext became normative in W7 via explicit governance policy action.
- Promotion was validated post-flip with replay/API/Coq parity gates, release gate, and closure spine.

## Compatibility
- Hash-default helpers remain compatibility-only during the one-major-cycle migration window.
- Consumers should migrate to algorithmic identity APIs.

## Boundary
This release note records governance action and compatibility posture only; it does not authorize feature expansion.
