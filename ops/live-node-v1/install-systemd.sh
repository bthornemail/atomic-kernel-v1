#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "run as root" >&2
  exit 1
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIT_DIR="$HERE/systemd"
TARGET_DIR="/etc/systemd/system"

for f in \
  atomic-kernel-mcp.service \
  atomic-kernel-gates-smoke.service \
  atomic-kernel-gates-smoke.timer \
  atomic-kernel-gates-snapshot.service \
  atomic-kernel-gates-snapshot.timer \
  atomic-kernel-gates-parity.service \
  atomic-kernel-gates-parity.timer \
  ulp-resolver.service \
  ulp-symbol.service
do
  install -m 644 "$UNIT_DIR/$f" "$TARGET_DIR/$f"
done

systemctl daemon-reload
systemctl enable --now atomic-kernel-mcp.service
systemctl enable --now atomic-kernel-gates-smoke.timer
systemctl enable --now atomic-kernel-gates-snapshot.timer
systemctl enable --now atomic-kernel-gates-parity.timer
systemctl enable --now ulp-resolver.service
systemctl enable --now ulp-symbol.service

echo "ok systemd installed and enabled"
