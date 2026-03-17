# Compatibility Matrix: v1 and v2

Status: prototype lane guidance  
Scope: `dev-docs/prototype/atomic-kernel` only

## Policy
- **Canonical truth is the direct package bytes. Carriers are reversible projections only.**
- `v1` remains supported and unchanged.
- `v2` is parallel and direct-byte canonical (`ak.canonical.package.v2`).
- Carrier formats are projection/transport only.
- Package digest is derived only from canonical package bytes.
- Carrier-local metadata must never affect package digest.

## Artifact Types
- `v1` canonical transport bundle: `ak.aztec.bundle.v1` / `ak.aztec.chunk.v1`
- `v2` canonical package: `ak.canonical.package.v2`
- `v2` carrier bundle: `ak.aztec.bundle.v2` / `ak.aztec.chunk.v2`
- `v2` Unicode projection: `ak.unicode.projection.v2`

## Command Matrix
- Build v1 bundle: `./ak aztec-pack ...`
- Unpack v1 bundle: `./ak aztec-unpack ...`
- Build v2 package: `./ak package-v2-build ...`
- Verify v2 package: `./ak package-v2-verify --package ...`
- Build v2 Aztec carrier: `./ak package-v2-aztec-pack --package ...`
- Decode v2 Aztec carrier: `./ak package-v2-aztec-unpack --indir ... --output ...`
- Build v2 Unicode projection: `./ak package-v2-unicode-pack --package ...`
- Decode v2 Unicode projection: `./ak package-v2-unicode-unpack --projection ... --output ...`
- Run v2 parity check: `./ak package-v2-parity ...`

## Migration Notes
- Keep v1 consumers unchanged.
- For v2, treat package bytes as canonical truth.
- Only trust carrier data after strict reduction back to `ak.canonical.package.v2` and digest verification.
