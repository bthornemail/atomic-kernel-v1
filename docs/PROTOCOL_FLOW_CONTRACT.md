# Protocol Flow Contract (`protocol-flow.v0`)
Status: Draft
Authority: Extension
Depends on: `docs/APPLIED_ANALYSIS_REPORT_CONTRACT.md`, `docs/PATTERN_EXTRACTION_CONTRACT.md`

Purpose: define the fail-closed protocol-flow projection artifact generated from ASG and pattern evidence.

## Authority
- This artifact is projection-level and must remain `authority: "advisory"`.
- It cannot redefine canonical semantic contracts.

## Shape
Top-level keys are exact (no extras):
- `v`
- `authority`
- `states`
- `transitions`
- `state_digest`
- `transition_digest`
- `flow_digest`

Required values:
- `v = "protocol-flow.v0"`
- `authority = "advisory"`

State item shape:
- `id`: non-empty string
- `count`: integer `>= 0`

Transition item shape:
- `from`: non-empty string
- `to`: non-empty string
- `kind`: non-empty string
- `count`: integer `>= 0`
- `evidence_edges`: array of non-empty strings

## Digest Rules
All digests are canonical-JSON SHA-256 (sorted keys, compact separators).

- `state_digest = sha256(canonical_json(states))`
- `transition_digest = sha256(canonical_json(transitions))`
- `flow_digest = sha256(canonical_json({"states": states, "transitions": transitions}))`

Any mismatch is reject.

## Validation/Gate
- Schema: `runtime/atomic_kernel/schemas/protocol-flow.v0.schema.json`
- Validator: `scripts/validate-protocol-flow.py`
- Gate: `scripts/protocol-flow-gate.sh`
- Golden lock: `golden/protocol-flow/replay-hash`
- Report artifact: `reports/phase27Q-protocol-flow.json`

## Boundary
This contract governs a derived protocol-flow projection and does not upgrade authority.
