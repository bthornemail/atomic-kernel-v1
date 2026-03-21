#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { spawnSync } from "node:child_process";
import os from "node:os";

export const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const pagesCatalogFile = process.env.MCP_ALLOWED_PAGES_PATH
  ? path.resolve(root, process.env.MCP_ALLOWED_PAGES_PATH)
  : path.resolve(root, "docs/control-plane.pages.v0.json");

export const toolNames = [
  "list_control_plane_pages",
  "get_control_plane_page",
  "verify_mcp_contract",
  "get_incidence_schedule_snapshot",
  "get_capability_kernel_virtual_graph",
  "refresh_capability_kernel_virtual_graph",
  "get_world_state",
  "step_world",
  "get_world_projection",
  "verify_world",
  "send_message_to_future",
  "get_future_message"
];

function sha256Hex(buf) {
  return crypto.createHash("sha256").update(buf).digest("hex");
}

function sortValue(value) {
  if (Array.isArray(value)) return value.map(sortValue);
  if (value && typeof value === "object") {
    const out = {};
    for (const key of Object.keys(value).sort()) out[key] = sortValue(value[key]);
    return out;
  }
  return value;
}

function stableJson(value, pretty = false) {
  const sorted = sortValue(value);
  return pretty ? JSON.stringify(sorted, null, 2) : JSON.stringify(sorted);
}

const schedulerStateDir = path.resolve(root, "artifacts/mcp-action-scheduler.lock");

function readIntEnv(name, fallback) {
  const v = Number.parseInt(process.env[name] ?? "", 10);
  return Number.isFinite(v) ? v : fallback;
}

function readFloatEnv(name, fallback) {
  const v = Number.parseFloat(process.env[name] ?? "");
  return Number.isFinite(v) ? v : fallback;
}

function schedulerEligibility(task) {
  const cpuCount = Math.max(1, os.cpus().length);
  const oneMinLoad = os.loadavg()[0] || 0;
  const loadPerCpu = oneMinLoad / cpuCount;
  const freeMemMb = Math.floor(os.freemem() / (1024 * 1024));
  const maxLoadPerCpu = readFloatEnv("MCP_MAX_LOAD_PER_CPU", 2.5);
  const minFreeMemMb = readIntEnv("MCP_MIN_FREE_MEM_MB", 256);
  const busy = fs.existsSync(schedulerStateDir);
  const eligible = !busy && loadPerCpu <= maxLoadPerCpu && freeMemMb >= minFreeMemMb;
  const reason = busy
    ? "scheduler_busy"
    : loadPerCpu > maxLoadPerCpu
      ? "scheduler_load_exceeded"
      : freeMemMb < minFreeMemMb
        ? "scheduler_memory_low"
        : "ok";
  return {
    eligible,
    reason,
    task,
    metrics: {
      cpu_count: cpuCount,
      one_min_load: oneMinLoad,
      load_per_cpu: Number(loadPerCpu.toFixed(4)),
      max_load_per_cpu: maxLoadPerCpu,
      free_mem_mb: freeMemMb,
      min_free_mem_mb: minFreeMemMb,
      scheduler_busy: busy
    }
  };
}

function runScheduled(task, fn) {
  const gate = schedulerEligibility(task);
  if (!gate.eligible) return { ok: false, gate };
  try {
    fs.mkdirSync(schedulerStateDir, { recursive: false });
  } catch {
    return {
      ok: false,
      gate: {
        ...gate,
        eligible: false,
        reason: "scheduler_busy_after_check",
        metrics: { ...gate.metrics, scheduler_busy: true }
      }
    };
  }
  try {
    const marker = {
      v: "ak.mcp.action_scheduler.lock.v0",
      authority: "advisory",
      task,
      started_at_utc: new Date().toISOString(),
      metrics: gate.metrics
    };
    fs.writeFileSync(path.resolve(schedulerStateDir, "task.json"), stableJson(marker, true) + "\n", "utf8");
    return { ok: true, gate, value: fn(gate) };
  } finally {
    fs.rmSync(schedulerStateDir, { recursive: true, force: true });
  }
}

function readPagesCatalog() {
  const raw = fs.readFileSync(pagesCatalogFile, "utf8");
  const parsed = JSON.parse(raw);
  if (!parsed || parsed.v !== "ak.control_plane.pages.v0" || !Array.isArray(parsed.pages)) {
    throw new Error("invalid pages catalog");
  }
  const byId = new Map();
  for (const page of parsed.pages) {
    if (!page || typeof page.id !== "string" || typeof page.path !== "string") {
      throw new Error("invalid page entry");
    }
    byId.set(page.id, page);
  }
  return byId;
}

function jsonRpcResult(id, result) {
  return { jsonrpc: "2.0", id, result };
}

