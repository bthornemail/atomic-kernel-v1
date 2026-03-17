# Semantic Contracts Index
Status: Draft
Authority: Extension
Depends on: `docs/ABSTRACT_SYNTAX_GRAPH_SCHEMA.md`, `docs/STATE_MACHINE_FRAMEWORK.md`

Purpose: define the canonical semantic contract family and shared envelope conventions.

Primary ingestion contracts:
- `ASG_INGESTION_CONTRACT.md` (Python/TypeScript/MJS)
- `MJS_ASG_INGESTION_CONTRACT.md` (MJS-specific frontend contract)
- `WORKSPACE_INGESTION_CONTRACT.md` (workspace discovery + orchestration)
- `PROJECT_PROFILE_CONTRACT.md` (project boundary profiling)
- `WORKSPACE_SUMMARY_CONTRACT.md` (workspace-level aggregation)
- `PROJECT_ANALYSIS_OVERLAY_CONTRACT.md` (project-scoped exclusion overlays)

## Contract Family
Canonical semantic contracts:
- `AbstractSyntaxGraph`
- `OntologyNode`
- `TopologyEdge`
- `EpistemicAssertion`
- `StateMachine`
- `PatternInstance`
- `DiagramView`

Projection/export contracts:
- `RdfExport`
- `ProtocolFlow`
- `XmlProjection` (advisory)
- `UmlProjection` (advisory)

## Shared Envelope Conventions
All canonical semantic contracts should include:
- `v`: versioned contract id
- `authority`: `advisory` unless explicitly promoted
- stable object identity field (for example `*_id`)
- `source_frame_hash`: 64 hex chars for provenance

Allowed contract-specific extensions are explicit; unknown keys fail closed.

## Authority Rule
Canonical semantic contracts are the truth substrate.
Projection contracts are derived and cannot upgrade authority.

## Validation Rule
Every contract must ship with:
- schema
- accept fixtures
- must-reject fixtures
- validator coverage
- gate integration

## Boundary
This index normalizes conventions and references contracts; it does not redefine kernel law.
