# Quick Start
Status: Advisory
Authority: Extension
Depends on: `pyproject.toml`, `conformance/run-tests.sh`, `scripts/release-gate.sh`

Purpose: get a first deterministic run in under five minutes.

## 1) Use the public API
```python
import atomic_kernel as ak

seq = ak.replay(16, 0x0001, 8)
print(seq)
```

Expected property: rerunning this with the same inputs yields the same sequence.

## 2) Run verification rituals
```bash
cd /home/main/devops/atomic-kernel
./conformance/run-tests.sh
./scripts/atomic-kernel-gate.sh
./scripts/release-gate.sh
```

## 3) Know the import boundary
Use only:
- `atomic_kernel.*`

Do not import:
- `runtime.atomic_kernel.*`

Enforcement: `scripts/check-downstream-import-surface.sh` (included by release gate).

## Boundary
Quick-start examples are derived from enforced release contracts and cannot redefine kernel law.
