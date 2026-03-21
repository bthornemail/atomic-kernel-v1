# CHIRALITY_SELECTION_LAW_v0
Status: Normative
Authority: Canonical (Pure Algorithm)
Depends on: `docs/PURE_ALGORITHMS.md`, `docs/A5_FANO_SELECTION_LAW.md`, `docs/ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md`, `docs/ESCAPE_ACCESS_LAW.md`, `docs/imports/folder1-v1_2/ALGORITHM_A13_ESC_DEPTH_MIXED_RADIX.md`, `docs/imports/folder1-v1_2/WITNESS_PLANE_SPEC.md`, `docs/imports/folder1-v1_2/112_PROOFS_MATRIX.md`

Purpose: define the canonical orientation law for partitioned candidate space.

## 0. Purpose

This law removes ambiguity in:

- branch ordering
- first selection
- traversal direction

Selection order is derived from canonical state, not representation.

## 1. Definitions

### 1.1 Candidate Set

Finite non-empty set:

`S = {x0, x1, ..., xn}`

### 1.2 Partition (A5a)

Deterministic function:

`partition(S) -> (S0, S1)`

Constraints:

- `S0 ∪ S1 = S`
- `S0 ∩ S1 = ∅`
- `|S0| ~= |S1|` where balanced split is applicable

### 1.3 Chirality Bit

`bit := kernel_bit(state, tick)`

Constraints:

- deterministic and replayable
- independent of UI/layout/declaration order
- independent of wall-clock time

## 2. Chirality Selection Law

Given:

- `(S0, S1) := partition(S)`
- `bit := kernel_bit(state, tick)`

Define orientation:

```text
if bit = 0:
  ordered := (S0, S1)
else:
  ordered := (S1, S0)
```

Define canonical selection:

`next(S) := first(ordered)`

## 3. Invariants (Mandatory)

### 3.1 Determinism

`same(state, tick, S) -> same(next(S))`

### 3.2 Replay Stability

Same initial state and ticks must produce identical chirality trace and winner path.

### 3.3 Label Invariance

Swapping labels (`S0/S1`) does not change canonical winner path.

### 3.4 Projection/UI Invariance

Rendering order, list order, or serialization order has zero authority on selection.

### 3.5 Static Order Rejection

Rules like always-`S0`, always-first-listed, always-low/high are non-canonical.

### 3.6 Single Activation Per Tick

Each tick yields exactly one orientation decision:

`tick_n -> one bit -> one ordered pair -> one selected subset`

### 3.7 Canonical Input Constraint

`kernel_bit` must be derived from canonical state only.

Invalid sources include:

- system clock
- UI state
- external randomness without canonical seeding

## 4. Consequences

### 4.1 Partition != Order

Partition defines structure only.
Chirality defines orientation.

### 4.2 Firstness is Derived

There is no intrinsic first subset.
Firstness is kernel-derived orientation.

### 4.3 Incidence Scheduling

Chirality induces scheduling:

- partition -> possible interactions
- chirality -> active interaction

Applies to animate and inanimate entities.

### 4.4 Temporal Interpretation

- future = unselected branches
- present = selected branch
- past = previously selected branches

## 5. Reference Algorithm (Canonical)

```text
function chirality_select(state, tick, S):
    (S0, S1) = partition(S)
    bit = kernel_bit(state, tick)

    if bit == 0:
        return S0
    else:
        return S1
```

## 6. Reject Conditions (Fail-Closed)

- non-deterministic partition
- non-replayable `kernel_bit`
- selection influenced by representation order
- multi-activation within one tick

## 7. Relation to Other Laws

- A5 (Fano Selection):
  - A5a = Partition
  - A5b = Chirality (this document)
- A13:
  - defines extension-depth coordinate behavior
  - chirality defines traversal orientation through partitioned extension space
- Escape Access Law:
  - defines entry/scope/return
  - chirality defines ordered traversal within escaped partitioned regions

## 8. Authority Statement

This document is normative and algorithm-first.

Any implementation violating these invariants is non-conforming.

Formal proof systems (for example Coq) are advisory witnesses unless explicitly promoted.

## 9. Summary

Chirality turns partition into order.
Order turns incidence into schedule.
Schedule governs interaction under replay law.
