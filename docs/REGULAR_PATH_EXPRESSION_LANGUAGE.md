# Regular Path Expression Language
Status: Draft
Authority: Extension
Depends on: `docs/ABSTRACT_SYNTAX_GRAPH_SCHEMA.md`, `docs/PATTERN_INSTANCE_SCHEMA.md`

Purpose: define a finite-state query language for recurring structural motifs over the semantic graph.

## Role
This language targets regular path recognition over typed graph walks.
It is not a full programming-language semantics replacement.

## Core syntax (v0)
- Atom: `NodeKind` or `EdgeKind`
- Concatenation: `A B`
- Alternation: `A | B`
- Kleene star: `A*`
- One-or-more: `A+`
- Optional: `A?`
- Grouping: `( ... )`
- Typed step: `NodeKind -EdgeKind-> NodeKind`

Example:
`Class -Implements-> Interface  Class -Constructs-> Product  Class -DelegatesTo-> Interface`

## Execution model
- Compile expression to NFA/DFA for path matching.
- Run against ASG edges with deterministic traversal order.
- Emit match bindings (node/edge ids) and rule id.

## Determinism rules
- Fixed graph + fixed expression + fixed engine version => same match set.
- Stable ordering for emitted match bindings.
- Reject unknown node/edge symbols.

## Intended usage
- Pattern prefilters
- Navigation constraints in diagram editors
- Validation of XML projection transforms
- Semantic search predicates

## Boundary
Regular path expressions are a recognition layer over ASG, not canonical semantic truth alone.
