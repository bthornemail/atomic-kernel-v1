# Atomic Kernel - Deterministic Core

This repository contains a pure, extendable kernel surface with deterministic replay and fail-closed validation.
Implementation milestone is complete; release packaging surface is now normalized for `0.1.0`.

## Core guarantees
- Deterministic replay from canonical seed.
- Bounded state transitions for supported widths.
- Fail-closed schema/runtime validation.
- Append-only identity/occurrence chains (SID/OID/CLOCK split).

## Main entrypoints
- `scripts/atomic-kernel-gate.sh`
- `scripts/release-gate.sh`
- `conformance/run-tests.sh`
- `kernel/coq/AtomicKernel.v`

## Quick run
```bash
cd /home/main/devops/atomic-kernel
./conformance/run-tests.sh
./scripts/atomic-kernel-gate.sh
./scripts/release-gate.sh
```

## Public API (`atomic_kernel.*`)
```python
import atomic_kernel as ak

seq = ak.replay(16, 0x0001, 8)
sid = ak.compute_typed_sid("living_xml", "0011100")
clock1 = ak.advance_clock({"frame": 0, "tick": 1, "control": 0})
header = ak.closure_fixpoint(0x1C)
```

## Authority
Transport and projection layers are non-authoritative. Canonical truth is deterministic runtime + fixtures + replay-hash locks.
# atomic-kernel
