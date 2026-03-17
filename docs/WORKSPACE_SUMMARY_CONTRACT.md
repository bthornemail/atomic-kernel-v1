# Workspace Summary Contract
Status: Draft
Authority: Extension
Depends on: `docs/WORKSPACE_INGESTION_CONTRACT.md`, `docs/APPLIED_ANALYSIS_REPORT_CONTRACT.md`

Purpose: define deterministic aggregate reporting over project-level analysis outputs.

## Artifact
- `v = workspace-summary.v0`
- `authority = advisory`
- keys (exact):
  - `workspace_id`
  - `workspace_root`
  - `projects_total`
  - `projects_analyzed`
  - `projects_skipped`
  - `coverage`
  - `project_reports[]`
  - `aggregate_counts`
  - `inputs_digest`
  - `outputs_digest`

## Project Report Rows
- exact row keys:
  - `project_id`
  - `root_path`
  - `analyzed`
  - `reason`
  - `report_path`
  - `report_digest`
  - `summary`

## Aggregate Counts
- `files`
- `asg_nodes`
- `asg_edges`
- `language_counts`
- `domain_counts`
- `patterns`

## Coverage Delta
- `discovered`
- `analyzable`
- `analyzed`
- `analyzed_with_conformance`
- `analyzed_with_protocol_flow`

## Digest Rules
- `inputs_digest` covers workspace manifest digest + per-project analyzed/skip state.
- `outputs_digest` covers:
  - workspace id and project totals
  - aggregate counts
  - ordered `project_reports`
  - `inputs_digest`
- canonical JSON SHA-256 is required.

## Validation
- validator: `scripts/validate-workspace-summary.py`
- unknown keys reject
- unsorted project rows reject
- totals mismatch reject
- digest mismatch reject

## Boundary
Workspace summary is an advisory map over project analyses and cannot upgrade authority.
