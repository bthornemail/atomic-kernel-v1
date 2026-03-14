# UML Projection Contract
Status: Draft
Authority: Projection
Depends on: `docs/ABSTRACT_SYNTAX_GRAPH_SCHEMA.md`, `docs/REGULAR_PATH_EXPRESSION_LANGUAGE.md`, `docs/STATUS.md`

Purpose: define how ASG truth is projected into editable UML/XML views without authority escalation.

## Projection model
- Canonical truth: ASG frame (`GraphFrame`).
- Projection output: UML view model serialized to XML/JSON.
- Edits: transformed back into ASG deltas through validated rules.

## Required view types (v0)
- Class diagram projection
- Component/dependency projection
- Sequence-like interaction projection (subset)

## Round-trip rules
- `ASG -> UML` must be deterministic.
- `UML edit -> ASG delta` must be validated against:
  - ASG schema
  - path expression constraints (where configured)
  - authority boundary (projection cannot mutate canonical state directly)
- Invalid edit transforms fail closed.

## Minimal projection object
### DiagramView
- `v`: schema version (`ak.uml.projection.v0`)
- `authority`: `advisory`
- `source_frame_hash`: ASG `graph_hash`
- `view_type`: `class|component|sequence_subset`
- `elements`: projected UML elements
- `relations`: projected UML relations
- `layout`: optional non-authoritative coordinates

## Authority rules
- Diagram coordinates/styles are non-authoritative.
- Semantic structure must map back to ASG node/edge symbols.
- No direct canonical mutation from UI state.

## Boundary
UML/XML are projection/interchange surfaces and cannot redefine kernel or ASG authority.
