# Applied Analysis Report Contract
Status: Draft
Authority: Extension
Depends on: `docs/ASG_INGESTION_CONTRACT.md`, `docs/PATTERN_EXTRACTION_CONTRACT.md`

Purpose: define deterministic applied repository analysis as an advisory artifact.

## Artifact
- `v = analysis-report.v0`
- `authority = advisory`
- target metadata (`path`, `languages`)
- deterministic summary counts
  - includes deterministic `domain_counts`
- pattern instances with evidence references
- integrity digests:
  - `inputs_digest`
  - `evidence_digest`
  - `outputs_digest`

## Scope (v0)
- Ingestion languages: `python`, `typescript`, `mjs`
- Pattern detectors: `Adapter`, `Builder`, `Facade`, `Observer`, `Strategy`

## Determinism rules
- File walk order is lexicographic.
- Instance ordering is stable by `(pattern_type, pattern_id, file)`.
- Equal target tree bytes => equal report JSON bytes.

## Validation/gate
- validator: `scripts/validate-analysis-report.py`
- analyzer: `scripts/semantic-analyze.py`
- operator wrapper: `scripts/run-applied-analysis.sh`
- gate: `scripts/analysis-report-gate.sh`
- replay lock: `golden/analysis-report/replay-hash`

## Operator output layout
`run-applied-analysis.sh` emits deterministic artifacts to:
- `reports/analysis/<name>/report.json`
- `reports/analysis/<name>/report.md`
- `reports/analysis/<name>/asg/*.json`
- `reports/analysis/<name>/patterns/*.json`
- `reports/analysis/<name>/receipt.json`

## Boundary
Applied analysis reports are derived advisory artifacts and cannot mutate canonical semantic contracts.
