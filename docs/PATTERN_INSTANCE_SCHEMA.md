# Pattern Instance Schema
Status: Draft
Authority: Extension
Depends on: `docs/ABSTRACT_SYNTAX_GRAPH_SCHEMA.md`, `docs/STATUS.md`

Purpose: represent inferred design-pattern matches with evidence and confidence.

## Role
Pattern inference is not binary truth by default. Each match must carry explicit evidence.

## Object
### PatternInstance
- `v`: schema version (`ak.pattern.instance.v0`)
- `authority`: `advisory`
- `pattern_type`: one of `Adapter|Facade|Strategy|Observer|Builder|...`
- `subject_nodes`: list of node ids from ASG
- `role_bindings`: map from semantic role to node id (`adapter`, `target_interface`, ...)
- `evidence_edges`: list of edge ids from ASG
- `constraints_passed`: list of satisfied rule ids
- `confidence`: float in `[0.0, 1.0]`
- `alternates`: optional list of competing pattern interpretations
- `source_frame_hash`: `graph_hash` of the ASG frame used

## Inference rules (v0)
- Rules are graph-shape + constraints.
- A match must include at least one node and one evidence edge.
- `confidence` must be deterministic for fixed inputs and rule version.
- Conflicting matches are allowed but must be explicit in `alternates`.

## Minimal detectors for first implementation
- Adapter
- Facade
- Strategy
- Observer
- Builder

## Boundary
Pattern instances are derived advisory artifacts and cannot upgrade authority over ASG truth.
