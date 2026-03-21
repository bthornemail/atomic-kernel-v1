# Workspace Snapshot Spec v0
Status: Normative
Authority: Canonical (spec)
Depends on: `docs/WORKSPACE_INGESTION_CONTRACT.md`, `docs/A15_REGENERATIVE_ARTIFACT_LAW_v0.md`

Purpose: define a deterministic, restorable snapshot lane for full tracked source files in the capability-kernel repository.

## Artifact

- `artifacts/workspace-snapshot-v0.normalized.json`
- `artifacts/workspace-snapshot-v0.bundle`
- `artifacts/workspace-snapshot-v0.replay-hash`
- `artifacts/workspace-snapshot-v0.restore.normalized.json`
- `artifacts/workspace-snapshot-v0.restore.replay-hash`

## v0 Contract

The normalized artifact is `workspace_snapshot.v0` and includes:

- `v`
- `authority` (`"advisory"` for runtime-emitted artifacts)
- `scope` (`"git_tracked_files"`)
- `repo_root`
- `head_commit`
- `file_count`
- `files_rollup_sha256`
- `bundle` (`path`, `sha256`)
- `files[]` with:
  - `path`
  - `sha256`
  - `bytes`
  - `mode`
  - `blob_oid`

Fail-closed behavior:

- tracked path missing on disk => reject
- normalized rerun mismatch => reject
- restore clone path set mismatch => reject
- restore blob/mode mismatch => reject

## Restore Semantics

Restore proof is produced by cloning from `workspace-snapshot-v0.bundle`, checking out `head_commit`, and verifying blob+mode parity for every tracked file in the manifest.

This lane proves:

- full tracked source set is encoded into a deterministic artifact family
- the same tracked source set is restorable from bundle + manifest

## Boundary

This lane covers full **tracked** repository content.
It does not include untracked local files, editor state, or host environment state.
