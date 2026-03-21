# Artifact Lifecycle v0
Status: Normative
Authority: Kernel Policy
Depends on: `docs/imports/folder1-v1_2/LIFECYCLE_REGISTRY.v0.json`, `scripts/artifact-lifecycle-v0-gate.sh`, `docs/FORK_IMPORT_INDEX_v1_2.md`

Purpose: define fail-closed lifecycle states and transition law for fork-import artifact governance.

## Scope

This policy applies only to the fork-import lane:

- `docs/imports/folder1-v1_2/`

It does not redefine kernel semantic authority.

## Lifecycle States

- `candidate`
- `validated`
- `receipted`
- `promotion-ready`
- `canonical`
- `deprecated`
- `superseded`

## Allowed Transitions

- `candidate -> validated`
- `validated -> receipted`
- `receipted -> promotion-ready`
- `promotion-ready -> canonical`
- `canonical -> deprecated`
- `canonical -> superseded`
- `deprecated -> superseded`

Rules:

- backward transitions are forbidden
- skip transitions are forbidden
- exception: transition to `superseded` is allowed only from states listed above

## Decision/State Consistency

- `lifecycle_state=canonical` requires `promotion_decision=merge|supersede`.
- `promotion_decision=defer` cannot be `canonical`.
- `canonical` requires existing `canonical_target` path.

## Index Boundary

- imported files may appear in canonical docs index only when lifecycle state is `canonical`.
- all non-canonical entries must stay out of canonical index surfaces.

## Source of Truth

Machine state is authoritative in:

- `docs/imports/folder1-v1_2/LIFECYCLE_REGISTRY.v0.json`

Human-facing docs may summarize state but do not override registry values.

## Gate Requirement

Required gate:

- `bash scripts/artifact-lifecycle-v0-gate.sh`

Gate must fail closed on unknown states, missing keys, illegal transitions, index boundary breaches, and decision/state inconsistency.

## Boundary

This policy governs artifact promotion workflow only and does not change kernel law semantics.
