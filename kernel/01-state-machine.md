# Atomic State Machine
Status: Normative
Authority: Kernel
Depends on: `kernel/coq/AtomicKernel.v`, `runtime/atomic_kernel/lane16.py`

Purpose: define the strict 4-bit lane state set used by runtime projections.

## Valid States
- `0000` VOID
- `1000` NULL
- `1100` ACTIVE0
- `1101` ACTIVE1
- `1110` ACTIVE2
- `1111` ACTIVE3

All other 4-bit states are invalid and must reject fail-closed.

## Boundary
State-machine projection does not redefine kernel replay law; it is derived from canonical runtime artifacts.
