# Onboarding Checklist
Status: Advisory
Authority: Extension
Depends on: `README.md`, `docs/STATUS.md`, `docs/KERNEL_CHANGE_POLICY.md`, `scripts/release-gate.sh`

Purpose: provide a deterministic onboarding path for new contributors and integrators.

## Day 1 checklist
- Read `README.md`.
- Read `docs/STATUS.md`.
- Read `docs/KERNEL_CHANGE_POLICY.md`.
- Run `./scripts/release-gate.sh`.

## Day 2 checklist
- Read `docs/INDEX.md` and Wave ABI docs relevant to your task.
- Run `./scripts/docs-publish.sh --release 0.1.0 --no-build`.
- Open the live demo page (`docs/demo/scan-verify-render.md`) in local docs site.

## First contribution checklist
- Classify change as patch/minor/major (per `docs/KERNEL_CHANGE_POLICY.md`).
- Confirm no authority escalation from advisory/projection layers.
- Confirm deterministic outputs are unchanged unless intentionally versioned.
- Run relevant tests + `./scripts/release-gate.sh`.

## Integration checklist (downstream)
- Import only `atomic_kernel.*`.
- Add boundary guard against `runtime.atomic_kernel.*`.
- Add fixture-backed deterministic smoke test.
- Add one visible proof command/panel (read-only).

## Boundary
This checklist guides contributors. It does not alter normative kernel contracts.
