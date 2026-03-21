# Capability Kernel Virtual Graph v0
Status: Advisory
Authority: Extension
Depends on: `scripts/capability-kernel-virtual-graph.sh`, `docs/WORKSPACE_INGESTION_CONTRACT.md`

Purpose: render a deterministic virtual graph of the capability-kernel workspace from workspace-ingest outputs.

## Command Surface

```bash
npm run -s capability:virtual:graph
```

Optional refresh before graphing:

```bash
bash scripts/capability-kernel-virtual-graph.sh --refresh
```

Optional run-id selection:

```bash
bash scripts/capability-kernel-virtual-graph.sh --run-id devops-scan-w6-004
```

## Output Artifacts

- `artifacts/capability-kernel-virtual-graph.normalized.json`
- `artifacts/capability-kernel-virtual-graph.projection.json`
- `artifacts/capability-kernel-virtual-graph.mermaid.md`
- `artifacts/capability-kernel-virtual-graph.replay-hash`
- `docs/proofs/capability-kernel-virtual-graph.latest.md`

## Graph Model (v0)

- workspace node
- project nodes (analyzed projects)
- language nodes
- domain nodes
- pattern nodes
- weighted edges:
  - workspace -> project (`contains_project`)
  - project -> language (`uses_language`)
  - project -> domain (`emits_domain_surface`)
  - project -> pattern (`matches_pattern`)

## Boundary

This lane is projection/analysis only and does not mutate canonical authority surfaces.
