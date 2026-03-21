#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$ROOT/artifacts"
PROOFS_DIR="$ROOT/docs/proofs"
mkdir -p "$ARTIFACTS_DIR" "$PROOFS_DIR"

OUT_JSON="$ARTIFACTS_DIR/mcp-capability-benchmark.normalized.json"
OUT_HASH="$ARTIFACTS_DIR/mcp-capability-benchmark.replay-hash"
RECEIPT="$PROOFS_DIR/mcp-capability-benchmark.latest.md"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-18787}"
MCP_URL="http://$HOST:$PORT/mcp"

ITER_HTTP="${ITER_HTTP:-30}"
ITER_STDIO="${ITER_STDIO:-20}"

# Optional thresholds. If set, benchmark fails when exceeded.
MAX_HTTP_P95_MS="${MAX_HTTP_P95_MS:-}"
MAX_STDIO_P95_MS="${MAX_STDIO_P95_MS:-}"

SERVER_LOG="$(mktemp)"
server_pid=""
cleanup() {
  if [[ -n "${server_pid:-}" ]]; then
    kill "$server_pid" >/dev/null 2>&1 || true
    wait "$server_pid" >/dev/null 2>&1 || true
  fi
  rm -f "$SERVER_LOG"
}
trap cleanup EXIT

HOST="$HOST" PORT="$PORT" npm run -s mcp:unified:server >"$SERVER_LOG" 2>&1 &
server_pid="$!"

python3 - "$MCP_URL" "$ITER_HTTP" "$ITER_STDIO" "$OUT_JSON" "$MAX_HTTP_P95_MS" "$MAX_STDIO_P95_MS" "$ROOT" <<'PY'
import json
import statistics
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

url = sys.argv[1]
iter_http = int(sys.argv[2])
iter_stdio = int(sys.argv[3])
out_json = Path(sys.argv[4])
max_http_p95 = float(sys.argv[5]) if sys.argv[5] else None
max_stdio_p95 = float(sys.argv[6]) if sys.argv[6] else None
root = Path(sys.argv[7])

tools = [
    ("list_control_plane_pages", {}),
    ("get_control_plane_page", {"id": "protocol_spec"}),
    ("get_incidence_schedule_snapshot", {"start_tick": 0, "ticks": 8}),
    ("verify_mcp_contract", {"strict": True}),
]

def percentile(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    idx = (len(sorted_vals) - 1) * p
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return float(sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac)

def wait_ready():
    init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "ak-mcp-benchmark", "version": "0.1.0"},
        },
    }
    for _ in range(60):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(init).encode("utf-8"),
                headers={"content-type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=1.0) as r:
                if r.status == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError("HTTP MCP server did not become ready")

def http_rpc(req_obj):
    req = urllib.request.Request(
        url,
        data=json.dumps(req_obj).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5.0) as r:
        return json.loads(r.read().decode("utf-8"))

def parse_tool_text(resp):
    content = resp["result"]["content"]
    return json.loads(content[0]["text"])

def run_http_bench():
    # initialize once
    http_rpc({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "ak-mcp-benchmark", "version": "0.1.0"},
        },
    })
    lat_by_tool = {name: [] for name, _ in tools}
    ok = {name: True for name, _ in tools}
    t0 = time.perf_counter()
    rid = 10
    for _ in range(iter_http):
        for name, args in tools:
            start = time.perf_counter()
            resp = http_rpc({
                "jsonrpc": "2.0",
                "id": rid,
                "method": "tools/call",
                "params": {"name": name, "arguments": args},
            })
            rid += 1
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            lat_by_tool[name].append(elapsed_ms)
            try:
                parsed = parse_tool_text(resp)
                if parsed.get("authority") != "advisory":
                    ok[name] = False
                if name == "verify_mcp_contract" and parsed.get("valid") is not True:
                    ok[name] = False
                if name == "get_control_plane_page" and parsed.get("found") is not True:
                    ok[name] = False
                if name == "get_incidence_schedule_snapshot" and parsed.get("valid") is not True:
                    ok[name] = False
            except Exception:
                ok[name] = False
    total_s = max(time.perf_counter() - t0, 1e-9)
    total_calls = iter_http * len(tools)
    ops = total_calls / total_s
    return lat_by_tool, ok, ops, total_calls

