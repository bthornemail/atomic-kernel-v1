#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_ROOT="/home/main/devops"
REPORTS_ROOT="$ROOT/reports/workspace"
ARTIFACTS_DIR="$ROOT/artifacts"
PROOFS_DIR="$ROOT/docs/proofs"
mkdir -p "$ARTIFACTS_DIR" "$PROOFS_DIR"

RUN_ID=""
REFRESH=false
ALLOWLIST="atomic-kernel,metaverse-kit,tetragrammatron-os,automaton,autonomous-ai,waveform-core,universal-life-protocol"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-id)
      RUN_ID="${2:-}"
      shift 2
      ;;
    --refresh)
      REFRESH=true
      shift
      ;;
    --allowlist)
      ALLOWLIST="${2:-}"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ "$REFRESH" == "true" ]]; then
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  RUN_ID="capability-graph-${stamp}"
  MANIFEST="$REPORTS_ROOT/${RUN_ID}.manifest.json"
  python3 "$ROOT/scripts/build-workspace-manifest.py" --workspace "$WORKSPACE_ROOT" --out "$MANIFEST" >/dev/null
  python3 "$ROOT/scripts/validate-workspace-manifest.py" --manifest "$MANIFEST" >/dev/null
  bash "$ROOT/scripts/run-workspace-ingest.sh" \
    --workspace "$WORKSPACE_ROOT" \
    --manifest "$MANIFEST" \
    --out-root "$REPORTS_ROOT" \
    --run-id "$RUN_ID" \
    --allowlist "$ALLOWLIST" \
    >/dev/null
fi

if [[ -z "$RUN_ID" ]]; then
  RUN_ID="$(basename "$(ls -td "$REPORTS_ROOT"/devops-scan-* 2>/dev/null | head -n 1)")"
fi
if [[ -z "$RUN_ID" ]]; then
  RUN_ID="$(basename "$(ls -td "$REPORTS_ROOT"/capability-graph-* 2>/dev/null | head -n 1)")"
fi
[[ -n "$RUN_ID" ]] || { echo "no workspace run-id available" >&2; exit 1; }

RUN_DIR="$REPORTS_ROOT/$RUN_ID"
SUMMARY_JSON="$RUN_DIR/workspace-summary.json"
INDEX_JSON="$RUN_DIR/project-index.json"
[[ -f "$SUMMARY_JSON" ]] || { echo "missing workspace summary: $SUMMARY_JSON" >&2; exit 1; }
[[ -f "$INDEX_JSON" ]] || { echo "missing project index: $INDEX_JSON" >&2; exit 1; }

OUT_JSON="$ARTIFACTS_DIR/capability-kernel-virtual-graph.normalized.json"
OUT_PROJECTION="$ARTIFACTS_DIR/capability-kernel-virtual-graph.projection.json"
OUT_MERMAID="$ARTIFACTS_DIR/capability-kernel-virtual-graph.mermaid.md"
OUT_HASH="$ARTIFACTS_DIR/capability-kernel-virtual-graph.replay-hash"
RECEIPT="$PROOFS_DIR/capability-kernel-virtual-graph.latest.md"

python3 - "$SUMMARY_JSON" "$RUN_DIR/projects" "$OUT_JSON" "$OUT_PROJECTION" "$OUT_MERMAID" <<'PY'
import json
import pathlib
import sys

summary_path = pathlib.Path(sys.argv[1])
projects_root = pathlib.Path(sys.argv[2])
out_json = pathlib.Path(sys.argv[3])
out_projection = pathlib.Path(sys.argv[4])
out_mermaid = pathlib.Path(sys.argv[5])

summary = json.loads(summary_path.read_text(encoding="utf-8"))
reports = summary.get("project_reports", [])

nodes = []
edges = []

workspace_id = summary["workspace_id"]
workspace_node = {
    "id": f"workspace:{workspace_id}",
    "kind": "workspace",
    "label": workspace_id,
    "authority": "advisory"
}
nodes.append(workspace_node)

analyzed_reports = [r for r in reports if r.get("analyzed")]
analyzed_reports.sort(key=lambda r: r["project_id"])

lang_totals = {}
domain_totals = {}
pattern_totals = {}

