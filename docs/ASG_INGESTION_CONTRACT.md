# ASG Ingestion Contract
Status: Draft
Authority: Extension
Depends on: `docs/ABSTRACT_SYNTAX_GRAPH_SCHEMA.md`, `docs/SEMANTIC_CONTRACTS_INDEX.md`

Purpose: define deterministic source ingestion (Python + TypeScript + MJS) into canonical ASG v0.

## Scope (v0)
- Input languages: `python`, `typescript`, `mjs`
- Parsers:
  - Python: stdlib `ast`
  - TypeScript: deterministic regex frontend (`typescript-regex`)
  - MJS: Acorn ESTree frontend (`mjs-acorn-estree`)
- Output: `ak.asg.v0` frame

## Ingestion rules
- Same source bytes + same parser version => same ASG JSON bytes.
- Unknown keys in ASG frame reject.
- Graph edge references must resolve to existing node ids.
- `graph_hash` must equal hash of canonical frame serialization (excluding `graph_hash` field).

## Output contract
- `v = ak.asg.v0`
- `authority = advisory`
- `language = python|typescript|mjs`
- `namespace` required
- `nodes`, `edges` deterministic ordering by `id`
- `provenance.parser = python-ast|typescript-regex|mjs-acorn-estree`
- `graph_hash = sha256:<hex64>`

## Fixtures
- Accept source fixtures under:
  - `runtime/atomic_kernel/fixtures/asg-ingest/accept/source-*.py`
  - `runtime/atomic_kernel/fixtures/asg-ingest/accept/source-*.ts`
  - `runtime/atomic_kernel/fixtures/asg-ingest/accept/source-*.mjs`
- Expected frame fixtures:
  - `runtime/atomic_kernel/fixtures/asg-ingest/accept/expected-*.json`
- Must-reject fixtures under:
  - `runtime/atomic_kernel/fixtures/asg-ingest/must-reject/`

## Gate
- `scripts/asg-ingest-gate.sh`
- Replay lock:
  - `golden/asg-ingest/replay-hash`

## Boundary
ASG ingestion defines canonical semantic extraction for this extension layer. It does not redefine kernel transition law.
