# WAVE27I IDENTITY AND OCCURRENCE ABI

Status: frozen advisory contract.
Version: `wave27I.identity_occurrence_chain.v0`
Date: `2026-03-12`

## 1. Purpose

This ABI defines a constitutional split between:

- `SID`: semantic identity (`what`)
- `CLOCK`: deterministic temporal position (`when/where in traversal`)
- `OID`: occurrence identity (`one occurrence of SID at CLOCK in chain`)

## 2. Constitutional Rule

Temporal occurrence must not be encoded into semantic identity.

## 3. Definitions

### 3.1 SID

`SID = sha256(type || ":" || canonical_form)`

Properties:

- same `type` + same canonical content -> same SID
- different canonical content -> different SID
- different type -> different SID
- SID is independent of path/inode/host/wall-clock

### 3.2 CLOCK

`CLOCK = (frame, tick, control)`

Ranges:

- `frame in [0,239]`
- `tick in [1,7]`
- `control in [0,59]`

Canonical text: `frame.tick.control` with `control` uppercase hex (`42.3.1C`).

### 3.3 OID

`OID = sha256(clock_position || ":" || sid || ":" || prev_oid_or_null)`

Properties:

- chain-sensitive
- occurrence-specific
- same SID may appear multiple times in one chain

## 4. Required SID Domains

Minimum supported types:

- `living_xml`
- `memory_frame`
- `protocol_message`
- `replay_trace`

## 5. Canonicalization Law

Canonicalization must be deterministic, total for valid inputs, fail-closed for invalid inputs, and independent of path/inode/host/wall-clock.

## 6. Clock Law

Initial:

`(frame=0, tick=1, control=0)`

Advance:

1. `tick = (tick % 7) + 1`
2. if `tick == 1` then:
- `frame = (frame + 1) % 240`
- `control = (control + 1) % 60`

Nondeterministic clocks are forbidden.

## 7. Occurrence Chain Law

Occurrence fields:

- `oid`
- `sid`
- `clock`
- `prev_oid`
- `next_oid` (optional materialized)
- `type`

Invariants:

- append-only chain
- immutable `oid` and `prev_oid` once written
- linkage consistency (`prev/next` symmetry)
- exactly one tail and one head

## 8. Determinism Guarantees

- SID determinism
- CLOCK determinism
- OID determinism
- replay determinism over fixed chain

## 9. Prohibited SID Inputs

Forbidden in SID derivation:

- wall-clock timestamp
- pid/nonce/randomness
- inode/path/hostname
- env-specific temporary locations

## 10. Living XML Interaction

For `living_xml`:

- SID identifies semantic document content
- OID identifies concrete chain occurrence
- internal document tick and occurrence CLOCK are distinct

## 11. Reference Model

```python
class Clock:
    frame: int
    tick: int
    control: int

class Occurrence:
    oid: str
    sid: str
    type: str
    clock: Clock
    prev_oid: str | None
    next_oid: str | None
```

## 12. Minimum Fixture Surface

Accept:

- same content + same type -> same SID
- same SID + different clock -> different OID
- same SID + same clock + different prev_oid -> different OID
- fixed chain -> stable replay hash

Must-reject:

- invalid type
- invalid canonical content
- invalid tick/frame/control bounds
- malformed occurrence record
- broken `prev_oid` linkage

## 13. Gate Requirements

`bash scripts/identity-gate.sh` must verify:

1. SID accept corpus
2. SID must-reject corpus
3. CLOCK deterministic advancement corpus
4. OID accept corpus
5. OID must-reject corpus
6. replay hash lock

## 14. Migration Rule

`agent_memory.put()` may remain a compatibility wrapper.
Normative storage model is occurrence-based:

- `content -> SID`
- `CLOCK + SID + prev_oid -> OID`
- append occurrence
- advance CLOCK

## 15. Final Invariant

Meaning has identity.
Occurrence has time.
Replay is the chain between them.

## Wave27J Interoperability Note

Wave27J seed companions bind seed-derived SID fields to this ABI's `CLOCK`/`OID`.

- SID derivation remains temporal-free.
- OID derivation remains `clock + sid + prev_oid`.
- Companion XML blocks are advisory projection only; canonical identity/occurrence checks
  are performed on JSON artifacts through the identity and seed gates.
