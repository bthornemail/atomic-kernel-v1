# Architecture Overview
Status: Advisory
Authority: Extension
Depends on: `ARCHITECTURE.md`, `publications/`, `docs/STATUS.md`

Purpose: provide a human-readable map of the system layers and authority boundaries.

## Canonical flow
```text
Canonical Artifact
    ->
Replay Engine
    ->
Identity Layer (SID/OID)
    ->
Encoded Runtime (XML / Control)
    ->
Propagation (Aztec / Clipboard)
    ->
Applications
```

## Authority ladder
```text
Publication I - Kernel Law
    ->
Publication II - Encoded Runtime
    ->
Publication III - Distributed Identity
    ->
Publication IV - Extension Structures
    ->
Publication V - Adoption Rules
    ->
Propagation Profiles - Transport / Projection
```

Practical rule: lower layers constrain higher layers; higher layers cannot override lower-layer law.

## Boundary
This overview is descriptive and derived from canonical artifacts. It does not redefine kernel law or upgrade authority.
