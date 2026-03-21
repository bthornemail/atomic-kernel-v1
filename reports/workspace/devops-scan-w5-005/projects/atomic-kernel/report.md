# Applied Analysis Report

- v: `analysis-report.v0`
- authority: `advisory`
- target: `/home/main/devops/atomic-kernel`
- languages: `mjs, python`

## Summary
- files: 68
- asg_nodes: 2243
- asg_edges: 4288
- domain counts:
  - conformance: 13
  - core: 55
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
- inputs_digest: `sha256:73f96ba1896659731cea29fa0288aa3bbfa00d81031f59ae62044040957717da`
- evidence_digest: `sha256:58d9975b716bdf0bd2af16f105df2100438ea7a5ba9be42d5bde531ee5ae18d0`
- outputs_digest: `sha256:5b1cb734c4d498885c5978a1fe4088cc2f77de8312ba61f40863369acea66733`
