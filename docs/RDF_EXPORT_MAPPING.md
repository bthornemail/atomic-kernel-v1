# RDF Export Mapping
Status: Draft
Authority: Projection
Depends on: `docs/ONTOLOGY_NODE_SCHEMA.md`, `docs/TOPOLOGY_EDGE_SCHEMA.md`, `docs/EPISTEMIC_ASSERTION_SCHEMA.md`

Purpose: define deterministic RDF projection from canonical semantic contracts.

## Rule
Canonical truth remains in validated JSON contracts.
RDF is a projection/query surface and cannot upgrade authority.

## Export scope (v0)
Included:
- ontology-node
- topology-edge
- epistemic-assertion
- pattern-instance
- state-machine
- diagram-view

Deferred:
- asg subsets (future)

## Export envelope
- `v`: `ak.rdf_export.v0`
- `authority`: `advisory`
- `export_profile`: `core-minimal`
- `source_frame_hash`: hash string
- `namespaces`: prefix map (`ak`, `rdf`, `rdfs`)
- `triples`: deterministic ordered triple list

## Triple mapping
### ontology-node
- `ak:node/{node_id} rdf:type ak:{class}`
- `ak:node/{node_id} rdfs:label "{label}"`
- `ak:node/{node_id} ak:sourceFrameHash "{source_frame_hash}"`
- `properties` projected as `ak:prop/{key}` literal values

### topology-edge
- `ak:node/{from_id} ak:{kind} ak:node/{to_id}`
- `ak:topology/{edge_id} rdf:type ak:TopologyEdge`
- `ak:topology/{edge_id} ak:from ak:node/{from_id}`
- `ak:topology/{edge_id} ak:to ak:node/{to_id}`
- `ak:topology/{edge_id} ak:confidence "{confidence}"`

### epistemic-assertion
- `ak:assert/{assertion_id} rdf:type ak:EpistemicAssertion`
- `ak:assert/{assertion_id} ak:asserts ak:node/{subject_id}`
- `ak:assert/{assertion_id} ak:status ak:{status}`
- `ak:assert/{assertion_id} ak:confidence "{confidence}"`
- `ak:assert/{assertion_id} ak:evidenceRef "..."` (repeat)

### pattern-instance
- `ak:pattern/{pattern_id} rdf:type ak:PatternInstance`
- `ak:pattern/{pattern_id} ak:patternType ak:{pattern_type}`
- `ak:pattern/{pattern_id} ak:subject ak:node/{subject_id}` (repeat)
- role bindings projected as `ak:role/{role}` IRI links
- evidence projected as `ak:evidenceEdge "..."` (repeat)
- constraints projected as `ak:constraintPassed "..."` (repeat)
- alternates projected as `ak:alternatePattern ak:{pattern_type}` (repeat)

### state-machine
- `ak:machine/{machine_id} rdf:type ak:StateMachine`
- `ak:machine/{machine_id} ak:machineKind ak:BehavioralMachine|ak:ProtocolMachine`
- `ak:machine/{machine_id} ak:hasRegion ak:region/{machine_id}/{region_id}`
- `ak:region/{machine_id}/{region_id} ak:hasState ak:state/{machine_id}/{state_id}`
- `ak:machine/{machine_id} ak:hasTransition ak:transition/{machine_id}/{transition_id}`
- `ak:transition/{machine_id}/{transition_id} ak:sourceState ak:state/{machine_id}/{source_state_id}`
- `ak:transition/{machine_id}/{transition_id} ak:targetState ak:state/{machine_id}/{target_state_id}` (if target exists)
- `ak:transition/{machine_id}/{transition_id} ak:trigger "{event}"`
- `ak:transition/{machine_id}/{transition_id} ak:hasGuard "true|false"`
- `ak:transition/{machine_id}/{transition_id} ak:hasAction "true|false"`

### diagram-view
- `ak:diagram/{view_id} rdf:type ak:DiagramView`
- `ak:diagram/{view_id} ak:viewType ak:{view_type}`
- `ak:diagram/{view_id} ak:hasElement ak:diagram/{view_id}/element/{element_id}`
- `ak:diagram/{view_id} ak:hasRelation ak:diagram/{view_id}/relation/{relation_id}`
- `ak:diagram/{view_id}/element/{element_id} ak:elementKind ak:{kind}`
- `ak:diagram/{view_id}/relation/{relation_id} ak:relationKind ak:{kind}`
- element refs are projected by `ref_kind` (`ak:refNode`, `ak:refState`, `ak:refRegion`, `ak:refPattern`)

## Determinism rules
- Fixed input set + exporter version => byte-stable envelope and Turtle output.
- Triples sorted lexicographically by `(s, p, o, o_kind)`.
- Unknown keys in export envelope fail closed.

## Boundary
RDF export is a projection layer for query/interoperability and does not redefine canonical semantic contracts.
