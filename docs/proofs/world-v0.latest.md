# World v0 Proof Receipt

Generated (UTC): 2026-03-21T16:03:24Z
Repo: /home/main/devops/atomic-kernel

Command:
bash scripts/world-v0-gate.sh

Checks:
world_generate deterministic canonical artifact: PASS
world_step proposal-only boundary and eligibility checks: PASS
world_project deterministic JSON text projection: PASS
world_branch_reconcile lineage fixture/reject checks: PASS
world_verify schema/digest/replay and fail-closed checks: PASS

Artifacts:
- artifacts/world-v0.generate.normalized.json
- artifacts/world-v0.step.normalized.json
- artifacts/world-v0.project.normalized.json
- artifacts/world-v0.branch-reconcile.normalized.json
- artifacts/world-v0.verify.normalized.json
- artifacts/world-v0.normalized.json
- artifacts/world-v0.replay-hash (sha256:72303e5221fcb2e2c69324b3ce99905c767769edb084e2a3361872ed674bec18)

Result: PASS
