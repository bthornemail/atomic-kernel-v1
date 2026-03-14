# Living XML Runtime
Status: Advisory
Authority: Projection
Depends on: `runtime/atomic_kernel/living_xml.py`, `scripts/living-xml-gate.sh`

Purpose: document the current enforced contract and usage boundaries for this layer.


Implemented behavior:
- strict `fs -> gs -> rs -> us` hierarchy
- deterministic 7-cycle tick behavior
- fail-closed schema + runtime validation

Boundary:
- XML representation is derived runtime surface,
- canonical truth is enforced by gate + replay-hash lock.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
