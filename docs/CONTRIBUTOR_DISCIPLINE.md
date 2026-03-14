# Contributor Discipline
Status: Normative
Authority: Extension
Depends on: `docs/STATUS.md`, `docs/KERNEL_CHANGE_POLICY.md`, `scripts/release-gate.sh`

Purpose: define mandatory contributor behavior that preserves replay trust and authority boundaries.

## Required discipline
- Use only proven/public surfaces for downstream contracts.
- Keep projection/advisory artifacts non-authoritative.
- Preserve deterministic outputs unless change is explicitly classified and versioned.
- Fail closed on malformed artifacts; do not add silent coercion.

## Mandatory checks before merge
- `./scripts/release-gate.sh` must pass.
- If touching docs publish path: `./scripts/docs-publish.sh --release 0.1.0 --no-build`.
- If touching projection payload contracts: `./scripts/aztec-payload-gate.sh`.

## Forbidden shortcuts
- Importing internal runtime paths as public contracts.
- Relocking replay hashes without explicit reason and release-note callout.
- Mixing draft/advisory claims into normative documents.
- Accepting malformed payloads “best effort”.

## Change declaration
Every substantial change should state:
- Classification: patch/minor/major.
- Affected authority layer.
- Deterministic impact: none / intentional.
- Migration note: required / not required.

## Boundary
This discipline governs contributor process. It does not grant authority to projection layers.
