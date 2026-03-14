# Seed Derivation

Canonical seed derives from canonical payload bytes:
`seed = sha256(canonical_payload) truncated to width`

For seed algebra (Wave27J), 7-bit domain uses strict `0..127` and closure-fixpoint canonical header.
