# P2 Propagation Profile — Aztec
Status: Advisory
Authority: Projection
Depends on: `propagation/aztec/create-aztec-manifest.py`, `propagation/aztec/genesis-32-layer-manifest.yaml`

Purpose: document the current enforced contract and usage boundaries for this layer.


Aztec profile is a propagation/packaging surface.

Rules:
- carries derived artifacts,
- does not redefine kernel law,
- does not upgrade authority of projection data.

Canonical validation remains runtime/gate/hash lock based.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
