# Example Workflow
Status: Advisory
Authority: Extension
Depends on: `atomic_kernel/*`, `docs/WAVE27I_IDENTITY_AND_OCCURRENCE_ABI.md`, `scripts/atomic-kernel-gate.sh`

Purpose: show one end-to-end deterministic workflow from canonical input to verification.

## Steps
1. Canonicalize payload.
2. Derive seed and replay orbit.
3. Compute `SID` from canonical semantic form.
4. Advance deterministic `CLOCK` and compute `OID`.
5. Build/verify witness artifacts and chain links.
6. Validate using gate + replay-hash locks.

## Minimal code sketch
```python
import atomic_kernel as ak

seed_orbit = ak.replay(16, 0x0001, 8)
sid = ak.compute_typed_sid("living_xml", "0011100")
clock = ak.advance_clock({"frame": 0, "tick": 1, "control": 0})
oid = ak.compute_oid(clock, sid, None)
```

## Verify
```bash
./scripts/atomic-kernel-gate.sh
```

## Boundary
Workflow guidance is derived from canonical contracts and cannot redefine kernel law.
