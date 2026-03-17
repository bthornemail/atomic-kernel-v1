# Project Analysis Overlay Contract
Status: Draft
Authority: Extension
Depends on: `docs/WORKSPACE_INGESTION_CONTRACT.md`, `docs/PROJECT_PROFILE_CONTRACT.md`

Purpose: define deterministic, project-scoped exclusion overlays used by workspace orchestration to narrow candidate file sets without weakening global parser strictness.

## Artifact
- `v = project-analysis-overlay.v0`
- `authority = advisory`
- exact keys:
  - `project_id`
  - `root_path`
  - `include_globs`
  - `exclude_globs`
  - `overlay_digest`

## Rules (v0)
- Overlays are stored under:
  - `runtime/atomic_kernel/overlays/project-analysis/*.overlay.json`
- Overlays are project-boundary confined:
  - `project_id` and `root_path` must match the workspace-discovered project profile.
- Overlays may only narrow candidate file sets:
  - `include_globs` must be an empty list in v0.
  - `exclude_globs` must be sorted, unique, non-empty strings.
- Unknown keys reject.

## Digest
- `overlay_digest` is canonical JSON SHA-256 over:
  - `v`, `authority`, `project_id`, `root_path`, `include_globs`, `exclude_globs`
- Mismatch rejects fail-closed.

## Validation / Integration
- validator: `scripts/validate-project-analysis-overlay.py`
- runtime integration: `scripts/workspace-ingest.py`
- invalid overlay result:
  - project marked `analysis_failed:overlay_invalid`
  - overlay is never silently ignored

## Boundary
Overlays are advisory operational constraints and cannot redefine canonical semantic contracts.
