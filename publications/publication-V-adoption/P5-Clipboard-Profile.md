# P5 Clipboard Profile
Status: Advisory
Authority: Projection
Depends on: `propagation/clipboard/clipboard-runtime-spec.md`

Purpose: document the current enforced contract and usage boundaries for this layer.


Clipboard profile is a transfer boundary pattern.

Required behavior when used:
- canonicalize payload,
- derive seed/witness deterministically,
- verify before acceptance.

Clipboard profile is advisory and cannot upgrade authority.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
