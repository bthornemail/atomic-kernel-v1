# Wave27K ABI - 16-Lane Parallel Algebra

Status: proposed advisory contract.
Version: `wave27K.lane16.v0`
Date: `2026-03-13`
Depends on: Wave27J Seed Algebra, Wave27I Identity+Occurrence, Wave27H Living XML.

## 1. Purpose

Wave27K introduces a deterministic 16-lane execution surface. Lanes are grouped 4x4 and each lane
uses a strict 4-bit state machine. Synchronization is checked with Fano-line PCG predicates.

## 2. Lane Model

- lane indices: `0..15`
- groups: `0:[0..3]`, `1:[4..7]`, `2:[8..11]`, `3:[12..15]`
- valid lane states only:
  - `0x0` VOID
  - `0x8` NULL
  - `0xC` ACTIVE0
  - `0xD` ACTIVE1
  - `0xE` ACTIVE2
  - `0xF` ACTIVE3

Any other 4-bit value must reject.

## 3. Deterministic Operations

Module: `runtime/tetragrammatron/io/lane16.py`

- `lane_step(state) -> state`
- `lane_phase(lane_idx, state) -> 1..7`
- `lane_sid(lane_idx, state) -> sha256`
- `system_sid(states16) -> sha256`
- `encode_lane_state(lane_idx, state) -> [control codes]`
- `fano_pcg_check(group_states4, group_base_lane) -> bool`
- `lane_pair_digest(states16) -> sha256`
- `Lane16System.init(states16)`
- `Lane16System.tick()`
- `Lane16System.sync_group(group)`
- `Lane16System.sync_all()`

All functions are deterministic and fail-closed.

## 4. Identity Rules

- lane SID canonical form: `lane:<idx>:<state_bits>` with type `lane`
- system SID canonical form: `state0|state1|...|state15` with type `lane16`
- temporal fields are excluded from SID derivation.

## 5. Control-Code Projection

Control-code projection uses channel bases `FS/GS/RS/US = 0x1C/0x1D/0x1E/0x1F` with lane offset `+4*lane`.
This is a projection surface only; identity and validation remain JSON/runtime authoritative.

## 6. Fixture Corpus

Accept corpus (`runtime/tetragrammatron/fixtures/lane16/accept`):

- `lane-basic/*`
- `lane-groups/*`
- `lane-full/*`
- `lane-invariant/all-pairs.json`

Must-reject corpus (`runtime/tetragrammatron/fixtures/lane16/must-reject`):

- invalid lane index
- invalid lane state
- invalid group cardinality/sync claim
- invalid code projection inputs
- invalid system sync claim

## 7. Gate Requirements

`bash scripts/lane16-gate.sh` must:

1. validate all accept fixtures
2. reject all must-reject fixtures
3. emit deterministic report: `reports/phase27K-lane16.json`
4. verify replay hash: `golden/lane16/replay-hash`

## 8. Integration

- included by `scripts/tetragrammatron-gate.sh`
- included by closure spine as: `[7o/9] metaverse: lane16 parallel gate`
