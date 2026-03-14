# Witness Format

Canonical witness package:
- payload hash
- seed
- orbit/projection signature
- basis/runtime version

Verification recomputes hash, seed, and replay signature and rejects on mismatch.
