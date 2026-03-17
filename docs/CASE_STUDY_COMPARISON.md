# Case Study Comparison
Status: Advisory
Authority: Projection
Depends on: `docs/CASE_STUDY_SAMPLE_ANALYSIS.md`, `docs/CASE_STUDY_REAL_REPO_METAVERSE_KIT_NF.md`, `docs/CASE_STUDY_REAL_REPO_TETRAGRAMMATRON_OS.md`

Purpose: compare baseline fixture analysis and first real-repo analysis in one operator-readable view.

## Compared Targets
- Baseline fixture corpus:
  - `runtime/atomic_kernel/fixtures/analysis-report/accept/target-sample/`
- Real repo case:
  - `/home/main/devops/metaverse-kit/packages/nf` at commit `f48da60`
- Real repo case:
  - `/home/main/devops/tetragrammatron-os` at commit `65a0d2cf2b8bf06ed5abd7f96f00dd52b539b7f9`

## Summary Table

| Metric | Baseline Fixture | Real Repo (`metaverse-kit/packages/nf`) | Real Repo (`tetragrammatron-os`) |
|---|---:|---:|---:|
| Files analyzed | 4 | 1 | 35 |
| Languages | python, typescript | typescript | mjs |
| ASG nodes | 36 | 52 | 3737 |
| ASG edges | 32 | 67 | 2717 |
| Adapter | 1 | 0 | 0 |
| Builder | 1 | 0 | 0 |
| Facade | 1 | 0 | 0 |
| Observer | 1 | 0 | 0 |
| Strategy | 1 | 0 | 0 |
| BoundarySplit | 0 | 0 | 4 |
| ProjectionOnlySurface | 0 | 0 | 2 |
| BridgeLayer | 0 | 0 | 4 |
| ConformanceSurface | 0 | 0 | 12 |
| CarrierLayer | 0 | 0 | 14 |
| Total pattern instances | 5 | 0 | 36 |

## Interpretation
1. Baseline fixture confirms full detector/path coverage under controlled inputs.
2. Real repo confirms end-to-end deterministic operation on non-fixture code.
3. Architecture-aware MJS detectors materially improve real-repo semantic yield for Tetragrammatron without changing canonical authority boundaries.

## Trust Notes
- Both case studies are advisory outputs over deterministic gates.
- Receipt consistency rule:
  - `pattern_count` in receipt must equal `len(report.instances)` from report JSON.
- Reproduce commands are documented in each case-study page.

## Boundary
This comparison is projection-level analysis and does not redefine canonical semantic contracts or authority.
