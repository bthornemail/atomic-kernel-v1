# Ontology Node Schema
Status: Draft
Authority: Extension
Depends on: `docs/ABSTRACT_SYNTAX_GRAPH_SCHEMA.md`, `docs/TOPOLOGY_EDGE_SCHEMA.md`

Purpose: define canonical ontology node classes for semantic topology.

## Role
Ontology nodes define what kinds of semantic entities exist in the topology.

## OntologyNode object (v0)
- `v`: `ak.ontology_node.v0`
- `authority`: `advisory`
- `node_id`: stable id
- `class`: ontology class
- `label`: human-readable label
- `properties`: class-specific key/value map
- `source_frame_hash`: canonical source hash

## Ontology classes (v0)
- `GraphFrame`
- `Node`
- `Edge`
- `Machine`
- `Region`
- `State`
- `Transition`
- `PatternInstance`
- `DiagramView`
- `EpistemicAssertion`
- `TopologyEdge`

## Determinism and fail-closed rules
- Unknown classes fail closed.
- Unknown top-level keys fail closed.
- `properties` must be deterministic JSON object values.

## Machine-readable schema
- `runtime/atomic_kernel/schemas/ontology-node.v0.schema.json`

## Boundary
Ontology nodes are extension-layer semantic vocabulary and do not redefine kernel law.
