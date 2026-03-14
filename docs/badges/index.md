# Verification Badges
Status: Advisory
Authority: Projection
Depends on: `propagation/aztec/payloads/*`, `scripts/docs-publish.sh`

Purpose: expose generated verification payloads used by scan/verify/render flows.

These payloads are projection artifacts and must be verified before rendering.

## Badge Payloads
- `docs/badges/payloads/doc-badges/README.json`
- `docs/badges/payloads/doc-badges/P1-Kernel.json`
- `docs/badges/payloads/doc-badges/P3-Distributed-Runtime-API.json`
- `docs/badges/payloads/doc-badges/P5-Adoption-Guide.json`
- `docs/badges/payloads/doc-badges/RELEASE_NOTES.json`

## Experience Payload
- `docs/badges/payloads/experience-manifest.json`

## Optional Aztec Images
If generated (`--emit-aztec`), image files are written under:
- `docs/badges/aztec/*.svg`

## Publish
```bash
./scripts/docs-publish.sh --release 0.1.0 --no-build
```

## Boundary
Badges are projection-layer verification aids and cannot upgrade kernel authority.
