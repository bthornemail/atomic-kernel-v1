#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "run as root" >&2
  exit 1
fi

REPO_DIR="${1:-/opt/atomic-kernel}"
DOMAIN="${2:-mcp.universal-life-protocol.com}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -d "$REPO_DIR" ]]; then
  echo "repo dir not found: $REPO_DIR" >&2
  exit 1
fi

echo "[1/5] install systemd units"
bash "$HERE/install-systemd.sh"

echo "[2/5] install nginx vhosts"
bash "$HERE/install-nginx-vhosts.sh"

echo "[3/5] ensure runtime services exist"
install -d -m 755 "$REPO_DIR/runtime/ulp"
for f in resolver-service.mjs symbol-service.mjs; do
  src="$HERE/../../runtime/ulp/$f"
  dst="$REPO_DIR/runtime/ulp/$f"
  src_real="$(readlink -f "$src")"
  dst_real="$(readlink -f "$dst" 2>/dev/null || true)"
  if [[ "$src_real" != "$dst_real" ]]; then
    install -m 755 "$src" "$dst"
  fi
done
systemctl restart ulp-resolver.service ulp-symbol.service

echo "[4/5] reload nginx"
nginx -t
systemctl reload nginx

echo "[5/5] verify node"
bash "$HERE/verify-node.sh" "$REPO_DIR" "$DOMAIN"

echo "ok live node apply complete"
