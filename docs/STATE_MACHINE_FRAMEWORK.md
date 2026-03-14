# State Machine Framework
Status: Draft
Authority: Extension
Depends on: `docs/ABSTRACT_SYNTAX_GRAPH_SCHEMA.md`, `docs/UML_PROJECTION_CONTRACT.md`, `docs/WAVE27H_LIVING_XML_ABI.md`

Purpose: define a canonical hierarchical extended-state-machine layer mapped onto the 4-channel runtime.

## 1. Scope
This framework defines:
- Behavioral machines (runtime behavior/replay).
- Protocol machines (allowed interaction sequences/contracts).
- Deterministic run-to-completion execution.
- Projection boundaries into XML/UML views.

This framework does not attempt full UML semantic coverage in v0.

## 2. Behavioral vs Protocol Machines
### Behavioral machine
- Models actual event-driven behavior of a subsystem.
- Produces deterministic state/configuration changes and effects.

### Protocol machine
- Models legal/illegal interaction sequences.
- Used for validation/conformance gates and API contract checking.

Both machine kinds share one canonical representation and differ by `machine_kind`.

## 3. Canonical Machine Model (v0)
### Machine
- `v`: `ak.state_machine.v0`
- `authority`: `advisory`
- `machine_id`: stable id
- `machine_kind`: `behavioral|protocol`
- `root_region`: region id
- `regions`: list of `Region`
- `states`: list of `State`
- `transitions`: list of `Transition`
- `extended_state_schema`: deterministic variable schema
- `source_frame_hash`: ASG `graph_hash` (when derived)

### Region
- `id`
- `parent_state_id` (nullable for root)
- `orthogonal_index` (integer)

### State
- `id`
- `name`
- `region_id`
- `state_kind`: `simple|composite|final`
- `entry_actions`: action refs
- `exit_actions`: action refs
- `internal_transitions`: transition ids

### Transition
- `id`
- `source_state_id`
- `target_state_id` (nullable for internal-only)
- `event`
- `guard`
- `actions`
- `priority`

## 4. 4-Channel Runtime Mapping
- `FS`: machine/frame boundary (`Machine` root and machine-level delimiters)
- `GS`: region/composite grouping (nested or orthogonal partitions)
- `RS`: state/transition record
- `US`: atomic event/guard/action clause

This mapping defines a hierarchical control grammar, not a new authority source.

## 5. Run-To-Completion (RTC) Law
Given one input event:
1. Resolve active configuration.
2. Select enabled transition(s) deterministically.
3. Execute exit actions for exited states.
4. Execute transition actions.
5. Execute entry actions for entered states.
6. Emit resulting configuration + deterministic outputs.

One RTC step must complete before the next event is processed.

Determinism rule:
- Fixed machine + fixed extended state + fixed event => fixed RTC result.

## 6. Extended State and Guard Law
- Extended state stores quantitative/context variables without exploding topological states.
- Guards must be side-effect-free predicates.
- Guard evaluation order must be deterministic and explicitly specified.
- Guard expression failures are fail-closed.

## 7. Entry / Exit / Internal Semantics
- `entry_actions`: run only when entering state topology.
- `exit_actions`: run only when leaving state topology.
- `internal_transitions`: event handling without state topology change.

Action execution order is deterministic and stable by declared ordering.

## 8. Orthogonal Regions
- Regions may execute as orthogonal partitions within one machine.
- Semantically, orthogonal regions are machine-level model constructs.
- Execution projection may map to lane groups (e.g., Wave27K), but lane execution is not required by this framework.

## 9. XML Projection
- Machines can be projected to XML using FS/GS/RS/US hierarchy.
- XML is projection/interchange only; canonical truth remains the machine model.
- XML edits must produce validated machine deltas before acceptance.

## 10. UML Projection Boundary
- UML diagrams are projections over canonical machine model.
- Diagram layout/style metadata is non-authoritative.
- Structural edits round-trip through validated transforms:
  - UML edit -> machine delta -> schema checks -> accept/reject.

## 11. Edit Round-Trip Rules
- No direct canonical mutation from UI state.
- Unknown keys/elements fail closed.
- All accepted edits must preserve deterministic serialization and hashability.

## 12. Initial v0 Feature Set
Included:
- Hierarchical states.
- Orthogonal regions.
- Events, guards, entry/exit/internal actions.
- Behavioral/protocol machine split.
- RTC semantics.

Deferred:
- Full UML pseudostate matrix.
- Tool-specific UML edge-case behavior.
- Broad OCL compatibility.

## Boundary
This is a draft extension contract for semantic modeling over the kernel. It does not redefine kernel law.
