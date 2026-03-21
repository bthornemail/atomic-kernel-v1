#!/usr/bin/env bash
set -euo pipefail

AK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEVOPS_ROOT="$(cd "$AK_ROOT/.." && pwd)"
MK_ROOT="$DEVOPS_ROOT/metaverse-kit"

ARTIFACTS_DIR="$AK_ROOT/artifacts"
PROOFS_DIR="$AK_ROOT/docs/proofs"
mkdir -p "$ARTIFACTS_DIR" "$PROOFS_DIR"

OUT_JSON="$ARTIFACTS_DIR/metaverse-future-scope-smoke.normalized.json"
OUT_HASH="$ARTIFACTS_DIR/metaverse-future-scope-smoke.replay-hash"
RECEIPT="$PROOFS_DIR/metaverse-future-scope-smoke.latest.md"

WITH_BENCHMARK=false
if [[ "${1:-}" == "--with-benchmark" ]]; then
  WITH_BENCHMARK=true
fi

if [[ ! -d "$MK_ROOT" ]]; then
  echo "missing metaverse-kit repo at: $MK_ROOT" >&2
  exit 1
fi

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
RESULTS_JSON="$WORK_DIR/results.jsonl"

record_result() {
  local key="$1"
  local status="$2"
  python3 - "$RESULTS_JSON" "$key" "$status" <<'PY'
import json, pathlib, sys
f = pathlib.Path(sys.argv[1])
obj = {"key": sys.argv[2], "status": sys.argv[3]}
with f.open("a", encoding="utf-8") as fp:
    fp.write(json.dumps(obj, sort_keys=True) + "\n")
PY
}

run_step() {
  local key="$1"
  shift
  echo "[scope] $key"
  if "$@" >"$WORK_DIR/$key.log" 2>&1; then
    record_result "$key" "pass"
  else
    sed -n '1,80p' "$WORK_DIR/$key.log" >&2 || true
    record_result "$key" "fail"
    echo "failed step: $key" >&2
    exit 1
  fi
}

doc_check_contains() {
  local key="$1"
  local file="$2"
  local pattern="$3"
  echo "[scope] $key"
  if rg -q "$pattern" "$file"; then
    record_result "$key" "pass"
  else
    echo "pattern not found: $pattern in $file" >&2
    record_result "$key" "fail"
    exit 1
  fi
}

# Atomic-kernel smoke/proof surface
run_step "ak_mcp_http_smoke" bash -lc "cd '$AK_ROOT' && HOST=127.0.0.1 PORT=18887 npm run -s mcp:unified:smoke"
run_step "ak_mcp_stdio_smoke" bash -lc "cd '$AK_ROOT' && npm run -s mcp:unified:stdio:smoke"
run_step "ak_world_v0_gate" bash -lc "cd '$AK_ROOT' && npm run -s world:v0:gate"
run_step "ak_workspace_snapshot_v0_gate" bash -lc "cd '$AK_ROOT' && npm run -s workspace:snapshot:v0:gate"
run_step "ak_source_capability_parity_gate" bash -lc "cd '$AK_ROOT' && npm run -s source:capability:parity:gate"
run_step "ak_universe_gate" bash -lc "cd '$AK_ROOT' && npm run -s universe:v0:gate"
run_step "ak_fork_import_gate" bash -lc "cd '$AK_ROOT' && bash scripts/fork-import-v1_2-gate.sh"
run_step "ak_release_gate" bash -lc "cd '$AK_ROOT' && ./scripts/release-gate.sh"

# metaverse-kit smoke/proof surface
run_step "mk_no_authority_gate" bash -lc "cd '$MK_ROOT' && ./scripts/no-authority-check.sh"
run_step "mk_portal_contract_gate" bash -lc "cd '$MK_ROOT' && npm run -s check:portal-contract"
run_step "mk_release_verify" bash -lc "cd '$MK_ROOT' && npm run -s release:verify"
run_step "mk_mcp_http_smoke" bash -lc "cd '$MK_ROOT' && MCP_SMOKE_PORT=18797 npm run -s mcp:unified:smoke"
run_step "mk_mcp_stdio_smoke" bash -lc "cd '$MK_ROOT' && npm run -s mcp:unified:stdio:smoke"
run_step "mk_mcp_contract_verify" bash -lc "cd '$MK_ROOT' && npm run -s mcp:contract:verify"

