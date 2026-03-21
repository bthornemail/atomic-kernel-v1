# Metaverse Future Scope v0
Status: Advisory
Authority: Extension
Depends on: `scripts/metaverse-future-scope-smoke.sh`, `docs/MCP_ENTRYPOINTS.md`, `docs/UNIVERSE_SPEC_v0.md`, `docs/WORLD_SPEC_v0.md`, `docs/CHIRALITY_SELECTION_LAW_v0.md`, `docs/A14_INCIDENCE_SCHEDULING_LAW_v0.md`

Purpose: define a bounded, executable cross-repo scope for “future build readiness” using smoke proofs, integration docs, and optional capability benchmarks.

## Core Principle

Scope progression is driven by executable evidence, not narrative intent.

Pipeline:

`smoke gates -> integration checks -> optional benchmark/drill -> receipt`

## Scope Command Surface

```bash
npm run -s metaverse:future:scope:smoke
npm run -s metaverse:future:scope:smoke:bench
```

## What the Scope Smoke Covers

1. `atomic-kernel` proof surfaces:
- MCP HTTP smoke
- MCP STDIO smoke
- World v0 gate
- Universe v0 gate (A5 + A14)
- fork-import governance gate
- release gate

2. `metaverse-kit` proof surfaces:
- no-authority gate
- portal contract
- release verify
- MCP HTTP/STDIO smokes
- MCP contract verify

3. workspace constitutional spine:
- `/home/main/devops/scripts/closure-spine-smoke.sh`

4. docs integration checks:
- MCP benchmark command documented
- A14 MCP scheduling tool documented
- world MCP tools documented
- chirality and A14 indexed in atomic-kernel docs
- world spec indexed in atomic-kernel docs

## Optional Benchmark Extension

`--with-benchmark` adds:

- atomic-kernel MCP capability benchmark
- metaverse-kit runtime scale drill

This is used for runtime capability evidence, not canonical law authority.

## Artifacts

Smoke emits:

- `artifacts/metaverse-future-scope-smoke.normalized.json`
- `artifacts/metaverse-future-scope-smoke.replay-hash`
- `docs/proofs/metaverse-future-scope-smoke.latest.md`

## Boundary

This scope lane is advisory/proof orchestration.
It does not promote authority or alter kernel semantic truth.
