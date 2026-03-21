# PoC Video Runbook
Status: Advisory
Authority: Extension
Depends on: `scripts/poc-video-sequence.sh`, `scripts/poc-video-capture.sh`, `docs/MCP_ENTRYPOINTS.md`

Purpose: generate a complete proof-of-concept video showing deterministic MCP and gate proofs.

## One-Command Capture

```bash
cd /home/main/devops/atomic-kernel
bash scripts/poc-video-capture.sh
```

## What It Records

The sequence script runs:

1. `npm run -s mcp:unified:info`
2. `npm run -s mcp:unified:smoke`
3. `npm run -s mcp:unified:stdio:smoke`
4. `./scripts/fork-import-v1_2-gate.sh`
5. `./scripts/release-gate.sh`
6. `/home/main/devops/scripts/closure-spine-smoke.sh`
7. message-to-future digest verification

## Output Artifacts

- `artifacts/poc-video/atomic-kernel-poc.cast`
- `artifacts/poc-video/atomic-kernel-poc.gif`
- `artifacts/poc-video/atomic-kernel-poc.mp4` (if `ffmpeg` is present)
- `docs/proofs/poc-video-capture.latest.md`

## Notes

- The capture is deterministic in structure but includes runtime timestamps in receipts.
- For voiceover editing, use the generated mp4/gif as base and narrate each numbered section.
