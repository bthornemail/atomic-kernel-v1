# Law-to-Code Traceability Map
## Atomic Kernel v1.2

This map links normative laws to concrete implementation and test artifacts.

---

## 1. Kernel Evolution Law

- Law: deterministic bounded delta/replay over fixed-width state.
- Code:
  - `dev-docs/prototype/atomic-kernel/kernel.py`
  - `dev-docs/prototype/atomic-kernel/crystal.py`
  - `atomic_kernel/identity.py`
- Formal:
  - `kernel/coq/AtomicKernel.v`
  - `docs/imports/folder1-v1_2/AtomicKernelCoq.v`
- Tests:
  - `dev-docs/prototype/atomic-kernel/tests/test_all.py` (`Kernel law`, `Crystal`, `Identity`, `World`)

---

## 2. Reversible Basis Law

- Law: basis projection/interpretation is reversible for valid `basis_spec`.
- Code:
  - `dev-docs/prototype/atomic-kernel/canonical.py` (closest available basis/canonical surface in current repo)
  - `dev-docs/prototype/atomic-kernel/world.html` (`projectValue`, `interpretValue`, basis registry)
- Tests:
  - `dev-docs/prototype/atomic-kernel/tests/test_all.py` (`Basis specs` section)

---

## 3. Structural Plane Law (FS/GS/RS/US)

- Law: structural interaction is reduced to recursive selection + projection across four planes.
- Code:
  - `dev-docs/prototype/atomic-kernel/world.html`
    - `projectArtifact(node, plane)`
    - recursive navigator/context behavior
    - global plane controls (`FS`, `GS`, `RS`, `US`)
- Tests:
  - UI behavior is exercised via runtime smoke/manual workflows; non-UI invariants remain covered in `test_all.py`.

---

## 4. Scoped Interpretation Law (Escape/Control)

- Law: bounded scope push/pop with deterministic return.
- Code:
  - `dev-docs/prototype/atomic-kernel/control_plane.py`
  - `dev-docs/prototype/atomic-kernel/world.html` (`cpPushScope`, `cpPopScope`, `cpResolveBoundary`, control events)
- Tests:
  - `dev-docs/prototype/atomic-kernel/tests/test_all.py` (`Control Plane + Artifacts`, fail-closed cases)

---

## 5. Carrier Boundary Law (artifact_package.v1)

- Law: carrier is non-authoritative transport; decode/parse/verify before apply.
- Code:
  - `dev-docs/prototype/atomic-kernel/aztec_bundle.py` (current carrier/bundle surface)
  - `dev-docs/prototype/atomic-kernel/world.html` (Aztec PNG import/export + verification path)
- Fixture builders:
  - (deferred) no direct `build_artifact_package_fixture.py` path in current repo
  - (deferred) no direct `build_artifact_package_png_fixture.mjs` path in current repo
- Tests/fixtures:
  - (deferred) explicit `artifact_package_*` fixtures not present in current repo
  - `dev-docs/prototype/atomic-kernel/tests/test_all.py` (`Artifact package carrier` section)

---

## Reading Order

1. `ATOMIC_KERNEL_NORMATIVE_CORE_v1_2.md`
2. `ATOMIC_KERNEL_PROOF_NOTES_v1_2.md`
3. `ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md`
4. This traceability map for implementation linkage
