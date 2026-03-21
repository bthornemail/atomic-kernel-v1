#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "run as root" >&2
  exit 1
fi

REPO_URL=""
REPO_DIR="/opt/atomic-kernel"
RUN_USER="root"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-url)
      REPO_URL="${2:-}"
      shift 2
      ;;
    --repo-dir)
      REPO_DIR="${2:-}"
      shift 2
      ;;
    --run-user)
      RUN_USER="${2:-}"
      shift 2
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$REPO_URL" ]]; then
  echo "usage: $0 --repo-url <git-url> [--repo-dir /opt/atomic-kernel] [--run-user akops]" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

if [[ ! -d "$REPO_DIR/.git" ]]; then
  git clone "$REPO_URL" "$REPO_DIR"
else
  git -C "$REPO_DIR" fetch --all --prune
  git -C "$REPO_DIR" pull --ff-only
fi

if ! id "$RUN_USER" >/dev/null 2>&1; then
  echo "run-user does not exist: $RUN_USER" >&2
  exit 1
fi

chown -R "$RUN_USER:$RUN_USER" "$REPO_DIR"
sudo -u "$RUN_USER" bash -lc "cd '$REPO_DIR' && npm ci"

install -d -m 755 /etc/atomic-kernel
cp "$(dirname "$0")/config/node.env.example" /etc/atomic-kernel/node.env
chown root:root /etc/atomic-kernel/node.env
chmod 640 /etc/atomic-kernel/node.env

echo "ok runtime setup complete repo=$REPO_DIR node=$(node -v) npm=$(npm -v)"
