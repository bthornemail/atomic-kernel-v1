# Applied Analysis Report

- v: `analysis-report.v0`
- authority: `advisory`
- target: `/home/main/devops/tetragrammatron-os`
- languages: `mjs, python, typescript`

## Summary
- files: 55
- asg_nodes: 2905
- asg_edges: 2824
- domain counts:
  - carrier: 3
  - conformance: 10
  - core: 14
  - projection: 28
- pattern counts:
  - BoundarySplit: 3
  - BridgeLayer: 3
  - CarrierLayer: 7
  - ConformanceSurface: 6
  - ProjectionOnlySurface: 1

## Instances
- BoundarySplit `pi.boundary_split.scripts.bench-can-vm.mjs` in `scripts/bench-can-vm.mjs` confidence=0.86
- BoundarySplit `pi.boundary_split.scripts.run-can-vm-vectors.mjs` in `scripts/run-can-vm-vectors.mjs` confidence=0.86
- BoundarySplit `pi.boundary_split.tools.canbc.cli.mjs` in `tools/canbc/cli.mjs` confidence=0.86
- BridgeLayer `pi.bridge_layer.scripts.bench-can-vm.mjs` in `scripts/bench-can-vm.mjs` confidence=0.82
- BridgeLayer `pi.bridge_layer.scripts.run-can-vm-vectors.mjs` in `scripts/run-can-vm-vectors.mjs` confidence=0.82
- BridgeLayer `pi.bridge_layer.tools.canbc.cli.mjs` in `tools/canbc/cli.mjs` confidence=0.82
- CarrierLayer `pi.carrier_layer.tests.unit.test_hw_canon.mjs` in `tests/unit/test_hw_canon.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tests.unit.test_hw_project.mjs` in `tests/unit/test_hw_project.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tests.unit.test_validate_jsonl.mjs` in `tests/unit/test_validate_jsonl.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tools.drift_scan.mjs` in `tools/drift_scan.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tools.hw_canon.mjs` in `tools/hw_canon.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tools.hw_project.mjs` in `tools/hw_project.mjs` confidence=0.8
- CarrierLayer `pi.carrier_layer.tools.validate_jsonl.mjs` in `tools/validate_jsonl.mjs` confidence=0.8
- ConformanceSurface `pi.conformance_surface.tests.integration.test_pipeline.mjs` in `tests/integration/test_pipeline.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.tests.run_all.mjs` in `tests/run_all.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.tests.unit.test_gen_indexes.mjs` in `tests/unit/test_gen_indexes.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.tests.unit.test_hw_canon.mjs` in `tests/unit/test_hw_canon.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.tests.unit.test_hw_project.mjs` in `tests/unit/test_hw_project.mjs` confidence=0.82
- ConformanceSurface `pi.conformance_surface.tests.unit.test_validate_jsonl.mjs` in `tests/unit/test_validate_jsonl.mjs` confidence=0.82
- ProjectionOnlySurface `pi.projection_only_surface.trees.obsidian.plugin.esbuild.config.mjs` in `trees/obsidian/plugin/esbuild.config.mjs` confidence=0.8

## Digests
- inputs_digest: `sha256:1faebe37b27f28a9b710218c5e885a912135370524bc4dc21514a65d3a717faa`
- evidence_digest: `sha256:a674014daa1a6c71883f2780c84ee5d61292daf209c990f65172e10793db3d25`
- outputs_digest: `sha256:8750669baf0b5dd368c8b5dd200dca1076ff252f24c150a870a0486270afe181`