for row in analyzed_reports:
    pid = row["project_id"]
    report_path = projects_root / pid / "report.json"
    if not report_path.exists():
        continue
    report = json.loads(report_path.read_text(encoding="utf-8"))
    s = report.get("summary", {})
    project_node_id = f"project:{pid}"
    nodes.append({
        "id": project_node_id,
        "kind": "project",
        "label": pid,
        "authority": "advisory",
        "files": int(s.get("files", 0)),
        "asg_nodes": int(s.get("asg_nodes", 0)),
        "asg_edges": int(s.get("asg_edges", 0)),
    })
    edges.append({
        "from": workspace_node["id"],
        "to": project_node_id,
        "kind": "contains_project",
        "weight": 1
    })

    for lang, count in sorted(s.get("language_counts", {}).items()):
        lang_node = f"lang:{lang}"
        lang_totals[lang] = lang_totals.get(lang, 0) + int(count)
        edges.append({
            "from": project_node_id,
            "to": lang_node,
            "kind": "uses_language",
            "weight": int(count)
        })

    for domain, count in sorted(s.get("domain_counts", {}).items()):
        domain_node = f"domain:{domain}"
        domain_totals[domain] = domain_totals.get(domain, 0) + int(count)
        edges.append({
            "from": project_node_id,
            "to": domain_node,
            "kind": "emits_domain_surface",
            "weight": int(count)
        })

    for pattern, count in sorted(s.get("patterns", {}).items()):
        pat_node = f"pattern:{pattern}"
        pattern_totals[pattern] = pattern_totals.get(pattern, 0) + int(count)
        edges.append({
            "from": project_node_id,
            "to": pat_node,
            "kind": "matches_pattern",
            "weight": int(count)
        })

for lang, count in sorted(lang_totals.items()):
    nodes.append({"id": f"lang:{lang}", "kind": "language", "label": lang, "authority": "advisory", "total": count})
for domain, count in sorted(domain_totals.items()):
    nodes.append({"id": f"domain:{domain}", "kind": "domain", "label": domain, "authority": "advisory", "total": count})
for pattern, count in sorted(pattern_totals.items()):
    nodes.append({"id": f"pattern:{pattern}", "kind": "pattern", "label": pattern, "authority": "advisory", "total": count})

# deterministic sort
nodes = sorted(nodes, key=lambda n: (n["kind"], n["id"]))
edges = sorted(edges, key=lambda e: (e["from"], e["to"], e["kind"], e["weight"]))

normalized = {
    "v": "capability_kernel_virtual_graph.normalized.v0",
    "authority": "advisory",
    "workspace_id": workspace_id,
    "source_workspace_summary": str(summary_path),
    "project_count_analyzed": len(analyzed_reports),
    "node_count": len(nodes),
    "edge_count": len(edges),
    "nodes": nodes,
    "edges": edges,
    "totals": {
        "language": {k: lang_totals[k] for k in sorted(lang_totals.keys())},
        "domain": {k: domain_totals[k] for k in sorted(domain_totals.keys())},
        "pattern": {k: pattern_totals[k] for k in sorted(pattern_totals.keys())}
    }
}
out_json.write_text(json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

projection = {
    "v": "capability_kernel_virtual_graph.projection.v0",
    "authority": "advisory",
    "workspace_id": workspace_id,
    "summary": {
        "projects": len(analyzed_reports),
        "languages": len(lang_totals),
        "domains": len(domain_totals),
        "patterns": len(pattern_totals)
    },
    "top_languages": sorted(lang_totals.items(), key=lambda kv: (-kv[1], kv[0]))[:10],
    "top_domains": sorted(domain_totals.items(), key=lambda kv: (-kv[1], kv[0]))[:10],
    "top_patterns": sorted(pattern_totals.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
}
out_projection.write_text(json.dumps(projection, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

lines = ["```mermaid", "graph TD"]
lines.append(f"  W[{workspace_id}]")
for row in analyzed_reports:
    pid = row["project_id"]
    nid = pid.replace("-", "_")
    lines.append(f"  W --> P_{nid}[{pid}]")
for lang in sorted(lang_totals.keys()):
    lid = lang.replace("-", "_")
    lines.append(f"  L_{lid}[lang:{lang}]")
for domain in sorted(domain_totals.keys()):
    did = domain.replace("-", "_")
    lines.append(f"  D_{did}[domain:{domain}]")
lines.append("```")
out_mermaid.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("ok capability kernel virtual graph")
PY

python3 - "$OUT_JSON" "$OUT_HASH" <<'PY'
import hashlib
import pathlib
import sys
artifact = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.write_text("sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() + "\n", encoding="utf-8")
print("ok capability kernel virtual graph replay hash")
PY

cat > "$RECEIPT" <<EOF2
# Capability Kernel Virtual Graph Proof

Generated (UTC): $(date -u +%FT%TZ)
Repo: /home/main/devops/atomic-kernel

Command:
bash scripts/capability-kernel-virtual-graph.sh${REFRESH:+ --refresh}

Source:
workspace run-id: $RUN_ID
workspace summary: $SUMMARY_JSON

Checks:
workspace summary present: PASS
project index present: PASS
analyzed project graph extraction: PASS
deterministic normalized graph artifact emitted: PASS
projection artifact emitted: PASS
mermaid projection emitted: PASS

Artifacts:
- artifacts/capability-kernel-virtual-graph.normalized.json
- artifacts/capability-kernel-virtual-graph.projection.json
- artifacts/capability-kernel-virtual-graph.mermaid.md
- artifacts/capability-kernel-virtual-graph.replay-hash ($(cat "$OUT_HASH"))

Result: PASS
EOF2

echo "ok capability kernel virtual graph gate"
