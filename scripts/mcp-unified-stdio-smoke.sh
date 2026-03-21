#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROOFS_DIR="$ROOT/docs/proofs"
ARTIFACTS_DIR="$ROOT/artifacts"
mkdir -p "$PROOFS_DIR" "$ARTIFACTS_DIR"

# Keep local stdio smoke aligned with constrained live-node scheduler defaults.
export MCP_MAX_LOAD_PER_CPU="${MCP_MAX_LOAD_PER_CPU:-1.0}"
export MCP_MIN_FREE_MEM_MB="${MCP_MIN_FREE_MEM_MB:-128}"

RECEIPT="$PROOFS_DIR/mcp-unified-stdio-smoke.latest.md"
ARTIFACT_JSON="$ARTIFACTS_DIR/mcp-unified-stdio-smoke.normalized.json"
ARTIFACT_HASH="$ARTIFACTS_DIR/mcp-unified-stdio-smoke.replay-hash"

KNOWN_PAGE_ID="${KNOWN_PAGE_ID:-protocol_spec}"
BLOCKED_PAGE_ID="__non_allowlisted_page_id__"

# Ensure world.v0 lane is present before MCP world tool probes.
bash "$ROOT/scripts/world-v0-gate.sh" >/dev/null
# Ensure virtual graph lane is present before MCP graph tool probes.
bash "$ROOT/scripts/capability-kernel-virtual-graph.sh" >/dev/null

norm1="$(mktemp)"
norm2="$(mktemp)"
trap 'rm -f "$norm1" "$norm2"' EXIT

python3 - "$ROOT" "$KNOWN_PAGE_ID" "$BLOCKED_PAGE_ID" "$norm1" <<'PY'
import hashlib, json, os, subprocess, sys
root, known_page_id, blocked_page_id, out = sys.argv[1:5]

