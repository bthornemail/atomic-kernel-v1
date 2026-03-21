# A5 Fano Selection Law
Status: Normative
Authority: Extension
Depends on: `docs/ATOMIC_KERNEL_REDUCTION_SPEC_v1_2.md`, `docs/PURE_ALGORITHMS.md`, `docs/UNIVERSE_SPEC_v0.md`, `docs/CHIRALITY_SELECTION_LAW_v0.md`

Purpose: define deterministic, replayable ordering for Fano-style partition refinement without introducing timing/selection bias.

## Core Rule

There is no natural first partition in a Fano split.

Partition order MUST be derived from canonical kernel state for the current tick; it MUST NOT be hardcoded by label (`low/high`, `left/right`, etc.). This orientation requirement is formalized by `CHIRALITY_SELECTION_LAW_v0`.

## Scope

Applies to A5 selection/refinement behavior in Universe v0 and related bounded selection lanes.

## Deterministic Ordering Law

Given current candidate set `S` at tick `t`:

1. compute a deterministic binary partition `(S0, S1)` from `S`.
2. derive `b = kernel_bit(state_t, t)`.
3. evaluate order as:
   - `b = 0` -> `[S0, S1]`
   - `b = 1` -> `[S1, S0]`

`kernel_bit` MUST be deterministic and replay-stable for the same kernel seed/state.

## Continuous Winner (Successive Refinement)

A5 is interpreted as successive refinement of one outcome, not independent rotating draws.

At each tick:

- choose one ordered branch as the winner branch under deterministic rule.
- set `S := winner_branch` and continue.

When `|S| = 1`, remaining ticks MUST preserve that singleton deterministically.

## Forbidden Patterns

- hardcoded static ordering (`[low, high]` globally)
- label-based precedence not derived from kernel state
- nondeterministic ordering sources (clock, randomness)
- projection or UI-derived ordering authority

## Constructive Proof Target

For fixed seed and input domain, replay MUST produce byte-identical selection trace and winner.

## Falsification Proof Target

A static-order variant MUST be rejected if it can diverge from kernel-derived ordering under the same seed/domain.

## Boundary

Fano structure defines partition topology.
Kernel law defines temporal ordering authority.

A5 does not redefine kernel semantic truth.
