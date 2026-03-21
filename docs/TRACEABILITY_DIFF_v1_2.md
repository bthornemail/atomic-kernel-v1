# Traceability Diff v1.2

Status: Advisory
Authority: Extension
Depends on: `docs/imports/folder1-v1_2/LAW_TO_CODE_TRACEABILITY.md`, `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json`

Purpose: map declared fork paths to actual current `atomic-kernel` paths and record action decisions.

## Path Mapping

| Declared Path (fork) | Actual Path (current repo) | Action |
| --- | --- | --- |
| `atomic-kernel/kernel.py` | `dev-docs/prototype/atomic-kernel/kernel.py` | `update` |
| `atomic-kernel/crystal.py` | `dev-docs/prototype/atomic-kernel/crystal.py` | `update` |
| `atomic-kernel/identity.py` | `atomic_kernel/identity.py` | `update` |
| `atomic-kernel/docs/AtomicKernelCoq.v` | `kernel/coq/AtomicKernel.v` and `docs/imports/folder1-v1_2/AtomicKernelCoq.v` | `update` |
| `atomic-kernel/tests/test_all.py` | `dev-docs/prototype/atomic-kernel/tests/test_all.py` | `update` |
| `atomic-kernel/basis_spec.py` | `dev-docs/prototype/atomic-kernel/canonical.py` | `update` |
| `atomic-kernel/world.html` | `dev-docs/prototype/atomic-kernel/world.html` | `update` |
| `atomic-kernel/control_plane.py` | `dev-docs/prototype/atomic-kernel/control_plane.py` | `update` |
| `atomic-kernel/artifact_package.py` | `dev-docs/prototype/atomic-kernel/aztec_bundle.py` | `update` |
| `atomic-kernel/tools/build_artifact_package_fixture.py` | `N/A (not present in current repo)` | `defer` |
| `atomic-kernel/tools/build_artifact_package_png_fixture.mjs` | `N/A (not present in current repo)` | `defer` |
| `atomic-kernel/tests/artifact_package_payload.json` | `N/A (not present in current repo)` | `defer` |
| `atomic-kernel/tests/artifact_package_v1.json` | `N/A (not present in current repo)` | `defer` |
| `atomic-kernel/tests/artifact_package_aztec.png` | `N/A (not present in current repo)` | `defer` |
| `atomic-kernel/tests/artifact_package_aztec_png_sha256.txt` | `N/A (not present in current repo)` | `defer` |

## Notes

- `LAW_TO_CODE_TRACEABILITY.md` in import lane was normalized to current paths.
- Any future promotion to canonical docs should replace dev-docs/prototype paths with stable non-prototype paths.

## Boundary

This file is a migration aid. It does not alter kernel authority or ABI contracts.
