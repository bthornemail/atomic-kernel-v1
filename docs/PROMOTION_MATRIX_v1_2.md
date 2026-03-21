# Promotion Matrix v1.2

Status: Advisory
Authority: Extension
Depends on: `docs/FORK_IMPORT_INDEX_v1_2.md`, `docs/TRACEABILITY_DIFF_v1_2.md`, `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json`, `docs/imports/folder1-v1_2/LIFECYCLE_REGISTRY.v0.json`

Purpose: assign promotion intent and conflict posture for all imported fork docs.

## Matrix

| File | Class | Target Canonical Location | Conflicts | Promotion Decision |
| --- | --- | --- | --- | --- |
| `ATOMIC_KERNEL_NORMATIVE_CORE_v1_2.md` | `normative-candidate` | `docs/ATOMIC_KERNEL_NORMATIVE_CORE_v1_2.md` | potential overlap with existing architecture/kernel policy docs | `defer` |
| `ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md` | `normative-candidate` | `docs/ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md` | overlap reviewed; promoted as explicit v1.2 candidate surface | `merge` |
| `PURE_ALGORITHMS.md` | `normative-candidate` | `docs/PURE_ALGORITHMS.md` | terminology aligned to promoted v1.2 naming lane | `merge` |
| `ESCAPE_ACCESS_LAW.md` | `normative-candidate` | `docs/ESCAPE_ACCESS_LAW.md` | control/escape law promoted with governance boundary retained | `merge` |
| `CONTROL_PLANE_SPEC.md` | `normative-candidate` | `docs/CONTROL_PLANE_SPEC.md` | may conflict with current lane/ABI naming | `defer` |
| `WITNESS_PLANE_SPEC.md` | `normative-candidate` | `docs/WITNESS_PLANE_SPEC.md` | authority classification must remain advisory | `defer` |
| `HEADER8_CANONICAL_ALGORITHM.md` | `normative-candidate` | `docs/HEADER8_CANONICAL_ALGORITHM.md` | potential overlap with control-plane algorithm docs | `defer` |
| `ALGORITHM_A13_ESC_DEPTH_MIXED_RADIX.md` | `normative-candidate` | `docs/ALGORITHM_A13_ESC_DEPTH_MIXED_RADIX.md` | algorithm numbering may collide with existing naming | `defer` |
| `ATOMIC_KERNEL_PROOF_NOTES_v1_2.md` | `proof-candidate` | `docs/proofs/ATOMIC_KERNEL_PROOF_NOTES_v1_2.md` | proof style differences vs existing formal notes | `defer` |
| `112_PROOFS_MATRIX.md` | `proof-candidate` | `docs/proofs/112_PROOFS_MATRIX.md` | matrix references require stable dependency mapping | `defer` |
| `LAW_TO_CODE_TRACEABILITY.md` | `proof-candidate` | `docs/LAW_TO_CODE_TRACEABILITY.md` | currently mapped to prototype paths | `defer` |
| `AtomicKernelCoq.v` | `proof-candidate` | `kernel/coq/AtomicKernelImportedV1_2.v` | overlap with `kernel/coq/AtomicKernel.v` and `AtomicKernelVNext.v` | `defer` |
| `FROM_FIRST_PRINCIPLES.md` | `advisory-rationale` | `docs/rationale/FROM_FIRST_PRINCIPLES.md` | rationale-only; must not be normative by implication | `defer` |
| `CANONICAL_MULTIPLEXING.md` | `advisory-rationale` | `docs/rationale/CANONICAL_MULTIPLEXING.md` | transport rationale overlap with historical docs | `defer` |
| `MULTIFRAME_ANALYSIS.md` | `advisory-rationale` | `docs/rationale/MULTIFRAME_ANALYSIS.md` | analysis-level overlap only | `defer` |
| `ESCAPE_MANIFESTO.md` | `advisory-rationale` | `docs/rationale/ESCAPE_MANIFESTO.md` | manifesto language requires boundary guard | `defer` |

## Default Conflict Rule

- `defer` remains default until explicit promotion PR includes:
  - normalized status line,
  - dependency resolution,
  - cross-link verification,
  - conflict decision update (`merge` or `supersede`).

## Boundary

This matrix is a decision registry for promotion workflow. It does not perform promotion.

## Lifecycle State Source

Per-file lifecycle state is authoritative in:

- `docs/imports/folder1-v1_2/LIFECYCLE_REGISTRY.v0.json`
