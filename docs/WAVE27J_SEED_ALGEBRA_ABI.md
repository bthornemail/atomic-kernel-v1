# Wave 27J Seed Algebra ABI

Status: frozen advisory contract.
Version: `wave27J.seed_algebra.v0`
Date: `2026-03-12`

## 1. Purpose

Defines deterministic 7-bit seed closure algebra used to derive self-defined headers and stable semantic classes.

## 2. Domain

- Seeds: integers in `0..127` (`{0,1}^7`)
- Ring topology: cyclic 7-bit neighborhood

## 3. Normative Operations

- `step_closure(seed)`:
  - `left = ((seed << 1) | (seed >> 6)) & 0x7f`
  - `right = ((seed >> 1) | ((seed & 1) << 6)) & 0x7f`
  - result: `seed | left | right`
- `closure_fixpoint(seed)`: iterated `step_closure` until stable
- `phase(seed)`: `popcount(closure_fixpoint(seed)) mod 7`, with `0 -> 7`
- `compose_xor(a,b) = a ^ b`
- `compose_and(a,b) = a & b`
- `shared_phase(a,b) = phase(a & b)`

All operations must be deterministic and fail-closed for out-of-range inputs.

## 4. Seed Entity

Canonical entity:

- `v` = `wave27J.seed_algebra.v0`
- `seed` (0..127)
- `header` = `closure_fixpoint(seed)`
- `phase` = phase from header
- `type` (SID domain)
- `canonical` = 7-bit header binary string
- `sid` = typed SID over canonical header

Validation must reject any mismatch among these fields.

## 5. Determinism Invariant

`invariant_digest` is computed from `shared_phase(a,b)` over all seed pairs `a,b in [0..127]`.

Digest must be byte-stable across reruns.

## 6. Gate Requirements

`bash scripts/seed-algebra-gate.sh` must validate:

1. accept corpus (`seed-basic`, `closure`, `phase`, `composition`, `entity`, `invariant`)
2. must-reject corpus (invalid seed/op/entity/clock projection)
3. deterministic report lock at `golden/seed-algebra/replay-hash`

Report path:
- `reports/phase27J-seed-algebra.json`

## 7. Companion JSON Contract (Normative)

Wave27J defines a normative companion object that binds seed-derived SID to occurrence context.

Required keys (strict keyset):

- `v` (`wave27J.seed_companion.v0`)
- `authority` (`advisory`)
- `seed` (`0..127`)
- `header` (`closure_fixpoint(seed)`)
- `phase` (`phase_from_header(header)`)
- `type` (SID domain)
- `sid` (`sha256:<64-hex>`)
- `clock` (`frame/tick/control` in Wave27I bounds)
- `oid` (`sha256(clock:sid:prev_oid_or_null)`)
- `prev_oid` (`sha256:<64-hex>` or `null`)
- `next_oid` (`sha256:<64-hex>` or `null`)
- `links` (`{derived_from: [sha256...], references: [sha256...]}`)

Canonical truth is the JSON companion object.

## 8. XML Companion Embedding (Projection-Only)

Wave27J supports optional XML embedding for consumers via namespace
`urn:tetragrammatron:seed-companion:v1`.

Rules:

- XML companion blocks are non-normative projection artifacts.
- They must be reconstructible from normative companion JSON.
- Wave27H living XML schema remains unchanged.
- Validation authority remains the companion JSON + Wave27I/Wave27J gates.
