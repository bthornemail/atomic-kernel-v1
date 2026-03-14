# Atomic State Machine

4-bit lane state uses strict valid set:
- `0000` VOID
- `1000` NULL
- `1100` ACTIVE0
- `1101` ACTIVE1
- `1110` ACTIVE2
- `1111` ACTIVE3

All other 4-bit states are invalid and reject fail-closed.
