# Applied Analysis Report

- v: `analysis-report.v0`
- authority: `advisory`
- target: `/home/main/devops/atomic-kernel`
- languages: `mjs, python`

## Summary
- files: 107
- asg_nodes: 3393
- asg_edges: 6113
- domain counts:
  - conformance: 22
  - control: 1
  - core: 84
- pattern counts:
  - Adapter: 1
  - Facade: 20

## Instances
- Adapter `pi.adapter.AtomicKernelHandler` in `dev-docs/prototype/atomic-kernel/api_server.py` confidence=0.91
- Facade `pi.facade.APITests` in `dev-docs/prototype/atomic-kernel/tests/test_v1.py` confidence=0.83
- Facade `pi.facade.AsgTests` in `runtime/atomic_kernel/tests/test_asg.py` confidence=0.83
- Facade `pi.facade.AtomicKernelHandler` in `dev-docs/prototype/atomic-kernel/api_server.py` confidence=0.83
- Facade `pi.facade.Component` in `scripts/rumsfeldian-discovery.py` confidence=0.83
- Facade `pi.facade.FanoProcess` in `runtime/atomic_kernel/fano_scheduler.py` confidence=0.83
- Facade `pi.facade.FanoScheduler` in `runtime/atomic_kernel/fano_scheduler.py` confidence=0.83
- Facade `pi.facade.IdentityOccurrenceTests` in `runtime/atomic_kernel/tests/test_identity_occurrence.py` confidence=0.83
- Facade `pi.facade.Lane16System` in `runtime/atomic_kernel/lane16.py` confidence=0.83
- Facade `pi.facade.Lane16Tests` in `runtime/atomic_kernel/tests/test_lane16.py` confidence=0.83
- Facade `pi.facade.LivingXmlTests` in `runtime/atomic_kernel/tests/test_living_xml.py` confidence=0.83
- Facade `pi.facade.ObjectChain` in `dev-docs/prototype/atomic-kernel/identity.py` confidence=0.83
- Facade `pi.facade.PatternExtractTests` in `runtime/atomic_kernel/tests/test_pattern_extract.py` confidence=0.83
- Facade `pi.facade.PublicApiTests` in `atomic_kernel/tests/test_public_api.py` confidence=0.83
- Facade `pi.facade.RepoAnalysisTests` in `runtime/atomic_kernel/tests/test_repo_analysis.py` confidence=0.83
- Facade `pi.facade.SeedAlgebraTests` in `runtime/atomic_kernel/tests/test_seed_algebra.py` confidence=0.83
- Facade `pi.facade.SeedCompanionTests` in `runtime/atomic_kernel/tests/test_seed_companion.py` confidence=0.83
- Facade `pi.facade.SemanticIdentityTests` in `runtime/atomic_kernel/tests/test_semantic_identity.py` confidence=0.83
- Facade `pi.facade.V1Tests` in `dev-docs/prototype/atomic-kernel/tests/test_v1.py` confidence=0.83
- Facade `pi.facade.VNextLaneTests` in `runtime/atomic_kernel/tests/test_vnext_lane.py` confidence=0.83
- Facade `pi.facade.WorkspaceIngestTests` in `runtime/atomic_kernel/tests/test_workspace_ingest.py` confidence=0.83

## Digests
- inputs_digest: `sha256:fb807fe29cda3df8ae74dc9b3f681adad7d7ba024fc4f6d4f2f4ed443b1fb63e`
- evidence_digest: `sha256:380991c3162716978507d5fd5f6a96beb162739ab7027bed862d063b94d7c30f`
- outputs_digest: `sha256:6cf16012b1f405fb4a499eacf71a0fdb3d5fbbaadda5f3ad925947d21876113f`
