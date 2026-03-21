# Live Governed Node v1 Runbook
Status: Advisory
Authority: Extension
Depends on: `docs/MCP_ENTRYPOINTS.md`, `docs/WORKSPACE_SNAPSHOT_SPEC_v0.md`, `docs/SOURCE_CAPABILITY_PARITY_v0.md`

Purpose: operationalize a control-plane-only VPS node for `atomic-kernel` with fail-closed deterministic gates.

## Node profile

- Role: control-plane governed node
- Runtime: `atomic-kernel`
- Public interface: `https://<domain>/mcp`
- Non-goals: portal/API hosting, heavy compute workloads

## Host baseline

The deployment bundle is in:

- `ops/live-node-v1/`

Main scripts:

- `bootstrap-vps.sh`
- `create-operator-user.sh`
- `setup-runtime.sh`
- `install-systemd.sh`
- `harden-ssh.sh`
- `verify-node.sh`

## Execution sequence

1. Bootstrap OS + firewall + baseline packages:

```bash
cd /opt/atomic-kernel/ops/live-node-v1
sudo bash bootstrap-vps.sh
```

2. Create operator user and install SSH key:

```bash
sudo bash create-operator-user.sh akops "<PUBKEY>"
```

3. Install Node 20 + clone runtime + install deps + env:

```bash
sudo bash setup-runtime.sh \
  --repo-url https://github.com/bthornemail/atomic-kernel.git \
  --repo-dir /opt/atomic-kernel
```

4. Install and enable systemd services/timers:

```bash
sudo bash install-systemd.sh
```

5. Configure Nginx reverse proxy:

```bash
sudo bash install-nginx-vhosts.sh
```

Edit deployed vhosts:

- `/etc/nginx/sites-available/00-root-and-discovery.conf`
- `/etc/nginx/sites-available/10-mcp.conf`
- `/etc/nginx/sites-available/20-portal.conf`
- `/etc/nginx/sites-available/30-artifact.conf`
- `/etc/nginx/sites-available/40-sid-oid.conf`
- `/etc/nginx/sites-available/50-symbol-plane.conf`

Discovery endpoint template:

- `/var/www/ulp-root/.well-known/ulp.json`

6. Issue TLS certificate:

```bash
sudo certbot --nginx \
  -d universal-life-protocol.com \
  -d www.universal-life-protocol.com \
  -d mcp.universal-life-protocol.com \
  -d portal.universal-life-protocol.com \
  -d artifact.universal-life-protocol.com \
  -d sid.universal-life-protocol.com \
  -d oid.universal-life-protocol.com \
  -d fs.universal-life-protocol.com \
  -d gs.universal-life-protocol.com \
  -d rs.universal-life-protocol.com \
  -d us.universal-life-protocol.com \
  -d esc.universal-life-protocol.com \
  -d null.universal-life-protocol.com \
  -d codepoint.universal-life-protocol.com \
  -d controlpoint.universal-life-protocol.com
```

7. Harden SSH (after key login verified):

```bash
sudo bash harden-ssh.sh
```

8. Validate node:

```bash
sudo bash verify-node.sh /opt/atomic-kernel <domain>
```

## Service model

- `atomic-kernel-mcp.service` (always on)
- `atomic-kernel-gates-smoke.timer` (every 15 min)
- `atomic-kernel-gates-snapshot.timer` (every 6h at `:00`)
- `atomic-kernel-gates-parity.timer` (every 6h at `:10`)

## Monitoring surfaces

Primary artifacts:

- `docs/proofs/*.latest.md`
- `artifacts/*.replay-hash`

Primary logs:

```bash
journalctl -u atomic-kernel-mcp.service -f
journalctl -u atomic-kernel-gates-smoke.service -n 100
journalctl -u atomic-kernel-gates-snapshot.service -n 100
journalctl -u atomic-kernel-gates-parity.service -n 100
```

## Boundary

Plesk is intentionally not in runtime orchestration.
This runbook does not change authority semantics; it only deploys existing governed surfaces.
