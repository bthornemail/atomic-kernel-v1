# Why Deterministic Replay Matters
Status: Advisory
Authority: Extension
Depends on: `kernel/04-replay.md`, `docs/WAVE27I_IDENTITY_AND_OCCURRENCE_ABI.md`, `golden/**/replay-hash`

Purpose: explain the practical security and reliability value of deterministic replay.

Common failures in distributed/runtime systems:
- state drift across nodes
- hard-to-reproduce bugs
- identity ambiguity between events and occurrences
- replay tampering that is hard to detect

Atomic Kernel addresses these by fixing three things:
1. replay law (same seed -> same orbit)
2. identity law (`SID` for meaning, `OID` for occurrence)
3. artifact reproducibility locks (`replay-hash`)

This enables independent verification rather than trust in one process/machine.

## Boundary
Motivation text is explanatory and derived from canonical artifacts; it does not redefine kernel law.
