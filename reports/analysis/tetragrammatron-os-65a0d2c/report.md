# Applied Analysis Report

- v: `analysis-report.v0`
- authority: `advisory`
- target: `/home/main/devops/tetragrammatron-os`
- languages: `mjs`

## Summary
- files: 35
- asg_nodes: 3737
- asg_edges: 2717
- domain counts:
  - carrier: 6
  - conformance: 15
  - core: 12
  - projection: 2
- pattern counts:
  - BoundarySplit: 4
  - BridgeLayer: 4
  - CarrierLayer: 14
  - ConformanceSurface: 12
  - ProjectionOnlySurface: 2

## Instances
- BoundarySplit `pi.boundary_split.archive.tetragrammatron-os.tools.canbc.cli.mjs` in `archive/tetragrammatron-os/tools/canbc/cli.mjs` confidence=0.86
- BoundarySplit `pi.boundary_split.scripts.bench-can-vm.mjs` in `scripts/bench-can-vm.mjs` confidence=0.86
- BoundarySplit `pi.boundary_split.scripts.run-can-vm-vectors.mjs` in `scripts/run-can-vm-vectors.mjs` confidence=0.86
- BoundarySplit `pi.boundary_split.tools.canbc.cli.mjs` in `tools/canbc/cli.mjs` confidence=0.86
- BridgeLayer `pi.bridge_layer.archive.tetragrammatron-os.tools.canbc.cli.mjs` in `archive/tetragrammatron-os/tools/canbc/cli.mjs` confidence=0.82
- BridgeLayer `pi.bridge_layer.scripts.bench-can-vm.mjs` in `scripts/bench-can-vm.mjs` confidence=0.82
- BridgeLayer `pi.bridge_layer.scripts.run-can-vm-vectors.mjs` in `scripts/run-can-vm-vectors.mjs` confidence=0.82
- BridgeLayer `pi.bridge_layer.tools.canbc.cli.mjs` in `tools/canbc/cli.mjs` confidence=0.82
- CarrierLayer `pi.carrier_layer.archive.tetragrammatron-os.tests.unit.test_hw_canon.mjs` in `archive/tetragrammatron-os/tests/unit/test_hw_canon.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.archive.tetragrammatron-os.tests.unit.test_hw_project.mjs` in `archive/tetragrammatron-os/tests/unit/test_hw_project.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.archive.tetragrammatron-os.tests.unit.test_validate_jsonl.mjs` in `archive/tetragrammatron-os/tests/unit/test_validate_jsonl.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.archive.tetragrammatron-os.tools.drift_scan.mjs` in `archive/tetragrammatron-os/tools/drift_scan.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.archive.tetragrammatron-os.tools.hw_canon.mjs` in `archive/tetragrammatron-os/tools/hw_canon.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.archive.tetragrammatron-os.tools.hw_project.mjs` in `archive/tetragrammatron-os/tools/hw_project.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.archive.tetragrammatron-os.tools.validate_jsonl.mjs` in `archive/tetragrammatron-os/tools/validate_jsonl.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tests.unit.test_hw_canon.mjs` in `tests/unit/test_hw_canon.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tests.unit.test_hw_project.mjs` in `tests/unit/test_hw_project.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tests.unit.test_validate_jsonl.mjs` in `tests/unit/test_validate_jsonl.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tools.drift_scan.mjs` in `tools/drift_scan.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tools.hw_canon.mjs` in `tools/hw_canon.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tools.hw_project.mjs` in `tools/hw_project.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tools.validate_jsonl.mjs` in `tools/validate_jsonl.mjs` confidence=0.8
- ConformanceSurface `pi.conformance_surface.archive.tetragrammatron-os.tests.integration.test_pipeline.mjs` in `archive/tetragrammatron-os/tests/integration/test_pipeline.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.archive.tetragrammatron-os.tests.run_all.mjs` in `archive/tetragrammatron-os/tests/run_all.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.archive.tetragrammatron-os.tests.unit.test_gen_indexes.mjs` in `archive/tetragrammatron-os/tests/unit/test_gen_indexes.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.archive.tetragrammatron-os.tests.unit.test_hw_canon.mjs` in `archive/tetragrammatron-os/tests/unit/test_hw_canon.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.archive.tetragrammatron-os.tests.unit.test_hw_project.mjs` in `archive/tetragrammatron-os/tests/unit/test_hw_project.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.archive.tetragrammatron-os.tests.unit.test_validate_jsonl.mjs` in `archive/tetragrammatron-os/tests/unit/test_validate_jsonl.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.tests.integration.test_pipeline.mjs` in `tests/integration/test_pipeline.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.tests.run_all.mjs` in `tests/run_all.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.tests.unit.test_gen_indexes.mjs` in `tests/unit/test_gen_indexes.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.tests.unit.test_hw_canon.mjs` in `tests/unit/test_hw_canon.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.tests.unit.test_hw_project.mjs` in `tests/unit/test_hw_project.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.tests.unit.test_validate_jsonl.mjs` in `tests/unit/test_validate_jsonl.mjs` confidence=0.82
- ProjectionOnlySurface `pi.projection_only_surface.archive.tetragrammatron-os.trees.obsidian.plugin.esbuild.config.mjs` in `archive/tetragrammatron-os/trees/obsidian/plugin/esbuild.config.mjs` confidence=0.8
- ProjectionOnlySurface `pi.projection_only_surface.trees.obsidian.plugin.esbuild.config.mjs` in `trees/obsidian/plugin/esbuild.config.mjs` confidence=0.8

## Digests
- inputs_digest: `sha256:5be9c99840ef90a9cc4c7a649263bcceb290c8e77b027a8ea776a82b0be124a5`
- evidence_digest: `sha256:192459cf9ecd6fcb3480a43684e862ead3d825fc9d014f7b19b0ded0bdc54514`
- outputs_digest: `sha256:4fc1d2f28c427dd62ae772d48c278bfe76861707de7a453342d09c7b07bbf6fb`
