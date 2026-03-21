# MCP Entrypoints (Atomic Kernel)
Status: Advisory
Authority: Extension
Depends on: `scripts/mcp-unified-entry.sh`, `scripts/mcp-unified-server.mjs`, `scripts/mcp-unified-stdio.mjs`, `docs/control-plane.pages.v0.json`

Purpose: explain the bounded MCP entry surface for local host-managed integrations.

## Supported Modes

- `server` (HTTP, implemented)
- `stdio` (implemented)
- `info` (implemented)

## Commands

```bash
npm run -s mcp:unified:info
npm run -s mcp:unified:server
npm run -s mcp:unified:smoke
npm run -s mcp:unified:stdio
npm run -s mcp:unified:stdio:smoke
npm run -s mcp:capability:benchmark
npm run -s capability:virtual:graph
npm run -s world:v0:gate
npm run -s world:branch:reconcile:gate
npm run -s metaverse:future:scope:smoke
npm run -s metaverse:future:scope:smoke:bench
```

## Contract Boundary

- MCP surface is advisory/runtime evidence only.
- Allowlisted pages are defined in `docs/control-plane.pages.v0.json`.
- Tool surface is bounded to:
  - `list_control_plane_pages`
  - `get_control_plane_page`
  - `verify_mcp_contract`
  - `get_incidence_schedule_snapshot`
  - `get_capability_kernel_virtual_graph`
  - `refresh_capability_kernel_virtual_graph`
  - `get_world_state`
  - `step_world` (proposal-only, no direct canonical commit)
  - `get_world_projection`
  - `verify_world`
  - `send_message_to_future`
  - `get_future_message`
- Non-allowlisted page requests fail closed (`found=false`, `allowed=false`).

## Future Message Demo

```bash
npm run -s mcp:future:demo
```

Outputs:

- `artifacts/mcp-future-message-demo.normalized.json`
- `artifacts/mcp-future-message-demo.replay-hash`
- `docs/proofs/mcp-future-message-demo.latest.md`

## Capability Benchmark

```bash
npm run -s mcp:capability:benchmark
```

Optional thresholds:

```bash
MAX_HTTP_P95_MS=40 MAX_STDIO_P95_MS=60 npm run -s mcp:capability:benchmark
```

Benchmark outputs:

- `artifacts/mcp-capability-benchmark.normalized.json`
- `artifacts/mcp-capability-benchmark.replay-hash`
- `docs/proofs/mcp-capability-benchmark.latest.md`

## Cross-Repo Future Scope Smoke

```bash
npm run -s metaverse:future:scope:smoke
npm run -s metaverse:future:scope:smoke:bench
```

Outputs:

- `artifacts/metaverse-future-scope-smoke.normalized.json`
- `artifacts/metaverse-future-scope-smoke.replay-hash`
- `docs/proofs/metaverse-future-scope-smoke.latest.md`

## Deterministic Proof

Smoke gate emits:

- `artifacts/mcp-unified-smoke.normalized.json`
- `artifacts/mcp-unified-smoke.replay-hash`
- `docs/proofs/mcp-unified-smoke.latest.md`
- `artifacts/mcp-unified-stdio-smoke.normalized.json`
- `artifacts/mcp-unified-stdio-smoke.replay-hash`
- `docs/proofs/mcp-unified-stdio-smoke.latest.md`

Both smoke gates rerun probes and require byte-identical normalized output.

## World v0 MCP Surface

The unified MCP surface exposes a bounded world operation lane:

- `get_world_state`
- `step_world`
- `get_world_projection`
- `verify_world`

`step_world` is proposal-only. It emits proposal + receipt artifacts and MUST NOT mutate canonical world state directly.

## Capability Graph MCP Surface

The unified MCP surface exposes:

- `get_capability_kernel_virtual_graph`
- `refresh_capability_kernel_virtual_graph`

This tool returns the deterministic virtual graph artifacts (`normalized`, `projection`, replay hash) and can return compact metadata-only responses via `include_nodes=false` and `include_edges=false`.

Scheduler guardrails for action tools can be tuned via:

- `MCP_MAX_LOAD_PER_CPU` (default `2.5`)
- `MCP_MIN_FREE_MEM_MB` (default `256`)

## A14 Scheduling Surface via MCP

The unified MCP surface exposes deterministic incidence scheduling snapshots via:

- `get_incidence_schedule_snapshot`

Snapshot rows include:

- `canonical_tick`
- `incidence_tick`
- `proposal_state`
- `fano_rank`
- `eligible`

This surface is advisory/runtime evidence only and does not grant mutation authority.
