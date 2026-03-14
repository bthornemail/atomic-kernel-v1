# Abstract Syntax Graph Schema
Status: Draft
Authority: Extension
Depends on: `docs/STATUS.md`, `docs/KERNEL_CHANGE_POLICY.md`, `docs/WAVE27I_IDENTITY_AND_OCCURRENCE_ABI.md`

Purpose: define the canonical graph substrate for codepoint-backed semantic extraction.

## Role
This schema is the proposed canonical truth for semantic code analysis layers.
UML/XML/RDF are projection/search surfaces over this graph.

## Core objects
### GraphFrame
- `v`: schema version string (`ak.asg.v0`)
- `authority`: `advisory`
- `language`: source language id (`python`, `typescript`, ...)
- `namespace`: logical scope (`repo/package/module`)
- `nodes`: list of `Node`
- `edges`: list of `Edge`
- `provenance`: source metadata
- `graph_hash`: sha256 of canonical frame serialization

### Node
- `id`: stable node id
- `symbol`: codepoint-backed semantic symbol id
- `kind`: node kind (`Module`, `Class`, `Function`, `Method`, `Field`, `TypeRef`, ...)
- `attrs`: strict key/value map for kind-specific attributes
- `source`: source span reference (`path`, `line`, `column`, `end_line`, `end_column`)

### Edge
- `id`: stable edge id
- `symbol`: codepoint-backed relation symbol id
- `kind`: edge kind (`Defines`, `Calls`, `Implements`, `Constructs`, `DelegatesTo`, ...)
- `from`: node id
- `to`: node id
- `attrs`: strict key/value map

## Determinism rules
- Canonical serialization must use stable ordering of nodes/edges by `id`.
- Unknown keys are reject-on-parse.
- No wall-clock or host-specific fields in canonical graph hashes.
- Same source + same parser version => same `graph_hash`.

## Minimal node/edge vocab (v0)
- Node kinds: `Module`, `Namespace`, `Class`, `Interface`, `Function`, `Method`, `Field`, `TypeRef`, `Literal`.
- Edge kinds: `Defines`, `Imports`, `Calls`, `Implements`, `Extends`, `Constructs`, `Assigns`, `Returns`, `DelegatesTo`, `Observes`.

## Boundary
This is a draft extension contract. It does not redefine kernel transition law.