def call(reqs):
    payload = "\n".join(json.dumps(r, separators=(",", ":")) for r in reqs) + "\n"
    p = subprocess.run(
        ["node", os.path.join(root, "scripts", "mcp-unified-stdio.mjs")],
        input=payload.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    lines = [x for x in p.stdout.decode().splitlines() if x.strip()]
    return [json.loads(x) for x in lines]

def parse_text_result(resp):
    c = resp["result"]["content"]
    if not isinstance(c, list) or not c or c[0].get("type") != "text":
        raise RuntimeError("invalid text content")
    return json.loads(c[0]["text"])

reqs = [
    {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"ak-smoke","version":"0.1.0"}}},
    {"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}},
    {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_control_plane_pages","arguments":{}}},
    {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_control_plane_page","arguments":{"id":known_page_id}}},
    {"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"get_control_plane_page","arguments":{"id":blocked_page_id}}},
    {"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"get_incidence_schedule_snapshot","arguments":{"start_tick":0,"ticks":4}}},
    {"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"get_capability_kernel_virtual_graph","arguments":{"include_nodes":False,"include_edges":False}}},
    {"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"refresh_capability_kernel_virtual_graph","arguments":{"refresh":False}}},
    {"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"get_world_state","arguments":{"world_id":"world0-orchard-garden-lattice"}}},
    {"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"get_world_projection","arguments":{"world_id":"world0-orchard-garden-lattice"}}},
    {"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"step_world","arguments":{"world_id":"world0-orchard-garden-lattice","step_request":{"actor_id":"tree-02","action":"set_state","target":"gate-01","requested_state":"open"}}}},
    {"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"verify_world","arguments":{"world_id":"world0-orchard-garden-lattice"}}}
]
resps = call(reqs)
by_id = {r.get("id"): r for r in resps}

tools = sorted([t["name"] for t in by_id[2]["result"]["tools"]])
required = [
    "list_control_plane_pages",
    "get_control_plane_page",
    "get_incidence_schedule_snapshot",
    "get_capability_kernel_virtual_graph",
    "refresh_capability_kernel_virtual_graph",
    "get_world_state",
    "step_world",
    "get_world_projection",
    "verify_world"
]
missing = [t for t in required if t not in tools]
if missing:
    raise RuntimeError("missing required tools: " + ",".join(missing))

pages = parse_text_result(by_id[3])
page = parse_text_result(by_id[4])
blocked = parse_text_result(by_id[5])
sched = parse_text_result(by_id[6])
graph = parse_text_result(by_id[7])
graph_refresh = parse_text_result(by_id[8])
world_state = parse_text_result(by_id[9])
world_proj = parse_text_result(by_id[10])
world_step = parse_text_result(by_id[11])
world_verify = parse_text_result(by_id[12])

if not any(p.get("id") == known_page_id for p in pages.get("pages", [])):
    raise RuntimeError("known page id not present in list")
if page.get("found") is not True or page.get("allowed") is not True:
    raise RuntimeError("known page fetch did not resolve")
if blocked.get("found") is not False or blocked.get("allowed") is not False:
    raise RuntimeError("blocked page fetch unexpectedly resolved")
if sched.get("valid") is not True:
    raise RuntimeError("schedule snapshot invalid")
rows = sched.get("rows")
if not isinstance(rows, list) or len(rows) == 0:
    raise RuntimeError("schedule snapshot empty")
for k in ["canonical_tick","incidence_tick","proposal_state","fano_rank","eligible"]:
    if k not in rows[0]:
        raise RuntimeError(f"schedule row missing field: {k}")
if world_state.get("found") is not True:
    raise RuntimeError("world state fetch failed")
if graph.get("found") is not True:
    raise RuntimeError("capability graph fetch failed")
if graph_refresh.get("valid") is not True or graph_refresh.get("executed") is not True:
    raise RuntimeError("capability graph refresh failed")
if world_proj.get("found") is not True:
    raise RuntimeError("world projection fetch failed")
if world_step.get("valid") is not True or world_step.get("proposal_only") is not True or world_step.get("committed") is not False:
    raise RuntimeError("world step boundary failed")
if not world_step.get("proposal_path") or not world_step.get("receipt_path"):
    raise RuntimeError("world step missing proposal/receipt refs")
if world_verify.get("valid") is not True:
    raise RuntimeError("world verify failed")

norm = {
    "v": "ak.mcp_unified_stdio_smoke.normalized.v0",
    "authority": "advisory",
    "transport": "stdio",
    "known_page_id": known_page_id,
    "required_tools": required,
    "tools": tools,
    "page": {
        "id": page.get("page_id"),
        "title": page.get("title"),
        "version": page.get("version"),
        "path": page.get("path"),
        "content_sha256": page.get("content_sha256")
    },
    "incidence_schedule": {
        "law": sched.get("law"),
        "ticks": sched.get("ticks"),
        "rows": len(rows),
        "schedule_sha256": sched.get("schedule_sha256")
    },
    "capability_graph": {
        "workspace_id": graph.get("workspace_id"),
        "project_count_analyzed": graph.get("project_count_analyzed"),
        "node_count": graph.get("node_count"),
        "edge_count": graph.get("edge_count"),
        "normalized_sha256": graph.get("normalized_sha256"),
        "projection_sha256": graph.get("projection_sha256"),
        "replay_hash": graph.get("replay_hash"),
        "refresh": {
            "workspace_id": graph_refresh.get("workspace_id"),
            "normalized_sha256": graph_refresh.get("normalized_sha256"),
            "replay_hash": graph_refresh.get("replay_hash")
        }
    },
    "world": {
        "world_id": world_state.get("world_id"),
        "world_sha256": world_state.get("world_sha256"),
        "projection_sha256": world_proj.get("projection_sha256"),
        "step": {
            "proposal_only": world_step.get("proposal_only"),
            "proposal_ref_present": bool(world_step.get("proposal_path")),
            "receipt_ref_present": bool(world_step.get("receipt_path")),
            "committed": world_step.get("committed")
        },
        "verify_valid": world_verify.get("valid")
    },
    "non_allowlisted_resolution": {
        "page_id": blocked_page_id,
        "found": blocked.get("found"),
        "allowed": blocked.get("allowed"),
        "reason": blocked.get("reason")
    }
}

with open(out, "w", encoding="utf-8") as f:
    f.write(json.dumps(norm, sort_keys=True, separators=(",", ":")) + "\n")
PY

python3 - "$ROOT" "$KNOWN_PAGE_ID" "$BLOCKED_PAGE_ID" "$norm2" <<'PY'
import hashlib, json, os, subprocess, sys
root, known_page_id, blocked_page_id, out = sys.argv[1:5]

def call(reqs):
    payload = "\n".join(json.dumps(r, separators=(",", ":")) for r in reqs) + "\n"
    p = subprocess.run(
        ["node", os.path.join(root, "scripts", "mcp-unified-stdio.mjs")],
        input=payload.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    lines = [x for x in p.stdout.decode().splitlines() if x.strip()]
    return [json.loads(x) for x in lines]

def parse_text_result(resp):
    c = resp["result"]["content"]
    return json.loads(c[0]["text"])

reqs = [
    {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"ak-smoke","version":"0.1.0"}}},
    {"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}},
    {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_control_plane_pages","arguments":{}}},
    {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_control_plane_page","arguments":{"id":known_page_id}}},
    {"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"get_control_plane_page","arguments":{"id":blocked_page_id}}},
    {"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"get_incidence_schedule_snapshot","arguments":{"start_tick":0,"ticks":4}}},
    {"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"get_capability_kernel_virtual_graph","arguments":{"include_nodes":False,"include_edges":False}}},
    {"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"refresh_capability_kernel_virtual_graph","arguments":{"refresh":False}}},
    {"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"get_world_state","arguments":{"world_id":"world0-orchard-garden-lattice"}}},
    {"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"get_world_projection","arguments":{"world_id":"world0-orchard-garden-lattice"}}},
    {"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"step_world","arguments":{"world_id":"world0-orchard-garden-lattice","step_request":{"actor_id":"tree-02","action":"set_state","target":"gate-01","requested_state":"open"}}}},
    {"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"verify_world","arguments":{"world_id":"world0-orchard-garden-lattice"}}}
]
resps = call(reqs)
by_id = {r.get("id"): r for r in resps}
tools = sorted([t["name"] for t in by_id[2]["result"]["tools"]])
page = parse_text_result(by_id[4])
blocked = parse_text_result(by_id[5])
sched = parse_text_result(by_id[6])
graph = parse_text_result(by_id[7])
graph_refresh = parse_text_result(by_id[8])
world_state = parse_text_result(by_id[9])
world_proj = parse_text_result(by_id[10])
world_step = parse_text_result(by_id[11])
world_verify = parse_text_result(by_id[12])
norm = {
    "v": "ak.mcp_unified_stdio_smoke.normalized.v0",
    "authority": "advisory",
    "transport": "stdio",
    "known_page_id": known_page_id,
    "required_tools": [
        "list_control_plane_pages",
        "get_control_plane_page",
        "get_incidence_schedule_snapshot",
        "get_capability_kernel_virtual_graph",
        "refresh_capability_kernel_virtual_graph",
        "get_world_state",
        "step_world",
        "get_world_projection",
        "verify_world"
    ],
    "tools": tools,
    "page": {
        "id": page.get("page_id"),
        "title": page.get("title"),
        "version": page.get("version"),
        "path": page.get("path"),
        "content_sha256": page.get("content_sha256")
    },
    "incidence_schedule": {
        "law": sched.get("law"),
        "ticks": sched.get("ticks"),
        "rows": len(sched.get("rows", [])),
        "schedule_sha256": sched.get("schedule_sha256")
    },
    "capability_graph": {
        "workspace_id": graph.get("workspace_id"),
        "project_count_analyzed": graph.get("project_count_analyzed"),
        "node_count": graph.get("node_count"),
        "edge_count": graph.get("edge_count"),
        "normalized_sha256": graph.get("normalized_sha256"),
        "projection_sha256": graph.get("projection_sha256"),
        "replay_hash": graph.get("replay_hash"),
        "refresh": {
            "workspace_id": graph_refresh.get("workspace_id"),
            "normalized_sha256": graph_refresh.get("normalized_sha256"),
            "replay_hash": graph_refresh.get("replay_hash")
        }
    },
    "world": {
        "world_id": world_state.get("world_id"),
        "world_sha256": world_state.get("world_sha256"),
        "projection_sha256": world_proj.get("projection_sha256"),
        "step": {
            "proposal_only": world_step.get("proposal_only"),
            "proposal_ref_present": bool(world_step.get("proposal_path")),
            "receipt_ref_present": bool(world_step.get("receipt_path")),
            "committed": world_step.get("committed")
        },
        "verify_valid": world_verify.get("valid")
    },
    "non_allowlisted_resolution": {
        "page_id": blocked_page_id,
        "found": blocked.get("found"),
        "allowed": blocked.get("allowed"),
        "reason": blocked.get("reason")
    }
}
with open(out, "w", encoding="utf-8") as f:
    f.write(json.dumps(norm, sort_keys=True, separators=(",", ":")) + "\n")
PY

cmp -s "$norm1" "$norm2" || { echo "determinism check failed: normalized outputs differ" >&2; exit 1; }
cp "$norm1" "$ARTIFACT_JSON"

python3 - "$ARTIFACT_JSON" "$ARTIFACT_HASH" <<'PY'
import hashlib, pathlib, sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
h = hashlib.sha256(artifact.read_bytes()).hexdigest()
out.write_text(f"sha256:{h}\n", encoding="utf-8")
PY

sha="$(cat "$ARTIFACT_HASH")"
cat > "$RECEIPT" <<EOF
# MCP Unified STDIO Smoke Proof

Date: $(date -u +%F)
Generated (UTC): $(date -u +%FT%TZ)
Repo: /home/main/devops/atomic-kernel

Command Invoked:
npm run -s mcp:unified:stdio:smoke

Server Entry:
npm run -s mcp:unified:stdio

Checks:
stdio boot: PASS
tool list: PASS
list_control_plane_pages: PASS
get_control_plane_page($KNOWN_PAGE_ID): PASS
get_incidence_schedule_snapshot: PASS
get_capability_kernel_virtual_graph: PASS
refresh_capability_kernel_virtual_graph: PASS
get_world_state: PASS
get_world_projection: PASS
step_world proposal-only path: PASS
verify_world: PASS
non-allowlisted page fetch blocked: PASS
deterministic rerun byte-compare: PASS

Expected Tools Found:
list_control_plane_pages, get_control_plane_page, get_incidence_schedule_snapshot, get_capability_kernel_virtual_graph, refresh_capability_kernel_virtual_graph, get_world_state, step_world, get_world_projection, verify_world

Deterministic Artifacts:
artifacts/mcp-unified-stdio-smoke.normalized.json
artifacts/mcp-unified-stdio-smoke.replay-hash ($sha)

Result: PASS
EOF

echo "ok atomic-kernel mcp unified stdio smoke receipt=$RECEIPT"
