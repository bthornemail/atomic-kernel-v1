# Kernel Change Policy
Status: Normative
Authority: Kernel
Depends on: `README.md`, `docs/STATUS.md`, `scripts/release-gate.sh`, `golden/**/replay-hash`

Purpose: define how kernel and protocol changes are classified and what release discipline is required.

## Classification
### Patch
- Docs, tooling, test ergonomics, or non-semantic bug fixes.
- No deterministic output change for canonical fixtures/reports.
- No public API contract change.

Required:
- `./scripts/release-gate.sh` passes
- Release notes mention patch scope if user-visible

### Minor
- Backward-compatible additive behavior in extension/projection layers.
- New fixtures/gates may be added without redefining kernel law.
- New advisory documentation or demo capabilities.

Required:
- `./scripts/release-gate.sh` passes
- ABI/docs index updated
- Release notes enumerate additions and compatibility expectations

### Major
- Any change affecting deterministic outputs, kernel law, canonical fixture semantics, or public API contracts.
- Any authority-boundary shift.
- Any incompatible schema/runtime contract change in normative surfaces.

Required:
- Explicit migration guidance
- Version bump policy applied
- Replay-hash relock done intentionally and documented
- Release notes include compatibility break and upgrade path

## Relock Rules
Replay-hash regeneration is allowed only when one of these is true:
- Intentional normative semantic change (major/minor as applicable)
- Canonical fixture set intentionally changed
- Canonical report schema intentionally changed

Replay-hash regeneration is not allowed for:
- Styling/docs-only edits
- Incidental tooling changes that should not affect canonical outputs

## Public API Rule
External consumers must depend only on `atomic_kernel.*`.

Forbidden for downstream contracts:
- `runtime.atomic_kernel.*`
- Internal fixture/tool paths as API dependencies

## Mandatory Statement
Changes that affect deterministic outputs, public API contracts, canonical fixture semantics, or kernel law are not casual edits.

## Boundary
This policy constrains change discipline for kernel trust. It does not grant authority to projection layers.
