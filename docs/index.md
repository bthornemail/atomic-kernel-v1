# Atomic Kernel Docs
Status: Advisory
Authority: Extension
Depends on: `README.md`, `docs/STATUS.md`, `docs/KERNEL_CHANGE_POLICY.md`

Purpose: provide a public front door from first-time understanding to verified contracts.

Atomic Kernel is a deterministic replay substrate for systems that cannot tolerate state drift.
It matters because identity and replay outcomes can be recomputed and verified, not merely trusted.

## Try It Now
- **[Try the Scan / Verify / Render demo](demo/scan-verify-render.md)**
- **[Start with Quick Start](guide/quick-start.md)**

Used downstream in `metaverse-kit` through the stable `atomic_kernel.*` API boundary.

## Start Here
- New reader: [What Is Atomic Kernel](guide/what-is-atomic-kernel.md)
- Adoption decision: [Who Is This For](guide/who-is-this-for.md)
- Positioning: [What Makes Atomic Kernel Different](guide/what-makes-atomic-kernel-different.md)
- First run: [Quick Start](guide/quick-start.md)
- Product flow: [Scan / Verify / Render](guide/scan-demo.md)
- Interactive product demo: [Live Demo](demo/scan-verify-render.md)
- Badge catalog: [Verification Badges](badges/index.md)

## Formal Contracts
- [Status Classification](STATUS.md)
- [Kernel Change Policy](KERNEL_CHANGE_POLICY.md)
- [ABI Index](INDEX.md)
- [Onboarding Checklist](ONBOARDING_CHECKLIST.md)
- [Contributor Discipline](CONTRIBUTOR_DISCIPLINE.md)
- [Roadmap](ROADMAP.md)

## Next Schema Stack (Draft)
- [Abstract Syntax Graph Schema](ABSTRACT_SYNTAX_GRAPH_SCHEMA.md)
- [Pattern Instance Schema](PATTERN_INSTANCE_SCHEMA.md)
- [Regular Path Expression Language](REGULAR_PATH_EXPRESSION_LANGUAGE.md)
- [State Machine Framework](STATE_MACHINE_FRAMEWORK.md)
- [Diagram View Schema](DIAGRAM_VIEW_SCHEMA.md)
- [UML Projection Contract](UML_PROJECTION_CONTRACT.md)

## Core Rule
Scan, verify, then render.

Projection surfaces remain advisory and cannot upgrade kernel authority.

## Publish Path
```bash
./scripts/docs-publish.sh --release 0.1.0 --no-build
```

## Boundary
This page is a routing surface for documentation. It does not redefine kernel law.
