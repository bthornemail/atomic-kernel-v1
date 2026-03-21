# Source Capability Parity v0
Status: Normative
Authority: Canonical (spec)
Depends on: `docs/WORKSPACE_SNAPSHOT_SPEC_v0.md`, `docs/WORLD_SPEC_v0.md`, `docs/UNIVERSE_SPEC_v0.md`, `docs/MCP_ENTRYPOINTS.md`

Purpose: prove that restored source from snapshot can regenerate the same lawful capability surface.

## Contract

The parity gate must:

1. restore source from `workspace-snapshot-v0.bundle` at `head_commit`
2. run core capability surfaces on baseline and restored source
3. compare replay-hash outputs for parity
4. fail-closed on any mismatch

Core surfaces (v0):

- `world:v0:gate`
- `capability:virtual:graph`
- `universe:v0:gate`
- `mcp:unified:smoke`
- `mcp:unified:stdio:smoke`

## Artifacts

- `artifacts/source-capability-parity.normalized.json`
- `artifacts/source-capability-parity.replay-hash`
- `docs/proofs/source-capability-parity.latest.md`

## Boundary

This lane proves source-to-capability replay parity for defined surfaces.
It does not imply environment parity beyond what those surfaces already validate.
