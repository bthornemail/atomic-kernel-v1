# Clipboard Runtime Spec
Status: Advisory
Authority: Projection
Depends on: `atomic_kernel/core.py`, `atomic_kernel/seed.py`

Purpose: document the current enforced contract and usage boundaries for this layer.


Recommended flow:
1. copy: canonicalize -> derive seed -> attach witness
2. paste: verify witness -> replay check -> accept/reject

This is an advisory profile and not constitutional kernel law.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
