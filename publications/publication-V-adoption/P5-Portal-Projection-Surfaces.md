# P5 Portal Projection Surfaces
Status: Advisory
Authority: Projection
Depends on: `docs/STATUS.md`

Purpose: document the current enforced contract and usage boundaries for this layer.


Portal/projection surfaces are read-only views over canonical artifacts.

Forbidden:
- direct mutation of canonical state,
- hidden authority paths from projection/UI layers.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
