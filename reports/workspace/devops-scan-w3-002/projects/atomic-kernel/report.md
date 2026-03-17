# Applied Analysis Report

- v: `analysis-report.v0`
- authority: `advisory`
- target: `/home/main/devops/atomic-kernel`
- languages: `mjs, python`

## Summary
- files: 64
- asg_nodes: 2058
- asg_edges: 4004
- domain counts:
  - conformance: 13
  - core: 51
- pattern counts:
  - Facade: 15

## Instances
- Facade `pi.facade.AsgTests` in `runtime/atomic_kernel/tests/test_asg.py` confidence=0.83
- Facade `pi.facade.Component` in `scripts/rumsfeldian-discovery.py` confidence=0.83
- Facade `pi.facade.FanoProcess` in `runtime/atomic_kernel/fano_scheduler.py` confidence=0.83
- Facade `pi.facade.FanoScheduler` in `runtime/atomic_kernel/fano_scheduler.py` confidence=0.83
- Facade `pi.facade.IdentityOccurrenceTests` in `runtime/atomic_kernel/tests/test_identity_occurrence.py` confidence=0.83
- Facade `pi.facade.Lane16System` in `runtime/atomic_kernel/lane16.py` confidence=0.83
- Facade `pi.facade.Lane16Tests` in `runtime/atomic_kernel/tests/test_lane16.py` confidence=0.83
- Facade `pi.facade.LivingXmlTests` in `runtime/atomic_kernel/tests/test_living_xml.py` confidence=0.83
- Facade `pi.facade.PatternExtractTests` in `runtime/atomic_kernel/tests/test_pattern_extract.py` confidence=0.83
- Facade `pi.facade.PublicApiTests` in `atomic_kernel/tests/test_public_api.py` confidence=0.83
- Facade `pi.facade.RepoAnalysisTests` in `runtime/atomic_kernel/tests/test_repo_analysis.py` confidence=0.83
- Facade `pi.facade.SeedAlgebraTests` in `runtime/atomic_kernel/tests/test_seed_algebra.py` confidence=0.83
- Facade `pi.facade.SeedCompanionTests` in `runtime/atomic_kernel/tests/test_seed_companion.py` confidence=0.83
- Facade `pi.facade.SemanticIdentityTests` in `runtime/atomic_kernel/tests/test_semantic_identity.py` confidence=0.83
- Facade `pi.facade.WorkspaceIngestTests` in `runtime/atomic_kernel/tests/test_workspace_ingest.py` confidence=0.83

## Digests
- inputs_digest: `sha256:66fc3bc64b6cb9e997699a9eb992eee02489bc5047b35ed46608b19c6b5867b9`
- evidence_digest: `sha256:146a1d7f0eb0f540c9fd0e7eba1b7bb401d612e65594f42a65545abadf40deb8`
- outputs_digest: `sha256:7346f940a4f64e88862fcafbb253c172eb56ee918f9b4e731160d0f47370bcc3`
