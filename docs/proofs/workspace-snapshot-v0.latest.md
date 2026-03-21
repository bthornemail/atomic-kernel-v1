# Workspace Snapshot v0 Proof

Generated (UTC): 2026-03-21T16:05:12Z
Repo: /home/main/devops/atomic-kernel

Command:
bash scripts/workspace-snapshot-v0-gate.sh

Scope:
- git tracked files snapshot (full tracked codebase in target repo)
- deterministic normalized artifact emission
- restorable proof from snapshot bundle

Checks:
snapshot normalized deterministic rerun: PASS
bundle created from HEAD: PASS
restore clone from bundle: PASS
restore digest parity against snapshot manifest: PASS

Head Commit: 6673ea1e581a29f8b0ad6e275cee208e822b5764
Tracked File Count: 5679

Artifacts:
- artifacts/workspace-snapshot-v0.normalized.json
- artifacts/workspace-snapshot-v0.replay-hash (sha256:22a44ec267f7bfb88c7f4412b21553253a120e18fd844fb968920400c3aabfcf)
- artifacts/workspace-snapshot-v0.restore.normalized.json
- artifacts/workspace-snapshot-v0.restore.replay-hash (sha256:62000b6afdb1a5dbaf396a791498eb877787dbd8cdc972bdc4618f7e638a5181)
- artifacts/workspace-snapshot-v0.bundle

Result: PASS
