# Roadmap
Status: Advisory
Authority: Extension
Depends on: `README.md`, `docs/index.md`, `docs/STATUS.md`, `docs/KERNEL_CHANGE_POLICY.md`

Purpose: provide a concise milestone ledger and next-step scope for adoption.

Atomic Kernel has completed kernel stabilization, documentation, verification-badge publishing, demo validation, and first downstream adoption.

## Current Phase
Adoption and accessibility hardening: make the system easy to discover, verify, and evaluate from public docs.

## Milestones
### A-F (Complete)
- A: landing + freeze policy
- B: docs site scaffold
- C: deterministic badge publish pipeline
- D: scan/verify/render demo
- E: downstream integration (`metaverse-kit`) via `atomic_kernel.*`
- F: adoption pack (comparison, onboarding, contributor discipline)

### G (Next)
Public docs deployment + hosted demo polish.

Scope:
- Publish MkDocs site to a public URL.
- Make live demo one-click from docs home.
- Ensure badge catalog is browsable from hosted docs.
- Add one “Start here in 2 minutes” newcomer path.
- Link downstream proof reference to `metaverse-kit`.

Success criteria:
- Public docs URL is live.
- Demo reachable in one click from homepage.
- Badge flow and release docs remain consistent.
- Newcomer can understand core value from site alone.
- `./scripts/release-gate.sh` remains green.

Out of scope for G:
- Kernel law changes.
- New wave semantics.
- Broad downstream refactors.
- Authority model changes.

## Boundary
Roadmap guidance is advisory planning metadata. It does not redefine kernel law or authority classes.