# Workspace spine
run_step "workspace_closure_spine" bash -lc "cd '$DEVOPS_ROOT' && ./scripts/closure-spine-smoke.sh"

# Docs integration checks
doc_check_contains "docs_ak_mcp_entrypoints_benchmark" "$AK_ROOT/docs/MCP_ENTRYPOINTS.md" "mcp:capability:benchmark"
doc_check_contains "docs_ak_mcp_entrypoints_a14_tool" "$AK_ROOT/docs/MCP_ENTRYPOINTS.md" "get_incidence_schedule_snapshot"
doc_check_contains "docs_ak_mcp_entrypoints_world_tools" "$AK_ROOT/docs/MCP_ENTRYPOINTS.md" "get_world_state"
doc_check_contains "docs_ak_index_chirality" "$AK_ROOT/docs/index.md" "Chirality Selection Law v0"
doc_check_contains "docs_ak_index_a14" "$AK_ROOT/docs/index.md" "A14 Incidence Scheduling Law v0"
doc_check_contains "docs_ak_index_world_spec" "$AK_ROOT/docs/index.md" "World Spec v0"

if [[ "$WITH_BENCHMARK" == "true" ]]; then
  run_step "ak_mcp_capability_benchmark" bash -lc "cd '$AK_ROOT' && npm run -s mcp:capability:benchmark"
  run_step "mk_runtime_scale_drill" bash -lc "cd '$MK_ROOT' && npm run -s runtime:scale:drill"
fi

python3 - "$RESULTS_JSON" "$OUT_JSON" "$WITH_BENCHMARK" "$AK_ROOT" "$MK_ROOT" <<'PY'
import hashlib
import json
import pathlib
import sys

results_path = pathlib.Path(sys.argv[1])
out_path = pathlib.Path(sys.argv[2])
with_benchmark = sys.argv[3] == "true"
ak_root = pathlib.Path(sys.argv[4])
mk_root = pathlib.Path(sys.argv[5])

items = []
for line in results_path.read_text(encoding="utf-8").splitlines():
  if line.strip():
    items.append(json.loads(line))

items_sorted = sorted(items, key=lambda x: x["key"])
if not all(i["status"] == "pass" for i in items_sorted):
  raise SystemExit("one or more scope checks failed")

benchmark_refs = {}
if with_benchmark:
  ak_bench_hash = ak_root / "artifacts" / "mcp-capability-benchmark.replay-hash"
  mk_scale_receipt = mk_root / "docs" / "proofs" / "runtime-scale-drill.latest.md"
  benchmark_refs = {
    "ak_mcp_capability_benchmark_hash": ak_bench_hash.read_text(encoding="utf-8").strip() if ak_bench_hash.exists() else None,
    "mk_runtime_scale_receipt_present": mk_scale_receipt.exists(),
  }

normalized = {
  "v": "ak.metaverse_future_scope_smoke.normalized.v0",
  "authority": "advisory",
  "scope": "cross_repo_smoke_and_docs_integration",
  "with_benchmark": with_benchmark,
  "checks": items_sorted,
  "benchmark_refs": benchmark_refs,
}

out_path.write_text(json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok metaverse future scope normalized")
PY

python3 - "$OUT_JSON" "$OUT_HASH" <<'PY'
import hashlib, pathlib, sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok metaverse future scope replay hash")
PY

TOTAL_CHECKS="$(python3 - "$OUT_JSON" <<'PY'
import json, pathlib, sys
d = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print(len(d["checks"]))
PY
)"

cat > "$RECEIPT" <<EOF
# Metaverse Future Scope Smoke Proof

Generated (UTC): $(date -u +%FT%TZ)
Repo: /home/main/devops/atomic-kernel

Command:
bash scripts/metaverse-future-scope-smoke.sh${WITH_BENCHMARK:+ --with-benchmark}

Scope:
- atomic-kernel smoke/proof gates
- metaverse-kit smoke/proof gates
- workspace closure spine
- docs integration checks for MCP/A14/chirality surfaces
- optional runtime benchmark/drill lane

Checks Executed: $TOTAL_CHECKS
With Benchmark: $WITH_BENCHMARK

Artifacts:
- artifacts/metaverse-future-scope-smoke.normalized.json
- artifacts/metaverse-future-scope-smoke.replay-hash ($(cat "$OUT_HASH"))

Result: PASS
EOF

echo "ok metaverse future scope smoke receipt=$RECEIPT"
