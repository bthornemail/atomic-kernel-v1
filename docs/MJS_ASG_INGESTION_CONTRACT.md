# MJS ASG Ingestion Contract
Status: Draft
Authority: Extension
Depends on: `docs/ASG_INGESTION_CONTRACT.md`, `docs/ABSTRACT_SYNTAX_GRAPH_SCHEMA.md`

Purpose: define deterministic `.mjs` ingestion into canonical ASG frames without collapsing authority boundaries.

## Scope (v0)
- Input surface: `.mjs` source files only.
- Output surface: `ak.asg.v0` frames (`authority: advisory`).
- Parser chain:
  - deterministic parser: `acorn` (ESTree, module mode)
  - runtime provenance id: `mjs-acorn-estree`

## Fail-Closed Rules
- Node/acorn parser unavailable -> reject.
- ESTree parse failure -> reject.
- Unknown output keys -> reject.
- Invalid edge references -> reject.
- Hash mismatch -> reject.

## Determinism Rules
- Same source bytes + same parser version -> byte-stable ASG output.
- Node and edge ids are deterministic and sorted.
- `graph_hash` is canonical sha256 over the frame excluding `graph_hash`.

## Fixture Surface
- Accept:
  - `runtime/atomic_kernel/fixtures/mjs-asg-ingest/accept/source-basic-mjs.mjs`
  - `runtime/atomic_kernel/fixtures/mjs-asg-ingest/accept/expected-basic-mjs.json`
- Must-reject:
  - `runtime/atomic_kernel/fixtures/mjs-asg-ingest/must-reject/bad-source-syntax.mjs`

## Target Freeze (Phase 0)
Use deterministic target manifests before full-repo analysis:

```bash
python3 scripts/build-analysis-target-manifest.py \
  --target /home/main/devops/tetragrammatron-os \
  --language-profile mjs \
  --out reports/analysis-targets/tetragrammatron-os.json
```

## Boundary
MJS ASG ingestion is a semantic extraction extension. It does not redefine kernel law, replay law, or canonical authority surfaces.
