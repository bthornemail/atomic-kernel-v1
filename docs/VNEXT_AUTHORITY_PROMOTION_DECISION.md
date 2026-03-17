# vNext Authority Promotion Decision
Status: Draft
Authority: Kernel Policy
Depends on: `runtime/atomic_kernel/vnext_policy.json`, `docs/WAVE27L_VNEXT_ALGORITHMIC_ID_ABI.md`, `scripts/vnext-replay-parity-gate.sh`, `scripts/vnext-api-compat-gate.sh`, `scripts/vnext-coq-parity-gate.sh`

Purpose: define explicit criteria and rollback conditions for authority flip from legacy hash-first lane to vNext algorithmic-first lane.

## Default State (Pre-Promotion)
- `vnext_status = draft_extension_lane`
- `promotion_approved = false`
- `no_authority_change = true`

## Current State (W7)
- `vnext_status = promoted_normative_lane`
- `promotion_approved = true`
- `no_authority_change = false`

## Promotion Criteria
All must be true across the soak window:
1. Replay parity gate continuously green.
2. API compat gate continuously green.
3. Coq parity gate continuously green.
4. Current release gate and closure spine remain green.
5. No authority boundary regressions detected.

## Approval Action
Promotion requires explicit policy update:
- `promotion_approved: true`
- `no_authority_change: false`
- updated versioned docs and migration notice.

## Rollback Conditions
Revert promotion if any occurs:
- deterministic parity regression,
- public API incompatibility regression,
- proof parity regression,
- authority-boundary regression.

Rollback returns policy to draft defaults and re-enables hash-first normative lane.

## Boundary
Promotion is explicit policy action only. If rollback conditions trigger, policy returns to pre-promotion defaults and legacy lane is restored as normative.
