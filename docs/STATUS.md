# Status Classification
Status: Normative
Authority: Kernel
Depends on: `README.md`, `scripts/atomic-kernel-gate.sh`, `scripts/release-gate.sh`

Purpose: document the current enforced contract and usage boundaries for this layer.


## Normative
Definition:
- Constitutional contract enforced by proofs/tests/gates/hashes.
- May define kernel law or mandatory validation behavior.
- Any semantic drift here requires explicit versioning and release notes.

Current normative surfaces:
- Kernel transition/replay law: `atomic_kernel.core`
- Wave27H living XML validation/gate/hash lock
- Wave27I SID/OID/CLOCK and occurrence-chain validation
- Wave27J seed closure + canonical JSON companion validation
- Wave27L vNext algorithmic identity lane (policy-promoted)

Evidence:
- `conformance/run-tests.sh`
- `scripts/atomic-kernel-gate.sh`
- `golden/**/replay-hash`
- `runtime/atomic_kernel/vnext.py`
- `scripts/vnext-replay-parity-gate.sh`
- `scripts/vnext-api-compat-gate.sh`
- `scripts/vnext-coq-parity-gate.sh`
- `docs/WAVE27L_VNEXT_ALGORITHMIC_ID_ABI.md`
- `runtime/atomic_kernel/vnext_policy.json`

## Draft
Definition:
- Implemented and tested, but not constitutional.
- May evolve without redefining kernel law.
- Must remain clearly labeled until promoted.

Current draft surfaces:
- Wave27K lane16 runtime/gate

Evidence:
- `runtime/atomic_kernel/lane16.py`
- `scripts/lane16-gate.sh`
- `docs/WAVE27K_LANE16_ABI.md`

## Advisory
Definition:
- Explanatory, projection, or adoption surfaces.
- Cannot redefine kernel law.
- Cannot upgrade authority; must derive from canonical artifacts.

Current advisory/projection surfaces:
- Aztec/clipboard/XML propagation docs and manifests
- Publication IV/V adoption surfaces
- Guide pages and demo flows

Rule:
- Advisory layers never upgrade authority of kernel law.
- Projection artifacts are verify-before-render.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
