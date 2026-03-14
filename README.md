# Atomic Kernel
Status: Normative
Authority: Kernel
Depends on: `kernel/coq/AtomicKernel.v`, `conformance/run-tests.sh`, `scripts/atomic-kernel-gate.sh`

Purpose: document the current enforced contract and usage boundaries for this layer.

Atomic Kernel is a deterministic replay substrate for systems that cannot tolerate state drift. The same canonical input yields the same transition, identity, and replay witness across environments, so peers can recompute and verify instead of trusting runtime coincidence.

## What It Is
- A stable constitutional base layer with a release-normalized API: `atomic_kernel.*`.
- A deterministic kernel law with conformance tests, gates, and replay-hash locks.
- A split authority model where projection layers stay non-authoritative.

## Why It Exists
- Eliminate cross-machine state drift.
- Make identity derivable from canonical forms.
- Enforce fail-closed validation for malformed or forged artifacts.
- Keep XML/Aztec useful for projection without authority backflow.

## Who It Is For
- Deterministic distributed runtimes.
- Verifiable artifact/replay pipelines.
- Identity-safe coordination and audit-sensitive systems.

Not a good fit for ordinary CRUD apps that do not need deterministic replay guarantees.

## 60-Second Quick Start
```bash
cd /home/main/devops/atomic-kernel
./scripts/release-gate.sh
```

## Architecture (Authority Ladder)
```text
Kernel Law (normative)
  -> Encoded Runtime (extension)
  -> Distributed Identity (extension)
  -> Extensions and Adoption (extension/advisory)
  -> Propagation Surfaces (projection only)
```

## Public API (Stable v0.1.0)
External consumers should import only:

```python
import atomic_kernel as ak

orbit = ak.replay(16, 0x0001, 8)
sid = ak.compute_typed_sid("living_xml", "0011100")
clock1 = ak.advance_clock({"frame": 0, "tick": 1, "control": 0})
oid = ak.compute_oid(clock1, sid, None)
```

## Go Next
- Human docs: `docs/guide/README.md`
- Authority and status: `docs/STATUS.md`
- Change discipline: `docs/KERNEL_CHANGE_POLICY.md`
- Formal specs: `docs/INDEX.md`
- Scan/verify/render flow: `docs/guide/scan-demo.md`

## Docs Site (Milestone B)
```bash
cd /home/main/devops/atomic-kernel
./scripts/docs-site.sh serve
```

## Release Ritual
- `./conformance/run-tests.sh`
- `./scripts/atomic-kernel-gate.sh`
- `./scripts/release-gate.sh`

## Boundary
This layer is derived from canonical artifacts and does not redefine kernel law.
It cannot upgrade authority beyond its declared scope.
