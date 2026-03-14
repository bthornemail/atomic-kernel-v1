# Diagram View Schema
Status: Draft
Authority: Projection
Depends on: `docs/ABSTRACT_SYNTAX_GRAPH_SCHEMA.md`, `docs/STATE_MACHINE_FRAMEWORK.md`, `docs/UML_PROJECTION_CONTRACT.md`

Purpose: define a canonical projection object for diagram views over ASG/state-machine truth.

## Role
A diagram is a typed projection view, not canonical semantic truth.

Canonical meaning must map to:
- ASG nodes/edges
- state-machine objects (`State`, `Transition`, `Region`)
- pattern instances (for overlays)

Layout metadata is non-authoritative.

## DiagramView (v0)
- `v`: `ak.diagram_view.v0`
- `authority`: `advisory`
- `view_id`: stable id
- `view_type`: `class|component|state`
- `source_frame_hash`: source hash for semantic substrate
- `elements`: typed visual elements
- `relations`: typed visual relations
- `layout`: optional coordinates/sizes
- `annotations`: optional overlays/notes

## Element vocabulary (v0)
- `class`
- `interface`
- `component`
- `state`
- `region`
- `note`
- `pattern_overlay`

## Relation vocabulary (v0)
- `association`
- `dependency`
- `composition`
- `transition`
- `implements`
- `extends`

## Round-trip constraints
- `ASG/Machine -> Diagram` deterministic.
- `Diagram edit -> delta` must be schema-validated.
- Unknown keys fail closed.
- Relations/annotations/layout must reference existing element ids.

## Machine-readable schema
- `runtime/atomic_kernel/schemas/diagram-view.v0.schema.json`

## Boundary
Diagram view schema governs projection objects only and cannot redefine kernel or ASG authority.
