# vNext Migration Notice (W7 Promotion)
Status: Normative
Authority: Kernel Policy
Depends on: `runtime/atomic_kernel/vnext_policy.json`, `docs/VNEXT_API_MIGRATION_MATRIX.md`, `docs/VNEXT_AUTHORITY_PROMOTION_DECISION.md`

Purpose: publish the explicit W7 promotion action and compatibility expectations.

## Promotion Statement
- Legacy lane was normative through W6 soak.
- W7 executes explicit governance promotion.
- vNext is now the promoted normative lane by policy artifact.

## Compatibility Window
- Duration: one major cycle.
- Hash-based identity helpers remain available as compatibility adapters.
- Legacy hash-default helper calls emit deprecation warnings and are migration-path surfaces only.

## Required Consumer Action
1. Migrate from `compute_typed_sid`/`compute_oid` toward algorithmic APIs:
   - `compute_algorithmic_sid`
   - `compute_algorithmic_oid`
2. Use `compute_hash_sid_adapter` only where tagged hash IDs are still contractually required.
3. Complete consumer migration before compatibility window closes.

## Rollback Guard
Rollback conditions remain active per `VNEXT_AUTHORITY_PROMOTION_DECISION.md`.
Any parity/API/proof/authority regression reverts policy to pre-promotion defaults.

## Boundary
This notice documents policy execution. It does not authorize feature expansion or additional authority-surface changes.
