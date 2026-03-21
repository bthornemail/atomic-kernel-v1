# Live Governed Node v1 (IONOS VPS)

Status: Operational Runbook  
Authority: Advisory (deployment procedure)  
Scope: control-plane node only (no portal/app hosting)

This bundle stands up a hardened VPS node that runs `atomic-kernel` MCP + deterministic gate timers.

## What this node runs

- `atomic-kernel` as canonical runtime
- MCP unified HTTP server (bound localhost, published via Nginx TLS)
- systemd timers for:
  - smoke gates
  - workspace snapshot gate
  - source capability parity gate
- SID/OID resolver service (`ulp-resolver.service`)
- symbol interpreter service (`ulp-symbol.service`)

## What this node does not run (v1)

- `metaverse-kit` portal/API surfaces
- heavy analysis/build workloads
- public raw MCP port exposure

## Quick sequence

1. SSH in as root and copy this folder onto the VPS.
2. Run bootstrap:

```bash
cd /opt/atomic-kernel/ops/live-node-v1
sudo bash bootstrap-vps.sh
```

3. Create operator user + SSH key:

```bash
sudo bash create-operator-user.sh akops "<PUBKEY>"
```

4. Install runtime + clone repo:

```bash
sudo bash setup-runtime.sh \
  --repo-url https://github.com/bthornemail/atomic-kernel.git \
  --repo-dir /opt/atomic-kernel
```

5. Install systemd units/timers:

```bash
sudo bash install-systemd.sh
```

6. Configure Nginx reverse proxy:

```bash
sudo bash install-nginx-vhosts.sh
```

Then edit these installed files for your exact domain/targets:

- `/etc/nginx/sites-available/00-root-and-discovery.conf`
- `/etc/nginx/sites-available/10-mcp.conf`
- `/etc/nginx/sites-available/20-portal.conf`
- `/etc/nginx/sites-available/40-sid-oid.conf`
- `/etc/nginx/sites-available/50-symbol-plane.conf`

And set discovery doc:

- `/var/www/ulp-root/.well-known/ulp.json`

7. Issue TLS cert:

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

8. Harden SSH password/root settings (after key login verified):

```bash
sudo bash harden-ssh.sh
```

9. Validate node:

```bash
sudo bash verify-node.sh
```

## One-command apply (recommended after repo sync)

If the repo is already present at `/opt/atomic-kernel`, apply all node services + vhosts and verify:

```bash
cd /opt/atomic-kernel/ops/live-node-v1
sudo bash apply-live-node-v1.sh /opt/atomic-kernel mcp.universal-life-protocol.com
```

## Expected public interface

- `https://<your-domain>/mcp`
- `https://sid.<your-domain>/...` (resolver API)
- `https://oid.<your-domain>/...` (resolver API)
- `https://fs|gs|rs|us|esc|null|codepoint|controlpoint.<your-domain>/...` (symbol API)

Raw MCP port is local-only by default (`127.0.0.1:18787`).
