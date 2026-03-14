# Atomic Kernel
Status: Normative
Authority: Kernel
Depends on: `kernel/coq/AtomicKernel.v`, `conformance/run-tests.sh`, `scripts/atomic-kernel-gate.sh`

Purpose: document the current enforced contract and usage boundaries for this layer.


Atomic Kernel is a deterministic replay substrate with a release-normalized Python API (`atomic_kernel.*`).

Start here:
- quick start: `docs/guide/quick-start.md`
- concept overview: `docs/guide/what-is-atomic-kernel.md`
- architecture overview: `docs/guide/architecture-overview.md`

## What Is Guaranteed
- Deterministic transition/replay for supported widths (`16,32,64,128,256`).
- Fail-closed validation for Wave27H/27I/27J/27K gate surfaces.
- Replay-hash lock enforcement for canonical reports.
- Append-only SID/OID/CLOCK occurrence semantics (Wave27I).

## What Is Not Claimed
- No claim that projection/transport layers define authority.
- No claim beyond current proofs/tests/gates in this repository.
- Wave27K lane16 is implemented and validated but remains draft extension scope.

## Public API (Stable v0.1.0)
```python
import atomic_kernel as ak

x1 = ak.delta(16, 0x0001)
orbit = ak.replay(16, 0x0001, 8)

sid = ak.compute_typed_sid("living_xml", "0011100")
clock1 = ak.advance_clock({"frame": 0, "tick": 1, "control": 0})
oid = ak.compute_oid(clock1, sid, None)

header = ak.closure_fixpoint(0x1C)
p = ak.phase(0x1C)
```

## Release Ritual
```bash
cd /home/main/devops/atomic-kernel
./conformance/run-tests.sh
./scripts/atomic-kernel-gate.sh
./scripts/release-gate.sh
```

## Authority Boundary
Canonical truth is kernel/runtime + fixture corpora + replay-hash locks. All projection/propagation surfaces are derived and non-authoritative.

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
