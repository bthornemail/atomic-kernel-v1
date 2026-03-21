# MCP Unified STDIO Smoke Proof

Date: 2026-03-21
Generated (UTC): 2026-03-21T16:03:22Z
Repo: /home/main/devops/atomic-kernel

Command Invoked:
npm run -s mcp:unified:stdio:smoke

Server Entry:
npm run -s mcp:unified:stdio

Checks:
stdio boot: PASS
tool list: PASS
list_control_plane_pages: PASS
get_control_plane_page(protocol_spec): PASS
get_incidence_schedule_snapshot: PASS
get_capability_kernel_virtual_graph: PASS
refresh_capability_kernel_virtual_graph: PASS
get_world_state: PASS
get_world_projection: PASS
step_world proposal-only path: PASS
verify_world: PASS
non-allowlisted page fetch blocked: PASS
deterministic rerun byte-compare: PASS

Expected Tools Found:
list_control_plane_pages, get_control_plane_page, get_incidence_schedule_snapshot, get_capability_kernel_virtual_graph, refresh_capability_kernel_virtual_graph, get_world_state, step_world, get_world_projection, verify_world

Deterministic Artifacts:
artifacts/mcp-unified-stdio-smoke.normalized.json
artifacts/mcp-unified-stdio-smoke.replay-hash (sha256:16842a09a4dfc677ebb460dfbfe8271bb85a6b5641054eb448c6df7d90886291)

Result: PASS