def run_stdio_single(name, args):
    reqs = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "ak-mcp-benchmark", "version": "0.1.0"},
            },
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": name, "arguments": args},
        },
    ]
    payload = "\n".join(json.dumps(r, separators=(",", ":")) for r in reqs) + "\n"
    p = subprocess.run(
        ["node", str(root / "scripts" / "mcp-unified-stdio.mjs")],
        input=payload.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    lines = [x for x in p.stdout.decode("utf-8").splitlines() if x.strip()]
    return json.loads(lines[-1])

def run_stdio_bench():
    lat_by_tool = {name: [] for name, _ in tools}
    ok = {name: True for name, _ in tools}
    t0 = time.perf_counter()
    for _ in range(iter_stdio):
        for name, args in tools:
            start = time.perf_counter()
            resp = run_stdio_single(name, args)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            lat_by_tool[name].append(elapsed_ms)
            try:
                parsed = json.loads(resp["result"]["content"][0]["text"])
                if parsed.get("authority") != "advisory":
                    ok[name] = False
                if name == "verify_mcp_contract" and parsed.get("valid") is not True:
                    ok[name] = False
                if name == "get_control_plane_page" and parsed.get("found") is not True:
                    ok[name] = False
                if name == "get_incidence_schedule_snapshot" and parsed.get("valid") is not True:
                    ok[name] = False
            except Exception:
                ok[name] = False
    total_s = max(time.perf_counter() - t0, 1e-9)
    total_calls = iter_stdio * len(tools)
    ops = total_calls / total_s
    return lat_by_tool, ok, ops, total_calls

def summarize(lat_by_tool):
    tool_summary = {}
    all_vals = []
    for name, vals in lat_by_tool.items():
        s = sorted(vals)
        all_vals.extend(s)
        tool_summary[name] = {
            "calls": len(vals),
            "p50_ms": round(percentile(s, 0.50), 3),
            "p95_ms": round(percentile(s, 0.95), 3),
            "max_ms": round(max(s) if s else 0.0, 3),
            "mean_ms": round(statistics.fmean(s) if s else 0.0, 3),
        }
    all_sorted = sorted(all_vals)
    overall = {
        "calls": len(all_vals),
        "p50_ms": round(percentile(all_sorted, 0.50), 3),
        "p95_ms": round(percentile(all_sorted, 0.95), 3),
        "max_ms": round(max(all_sorted) if all_sorted else 0.0, 3),
        "mean_ms": round(statistics.fmean(all_sorted) if all_sorted else 0.0, 3),
    }
    return tool_summary, overall

wait_ready()
http_lat, http_ok, http_ops, http_calls = run_http_bench()
stdio_lat, stdio_ok, stdio_ops, stdio_calls = run_stdio_bench()

http_tools, http_overall = summarize(http_lat)
stdio_tools, stdio_overall = summarize(stdio_lat)

thresholds = {
    "max_http_p95_ms": max_http_p95,
    "max_stdio_p95_ms": max_stdio_p95,
}
threshold_failures = []
if max_http_p95 is not None and http_overall["p95_ms"] > max_http_p95:
    threshold_failures.append("http_p95_exceeded")
if max_stdio_p95 is not None and stdio_overall["p95_ms"] > max_stdio_p95:
    threshold_failures.append("stdio_p95_exceeded")

all_tools_ok = all(http_ok.values()) and all(stdio_ok.values())
pass_result = all_tools_ok and not threshold_failures

out = {
    "v": "ak.mcp_capability_benchmark.normalized.v0",
    "authority": "advisory",
    "benchmark_scope": "capability_runtime",
    "transports": {
        "http": {
            "iterations": iter_http,
            "total_calls": http_calls,
            "ops_per_sec": round(http_ops, 3),
            "tools_ok": http_ok,
            "tool_latency_ms": http_tools,
            "overall_latency_ms": http_overall,
        },
        "stdio": {
            "iterations": iter_stdio,
            "total_calls": stdio_calls,
            "ops_per_sec": round(stdio_ops, 3),
            "tools_ok": stdio_ok,
            "tool_latency_ms": stdio_tools,
            "overall_latency_ms": stdio_overall,
        },
    },
    "thresholds": thresholds,
    "threshold_failures": threshold_failures,
    "result": {"pass": pass_result},
}

out_json.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok mcp capability benchmark complete")
PY

python3 - "$OUT_JSON" "$OUT_HASH" <<'PY'
import hashlib, pathlib, sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok mcp capability benchmark replay hash")
PY

python3 - "$OUT_JSON" "$RECEIPT" "$OUT_HASH" "$ITER_HTTP" "$ITER_STDIO" "$MCP_URL" <<'PY'
import datetime
import json
import pathlib
import sys
artifact_path = pathlib.Path(sys.argv[1])
receipt_path = pathlib.Path(sys.argv[2])
hash_path = pathlib.Path(sys.argv[3])
iter_http = sys.argv[4]
iter_stdio = sys.argv[5]
mcp_url = sys.argv[6]

data = json.loads(artifact_path.read_text(encoding="utf-8"))
sha = hash_path.read_text(encoding="utf-8").strip()
status = "PASS" if data.get("result", {}).get("pass") else "FAIL"
now = datetime.datetime.now(datetime.timezone.utc)
date_str = now.strftime("%Y-%m-%d")
ts_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")

receipt = f"""# MCP Capability Benchmark Proof

Date: {date_str}
Generated (UTC): {ts_str}
Repo: /home/main/devops/atomic-kernel

Command Invoked:
npm run -s mcp:capability:benchmark

Scope:
runtime capability benchmark (HTTP + STDIO)
iterations_http: {iter_http}
iterations_stdio: {iter_stdio}
http_endpoint: {mcp_url}

Transport Summary:
http ops/sec: {data['transports']['http']['ops_per_sec']}
http p95 ms: {data['transports']['http']['overall_latency_ms']['p95_ms']}
stdio ops/sec: {data['transports']['stdio']['ops_per_sec']}
stdio p95 ms: {data['transports']['stdio']['overall_latency_ms']['p95_ms']}

Threshold Failures:
{", ".join(data.get("threshold_failures", [])) if data.get("threshold_failures") else "(none)"}

Artifacts:
- artifacts/mcp-capability-benchmark.normalized.json
- artifacts/mcp-capability-benchmark.replay-hash ({sha})

Result: {status}
"""
receipt_path.write_text(receipt, encoding="utf-8")
print("ok mcp capability benchmark receipt")
PY

# fail closed on benchmark failure
python3 - "$OUT_JSON" <<'PY'
import json, pathlib, sys
data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
if data.get("result", {}).get("pass") is not True:
    raise SystemExit("mcp capability benchmark failed")
print("ok mcp capability benchmark pass")
PY

echo "ok mcp capability benchmark receipt=$RECEIPT"
