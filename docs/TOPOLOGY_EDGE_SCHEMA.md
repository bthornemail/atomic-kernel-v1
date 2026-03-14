# Topology Edge Schema
Status: Draft
Authority: Extension
Depends on: `docs/ABSTRACT_SYNTAX_GRAPH_SCHEMA.md`, `docs/STATE_MACHINE_FRAMEWORK.md`, `docs/EPISTEMIC_ASSERTION_SCHEMA.md`

Purpose: formalize topology relations between canonical semantic objects.

## Role
Topology edges encode how semantic objects connect, derive, project, refine, and transition.

## TopologyEdge object (v0)
- `v`: `ak.topology_edge.v0`
- `authority`: `advisory`
- `edge_id`: stable id
- `kind`: relation kind
- `from_kind`: typed source category
- `from_id`: source object id
- `to_kind`: typed target category
- `to_id`: target object id
- `source_frame_hash`: canonical source hash
- `confidence`: numeric in `[0.0, 1.0]`
- `evidence_refs`: optional evidence references

## Relation kinds (v0)
- `contains`
- `refines`
- `derives_from`
- `projects_to`
- `transitions_to`
- `equivalent_to`
- `depends_on`
- `delegates_to`
- `implements`

## Determinism and fail-closed rules
- Unknown relation kinds fail closed.
- Unknown object kinds fail closed.
- Confidence outside `[0.0, 1.0]` fails closed.
- Unknown keys fail closed.

## Machine-readable schema
- `runtime/atomic_kernel/schemas/topology-edge.v0.schema.json`

## Boundary
Topology edges are extension-layer metadata and do not redefine kernel law.
