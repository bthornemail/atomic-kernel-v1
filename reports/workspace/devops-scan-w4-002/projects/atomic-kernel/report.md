# Applied Analysis Report

- v: `analysis-report.v0`
- authority: `advisory`
- target: `/home/main/devops/atomic-kernel`
- languages: `mjs, python`

## Summary
- files: 65
- asg_nodes: 2103
- asg_edges: 4088
- domain counts:
  - conformance: 13
  - core: 52
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
- inputs_digest: `sha256:589d240f59247540f6bdef855562027c9a87fd877cc5a3b0c655035b9455b232`
- evidence_digest: `sha256:3922c79c090c4c57bbb8faa06ffbd19ba5c9831e97ff3bcd94f865a145272c9c`
- outputs_digest: `sha256:17acd931c30083c5582f5fbe7b047d364b7bf89e5e99939d4cb2e42c6ae6199c`
