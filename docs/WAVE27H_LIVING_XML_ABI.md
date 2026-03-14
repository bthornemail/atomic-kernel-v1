# Wave 27H - Living XML ABI

Status: frozen advisory ABI.

Version: `wave27H.living_xml_abi.v0`  
Date: `2026-03-12`

Machine-readable schema:

- `runtime/tetragrammatron/schemas/living-xml.rng`

## Contract

Living XML defines a strict control hierarchy:

- `fs` with `code="0x1C"` (root)
- `gs` with `code="0x1D"` (1+)
- `rs` with `code="0x1E"` (1+)
- `us` with `code="0x1F"` (1+, terminal text only)

Fail-closed rule: unknown structure, unknown attributes, bad code values, bad tick values, or nested `us` content must reject.

## Tick Semantics

- `tick` is optional and allowed only on `fs`.
- If absent, default tick is `1`.
- If present, valid range is `1..7`.
- Advance rule: `next = (tick % 7) + 1`.

## API

Module: `runtime/tetragrammatron/io/living_xml.py`

- `parse_living_xml(xml: str) -> dict`
- `circulation_trace(xml: str, steps: int) -> list[int]`
- `advance_living_xml(xml: str) -> str`

All functions are pure and deterministic.

## Accept Fixtures

- `runtime/tetragrammatron/fixtures/living-xml/accept/canonical.xml`
- `runtime/tetragrammatron/fixtures/living-xml/accept/default-tick.xml`

## Must-Reject Fixtures

- `runtime/tetragrammatron/fixtures/living-xml/must-reject/bad-root-code.xml`
- `runtime/tetragrammatron/fixtures/living-xml/must-reject/bad-tick.xml`
- `runtime/tetragrammatron/fixtures/living-xml/must-reject/bad-unknown-child.xml`
- `runtime/tetragrammatron/fixtures/living-xml/must-reject/bad-non-terminal-us.xml`
- `runtime/tetragrammatron/fixtures/living-xml/must-reject/bad-missing-gs.xml`

## Gate

`scripts/living-xml-gate.sh` must:

1. Validate all accept fixtures.
2. Emit deterministic report at `reports/phase27H-living-xml.json`.
3. Verify digest lock against `golden/living-xml/replay-hash`.
4. Reject all must-reject fixtures.

## Formal Invariant

For well-formed living XML `x`:

- `tick(advance(x)) = (tick(x) % 7) + 1`
- `trace(x, n) = [tick(x), tick(advance(x)), ...]` length `n`
- `parse(advance(x))` remains well-formed

For malformed `x`:

- `parse_living_xml(x)` raises `LivingXmlError`.

## Wave27J Interoperability Note (Non-Breaking)

Wave27J companion embedding is projection-only:

- living XML schema/grammar in Wave27H is unchanged;
- companion identity data is carried in separate advisory metadata/namespace blocks;
- canonical validation remains against Wave27H XML + Wave27J companion JSON contracts.
