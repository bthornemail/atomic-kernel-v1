# World Spec v0
Status: Normative
Authority: Extension
Depends on: `docs/ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md`, `docs/PURE_ALGORITHMS.md`, `docs/CHIRALITY_SELECTION_LAW_v0.md`, `docs/A14_INCIDENCE_SCHEDULING_LAW_v0.md`, `docs/imports/folder1-v1_2/WITNESS_PLANE_SPEC.md`, `docs/world.v0.schema.json`, `docs/WORLD_PROOF_LEDGER_v0.json`

Purpose: define a bounded lawful world artifact lane with proposal-only mutation and deterministic projection.

## World v0 Definition

A world is a deterministic replay artifact with explicit authority boundaries:

- kernel seed anchors identity and replay,
- A5/A5b defines partition + chirality orientation,
- A14 defines response eligibility scheduling,
- witness boundary permits proposal/receipt only,
- projections are derived and non-authoritative.

## Canonical Artifact Shape

`world.v0` MUST include:

- `v`
- `authority`
- `world_id`
- `kernel_seed`
- `profile`
- `canonical_tick`
- `entities`
- `relations`
- `event_log`
- `branches`
- `proposal_queue`
- `receipts`
- `projection_views`

## Authority Boundary

- canonical world state and accepted event log are authoritative.
- projection views are derived and non-authoritative.
- `step_world` MUST emit proposal + receipt artifacts only.
- no hidden direct canonical mutation is permitted through MCP, projection, or witness surfaces.

## World 0 Profile (Bounded)

Profile id: `orchard_garden_lattice.v0`

Boundaries:

- entities: `8..16`
- relation types: `2..3`
- branch lanes: exactly `1` (`main`)
- proposal queue: exactly `1` queue surface
- projection views: exactly `1` deterministic JSON text view

The profile MUST include animate and inanimate entities under the same A14 eligibility law.

## Runtime Operation Surface (Exactly Four)

- `world_generate`: deterministic seed/profile to canonical `world.v0` artifact.
- `world_step`: compute next tick + eligibility, emit proposal + receipt artifacts only.
- `world_project`: deterministic JSON text projection from canonical world.
- `world_verify`: fail-closed schema/digest/replay verification.

## Boundary

This spec defines World v0 extension behavior for the capability-kernel lane and does not alter kernel semantic authority.
