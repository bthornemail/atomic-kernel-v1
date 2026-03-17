# Pattern Extraction Contract
Status: Draft
Authority: Extension
Depends on: `docs/ASG_INGESTION_CONTRACT.md`, `docs/PATTERN_INSTANCE_SCHEMA.md`

Purpose: define deterministic extraction of pattern instances from canonical ASG frames.

## Scope (v0)
- Source: validated `ak.asg.v0` frames.
- Output: deterministic `ak.pattern_extraction.v0` report with `ak.pattern.instance.v0` entries.
- Implemented detectors:
  - `Adapter`
  - `Builder`
  - `Facade`
  - `Observer`
  - `Strategy`
  - `BoundarySplit` (MJS architecture detector)
  - `ProjectionOnlySurface` (MJS architecture detector)
  - `BridgeLayer` (MJS architecture detector)
  - `CarrierLayer` (MJS architecture detector)
  - `ConformanceSurface` (MJS architecture detector)

## Rules
- Extraction is derived and advisory.
- Same ASG input => same pattern report bytes.
- Invalid ASG input fails closed.
- Pattern instances must satisfy pattern-instance contract constraints.
- Architecture detectors use topology-aware domain-edge constraints (`Imports` + `Calls`) for precision.

## Fixtures
- Accept corpus:
  - `runtime/atomic_kernel/fixtures/pattern-extraction/accept/asg-*.json`
  - expected reports in `expected-*.json`
- Must-reject corpus:
  - `runtime/atomic_kernel/fixtures/pattern-extraction/must-reject/bad-asg-*.json`

## Gate
- `scripts/pattern-extraction-gate.sh`
- Replay lock:
  - `golden/pattern-extraction/replay-hash`

## Boundary
Pattern extraction is a derived semantic layer and cannot mutate or redefine canonical ASG truth.
