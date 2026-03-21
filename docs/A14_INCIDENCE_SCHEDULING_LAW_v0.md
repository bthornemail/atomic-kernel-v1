# A14 Incidence Scheduling Law v0
Status: Normative
Authority: Extension
Depends on: `docs/ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md`, `docs/PURE_ALGORITHMS.md`, `docs/A5_FANO_SELECTION_LAW.md`, `docs/CHIRALITY_SELECTION_LAW_v0.md`, `docs/ESCAPE_ACCESS_LAW.md`, `docs/imports/folder1-v1_2/WITNESS_PLANE_SPEC.md`, `docs/UNIVERSE_SPEC_v0.md`

Purpose: define canonical eligibility scheduling for incidence responses across animate and inanimate entities without leaking authority through projection, labels, or runtime convention.

## First Principle

No entity defines ordering authority.
Only canonical scheduling derived from kernel state and lawful selection defines when an incidence becomes eligible to respond.

## Core Definitions

- `canonical_tick`: replay-authoritative order frontier.
- `incidence_tick`: tick where relation becomes eligible under law.
- `proposal_state`: `pending | accepted | rejected`.
- `fano_rank`: advisory ordering metadata; never canonical authority.
- `eligibility`: lawful ability to respond at a given tick.

## Normative Rules

1. Eligibility over forcing.
Scheduling marks incidences/entities as eligible; it does not force action.

2. Kernel-derived order.
Incidence response order MUST be derived from canonical state and A5 chirality rules.

3. Label/UI non-authority.
`low/high`, `left/right`, render order, and presentation dwell MUST NOT alter canonical eligibility order.

4. Past closure.
Receipted canonical past is closed. Scheduling/projection cannot rewrite prior canonical order.

5. Future discipline.
Future states are `pending proposal` or `branch possibility` until accepted by lawful transition.

6. Escape compatibility.
Escaped scopes may widen interpretation locally, but response eligibility ordering remains kernel-derived and returns deterministically.

7. Witness boundary.
Observers/agents may inspect/propose at any time, but canonical response application occurs only when scheduled and lawfully committed.

## Animate vs Inanimate

- Inanimate entities follow deterministic scheduled eligibility and transition rules.
- Animate agents may choose behavior locally, but only scheduled eligibility allows canonical effect.

## Minimal Canonical Timing Surface

Every time-sensitive artifact SHOULD expose:

- `canonical_tick`
- `incidence_tick`
- `proposal_state`
- `fano_rank` (advisory)

If omitted, canonical scheduling cannot be audited and proof quality degrades.

## Reject Conditions

- response applied before eligibility tick
- projection/UI order changes canonical response order
- pending proposal treated as accepted canonical fact
- branch response merged without lineage/receipt
- escaped scope overriding chirality-derived order

## Proof Obligations

Constructive:
- same seed/state/log => identical eligibility schedule and response receipts.

Falsification:
- altered UI/order labels do not change canonical schedule.
- forcing unscheduled response is rejected fail-closed.

## Boundary

A14 governs response eligibility and incidence scheduling only.
It does not redefine kernel truth, proposal authority, or projection authority.
