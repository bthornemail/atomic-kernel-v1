# Promotion Analysis v1.2

Status: Advisory
Authority: Extension
Depends on: `docs/FORK_IMPORT_INDEX_v1_2.md`, `docs/PROMOTION_MATRIX_v1_2.md`, `docs/TRACEABILITY_DIFF_v1_2.md`, `docs/imports/folder1-v1_2/IMPORT_MANIFEST.json`, `docs/imports/folder1-v1_2/LIFECYCLE_REGISTRY.v0.json`

Purpose: provide decision-ready promotion guidance for each imported fork document without changing canonical authority.

## Decision Rules

- Existing canonical docs remain authoritative until explicit promotion PR is merged.
- Promotion recommendation is classification guidance, not promotion execution.
- Any recommendation requiring semantic conflict resolution remains `defer`.

## Recommendation Legend

- `merge-first`: strong candidate to integrate after normalization.
- `split-merge`: integrate by splitting normative core from rationale/examples.
- `proof-merge`: merge into proof/formal surfaces after dependency cleanup.
- `keep-advisory`: keep as rationale/advisory only.
- `defer`: postpone until conflicts or code-path alignment are resolved.

## File-by-File Recommendations

| File | Class | Recommendation | Why | Blocking Items | Suggested Target |
| --- | --- | --- | --- | --- | --- |
| `ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md` | `normative-candidate` | `merge-first` | Closest to kernel-law anchor and deterministic reduction core | reconcile overlaps with existing spec wording and ABI terms | `docs/ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md` |
| `PURE_ALGORITHMS.md` | `normative-candidate` | `merge-first` | Provides executable algorithm condensation | align terminology with current public API names | `docs/PURE_ALGORITHMS.md` |
| `ESCAPE_ACCESS_LAW.md` | `normative-candidate` | `merge-first` | Strong bounded intervention law with fail-closed posture | confirm no authority escalation in projection language | `docs/ESCAPE_ACCESS_LAW.md` |
| `CONTROL_PLANE_SPEC.md` | `normative-candidate` | `split-merge` | Valuable control-plane law, broad scope | split normative wire law from historical/rationale narrative | `docs/CONTROL_PLANE_SPEC.md` |
| `HEADER8_CANONICAL_ALGORITHM.md` | `normative-candidate` | `merge-first` | Canonical micro-unit representation candidate | naming collision check with existing algorithm surfaces | `docs/HEADER8_CANONICAL_ALGORITHM.md` |
| `ALGORITHM_A13_ESC_DEPTH_MIXED_RADIX.md` | `normative-candidate` | `merge-first` | Clear extension-depth algorithm candidate | verify numbering namespace and references | `docs/ALGORITHM_A13_ESC_DEPTH_MIXED_RADIX.md` |
| `WITNESS_PLANE_SPEC.md` | `normative-candidate` | `split-merge` | High-value governance/witness model | split governance law from optional narrative hooks | `docs/WITNESS_PLANE_SPEC.md` |
| `ATOMIC_KERNEL_NORMATIVE_CORE_v1_2.md` | `normative-candidate` | `defer` | Broad synthesis doc likely to conflict with promoted components | promote underlying component specs first | `docs/ATOMIC_KERNEL_NORMATIVE_CORE_v1_2.md` |
| `ATOMIC_KERNEL_PROOF_NOTES_v1_2.md` | `proof-candidate` | `proof-merge` | Useful proof scaffold for promoted normative docs | bind all claims to stable promoted targets | `docs/proofs/ATOMIC_KERNEL_PROOF_NOTES_v1_2.md` |
| `112_PROOFS_MATRIX.md` | `proof-candidate` | `proof-merge` | Defines verification program coverage | dependency map must reference promoted/non-prototype paths | `docs/proofs/112_PROOFS_MATRIX.md` |
| `LAW_TO_CODE_TRACEABILITY.md` | `proof-candidate` | `defer` | Critical bridge doc, currently prototype-heavy | replace `dev-docs/prototype/...` mappings with stable code paths | `docs/LAW_TO_CODE_TRACEABILITY.md` |
| `AtomicKernelCoq.v` | `proof-candidate` | `proof-merge` | Formal companion already import-lane checked | resolve overlap with `kernel/coq/AtomicKernel.v` and `AtomicKernelVNext.v` by naming and theorem scope | `kernel/coq/AtomicKernelImportedV1_2.v` |
| `FROM_FIRST_PRINCIPLES.md` | `advisory-rationale` | `keep-advisory` | Design rationale, not canonical law | none | `docs/rationale/FROM_FIRST_PRINCIPLES.md` |
| `CANONICAL_MULTIPLEXING.md` | `advisory-rationale` | `keep-advisory` | Historical and conceptual multiplex rationale | none | `docs/rationale/CANONICAL_MULTIPLEXING.md` |
| `MULTIFRAME_ANALYSIS.md` | `advisory-rationale` | `keep-advisory` | Analytical context for framing/reconstruction tradeoffs | none | `docs/rationale/MULTIFRAME_ANALYSIS.md` |
| `ESCAPE_MANIFESTO.md` | `advisory-rationale` | `keep-advisory` | Manifesto framing; useful context, not normative | none | `docs/rationale/ESCAPE_MANIFESTO.md` |

## Recommended Promotion Order (Phased)

1. **Phase 1 (kernel law anchors)**
   - `ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md`
   - `PURE_ALGORITHMS.md`
   - `ESCAPE_ACCESS_LAW.md`

2. **Phase 2 (algorithm/control extensions)**
   - `HEADER8_CANONICAL_ALGORITHM.md`
   - `ALGORITHM_A13_ESC_DEPTH_MIXED_RADIX.md`
   - `CONTROL_PLANE_SPEC.md` (split normative subset first)

3. **Phase 3 (governance + proof)**
   - `WITNESS_PLANE_SPEC.md` (split normative subset first)
   - `ATOMIC_KERNEL_PROOF_NOTES_v1_2.md`
   - `112_PROOFS_MATRIX.md`
   - `AtomicKernelCoq.v`

4. **Phase 4 (traceability stabilization)**
   - `LAW_TO_CODE_TRACEABILITY.md` only after non-prototype mapping is complete

5. **Hold**
   - `ATOMIC_KERNEL_NORMATIVE_CORE_v1_2.md` until component docs are promoted
   - advisory rationale docs remain non-authoritative

## Promotion Gate Checklist (Per PR)

- status line normalized (`Status`, `Authority`, `Depends on`)
- conflict decision recorded (`merge` or `supersede`)
- cross-links valid
- no imported candidate file added to canonical index implicitly
- fail-closed checks pass:
  - `./scripts/fork-import-v1_2-gate.sh`
  - `./scripts/release-gate.sh`

## Boundary

This analysis is recommendation-only and does not alter canonical authority.

## Lifecycle State Source

This analysis is advisory. Authoritative lifecycle state is tracked in:

- `docs/imports/folder1-v1_2/LIFECYCLE_REGISTRY.v0.json`
