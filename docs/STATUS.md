# Status Classification
Status: Normative
Authority: Kernel
Depends on: `README.md`, `scripts/atomic-kernel-gate.sh`, `scripts/release-gate.sh`

Purpose: document the current enforced contract and usage boundaries for this layer.


## Normative (Enforced)
- Kernel transition/replay law: `atomic_kernel.core`
- Wave27H living XML validation/gate/hash lock
- Wave27I SID/OID/CLOCK and occurrence chain validation
- Wave27J seed closure + canonical JSON companion validation

Evidence:
- `conformance/run-tests.sh`
- `scripts/atomic-kernel-gate.sh`
- `golden/**/replay-hash`

## Draft (Implemented, Not Constitutional)
- Wave27K lane16 runtime/gate.

Evidence:
- `runtime/atomic_kernel/lane16.py`
- `scripts/lane16-gate.sh`
- `docs/WAVE27K_LANE16_ABI.md`

## Advisory / Projection
- Aztec/clipboard/XML propagation docs and manifests.
- Publication-IV/V adoption surfaces.

Rule: advisory layers never upgrade authority of kernel law.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
