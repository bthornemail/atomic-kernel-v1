#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$REPO_ROOT/artifacts/poc-video"
PROOF_FILE="$REPO_ROOT/docs/proofs/poc-video-capture.latest.md"
mkdir -p "$OUT_DIR" "$REPO_ROOT/docs/proofs"

CAST="$OUT_DIR/atomic-kernel-poc.cast"
GIF="$OUT_DIR/atomic-kernel-poc.gif"
MP4="$OUT_DIR/atomic-kernel-poc.mp4"
SKIP_MP4="${POC_VIDEO_SKIP_MP4:-1}"
rm -f "$MP4"

need_bin() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "missing required tool: $1" >&2
    exit 2
  }
}

need_bin asciinema
need_bin agg

echo "[1/4] recording asciinema cast"
asciinema rec \
  --overwrite \
  --idle-time-limit 1.2 \
  --cols 120 \
  --rows 36 \
  --command "bash scripts/poc-video-sequence.sh" \
  "$CAST"

echo "[2/4] rendering gif from cast"
agg --theme github-dark --speed 1 "$CAST" "$GIF"

mp4_note="MP4_SKIPPED"
if [[ "$SKIP_MP4" != "1" ]] && command -v ffmpeg >/dev/null 2>&1; then
  echo "[3/4] rendering mp4 from gif"
  ffmpeg -y -i "$GIF" -movflags faststart -pix_fmt yuv420p "$MP4" >/dev/null 2>&1
  mp4_note="$MP4"
else
  echo "[3/4] mp4 skipped (set POC_VIDEO_SKIP_MP4=0 to enable)"
fi

echo "[4/4] writing proof receipt"
cast_sha="$(sha256sum "$CAST" | awk '{print $1}')"
gif_sha="$(sha256sum "$GIF" | awk '{print $1}')"
if [[ -f "$MP4" ]]; then
  mp4_sha="$(sha256sum "$MP4" | awk '{print $1}')"
else
  mp4_sha="n/a"
fi

cat > "$PROOF_FILE" <<EOF
# PoC Video Capture Proof

Generated (UTC): $(date -u +%FT%TZ)
Repo: /home/main/devops/atomic-kernel

Command:
bash scripts/poc-video-capture.sh

Sequence:
scripts/poc-video-sequence.sh

Outputs:
- $CAST
- $GIF
- $mp4_note

Digests:
- cast sha256:$cast_sha
- gif sha256:$gif_sha
- mp4 sha256:$mp4_sha

Result: PASS
EOF

echo "ok poc video capture proof=$PROOF_FILE"
