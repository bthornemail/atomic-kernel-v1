# atomic-kernel v0.1.0
Status: Normative
Authority: Extension
Depends on: `pyproject.toml`, `scripts/release-gate.sh`, `releases/0.1.0/ARTIFACTS.sha256`

Purpose: capture release classification and externally consumable contract for v0.1.0.

## Classification
- implementation-complete
- verification-complete
- release-normalized

## Public API
- `atomic_kernel.delta`
- `atomic_kernel.replay`
- `atomic_kernel.compute_sid`
- `atomic_kernel.compute_typed_sid`
- `atomic_kernel.advance_clock`
- `atomic_kernel.compute_oid`
- `atomic_kernel.closure_fixpoint`
- `atomic_kernel.phase`

## Adoption Milestones (A-E)
- Milestone A: landing page clarity, status taxonomy, and kernel change policy frozen.
- Milestone B: MkDocs site scaffold with clear guide/spec navigation.
- Milestone C: deterministic docs publish path with badge payload generation/validation.
- Milestone D: interactive scan/verify/render demo page.
- Milestone E: downstream dependency proof in `metaverse-kit` using only `atomic_kernel.*` with boundary guard and deterministic smoke test.

## Downstream Proof
- Consumer: `metaverse-kit`
- Visible proof command: `npm run -s atomic-kernel:show`
- Boundary check: `npm run -s check:atomic-kernel-import-boundary`
- Deterministic smoke: `npm run -s atomic-kernel:test`

## Boundary
Release notes report enforced release state and do not redefine kernel law.
