# Case Study: Real Repo (`metaverse-kit/packages/nf`)
Status: Advisory
Authority: Projection
Depends on: `docs/APPLIED_ANALYSIS_REPORT_CONTRACT.md`, `docs/CASE_STUDY_SAMPLE_ANALYSIS.md`

Purpose: provide a real-repository baseline analysis using the deterministic applied-analysis pipeline.

## Target
- repo: `/home/main/devops/metaverse-kit`
- analyzed subpath: `packages/nf`
- repo commit at analysis time: `f48da60`
- note: working tree was not fully clean (`docs/index.md` modified; `docs/agents/` untracked)

## Produced Artifacts
- report JSON:
  - `reports/analysis/metaverse-kit-nf-f48da60/report.json`
- report Markdown:
  - `reports/analysis/metaverse-kit-nf-f48da60/report.md`
- ASG frames:
  - `reports/analysis/metaverse-kit-nf-f48da60/asg/*.json`
- per-file pattern extraction outputs:
  - `reports/analysis/metaverse-kit-nf-f48da60/patterns/*.json`
- receipt:
  - `reports/analysis/metaverse-kit-nf-f48da60/receipt.json`

## Summary
- files analyzed: `1` (TypeScript)
- language counts:
  - `typescript: 1`
- ASG totals:
  - nodes: `52`
  - edges: `67`
- pattern counts:
  - none detected by current detector set

## Findings
1. The pipeline runs end-to-end on a real repository target with deterministic outputs.
2. ASG extraction is successful and non-trivial (52 nodes / 67 edges from one TS source file).
3. Current pattern detectors (Adapter/Builder/Facade/Observer/Strategy) do not trigger on this package.

## Determinism / Trust Path
- report digests (from receipt):
  - `inputs_digest = sha256:6c1d94257de80cdea07b79c76efba77481e77bb4069a3ff094d1ecf1c4a6795f`
  - `evidence_digest = sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
  - `outputs_digest = sha256:ad1cdac4af85f073652a43fdd7647cb63f6265d4b0a645db4ca0d84fce75582e`
  - `report_json_sha = sha256:423eeb6ee48ad4d968efd62434badeac6f36bbb2058b850f14cf9245fca6deec`

## Reproduce
```bash
cd /home/main/devops/atomic-kernel
./scripts/run-applied-analysis.sh \
  --target /home/main/devops/metaverse-kit/packages/nf \
  --name metaverse-kit-nf-f48da60 \
  --out-root reports/analysis \
  --languages typescript
```

## Known Limitations (Current v0)
- TypeScript ingestion uses the deterministic `typescript-regex` frontend, not full TS AST semantics.
- Pattern detectors are tuned to explicit naming/shape cues and may under-detect in idiomatic TS code.

## Next Improvement
- Upgrade TypeScript ingestion fidelity (AST-level frontend) before broad real-repo pattern claims.

## Boundary
This page is a projection-level case-study summary and does not redefine canonical semantic contracts or authority.

