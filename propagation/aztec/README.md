# Aztec Propagation
Status: Advisory
Authority: Projection
Depends on: `propagation/aztec/schemas/*.json`, `propagation/aztec/payloads/*`, `docs/STATUS.md`

Purpose: document the current enforced contract and usage boundaries for this layer.

Aztec artifacts package derived deterministic data for transport/distribution.

They do not define canonical truth and cannot upgrade authority.

## Contracts
- `atomic-kernel.doc.badge/1` (small verification badge payload)
- `atomic-kernel.experience.manifest/1` (larger projection manifest)

## Files
- `schemas/doc-badge.schema.json`
- `schemas/experience-manifest.schema.json`
- `payloads/doc-badges/*.json`
- `payloads/experience-manifest.json`
- `genesis-32-layer-manifest.yaml` (YAML projection generated from `payloads/experience-manifest.json`)

## Verify
```bash
./scripts/aztec-payload-gate.sh
```

## Build
```bash
python3 propagation/aztec/build-payloads.py --release 0.1.0
python3 propagation/aztec/create-aztec-manifest.py
```

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
