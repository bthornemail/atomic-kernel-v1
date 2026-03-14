# P4 Wave32 Metaverse Extension
Status: Advisory
Authority: Extension
Depends on: `layers/32-full-manifest.md`, `docs/STATUS.md`

Purpose: document the current enforced contract and usage boundaries for this layer.


Wave32 structures are extension-layer compositions over deterministic kernel outputs.

Boundary:
- extension semantics may organize data,
- extension semantics cannot override kernel/runtime conformance law.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