function jsonRpcError(id, code, message) {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

function listToolsResult() {
  return {
    tools: [
      {
        name: "list_control_plane_pages",
        description: "List allowlisted control-plane page ids and metadata.",
        inputSchema: { type: "object", additionalProperties: false, properties: {} }
      },
      {
        name: "get_control_plane_page",
        description: "Fetch one allowlisted control-plane page by id.",
        inputSchema: {
          type: "object",
          additionalProperties: false,
          required: ["id"],
          properties: { id: { type: "string", minLength: 1 } }
        }
      },
      {
        name: "verify_mcp_contract",
        description: "Verify allowlisted pages and required tools are present.",
        inputSchema: {
          type: "object",
          additionalProperties: false,
          properties: { strict: { type: "boolean" } }
        }
      },
      {
        name: "get_incidence_schedule_snapshot",
        description: "Return deterministic A14 incidence scheduling snapshot for a bounded tick range.",
        inputSchema: {
          type: "object",
          additionalProperties: false,
          properties: {
            start_tick: { type: "integer", minimum: 0, maximum: 1000000 },
            ticks: { type: "integer", minimum: 1, maximum: 64 }
          }
        }
      },
      {
        name: "get_capability_kernel_virtual_graph",
        description: "Fetch deterministic capability-kernel virtual graph normalized and projection artifacts.",
        inputSchema: {
          type: "object",
          additionalProperties: false,
          properties: {
            include_nodes: { type: "boolean" },
            include_edges: { type: "boolean" }
          }
        }
      },
      {
        name: "refresh_capability_kernel_virtual_graph",
        description: "Run bounded virtual graph generation and return resulting artifact digests.",
        inputSchema: {
          type: "object",
          additionalProperties: false,
          properties: {
            refresh: { type: "boolean" },
            run_id: { type: "string", minLength: 1, maxLength: 128 },
            allowlist: { type: "string", minLength: 1, maxLength: 512 }
          }
        }
      },
      {
        name: "get_world_state",
        description: "Fetch the canonical world.v0 state artifact.",
        inputSchema: {
          type: "object",
          additionalProperties: false,
          properties: {
            world_id: { type: "string", minLength: 1 }
          }
        }
      },
      {
        name: "step_world",
        description: "Compute world step eligibility and emit proposal+receipt artifacts only.",
        inputSchema: {
          type: "object",
          additionalProperties: false,
          required: ["world_id", "step_request"],
          properties: {
            world_id: { type: "string", minLength: 1 },
            step_request: {
              type: "object",
              additionalProperties: false,
              required: ["actor_id", "action", "target"],
              properties: {
                actor_id: { type: "string", minLength: 1 },
                action: { type: "string", minLength: 1 },
                target: { type: "string", minLength: 1 },
                requested_state: { type: "string", minLength: 1 }
              }
            }
          }
        }
      },
      {
        name: "get_world_projection",
        description: "Fetch deterministic JSON text projection derived from canonical world.",
        inputSchema: {
          type: "object",
          additionalProperties: false,
          required: ["world_id"],
          properties: {
            world_id: { type: "string", minLength: 1 }
          }
        }
      },
      {
        name: "verify_world",
        description: "Run fail-closed world.v0 contract checks over canonical world artifact.",
        inputSchema: {
          type: "object",
          additionalProperties: false,
          required: ["world_id"],
          properties: {
            world_id: { type: "string", minLength: 1 }
          }
        }
      },
      {
        name: "send_message_to_future",
        description: "Write a bounded advisory future-message artifact.",
        inputSchema: {
          type: "object",
          additionalProperties: false,
          required: ["id", "message", "intended_read_after_utc"],
          properties: {
            id: { type: "string", minLength: 3, maxLength: 64 },
            message: { type: "string", minLength: 1, maxLength: 500 },
            intended_read_after_utc: { type: "string", minLength: 20, maxLength: 30 }
          }
        }
      },
      {
        name: "get_future_message",
        description: "Read a previously written future-message artifact by id.",
        inputSchema: {
          type: "object",
          additionalProperties: false,
          required: ["id"],
          properties: {
            id: { type: "string", minLength: 3, maxLength: 64 }
          }
        }
      }
    ]
  };
}

function makeToolText(resultJson) {
  return { content: [{ type: "text", text: JSON.stringify(resultJson) }] };
}

function futureMessagesDir() {
  const dir = path.resolve(root, "artifacts/future-messages");
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function isValidFutureId(id) {
  return /^[a-z0-9._-]{3,64}$/.test(id);
}

function parseUtcMillis(s) {
  const t = Date.parse(s);
  return Number.isFinite(t) ? t : NaN;
}

function worldPaths() {
  return {
    world: path.resolve(root, "artifacts/world-v0.canonical.json"),
    generate: path.resolve(root, "artifacts/world-v0.generate.normalized.json"),
    proposalDir: path.resolve(root, "artifacts/world-v0.proposals"),
    projection: path.resolve(root, "artifacts/world-v0.projection.json"),
    verify: path.resolve(root, "artifacts/world-v0.verify.normalized.json"),
    branchReconcile: path.resolve(root, "artifacts/world-v0.branch-reconcile.normalized.json")
  };
}

function capabilityGraphPaths() {
  return {
    normalized: path.resolve(root, "artifacts/capability-kernel-virtual-graph.normalized.json"),
    projection: path.resolve(root, "artifacts/capability-kernel-virtual-graph.projection.json"),
    replayHash: path.resolve(root, "artifacts/capability-kernel-virtual-graph.replay-hash")
  };
}

function readCapabilityGraphBundle() {
  const gp = capabilityGraphPaths();
  if (!fs.existsSync(gp.normalized) || !fs.existsSync(gp.projection) || !fs.existsSync(gp.replayHash)) {
    return null;
  }
  const normalizedRaw = fs.readFileSync(gp.normalized, "utf8");
  const projectionRaw = fs.readFileSync(gp.projection, "utf8");
  const replayHash = fs.readFileSync(gp.replayHash, "utf8").trim();
  return {
    normalized: JSON.parse(normalizedRaw),
    projection: JSON.parse(projectionRaw),
    normalized_sha256: `sha256:${sha256Hex(normalizedRaw)}`,
    projection_sha256: `sha256:${sha256Hex(projectionRaw)}`,
    replay_hash: replayHash
  };
}

function ensureWorldExists() {
  const wp = worldPaths();
  if (!fs.existsSync(wp.world) || !fs.existsSync(wp.generate)) {
    return null;
  }
  return wp;
}

function readWorldCanonical() {
  const wp = ensureWorldExists();
  if (!wp) return null;
  const raw = fs.readFileSync(wp.world, "utf8");
  const world = JSON.parse(raw);
  return { ...wp, world, raw };
}

function computeWorldScheduleRows(world, targetTick) {
  const entities = [...world.entities].sort((a, b) => a.id.localeCompare(b.id));
  return entities.map((entity) => {
    const material = `a14|${targetTick}|${entity.id}`;
    const digest = crypto.createHash("sha256").update(material).digest();
    return {
      entity_id: entity.id,
      kind: entity.kind,
      eligible: (digest[1] & 1) === 1,
      fano_rank: digest[0] & 1
    };
  });
}

function buildWorldProjection(world) {
  const entitiesByKind = { animate: 0, inanimate: 0 };
  for (const entity of world.entities) entitiesByKind[entity.kind] += 1;
  const relationCounts = {};
  for (const rel of world.relations) {
    relationCounts[rel.type] = (relationCounts[rel.type] || 0) + 1;
  }
  const projection = {
    v: "world.projection.v0",
    authority: "advisory",
    world_id: world.world_id,
    canonical_tick: world.canonical_tick,
    view_id: "json_text_v0",
    entities_by_kind: entitiesByKind,
    relation_counts: Object.fromEntries(
      Object.entries(relationCounts).sort((a, b) => a[0].localeCompare(b[0]))
    ),
    branch: world.branches[0]?.branch_id ?? null,
    proposal_queue_depth: world.proposal_queue?.[0]?.pending?.length ?? 0,
    event_log_size: world.event_log?.length ?? 0
  };
  const serialized = JSON.stringify(projection, null, 2) + "\n";
  return {
    projection,
    serialized,
    projection_sha256: `sha256:${sha256Hex(serialized)}`
  };
}

function verifyWorldState(world, rawWorld) {
  const wp = worldPaths();
  let branchEvidence = {
    present: false,
    valid_merge_with_lineage_accepted: false,
    missing_lineage_rejected: false
  };
  if (fs.existsSync(wp.branchReconcile)) {
    const parsed = JSON.parse(fs.readFileSync(wp.branchReconcile, "utf8"));
    branchEvidence = {
      present: parsed?.v === "world_v0.branch_reconcile.normalized.v0",
      valid_merge_with_lineage_accepted: parsed?.valid_merge_with_lineage_accepted === true,
      missing_lineage_rejected: parsed?.missing_lineage_rejected === true
    };
  }
  const requiredKeys = new Set([
    "v",
    "authority",
    "world_id",
    "kernel_seed",
    "profile",
    "canonical_tick",
    "entities",
    "relations",
    "event_log",
    "branches",
    "proposal_queue",
    "receipts",
    "projection_views"
  ]);
  const keys = Object.keys(world);
  const strictKeys = keys.length === requiredKeys.size && keys.every((k) => requiredKeys.has(k));
  const entityCount = Array.isArray(world.entities) ? world.entities.length : -1;
  const relationTypes = Array.isArray(world.relations)
    ? [...new Set(world.relations.map((r) => r?.type).filter((x) => typeof x === "string"))].sort()
    : [];
  const branchMain =
    Array.isArray(world.branches) &&
    world.branches.length === 1 &&
    world.branches[0] &&
    world.branches[0].branch_id === "main";
  const proposalQueueMain =
    Array.isArray(world.proposal_queue) &&
    world.proposal_queue.length === 1 &&
    world.proposal_queue[0] &&
    world.proposal_queue[0].queue_id === "main";
  const hasKinds = new Set((world.entities || []).map((e) => e?.kind));
  const animateInanimate = hasKinds.has("animate") && hasKinds.has("inanimate");
  const pendingPromoted = (world.event_log || []).some(
    (evt) => evt && typeof evt === "object" && evt.status === "accepted"
  );
  const worldSha = `sha256:${sha256Hex(rawWorld)}`;
  const valid =
    world.v === "world.v0" &&
    world.authority === "algorithmic" &&
    world.profile === "orchard_garden_lattice.v0" &&
    Number.isInteger(world.canonical_tick) &&
    world.canonical_tick >= 0 &&
    strictKeys &&
    entityCount >= 8 &&
    entityCount <= 16 &&
    relationTypes.length >= 2 &&
    relationTypes.length <= 3 &&
    branchMain &&
    proposalQueueMain &&
    animateInanimate &&
    !pendingPromoted &&
    branchEvidence.present &&
    branchEvidence.valid_merge_with_lineage_accepted &&
    branchEvidence.missing_lineage_rejected;
  return {
    valid,
    strict_keyset_checked: strictKeys,
    entity_count: entityCount,
    relation_types: relationTypes,
    branch_main_lane: branchMain,
    proposal_queue_main: proposalQueueMain,
    animate_inanimate_covered: animateInanimate,
    pending_proposal_promoted: pendingPromoted,
    branch_reconcile_fixture_present: branchEvidence.present,
    branch_merge_with_lineage_accepted: branchEvidence.valid_merge_with_lineage_accepted,
    branch_merge_without_lineage_rejected: branchEvidence.missing_lineage_rejected,
    world_sha256: worldSha
  };
}

function handleToolCall(name, args) {
  const pagesById = readPagesCatalog();
  if (name === "list_control_plane_pages") {
    const pages = [...pagesById.values()]
      .map((page) => {
        const absPath = path.resolve(root, page.path);
        const exists = fs.existsSync(absPath);
        const contentSha = exists ? `sha256:${sha256Hex(fs.readFileSync(absPath))}` : null;
        return {
          id: page.id,
          title: page.title,
          class: page.class,
          version: page.version,
          path: page.path,
          authority: page.authority,
          content_sha256: contentSha
        };
      })
      .sort((a, b) => a.id.localeCompare(b.id));
    return makeToolText({
      v: "ak.mcp.tool.list_control_plane_pages.output.v0",
      authority: "advisory",
      pages
    });
  }

  if (name === "get_control_plane_page") {
    const id = args?.id;
    if (typeof id !== "string" || id.length === 0) {
      return makeToolText({
        v: "ak.mcp.tool.get_control_plane_page.output.v0",
        authority: "advisory",
        page_id: "",
        found: false,
        allowed: false,
        reason: "invalid_id"
      });
    }
    const page = pagesById.get(id);
    if (!page) {
      return makeToolText({
        v: "ak.mcp.tool.get_control_plane_page.output.v0",
        authority: "advisory",
        page_id: id,
        found: false,
        allowed: false,
        reason: "not_allowlisted"
      });
    }
    const absPath = path.resolve(root, page.path);
    if (!fs.existsSync(absPath)) {
      return makeToolText({
        v: "ak.mcp.tool.get_control_plane_page.output.v0",
        authority: "advisory",
        page_id: id,
        found: false,
        allowed: true,
        reason: "missing_file"
      });
    }
    const content = fs.readFileSync(absPath, "utf8");
    const contentSha = `sha256:${sha256Hex(content)}`;
    return makeToolText({
      v: "ak.mcp.tool.get_control_plane_page.output.v0",
      authority: "advisory",
      page_id: id,
      found: true,
      allowed: true,
      title: page.title,
      class: page.class,
      version: page.version,
      path: page.path,
      content_sha256: contentSha,
      marker: `${id}:${page.version}`
    });
  }

  if (name === "verify_mcp_contract") {
    const issues = [];
    const requiredTools = [
      "list_control_plane_pages",
      "get_control_plane_page",
      "verify_mcp_contract",
      "get_incidence_schedule_snapshot",
      "get_capability_kernel_virtual_graph",
      "refresh_capability_kernel_virtual_graph",
      "get_world_state",
      "step_world",
      "get_world_projection",
      "verify_world"
    ];
    for (const requiredTool of requiredTools) {
      if (!toolNames.includes(requiredTool)) {
        issues.push(`tool_missing:${requiredTool}`);
      }
    }
    for (const pageId of [
      "protocol_spec",
      "chirality_selection_law",
      "incidence_scheduling_law",
      "world_spec",
      "world_proof_ledger",
      "world_proof_receipt"
    ]) {
      const page = pagesById.get(pageId);
      if (!page) {
        issues.push(`page_missing:${pageId}`);
        continue;
      }
      const p = path.resolve(root, page.path);
      if (!fs.existsSync(p)) issues.push(`page_file_missing:${pageId}`);
    }
    return makeToolText({
      v: "ak.mcp.tool.verify_mcp_contract.output.v0",
      authority: "advisory",
      valid: issues.length === 0,
      strict: Boolean(args?.strict),
      issues
    });
  }

  if (name === "get_incidence_schedule_snapshot") {
    const startTick = Number.isInteger(args?.start_tick) ? args.start_tick : 0;
    const ticks = Number.isInteger(args?.ticks) ? args.ticks : 8;
    if (startTick < 0 || ticks < 1 || ticks > 64) {
      return makeToolText({
        v: "ak.mcp.tool.get_incidence_schedule_snapshot.output.v0",
        authority: "advisory",
        valid: false,
        reason: "invalid_range"
      });
    }
    const entities = [
      { id: "stone-01", kind: "inanimate" },
      { id: "agent-01", kind: "animate" }
    ];
    const rows = [];
    for (let i = 0; i < ticks; i += 1) {
      const canonicalTick = startTick + i;
      for (const e of entities) {
        const material = `a14|${canonicalTick}|${e.id}`;
        const digest = crypto.createHash("sha256").update(material).digest();
        const fanoRank = digest[0] & 1;
        const eligible = (digest[1] & 1) === 1;
        const proposalState = (digest[2] % 3) === 0 ? "pending" : "accepted";
        rows.push({
          entity_id: e.id,
          kind: e.kind,
          canonical_tick: canonicalTick,
          incidence_tick: eligible ? canonicalTick : canonicalTick + 1,
          proposal_state: proposalState,
          fano_rank: fanoRank,
          eligible
        });
      }
    }
    const normalizedRows = rows.map((r) => ({
      canonical_tick: r.canonical_tick,
      eligible: r.eligible,
      entity_id: r.entity_id,
      fano_rank: r.fano_rank,
      incidence_tick: r.incidence_tick,
      kind: r.kind,
      proposal_state: r.proposal_state
    }));
    const normalized = JSON.stringify(normalizedRows, null, 0);
    const scheduleDigest = `sha256:${sha256Hex(normalized)}`;
    return makeToolText({
      v: "ak.mcp.tool.get_incidence_schedule_snapshot.output.v0",
      authority: "advisory",
      valid: true,
      law: "A14_INCIDENCE_SCHEDULING_LAW_v0",
      start_tick: startTick,
      ticks,
      rows,
      schedule_sha256: scheduleDigest
    });
  }

  if (name === "get_capability_kernel_virtual_graph") {
    const bundle = readCapabilityGraphBundle();
    if (!bundle) {
      return makeToolText({
        v: "ak.mcp.tool.get_capability_kernel_virtual_graph.output.v0",
        authority: "advisory",
        found: false,
        reason: "graph_not_generated"
      });
    }
    const includeNodes = args?.include_nodes !== false;
    const includeEdges = args?.include_edges !== false;
    const normalized = bundle.normalized;
    return makeToolText({
      v: "ak.mcp.tool.get_capability_kernel_virtual_graph.output.v0",
      authority: "advisory",
      found: true,
      workspace_id: normalized.workspace_id,
      node_count: normalized.node_count,
      edge_count: normalized.edge_count,
      project_count_analyzed: normalized.project_count_analyzed,
      totals: normalized.totals,
      normalized_sha256: bundle.normalized_sha256,
      projection_sha256: bundle.projection_sha256,
      replay_hash: bundle.replay_hash,
      projection: bundle.projection,
      nodes: includeNodes ? normalized.nodes : undefined,
      edges: includeEdges ? normalized.edges : undefined
    });
  }

  if (name === "refresh_capability_kernel_virtual_graph") {
    const refresh = args?.refresh === true;
    const runId = args?.run_id;
    const allowlist = args?.allowlist;
    if (runId !== undefined && (typeof runId !== "string" || !/^[a-zA-Z0-9._:-]+$/.test(runId))) {
      return makeToolText({
        v: "ak.mcp.tool.refresh_capability_kernel_virtual_graph.output.v0",
        authority: "advisory",
        valid: false,
        executed: false,
        reason: "invalid_run_id"
      });
    }
    if (
      allowlist !== undefined &&
      (typeof allowlist !== "string" || !/^[a-zA-Z0-9,._:-]+$/.test(allowlist))
    ) {
      return makeToolText({
        v: "ak.mcp.tool.refresh_capability_kernel_virtual_graph.output.v0",
        authority: "advisory",
        valid: false,
        executed: false,
        reason: "invalid_allowlist"
      });
    }
    const scheduled = runScheduled("refresh_capability_kernel_virtual_graph", () => {
      const script = path.resolve(root, "scripts/capability-kernel-virtual-graph.sh");
      const scriptArgs = [script];
      if (refresh) scriptArgs.push("--refresh");
      if (typeof runId === "string" && runId.length > 0) {
        scriptArgs.push("--run-id", runId);
      }
      if (typeof allowlist === "string" && allowlist.length > 0) {
        scriptArgs.push("--allowlist", allowlist);
      }
      return spawnSync("bash", scriptArgs, {
        cwd: root,
        encoding: "utf8",
        timeout: 300000
      });
    });
    if (!scheduled.ok) {
      return makeToolText({
        v: "ak.mcp.tool.refresh_capability_kernel_virtual_graph.output.v0",
        authority: "advisory",
        valid: false,
        executed: false,
        reason: scheduled.gate.reason,
        scheduler: scheduled.gate.metrics
      });
    }
    const proc = scheduled.value;
    if (proc.error) {
      return makeToolText({
        v: "ak.mcp.tool.refresh_capability_kernel_virtual_graph.output.v0",
        authority: "advisory",
        valid: false,
        executed: false,
        reason: "spawn_error",
        detail: proc.error.message,
        scheduler: scheduled.gate.metrics
      });
    }
    if (proc.status !== 0) {
      return makeToolText({
        v: "ak.mcp.tool.refresh_capability_kernel_virtual_graph.output.v0",
        authority: "advisory",
        valid: false,
        executed: true,
        reason: "command_failed",
        exit_code: proc.status,
        stderr: (proc.stderr || "").split("\n").slice(0, 3).join("\n"),
        scheduler: scheduled.gate.metrics
      });
    }
    const bundle = readCapabilityGraphBundle();
    if (!bundle) {
      return makeToolText({
        v: "ak.mcp.tool.refresh_capability_kernel_virtual_graph.output.v0",
        authority: "advisory",
        valid: false,
        executed: true,
        reason: "graph_missing_after_refresh",
        scheduler: scheduled.gate.metrics
      });
    }
    return makeToolText({
      v: "ak.mcp.tool.refresh_capability_kernel_virtual_graph.output.v0",
      authority: "advisory",
      valid: true,
      executed: true,
      refresh,
      workspace_id: bundle.normalized.workspace_id,
      project_count_analyzed: bundle.normalized.project_count_analyzed,
      normalized_sha256: bundle.normalized_sha256,
      projection_sha256: bundle.projection_sha256,
      replay_hash: bundle.replay_hash,
      scheduler: scheduled.gate.metrics
    });
  }

  if (name === "get_world_state") {
    const reqWorldId = args?.world_id;
    const bundle = readWorldCanonical();
    if (!bundle) {
      return makeToolText({
        v: "ak.mcp.tool.get_world_state.output.v0",
        authority: "advisory",
        found: false,
        reason: "world_not_generated"
      });
    }
    if (typeof reqWorldId === "string" && reqWorldId.length > 0 && reqWorldId !== bundle.world.world_id) {
      return makeToolText({
        v: "ak.mcp.tool.get_world_state.output.v0",
        authority: "advisory",
        found: false,
        reason: "world_id_mismatch",
        world_id: reqWorldId
      });
    }
    return makeToolText({
      v: "ak.mcp.tool.get_world_state.output.v0",
      authority: "advisory",
      found: true,
      world_id: bundle.world.world_id,
      path: "artifacts/world-v0.canonical.json",
      world_sha256: `sha256:${sha256Hex(bundle.raw)}`,
      world: bundle.world
    });
  }

  if (name === "step_world") {
    const reqWorldId = args?.world_id;
    const step = args?.step_request;
    const bundle = readWorldCanonical();
    if (!bundle) {
      return makeToolText({
        v: "ak.mcp.tool.step_world.output.v0",
        authority: "advisory",
        valid: false,
        proposal_written: false,
        reason: "world_not_generated"
      });
    }
    if (reqWorldId !== bundle.world.world_id) {
      return makeToolText({
        v: "ak.mcp.tool.step_world.output.v0",
        authority: "advisory",
        valid: false,
        proposal_written: false,
        reason: "world_id_mismatch"
      });
    }
    if (!step || typeof step !== "object") {
      return makeToolText({
        v: "ak.mcp.tool.step_world.output.v0",
        authority: "advisory",
        valid: false,
        proposal_written: false,
        reason: "invalid_step_request"
      });
    }
    const actorId = step.actor_id;
    const action = step.action;
    const target = step.target;
    const requestedState = step.requested_state ?? "open";
    if (
      typeof actorId !== "string" ||
      typeof action !== "string" ||
      typeof target !== "string" ||
      actorId.length === 0 ||
      action.length === 0 ||
      target.length === 0
    ) {
      return makeToolText({
        v: "ak.mcp.tool.step_world.output.v0",
        authority: "advisory",
        valid: false,
        proposal_written: false,
        reason: "invalid_step_request_fields"
      });
    }
    const scheduled = runScheduled("step_world", (gate) => {
      const targetTick = bundle.world.canonical_tick + 1;
      const scheduleRows = computeWorldScheduleRows(bundle.world, targetTick);
      const schedule = scheduleRows.find((row) => row.entity_id === actorId);
      if (!schedule || schedule.eligible !== true) {
        return {
          v: "ak.mcp.tool.step_world.output.v0",
          authority: "advisory",
          valid: false,
          proposal_written: false,
          reason: "actor_not_eligible",
          actor_id: actorId,
          target_tick: targetTick,
          scheduler: gate.metrics
        };
      }
      const proposalDir = bundle.proposalDir;
      fs.mkdirSync(proposalDir, { recursive: true });
      const proposalMaterial = [
        bundle.world.world_id,
        String(targetTick),
        actorId,
        action,
        target,
        requestedState
      ].join("|");
      const proposalId = `proposal-${sha256Hex(proposalMaterial).slice(0, 16)}`;
      const proposal = {
        v: "world.step.proposal.v0",
        authority: "advisory",
        world_id: bundle.world.world_id,
        proposal_id: proposalId,
        canonical_tick: bundle.world.canonical_tick,
        target_tick: targetTick,
        actor_id: actorId,
        action,
        payload: { target, requested_state: requestedState },
        status: "pending",
        eligibility_law: "A14_INCIDENCE_SCHEDULING_LAW_v0",
        chirality_law: "CHIRALITY_SELECTION_LAW_v0"
      };
      const proposalRaw = stableJson(proposal, true) + "\n";
      const proposalSha = `sha256:${sha256Hex(proposalRaw)}`;
      const proposalPath = path.resolve(proposalDir, `${proposalId}.proposal.json`);
      fs.writeFileSync(proposalPath, proposalRaw, "utf8");
      const receipt = {
        v: "world.step.receipt.v0",
        authority: "advisory",
        world_id: bundle.world.world_id,
        proposal_id: proposalId,
        status: "queued",
        receipt_ref: `receipts/${proposalId}`,
        proposal_sha256: proposalSha,
        committed: false
      };
      const receiptRaw = stableJson(receipt, true) + "\n";
      const receiptSha = `sha256:${sha256Hex(receiptRaw)}`;
      const receiptPath = path.resolve(proposalDir, `${proposalId}.receipt.json`);
      fs.writeFileSync(receiptPath, receiptRaw, "utf8");
      return {
        v: "ak.mcp.tool.step_world.output.v0",
        authority: "advisory",
        valid: true,
        proposal_only: true,
        proposal_written: true,
        committed: false,
        world_id: bundle.world.world_id,
        proposal_id: proposalId,
        proposal_path: `artifacts/world-v0.proposals/${proposalId}.proposal.json`,
        proposal_sha256: proposalSha,
        receipt_path: `artifacts/world-v0.proposals/${proposalId}.receipt.json`,
        receipt_sha256: receiptSha,
        scheduler: gate.metrics
      };
    });
    if (!scheduled.ok) {
      return makeToolText({
        v: "ak.mcp.tool.step_world.output.v0",
        authority: "advisory",
        valid: false,
        proposal_written: false,
        reason: scheduled.gate.reason,
        scheduler: scheduled.gate.metrics
      });
    }
    return makeToolText(scheduled.value);
  }

  if (name === "get_world_projection") {
    const reqWorldId = args?.world_id;
    const bundle = readWorldCanonical();
    if (!bundle) {
      return makeToolText({
        v: "ak.mcp.tool.get_world_projection.output.v0",
        authority: "advisory",
        found: false,
        reason: "world_not_generated"
      });
    }
    if (reqWorldId !== bundle.world.world_id) {
      return makeToolText({
        v: "ak.mcp.tool.get_world_projection.output.v0",
        authority: "advisory",
        found: false,
        reason: "world_id_mismatch"
      });
    }
    const projection = buildWorldProjection(bundle.world);
    fs.writeFileSync(bundle.projection, projection.serialized, "utf8");
    return makeToolText({
      v: "ak.mcp.tool.get_world_projection.output.v0",
      authority: "advisory",
      found: true,
      world_id: bundle.world.world_id,
      projection_path: "artifacts/world-v0.projection.json",
      projection_sha256: projection.projection_sha256,
      projection: projection.projection
    });
  }

  if (name === "verify_world") {
    const reqWorldId = args?.world_id;
    const bundle = readWorldCanonical();
    if (!bundle) {
      return makeToolText({
        v: "ak.mcp.tool.verify_world.output.v0",
        authority: "advisory",
        valid: false,
        reason: "world_not_generated"
      });
    }
    if (reqWorldId !== bundle.world.world_id) {
      return makeToolText({
        v: "ak.mcp.tool.verify_world.output.v0",
        authority: "advisory",
        valid: false,
        reason: "world_id_mismatch"
      });
    }
    const scheduled = runScheduled("verify_world", (gate) => {
      const verification = verifyWorldState(bundle.world, bundle.raw);
      fs.writeFileSync(
        bundle.verify,
        stableJson(
          {
            v: "world_v0.verify.normalized.v0",
            authority: "advisory",
            world_id: bundle.world.world_id,
            ...verification,
            scheduler: gate.metrics
          },
          true
        ) + "\n",
        "utf8"
      );
      return {
        v: "ak.mcp.tool.verify_world.output.v0",
        authority: "advisory",
        world_id: bundle.world.world_id,
        verify_artifact_path: "artifacts/world-v0.verify.normalized.json",
        ...verification,
        scheduler: gate.metrics
      };
    });
    if (!scheduled.ok) {
      return makeToolText({
        v: "ak.mcp.tool.verify_world.output.v0",
        authority: "advisory",
        world_id: bundle.world.world_id,
        valid: false,
        reason: scheduled.gate.reason,
        scheduler: scheduled.gate.metrics
      });
    }
    return makeToolText(scheduled.value);
  }

  if (name === "send_message_to_future") {
    const id = args?.id;
    const message = args?.message;
    const intended = args?.intended_read_after_utc;
    if (typeof id !== "string" || !isValidFutureId(id)) {
      return makeToolText({
        v: "ak.mcp.tool.send_message_to_future.output.v0",
        authority: "advisory",
        written: false,
        reason: "invalid_id"
      });
    }
    if (typeof message !== "string" || message.length < 1 || message.length > 500) {
      return makeToolText({
        v: "ak.mcp.tool.send_message_to_future.output.v0",
        authority: "advisory",
        written: false,
        reason: "invalid_message"
      });
    }
    if (typeof intended !== "string" || !Number.isFinite(parseUtcMillis(intended))) {
      return makeToolText({
        v: "ak.mcp.tool.send_message_to_future.output.v0",
        authority: "advisory",
        written: false,
        reason: "invalid_intended_read_after_utc"
      });
    }
    const createdAt = new Date().toISOString();
    const artifact = {
      v: "ak.message_to_future.v0",
      authority: "advisory",
      from: "mcp",
      to: "future-reader",
      id,
      created_at_utc: createdAt,
      intended_read_after_utc: intended,
      message
    };
    const serialized = JSON.stringify(artifact, null, 2) + "\n";
    const digest = `sha256:${sha256Hex(serialized)}`;
    const dir = futureMessagesDir();
    const jsonPath = path.resolve(dir, `${id}.v0.json`);
    const shaPath = path.resolve(dir, `${id}.v0.sha256`);
    fs.writeFileSync(jsonPath, serialized, "utf8");
    fs.writeFileSync(shaPath, `${digest}\n`, "utf8");
    return makeToolText({
      v: "ak.mcp.tool.send_message_to_future.output.v0",
      authority: "advisory",
      written: true,
      id,
      artifact_path: `artifacts/future-messages/${id}.v0.json`,
      digest_path: `artifacts/future-messages/${id}.v0.sha256`,
      digest
    });
  }

  if (name === "get_future_message") {
    const id = args?.id;
    if (typeof id !== "string" || !isValidFutureId(id)) {
      return makeToolText({
        v: "ak.mcp.tool.get_future_message.output.v0",
        authority: "advisory",
        found: false,
        reason: "invalid_id"
      });
    }
    const dir = futureMessagesDir();
    const jsonPath = path.resolve(dir, `${id}.v0.json`);
    const shaPath = path.resolve(dir, `${id}.v0.sha256`);
    if (!fs.existsSync(jsonPath) || !fs.existsSync(shaPath)) {
      return makeToolText({
        v: "ak.mcp.tool.get_future_message.output.v0",
        authority: "advisory",
        found: false,
        id,
        reason: "not_found"
      });
    }
    const raw = fs.readFileSync(jsonPath, "utf8");
    const parsed = JSON.parse(raw);
    const digest = `sha256:${sha256Hex(raw)}`;
    const declared = fs.readFileSync(shaPath, "utf8").trim();
    const intendedMs = parseUtcMillis(parsed.intended_read_after_utc);
    const released = Number.isFinite(intendedMs) && Date.now() >= intendedMs;
    return makeToolText({
      v: "ak.mcp.tool.get_future_message.output.v0",
      authority: "advisory",
      found: true,
      id,
      digest,
      digest_match: digest === declared,
      intended_read_after_utc: parsed.intended_read_after_utc,
      released,
      message: released ? parsed.message : null
    });
  }

  return makeToolText({
    v: "ak.mcp.tool.error.output.v0",
    authority: "advisory",
    error: `unknown_tool:${name}`
  });
}

export function handleRequest(req) {
  const id = Object.prototype.hasOwnProperty.call(req, "id") ? req.id : null;
  if (!req || req.jsonrpc !== "2.0" || typeof req.method !== "string") {
    return jsonRpcError(id, -32600, "invalid request");
  }

  if (req.method === "initialize") {
    return jsonRpcResult(id, {
      protocolVersion: "2025-11-25",
      serverInfo: { name: "atomic-kernel-mcp", version: "0.1.0" },
      capabilities: { tools: {}, resources: {} }
    });
  }

  if (req.method === "notifications/initialized") {
    return null;
  }

  if (req.method === "tools/list") {
    return jsonRpcResult(id, listToolsResult());
  }

  if (req.method === "tools/call") {
    const name = req.params?.name;
    const args = req.params?.arguments || {};
    if (typeof name !== "string" || !toolNames.includes(name)) {
      return jsonRpcError(id, -32602, "unknown tool");
    }
    return jsonRpcResult(id, handleToolCall(name, args));
  }

  return jsonRpcError(id, -32601, "method not found");
}
