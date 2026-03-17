# Project Profile Contract
Status: Draft
Authority: Extension
Depends on: `docs/WORKSPACE_INGESTION_CONTRACT.md`

Purpose: define the deterministic project boundary record used by workspace ingestion.

## Artifact
- `v = project-profile.v0`
- `authority = advisory`
- keys (exact):
  - `project_id`
  - `name`
  - `root_path`
  - `git_root`
  - `git_commit`
  - `dirty`
  - `markers`
  - `languages`
  - `project_kind`
  - `include_globs`
  - `exclude_globs`
  - `analysis_profile`
  - `analyzable`

## Rules
- `project_id` must be stable and deterministic per root path.
- `analyzable` is true only for git-root projects in v0.
- `languages` are currently limited to:
  - `python`
  - `typescript`
  - `mjs`
- `git_commit`/`dirty` may be `null` when git metadata cannot be resolved.
- Unknown keys reject.

## Use
- Included in `workspace-manifest.v0`.
- Materialized per project under workspace run output as `target-manifest.json`.

## Boundary
Project profiles describe analysis scope and cannot redefine project authority.
