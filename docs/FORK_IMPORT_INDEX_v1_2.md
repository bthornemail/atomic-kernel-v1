# Fork Import Index v1.2

Status: Advisory
Authority: Extension
Depends on: `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json`, `docs/imports/folder1-v1_2/LIFECYCLE_REGISTRY.v0.json`, `docs/TRACEABILITY_DIFF_v1_2.md`, `docs/PROMOTION_MATRIX_v1_2.md`, `docs/PROMOTION_ANALYSIS_v1_2.md`

Purpose: index the full Folder 1 fork import set with explicit class boundaries and promotion precedence.

## Precedence Policy

- Existing canonical docs in `docs/` and `kernel/coq/` remain authoritative until explicit promotion PR.
- Imported files in `docs/imports/folder1-v1_2/` are candidate authority only.
- Imported docs must not be treated as canonical by index implication.

## Import Root

- `docs/imports/folder1-v1_2/`
- Manifest: `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json`
- Lifecycle State Source: `docs/imports/folder1-v1_2/LIFECYCLE_REGISTRY.v0.json`

## Imported Files (First Pass)

| File | Class | Import Digest Source | Intended Destination (if promoted) |
| --- | --- | --- | --- |
| `112_PROOFS_MATRIX.md` | `proof-candidate` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/proofs/112_PROOFS_MATRIX.md` |
| `ALGORITHM_A13_ESC_DEPTH_MIXED_RADIX.md` | `normative-candidate` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/ALGORITHM_A13_ESC_DEPTH_MIXED_RADIX.md` |
| `ATOMIC_KERNEL_NORMATIVE_CORE_v1_2.md` | `normative-candidate` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/ATOMIC_KERNEL_NORMATIVE_CORE_v1_2.md` |
| `ATOMIC_KERNEL_PROOF_NOTES_v1_2.md` | `proof-candidate` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/proofs/ATOMIC_KERNEL_PROOF_NOTES_v1_2.md` |
| `ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md` | `normative-candidate` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md` |
| `AtomicKernelCoq.v` | `proof-candidate` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `kernel/coq/AtomicKernelImportedV1_2.v` |
| `CANONICAL_MULTIPLEXING.md` | `advisory-rationale` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/rationale/CANONICAL_MULTIPLEXING.md` |
| `CONTROL_PLANE_SPEC.md` | `normative-candidate` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/CONTROL_PLANE_SPEC.md` |
| `ESCAPE_ACCESS_LAW.md` | `normative-candidate` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/ESCAPE_ACCESS_LAW.md` |
| `ESCAPE_MANIFESTO.md` | `advisory-rationale` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/rationale/ESCAPE_MANIFESTO.md` |
| `FROM_FIRST_PRINCIPLES.md` | `advisory-rationale` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/rationale/FROM_FIRST_PRINCIPLES.md` |
| `HEADER8_CANONICAL_ALGORITHM.md` | `normative-candidate` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/HEADER8_CANONICAL_ALGORITHM.md` |
| `LAW_TO_CODE_TRACEABILITY.md` | `proof-candidate` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/LAW_TO_CODE_TRACEABILITY.md` |
| `MULTIFRAME_ANALYSIS.md` | `advisory-rationale` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/rationale/MULTIFRAME_ANALYSIS.md` |
| `PURE_ALGORITHMS.md` | `normative-candidate` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/PURE_ALGORITHMS.md` |
| `WITNESS_PLANE_SPEC.md` | `normative-candidate` | `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json` | `docs/WITNESS_PLANE_SPEC.md` |

## Promotion Checklist (Per Doc)

| File | Status Line Normalized | Dependencies Resolved | Cross-links Valid | Conflict Decision Recorded |
| --- | --- | --- | --- | --- |
| `all imported files` | `pending` | `pending` | `pending` | `pending` |

## Formal Pointer Note

- Imported Coq companion: `docs/imports/folder1-v1_2/AtomicKernelCoq.v`
- Existing kernel formal baseline: `kernel/coq/AtomicKernel.v`
- Existing vnext formal baseline: `kernel/coq/AtomicKernelVNext.v`

## Boundary

This index does not promote imported docs to canonical authority.
It records classification, provenance, and promotion workflow only.

## Related Analysis

- `docs/PROMOTION_ANALYSIS_v1_2.md` (recommendation-only promotion sequencing)
- `docs/ARTIFACT_LIFECYCLE_v0.md` (normative transition law)
