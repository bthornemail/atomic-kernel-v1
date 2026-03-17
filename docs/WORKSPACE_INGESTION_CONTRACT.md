# Workspace Ingestion Contract
Status: Draft
Authority: Extension
Depends on: `docs/ASG_INGESTION_CONTRACT.md`, `docs/APPLIED_ANALYSIS_REPORT_CONTRACT.md`

Purpose: define deterministic workspace-level discovery and orchestration over project-level analysis.

## Scope (v0)
- Workspace root contains many projects.
- Discovery and analysis preserve project boundaries.
- Workspace outputs are advisory and cannot upgrade authority.

## Discovery Rules
- Candidate project roots are direct child directories with either:
  - `.git` root, or
  - project marker (`package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, `Makefile`)
- Deterministic ordering: `(project_id, root_path)`.
- Default skip dirs include:
  - `.git`, `node_modules`, `.venv`, `venv`, `dist`, `build`, `.next`, `coverage`, `.cache`, `site`, `reports`, `.obsidian`

## Project Profiles
- `project-profile.v0` includes:
  - project id/name/root
  - git root/commit/dirty
  - language set
  - include/exclude globs
  - analysis profile
  - analyzable flag

## Workspace Manifest
- `workspace-manifest.v0` includes:
  - `workspace_root`
  - `project_count`
  - `projects[]` (project profiles)
  - `discovery_rules`
  - `scan_digest`

## Orchestration
- `run-workspace-ingest.sh` / `workspace-ingest.py` run project analysis sequentially in deterministic order.
- Hybrid mode in W1:
  - full discovery
  - allowlisted analysis set

## Outputs
- Canonical workspace output root:
  - `reports/workspace/<run-id>/`
- Required artifacts:
  - `workspace-manifest.json`
  - `project-index.json` (internal derived helper; not a public contract surface in v0)
  - `workspace-summary.json`
  - `workspace-summary.md`
  - per-project directories with target/report/receipt/asg/patterns and optional protocol-flow.

## Validation/Gate
- manifest validator: `scripts/validate-workspace-manifest.py`
- summary validator: `scripts/validate-workspace-summary.py`
- workspace gate (validation-only): `scripts/workspace-ingest-gate.sh`
- overlay validator: `scripts/validate-project-analysis-overlay.py`
- parser lane gate: `scripts/typescript-parser-gate.sh` (requires `npx` + `tsc`; fails closed if unavailable)

## Overlay Policy (W4)
- Project-specific overlays may be applied from:
  - `runtime/atomic_kernel/overlays/project-analysis/*.overlay.json`
- Overlays can only narrow candidate file sets (exclude-only in v0).
- Invalid overlays fail closed at project scope (`analysis_failed:overlay_invalid`).

## Boundary
Workspace ingestion orchestrates derived analyses and does not mutate project source truth.

## W5 Soak Evidence (Advisory)
- Soak evidence artifact:
  - `reports/workspace/soak/soak-status.json`
- Generator:
  - `scripts/update-workspace-soak-status.py`
- Intended use:
  - advisory stability tracking during W5 soak (coverage, cohort, gate status, stable digest, overlay count, TS fallback probe evidence)
- Replay-lock decision rubric:
  - `docs/WORKSPACE_REPLAY_LOCK_READINESS.md`
