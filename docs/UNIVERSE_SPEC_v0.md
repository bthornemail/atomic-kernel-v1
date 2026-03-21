# Universe Spec v0
Status: Normative
Authority: Extension
Depends on: `docs/ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md`, `docs/PURE_ALGORITHMS.md`, `docs/ESCAPE_ACCESS_LAW.md`, `docs/A5_FANO_SELECTION_LAW.md`, `docs/CHIRALITY_SELECTION_LAW_v0.md`, `docs/A14_INCIDENCE_SCHEDULING_LAW_v0.md`, `docs/imports/folder1-v1_2/WITNESS_PLANE_SPEC.md`, `docs/UNIVERSE_PROOF_LEDGER_v0.json`

Purpose: define a bounded canonical universe artifact and initial proof surface.

## Universe v0 Definition

A universe is a deterministic replay space:

- seeded by kernel law,
- structured by control/escape law,
- observed by witness/proposal surfaces,
- exposed by non-authoritative projections.

## Canonical Artifact Shape

`universe.v0` MUST include:

- `v`
- `authority`
- `kernel` (`n`, `C`, `x0`)
- `timeline` (`tick0`, `current_tick`)
- `planes` (`control`, `witness`, `projection`)
- `entities`
- `event_log`
- `receipts`

## Authority Boundary

- canonical kernel state and event log are authoritative.
- projection outputs are derived and non-authoritative.
- witness may propose and receipt changes; no direct canonical mutation.

## Universe Invariant Questions (Q1-Q8)

- Q1 deterministic replay identity
- Q2 lawful identity persistence across transforms
- Q3 payload/control separation
- Q4 projection faithfulness without authority escalation
- Q5 scoped intervention without replay loss
- Q6 proposal/receipt without hidden mutation
- Q7 branch/reconciliation without fragmentation
- Q8 open meaning with closed law

## Universe v0 Proof Slice

Phase 1 scope is `16` proofs:

- `8` questions × `2` proof forms (`constructive`, `falsification`)

Tracking and validation are bound to:

- `docs/UNIVERSE_PROOF_LEDGER_v0.json`
- `scripts/universe-v0-proof-slice-gate.sh`

## A5 Ordering Boundary

Fano partitioning defines structure, not temporal authority.

Selection order for partition evaluation MUST be derived from kernel state per tick and MUST NOT be hardcoded by label (`low/high`, `left/right`).

Authoritative A5 laws:

- `docs/A5_FANO_SELECTION_LAW.md`
- `docs/CHIRALITY_SELECTION_LAW_v0.md`

## Incidence Scheduling Boundary (A14)

Canonical scheduling distinguishes eligibility from action:

- scheduling defines when entities/incidences are eligible to respond,
- scheduling does not force response behavior,
- animate and inanimate responses gain canonical effect only through lawful scheduled commit.

Authoritative scheduling law:

- `docs/A14_INCIDENCE_SCHEDULING_LAW_v0.md`

## Boundary

This spec defines Universe v0 extension behavior and does not change kernel semantic authority.
