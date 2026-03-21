#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "run as root" >&2
  exit 1
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NGINX_SRC="$HERE/nginx"
SITE_AVAIL="/etc/nginx/sites-available"
SITE_ENAB="/etc/nginx/sites-enabled"
ROOT_DIR="/var/www/ulp-root"
FORCE="${FORCE:-0}"

install -d -m 755 "$ROOT_DIR/.well-known"

if [[ ! -f "$ROOT_DIR/index.html" ]]; then
  cp "$NGINX_SRC/ulp-root-index.html.example" "$ROOT_DIR/index.html"
elif [[ "$FORCE" == "1" ]]; then
  cp "$NGINX_SRC/ulp-root-index.html.example" "$ROOT_DIR/index.html"
fi

if [[ ! -f "$ROOT_DIR/.well-known/ulp.json" ]]; then
  cp "$NGINX_SRC/ulp-well-known.json.example" "$ROOT_DIR/.well-known/ulp.json"
fi

for conf in \
  00-root-and-discovery.conf.example \
  10-mcp.conf.example \
  20-portal.conf.example \
  30-artifact.conf.example \
  40-sid-oid.conf.example \
  50-symbol-plane.conf.example
do
  target="${conf%.example}"
  if [[ -f "$SITE_AVAIL/$target" && "$FORCE" != "1" ]]; then
    echo "keep existing $SITE_AVAIL/$target (set FORCE=1 to overwrite)"
  else
    cp "$NGINX_SRC/$conf" "$SITE_AVAIL/$target"
  fi
  ln -sf "$SITE_AVAIL/$target" "$SITE_ENAB/$target"
done

nginx -t
systemctl reload nginx

echo "ok nginx vhosts installed"
echo "next: run certbot for all domains"
