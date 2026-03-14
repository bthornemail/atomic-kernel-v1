# Epistemic Assertion Schema
Status: Draft
Authority: Extension
Depends on: `docs/ABSTRACT_SYNTAX_GRAPH_SCHEMA.md`, `docs/PATTERN_INSTANCE_SCHEMA.md`, `docs/DIAGRAM_VIEW_SCHEMA.md`

Purpose: encode how a claim is known (observed, inferred, validated, projected, rejected) with confidence and evidence references.

## Assertion object (v0)
- `v`: `ak.epistemic_assertion.v0`
- `authority`: `advisory`
- `assertion_id`: stable id
- `subject_kind`: `node|edge|state|transition|pattern|diagram_element|diagram_relation`
- `subject_id`: referenced object id
- `status`: `observed|inferred|validated|projected|rejected`
- `confidence`: numeric in `[0.0, 1.0]`
- `evidence_refs`: non-empty list of evidence ids
- `source_frame_hash`: canonical source hash
- `rationale`: short explanation
- `constraints`: optional list of rule ids

## Determinism and fail-closed rules
- Unknown keys fail closed.
- Assertions without evidence fail closed.
- Invalid status/subject enums fail closed.
- Confidence outside `[0.0, 1.0]` fails closed.

## Machine-readable schema
- `runtime/atomic_kernel/schemas/epistemic-assertion.v0.schema.json`

## Boundary
Epistemic assertions are an extension-layer contract and do not redefine kernel law.
