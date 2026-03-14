# Case Study: Real Repo (`tetragrammatron-os`)
Status: Advisory
Authority: Projection
Depends on: `docs/MJS_ASG_INGESTION_CONTRACT.md`, `docs/APPLIED_ANALYSIS_REPORT_CONTRACT.md`

Purpose: provide a full-project MJS-first analysis baseline for the Tetragrammatron repository using deterministic applied-analysis flow.

## Target
- repo: `/home/main/devops/tetragrammatron-os`
- repo commit at analysis time: `65a0d2cf2b8bf06ed5abd7f96f00dd52b539b7f9`
- language profile: `mjs`

## Target Manifest
- `reports/analysis-targets/tetragrammatron-os.json`

## Produced Artifacts
- report JSON:
  - `reports/analysis/tetragrammatron-os-65a0d2c/report.json`
- report Markdown:
  - `reports/analysis/tetragrammatron-os-65a0d2c/report.md`
- ASG frames:
  - `reports/analysis/tetragrammatron-os-65a0d2c/asg/*.json`
- per-file pattern extraction outputs:
  - `reports/analysis/tetragrammatron-os-65a0d2c/patterns/*.json`
- receipt:
  - `reports/analysis/tetragrammatron-os-65a0d2c/receipt.json`
- architecture diagram:
  - `docs/diagrams/tetragrammatron-architecture.svg`
- protocol diagram:
  - `docs/diagrams/tetragrammatron-protocol.svg`
- protocol flow:
  - `reports/analysis/tetragrammatron-os-65a0d2c/protocol-flow.json`

## Summary
- files analyzed: `35` (MJS)
- language counts:
  - `mjs: 35`
- domain counts:
  - `carrier: 6`
  - `conformance: 15`
  - `core: 12`
  - `projection: 2`
- ASG totals:
  - nodes: `3737`
  - edges: `2717`
- pattern counts:
  - `BoundarySplit: 4`
  - `BridgeLayer: 4`
  - `CarrierLayer: 14`
  - `ProjectionOnlySurface: 2`
  - `ConformanceSurface: 12`

## Findings
1. Full-project MJS ingestion is stable and deterministic at repository scale.
2. Structural extraction is substantial (3k+ nodes, 2k+ edges), confirming non-trivial semantic capture.
3. Architecture detectors now produce bridge/projection/conformance findings aligned with repository structure.

## Determinism / Trust Path
- report digests (from receipt):
  - `inputs_digest = sha256:5be9c99840ef90a9cc4c7a649263bcceb290c8e77b027a8ea776a82b0be124a5`
  - `evidence_digest = sha256:192459cf9ecd6fcb3480a43684e862ead3d825fc9d014f7b19b0ded0bdc54514`
  - `outputs_digest = sha256:4fc1d2f28c427dd62ae772d48c278bfe76861707de7a453342d09c7b07bbf6fb`
  - `report_json_sha = sha256:7dc7eded027bd4b87c01232cebfa695c5a6e0ca75baa1b80cf94f8fbacde7c5f`

## Reproduce
```bash
cd /home/main/devops/atomic-kernel
python3 scripts/build-analysis-target-manifest.py \
  --target /home/main/devops/tetragrammatron-os \
  --language-profile mjs \
  --out reports/analysis-targets/tetragrammatron-os.json

./scripts/run-applied-analysis.sh \
  --target /home/main/devops/tetragrammatron-os \
  --name tetragrammatron-os-65a0d2c \
  --out-root reports/analysis \
  --languages mjs

python3 scripts/generate-architecture-diagram.py \
  --report reports/analysis/tetragrammatron-os-65a0d2c/report.json \
  --output docs/diagrams/tetragrammatron-architecture.svg

python3 scripts/extract-protocol-flow.py \
  --asg reports/analysis/tetragrammatron-os-65a0d2c/asg \
  --patterns reports/analysis/tetragrammatron-os-65a0d2c/patterns \
  --output reports/analysis/tetragrammatron-os-65a0d2c/protocol-flow.json

python3 scripts/generate-protocol-diagram.py \
  --report reports/analysis/tetragrammatron-os-65a0d2c/report.json \
  --patterns reports/analysis/tetragrammatron-os-65a0d2c/patterns \
  --flow reports/analysis/tetragrammatron-os-65a0d2c/protocol-flow.json \
  --output docs/diagrams/tetragrammatron-protocol.svg
```

## Known Limitations (Current v0)
- MJS ingestion uses deterministic ESTree parsing through `acorn`; extraction remains structural and does not execute code.
- Topology-aware detectors require ASG `Imports/Calls` evidence and domain grouping, but still infer architecture from static structure and naming conventions.
- Protocol flow is a projection artifact (`authority: advisory`) and does not constitute canonical runtime state semantics.

## Next Improvement
- Add Tetragrammatron-specific pattern detectors after MJS domain partition enrichment.

## Boundary
This page is a projection-level case-study summary and does not redefine canonical semantic contracts or authority.
