#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "run as root" >&2
  exit 1
fi

USER_NAME="${1:-akops}"
PUBKEY="${2:-}"

if [[ -z "$PUBKEY" ]]; then
  echo "usage: $0 <username> \"<ssh-public-key>\"" >&2
  exit 1
fi

if ! id "$USER_NAME" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$USER_NAME"
fi

usermod -aG sudo "$USER_NAME"

HOME_DIR="$(eval echo "~$USER_NAME")"
install -d -m 700 -o "$USER_NAME" -g "$USER_NAME" "$HOME_DIR/.ssh"
AUTH_KEYS="$HOME_DIR/.ssh/authorized_keys"
touch "$AUTH_KEYS"
chmod 600 "$AUTH_KEYS"
chown "$USER_NAME:$USER_NAME" "$AUTH_KEYS"

if ! grep -qxF "$PUBKEY" "$AUTH_KEYS"; then
  echo "$PUBKEY" >> "$AUTH_KEYS"
fi

echo "ok operator user configured user=$USER_NAME"
