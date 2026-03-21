# A15 Regenerative Artifact Law v0
Status: Normative
Authority: Extension
Depends on: `docs/PURE_ALGORITHMS.md`, `docs/A14_INCIDENCE_SCHEDULING_LAW_v0.md`, `docs/MCP_ENTRYPOINTS.md`

Purpose: define lawful, deterministic regeneration of advisory artifacts through bounded execution surfaces.

## Definition

A regenerative action is a bounded transformation:

- input constraints `C`
- deterministic generator `G`
- output artifact set `A'`

Such that:

- `A'` is reproducible under the same `C`
- output digests are emitted and verifiable
- execution is scheduled by eligibility gates

## Normative Rules

1. Regeneration must run through explicit bounded interfaces (no arbitrary execution).
2. Regeneration outputs must include deterministic digest surfaces.
3. Regeneration must fail-closed on scheduler ineligibility (`busy`, `load`, `memory`).
4. Regeneration artifacts are advisory unless explicitly promoted by authority policy.
5. Regeneration must not mutate canonical truth in-place.

## MCP Binding (v0)

Bounded MCP tools:

- `refresh_capability_kernel_virtual_graph`
- `get_capability_kernel_virtual_graph`

Execution eligibility is governed by A14-style scheduler checks over compute incidence.

## Boundary

A15 governs controlled recomputation and artifact emission. It does not redefine kernel truth semantics.
