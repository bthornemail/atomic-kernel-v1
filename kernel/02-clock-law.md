# Clock Law
Status: Normative
Authority: Kernel
Depends on: `kernel/coq/AtomicKernel.v`, `atomic_kernel/core.py`

Purpose: define deterministic transition law over bounded widths.

For width `n`:
- `mask_n(x) = x mod 2^n`
- `rotl_n`, `rotr_n` are masked rotations.

Transition:
`δ_n(x) = mask_n(rotl_n(x,1) xor rotl_n(x,3) xor rotr_n(x,2) xor C_n)`

`C_n` is byte pattern `0x1D` repeated to width.

## Boundary
Clock law is constitutional kernel truth and cannot be overridden by extension or projection layers.
