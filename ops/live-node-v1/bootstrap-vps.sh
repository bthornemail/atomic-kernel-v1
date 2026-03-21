#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "run as root" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get upgrade -y
apt-get install -y \
  ufw \
  fail2ban \
  git \
  curl \
  nginx \
  certbot \
  python3-certbot-nginx \
  jq \
  ca-certificates \
  logrotate

ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

systemctl enable --now fail2ban
systemctl enable --now nginx

echo "ok bootstrap vps complete"
