# Workspace Replay-Lock Readiness
Status: Draft
Authority: Extension
Depends on: `docs/WORKSPACE_INGESTION_CONTRACT.md`, `docs/WORKSPACE_SUMMARY_CONTRACT.md`

Purpose: define the end-of-soak decision rule for introducing replay-hash locks on workspace artifacts.

## Scope
- Applies to workspace canonical artifacts only:
  - `workspace-manifest.json`
  - `workspace-summary.json`
- Applies after one full W5 soak cycle with CI-required gates:
  - `scripts/typescript-parser-gate.sh`
  - `scripts/workspace-ingest-gate.sh`

## Decision Rubric
Introduce workspace replay locks only if all are true across the soak window:

1. Manifest shape stability
- `workspace-manifest.v0` key shape remained stable.
- Use soak evidence:
  - `manifest_shape_digest`
  - `shape_keys.manifest_top_keys`
  - `shape_keys.manifest_project_profile_keys`

2. Summary shape stability
- `workspace-summary.v0` key shape remained stable.
- Use soak evidence:
  - `summary_shape_digest`
  - `shape_keys.summary_top_keys`
  - `shape_keys.summary_project_report_keys`

3. Parser lane stability
- `typescript-parser-gate.sh` stayed green for the full soak window.
- Soak evidence: `gates.typescript_parser`.

4. Workspace gate stability
- `workspace-ingest-gate.sh` stayed green for the full soak window.
- Soak evidence: `gates.workspace_ingest`.

5. Overlay policy stability
- Overlays remained exclude-only.
- No policy drift to include-glob expansion.
- Soak evidence:
  - `overlay_include_nonempty_count == 0`
  - `overlay_count` and `overlay_exclude_glob_total` trend is stable or justified.

6. Stable summary reproducibility
- `summary_stable_digest` stayed reproducible for unchanged inputs.

7. Canonical no-noise check
- Canonical lock targets contain no run-id key noise.
- Soak evidence:
  - `run_id_noise_signals.manifest_has_run_id_key == false`
  - `run_id_noise_signals.summary_has_run_id_key == false`

8. Coverage non-regression
- `coverage` did not regress without an explicit documented cause.

## Evidence Source
- Advisory soak artifact:
  - `reports/workspace/soak/soak-status.json`
- Generator:
  - `scripts/update-workspace-soak-status.py`
- Optional advisory history:
  - `reports/workspace/soak/history/<run-id>.json`
  - `reports/workspace/soak/history/index.json`
- History append helper:
  - `scripts/append-workspace-soak-history.py`

## Outcomes
- `READY`
  - All rubric items pass.
  - Proceed to workspace replay-lock introduction milestone.
- `EXTEND_SOAK`
  - Any rubric item fails or is inconclusive.
  - Keep validation-only gates and continue evidence collection.

## Boundary
- This rubric governs readiness decisions only.
- It does not introduce replay locks by itself.
