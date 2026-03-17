# RDF Query Examples
Status: Draft
Authority: Projection
Depends on: `docs/RDF_EXPORT_MAPPING.md`

Purpose: provide minimal query patterns over deterministic RDF exports.

## Notes
- RDF is projection-only.
- Canonical truth remains in validated JSON contracts.

## Example: all pattern instances
```sparql
SELECT ?pattern ?ptype
WHERE {
  ?pattern rdf:type ak:PatternInstance .
  ?pattern ak:patternType ?ptype .
}
```

## Example: inferred assertions over adapter patterns
```sparql
SELECT ?assert ?pattern
WHERE {
  ?pattern rdf:type ak:PatternInstance .
  ?pattern ak:patternType ak:Adapter .
  ?assert rdf:type ak:EpistemicAssertion .
  ?assert ak:status ak:inferred .
  ?assert ak:asserts ?node .
  ?pattern ak:subject ?node .
}
```

## Example: dependencies for a node
```sparql
SELECT ?to
WHERE {
  ak:node/n.payment_service ak:depends_on ?to .
}
```

## Example: transitions from a given state
```sparql
SELECT ?t ?trigger
WHERE {
  ?t rdf:type ak:Transition .
  ?t ak:sourceState ak:state/machine.demo.behavior/s_idle .
  ?t ak:trigger ?trigger .
}
```

## Example: diagram elements for a class view
```sparql
SELECT ?el ?kind
WHERE {
  ak:diagram/diagram.class.basic ak:hasElement ?el .
  ?el ak:elementKind ?kind .
}
```

## Boundary
Queries are read/projection surfaces and cannot upgrade authority.
