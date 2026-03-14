# P5 Adoption Guide
Status: Normative
Authority: Extension
Depends on: `README.md`, `scripts/release-gate.sh`, `scripts/check-downstream-import-surface.sh`

Purpose: document the current enforced contract and usage boundaries for this layer.


## Install/Import Boundary
Use public API only:
- `atomic_kernel.*`

Do not import:
- `runtime.atomic_kernel.*`

## Required Verification Ritual
```bash
./conformance/run-tests.sh
./scripts/atomic-kernel-gate.sh
./scripts/release-gate.sh
```

## Hash Lock Policy
- replay-hash relocking is explicit (`scripts/lock-replay-hashes.sh`), never implicit in release gate.

## Threat Model (Operational)
This architecture is designed to reduce:
- state drift across implementations,
- identity forgery (SID/OID mismatch),
- replay tampering (chain/hash inconsistency),
- projection-layer authority escalation,
- nondeterministic runtime behavior in canonical paths.

## Breaking Change Rule
Any change affecting deterministic outputs, public API contracts, or fixture semantics requires versioned release + updated lock artifacts.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
