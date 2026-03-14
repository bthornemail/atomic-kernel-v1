# Wave 27H - Living XML ABI
Status: Normative
Authority: Extension
Depends on: `runtime/atomic_kernel/living_xml.py`, `runtime/atomic_kernel/schemas/living-xml.rng`, `scripts/living-xml-gate.sh`

Purpose: freeze the strict living-XML contract enforced by deterministic gate and replay-hash lock.

Version: `wave27H.living_xml_abi.v0`  
Date: `2026-03-12`

Machine-readable schema:
- `runtime/atomic_kernel/schemas/living-xml.rng`

## Contract
- root `fs` with `code="0x1C"`
- `gs` children (`code="0x1D"`) 1+
- `rs` children (`code="0x1E"`) 1+
- terminal `us` children (`code="0x1F"`) text-only 1+

Fail-closed: unknown structure/attrs/code/tick or nested terminal content rejects.

## Tick Semantics
- `tick` optional on `fs` only.
- default `tick=1`.
- valid range `1..7`.
- advance rule: `next = (tick % 7) + 1`.

## API
Module: `runtime/atomic_kernel/living_xml.py`
- `parse_living_xml(xml: str) -> dict`
- `circulation_trace(xml: str, steps: int) -> list[int]`
- `advance_living_xml(xml: str) -> str`

## Fixtures
Accept:
- `runtime/atomic_kernel/fixtures/living-xml/accept/*.xml`

Must-reject:
- `runtime/atomic_kernel/fixtures/living-xml/must-reject/*.xml`

## Gate
`scripts/living-xml-gate.sh` must validate accepts, reject must-reject corpus, emit deterministic reports, and verify replay-hash locks.

## Boundary
This ABI is derived runtime contract and does not redefine kernel law.
It cannot upgrade authority; canonical truth remains in validated canonical artifacts.
