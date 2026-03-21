#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "run as root" >&2
  exit 1
fi

SSHD_CONFIG="/etc/ssh/sshd_config"
BACKUP="/etc/ssh/sshd_config.bak.$(date -u +%Y%m%d%H%M%S)"
cp "$SSHD_CONFIG" "$BACKUP"

set_or_add() {
  local key="$1"
  local value="$2"
  if grep -Eq "^[#[:space:]]*${key}[[:space:]]+" "$SSHD_CONFIG"; then
    sed -i -E "s|^[#[:space:]]*${key}[[:space:]]+.*|${key} ${value}|g" "$SSHD_CONFIG"
  else
    echo "${key} ${value}" >> "$SSHD_CONFIG"
  fi
}

set_or_add "PermitRootLogin" "no"
set_or_add "PasswordAuthentication" "no"
set_or_add "PubkeyAuthentication" "yes"
set_or_add "ChallengeResponseAuthentication" "no"
set_or_add "UsePAM" "yes"

sshd -t
systemctl reload ssh || systemctl reload sshd

echo "ok ssh hardened backup=$BACKUP"
