# Scan Demo Flow
Status: Advisory
Authority: Projection
Depends on: `propagation/aztec/genesis-32-layer-manifest.yaml`, `docs/WAVE27J_SEED_ALGEBRA_ABI.md`, `docs/WAVE27H_LIVING_XML_ABI.md`

Purpose: define the user-facing scan/verify/render flow for a demo page.

## Demo flow
```text
Scan Aztec
  ->
Decode manifest envelope
  ->
Verify schema/version/hash
  ->
Replay/identity checks
  ->
Show canonical JSON
  ->
Render XML projection
  ->
Display pass/fail badge
```

## Self-described envelope (recommended)
```json
{
  "schema": "atomic-kernel.experience.manifest/1",
  "authority": "projection",
  "release": "0.1.0",
  "version": 1,
  "kernel": {
    "package": "atomic-kernel",
    "public_api": "atomic_kernel.*",
    "release_artifacts": "releases/0.1.0/ARTIFACTS.sha256"
  }
}
```

Rule: verify first, render second.

## Verification badge envelope
Use `atomic-kernel.doc.badge/1` for small per-document Aztec badges.

## Boundary
Demo guidance is projection-layer design. It is derived from canonical artifacts and cannot upgrade authority.
