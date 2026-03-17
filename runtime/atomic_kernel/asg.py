"""Deterministic source -> ASG v0 ingestion (Python, TypeScript)."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any


class AsgError(ValueError):
  """ASG ingestion or validation error."""


NODE_KINDS = {
  "Module",
  "Namespace",
  "Import",
  "Export",
  "Class",
  "Interface",
  "Function",
  "Method",
  "Field",
  "Variable",
  "Constant",
  "ObjectLiteral",
  "Call",
  "JsonEnvelope",
  "SchemaRef",
  "GateScriptRef",
  "FixtureRef",
  "TypeRef",
  "Literal",
}

EDGE_KINDS = {
  "Defines",
  "Imports",
  "Exports",
  "Calls",
  "Implements",
  "Extends",
  "Constructs",
  "Assigns",
  "Returns",
  "DelegatesTo",
  "Observes",
  "DependsOn",
  "ValidatesAgainst",
  "ProjectsTo",
  "BridgesTo",
  "ImplementsBoundary",
  "FramingLayerOf",
  "BridgeLayerOf",
  "CarrierLayerOf",
  "InvokesEabi",
  "ConformsToAbi",
  "ProjectionOnlyOf",
}

TOP_KEYS = {"v", "authority", "language", "namespace", "nodes", "edges", "provenance", "graph_hash"}
NODE_KEYS = {"id", "symbol", "kind", "attrs", "source"}
EDGE_KEYS = {"id", "symbol", "kind", "from", "to", "attrs"}
SOURCE_KEYS = {"path", "line", "column", "end_line", "end_column"}
PROVENANCE_KEYS = {"source_path", "parser", "parser_version"}
LANGUAGES = {"python", "typescript", "mjs"}
PARSERS = {"python-ast", "typescript-regex", "mjs-acorn-estree"}
TS_DIAG_CODE_RE = re.compile(r"error TS(\d+):")


def _canonical_json(data: dict[str, Any]) -> str:
  return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash_frame_without_hash(frame: dict[str, Any]) -> str:
  payload = dict(frame)
  payload.pop("graph_hash", None)
  digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
  return f"sha256:{digest}"


def _source_span(node: ast.AST, path: str) -> dict[str, Any]:
  line = int(getattr(node, "lineno", 1))
  col = int(getattr(node, "col_offset", 0))
  end_line = int(getattr(node, "end_lineno", line))
  end_col = int(getattr(node, "end_col_offset", col))
  return {
    "path": path,
    "line": line,
    "column": col,
    "end_line": end_line,
    "end_column": end_col,
  }


def _call_name(call: ast.Call) -> str:
  fn = call.func
  if isinstance(fn, ast.Name):
    return fn.id
  if isinstance(fn, ast.Attribute):
    base = _call_name(ast.Call(func=fn.value, args=[], keywords=[])) if isinstance(fn.value, (ast.Name, ast.Attribute)) else "expr"
    return f"{base}.{fn.attr}"
  return "expr"


def ingest_python_to_asg(source: str, source_path: str, namespace: str) -> dict[str, Any]:
  tree = ast.parse(source, filename=source_path)

  nodes: dict[str, dict[str, Any]] = {}
  edges: dict[str, dict[str, Any]] = {}

  def add_node(node_id: str, kind: str, attrs: dict[str, Any], span_node: ast.AST, symbol: str | None = None) -> None:
    if kind not in NODE_KINDS:
      raise AsgError(f"invalid node kind: {kind}")
    nodes[node_id] = {
      "id": node_id,
      "symbol": symbol or f"cp:{kind}",
      "kind": kind,
      "attrs": attrs,
      "source": _source_span(span_node, source_path),
    }

  def add_edge(edge_id: str, kind: str, frm: str, to: str, attrs: dict[str, Any], symbol: str | None = None) -> None:
    if kind not in EDGE_KINDS:
      raise AsgError(f"invalid edge kind: {kind}")
    edges[edge_id] = {
      "id": edge_id,
      "symbol": symbol or f"cp:{kind}",
      "kind": kind,
      "from": frm,
      "to": to,
      "attrs": attrs,
    }

  module_id = "n:module"
  add_node(module_id, "Module", {"name": source_path}, tree)

  class_ids: dict[str, str] = {}

  for stmt in tree.body:
    if isinstance(stmt, ast.Import):
      for alias in stmt.names:
        target = alias.name
        imp_id = f"n:import:{target}"
        add_node(imp_id, "Namespace", {"name": target}, stmt, symbol="cp:Namespace")
        add_edge(f"e:imports:{target}", "Imports", module_id, imp_id, {"alias": alias.asname or ""})
    elif isinstance(stmt, ast.ImportFrom):
      mod = stmt.module or ""
      imp_id = f"n:import:{mod}"
      add_node(imp_id, "Namespace", {"name": mod}, stmt, symbol="cp:Namespace")
      add_edge(f"e:imports:{mod}", "Imports", module_id, imp_id, {"level": stmt.level})

  for stmt in tree.body:
    if isinstance(stmt, ast.ClassDef):
      cid = f"n:class:{stmt.name}"
      class_ids[stmt.name] = cid
      add_node(cid, "Class", {"name": stmt.name}, stmt)
      add_edge(f"e:defines:class:{stmt.name}", "Defines", module_id, cid, {})

      for base in stmt.bases:
        if isinstance(base, ast.Name):
          bid = f"n:typeref:{base.id}"
          if bid not in nodes:
            add_node(bid, "TypeRef", {"name": base.id}, base)
          add_edge(f"e:extends:{stmt.name}:{base.id}", "Extends", cid, bid, {})

      for item in stmt.body:
        if isinstance(item, ast.FunctionDef):
          mid = f"n:method:{stmt.name}.{item.name}"
          add_node(mid, "Method", {"name": item.name, "owner": stmt.name}, item)
          add_edge(f"e:defines:method:{stmt.name}.{item.name}", "Defines", cid, mid, {})
          for call in [n for n in ast.walk(item) if isinstance(n, ast.Call)]:
            callee = _call_name(call)
            tid = f"n:typeref:{callee}"
            if tid not in nodes:
              add_node(tid, "TypeRef", {"name": callee}, call)
            add_edge(
              f"e:calls:{stmt.name}.{item.name}:{callee}:{call.lineno}:{call.col_offset}",
              "Calls",
              mid,
              tid,
              {},
            )
        elif isinstance(item, ast.Assign):
          for t in item.targets:
            if isinstance(t, ast.Name):
              fid = f"n:field:{stmt.name}.{t.id}"
              add_node(fid, "Field", {"name": t.id, "owner": stmt.name}, t)
              add_edge(f"e:defines:field:{stmt.name}.{t.id}", "Defines", cid, fid, {})

    elif isinstance(stmt, ast.FunctionDef):
      fid = f"n:function:{stmt.name}"
      add_node(fid, "Function", {"name": stmt.name}, stmt)
      add_edge(f"e:defines:function:{stmt.name}", "Defines", module_id, fid, {})
      for call in [n for n in ast.walk(stmt) if isinstance(n, ast.Call)]:
        callee = _call_name(call)
        tid = f"n:typeref:{callee}"
        if tid not in nodes:
          add_node(tid, "TypeRef", {"name": callee}, call)
        add_edge(
          f"e:calls:{stmt.name}:{callee}:{call.lineno}:{call.col_offset}",
          "Calls",
          fid,
          tid,
          {},
        )

  frame = {
    "v": "ak.asg.v0",
    "authority": "advisory",
    "language": "python",
    "namespace": namespace,
    "nodes": [nodes[k] for k in sorted(nodes.keys())],
    "edges": [edges[k] for k in sorted(edges.keys())],
    "provenance": {
      "source_path": source_path,
      "parser": "python-ast",
      "parser_version": "v0",
    },
    "graph_hash": "",
  }
  frame["graph_hash"] = _hash_frame_without_hash(frame)
  return frame


def _ts_line_info(source: str, pos: int) -> tuple[int, int]:
  upto = source[:pos]
  line = upto.count("\n") + 1
  last_nl = upto.rfind("\n")
  col = pos if last_nl == -1 else pos - last_nl - 1
  return (line, col)


def _ts_span(source: str, source_path: str, start: int, end: int) -> dict[str, Any]:
  line, col = _ts_line_info(source, start)
  end_line, end_col = _ts_line_info(source, max(start, end))
  return {
    "path": source_path,
    "line": int(line),
    "column": int(col),
    "end_line": int(end_line),
    "end_column": int(end_col),
  }


def _check_ts_syntax(source: str) -> None:
  braces = 0
  parens = 0
  i = 0
  n = len(source)
  mode = "code"  # code|single|double|line_comment|block_comment|template
  template_expr_depth: list[int] = []

  while i < n:
    ch = source[i]
    nxt = source[i + 1] if i + 1 < n else ""

    if mode == "line_comment":
      if ch == "\n":
        mode = "code"
      i += 1
      continue

    if mode == "block_comment":
      if ch == "*" and nxt == "/":
        mode = "code"
        i += 2
      else:
        i += 1
      continue

    if mode == "single":
      if ch == "\\":
        i += 2
      elif ch == "'":
        mode = "code"
        i += 1
      else:
        i += 1
      continue

    if mode == "double":
      if ch == "\\":
        i += 2
      elif ch == '"':
        mode = "code"
        i += 1
      else:
        i += 1
      continue

    if mode == "template":
      if ch == "\\":
        i += 2
        continue
      if ch == "`":
        mode = "code"
        i += 1
        continue
      if ch == "$" and nxt == "{":
        template_expr_depth.append(0)
        mode = "code"
        i += 2
        continue
      i += 1
      continue

    # mode == code
    if ch == "/" and nxt == "/":
      mode = "line_comment"
      i += 2
      continue
    if ch == "/" and nxt == "*":
      mode = "block_comment"
      i += 2
      continue
    if ch == "'":
      mode = "single"
      i += 1
      continue
    if ch == '"':
      mode = "double"
      i += 1
      continue
    if ch == "`":
      mode = "template"
      i += 1
      continue

    if ch == "{":
      if template_expr_depth:
        template_expr_depth[-1] += 1
      else:
        braces += 1
      i += 1
      continue
    if ch == "}":
      if template_expr_depth:
        if template_expr_depth[-1] > 0:
          template_expr_depth[-1] -= 1
        else:
          template_expr_depth.pop()
          mode = "template"
      else:
        braces -= 1
        if braces < 0:
          raise AsgError("typescript syntax invalid: unmatched }")
      i += 1
      continue
    if ch == "(":
      parens += 1
      i += 1
      continue
    if ch == ")":
      parens -= 1
      if parens < 0:
        raise AsgError("typescript syntax invalid: unmatched )")
      i += 1
      continue

    i += 1

  if mode in {"single", "double", "template", "block_comment"}:
    raise AsgError("typescript syntax invalid: unterminated literal/comment")
  if template_expr_depth:
    raise AsgError("typescript syntax invalid: unterminated template expression")
  if braces != 0:
    raise AsgError("typescript syntax invalid: unbalanced braces")
  if parens != 0:
    raise AsgError("typescript syntax invalid: unbalanced parentheses")


def _ts_source_valid_via_tsc(source: str) -> bool:
  """Fallback syntax check using the TypeScript compiler diagnostics."""
  with tempfile.NamedTemporaryFile("w", suffix=".ts", delete=True, encoding="utf-8") as tmp:
    tmp.write(source)
    tmp.flush()
    try:
      proc = subprocess.run(
        [
          "npx",
          "-y",
          "tsc",
          "--pretty",
          "false",
          "--noEmit",
          "--target",
          "ESNext",
          "--lib",
          "ESNext",
          "--module",
          "ESNext",
          "--moduleResolution",
          "Bundler",
          "--skipLibCheck",
          "--noResolve",
          tmp.name,
        ],
        check=False,
        text=True,
        capture_output=True,
      )
    except FileNotFoundError as exc:
      raise AsgError("typescript fallback unavailable: npx not found") from exc
  if proc.returncode == 0:
    return True
  output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
  codes = [int(m.group(1)) for m in TS_DIAG_CODE_RE.finditer(output)]
  if not codes:
    return False
  # Syntax diagnostics are TS1xxx; treat non-syntax diagnostics as syntax-valid.
  return not any(1000 <= code < 2000 for code in codes)


def _run_mjs_estree_parse(source: str, source_path: str) -> dict[str, Any]:
  parser_script = Path(__file__).resolve().parents[2] / "scripts" / "parse-mjs-estree.mjs"
  if not parser_script.is_file():
    raise AsgError(f"mjs parser script missing: {parser_script}")
  try:
    proc = subprocess.run(
      ["node", str(parser_script), "--source-path", source_path],
      input=source,
      text=True,
      capture_output=True,
      check=False,
    )
  except FileNotFoundError as exc:
    raise AsgError("mjs parser unavailable: node not found") from exc
  if proc.returncode != 0:
    detail = (proc.stderr or "").strip().splitlines()
    msg = detail[0] if detail else "estree parse failed"
    raise AsgError(f"mjs syntax invalid: {msg}")
  try:
    payload = json.loads(proc.stdout)
  except json.JSONDecodeError as exc:
    raise AsgError("mjs parser produced invalid json") from exc
  if not isinstance(payload, dict) or "facts" not in payload:
    raise AsgError("mjs parser payload invalid")
  facts = payload["facts"]
  if not isinstance(facts, dict):
    raise AsgError("mjs parser facts invalid")
  return facts


def ingest_typescript_to_asg(source: str, source_path: str, namespace: str) -> dict[str, Any]:
  try:
    _check_ts_syntax(source)
  except AsgError:
    # Keep strict local checks but allow valid TS that trips lexical edge-cases.
    if not _ts_source_valid_via_tsc(source):
      raise
  nodes: dict[str, dict[str, Any]] = {}
  edges: dict[str, dict[str, Any]] = {}

  def add_node(node_id: str, kind: str, attrs: dict[str, Any], start: int, end: int, symbol: str | None = None) -> None:
    if kind not in NODE_KINDS:
      raise AsgError(f"invalid node kind: {kind}")
    nodes[node_id] = {
      "id": node_id,
      "symbol": symbol or f"cp:{kind}",
      "kind": kind,
      "attrs": attrs,
      "source": _ts_span(source, source_path, start, end),
    }

  def add_edge(edge_id: str, kind: str, frm: str, to: str, attrs: dict[str, Any], symbol: str | None = None) -> None:
    if kind not in EDGE_KINDS:
      raise AsgError(f"invalid edge kind: {kind}")
    edges[edge_id] = {
      "id": edge_id,
      "symbol": symbol or f"cp:{kind}",
      "kind": kind,
      "from": frm,
      "to": to,
      "attrs": attrs,
    }

  module_id = "n:module"
  add_node(module_id, "Module", {"name": source_path}, 0, max(0, len(source) - 1))

  for m in re.finditer(r"^\s*import\s+.*?from\s+['\"]([^'\"]+)['\"]\s*;?", source, re.M):
    mod = m.group(1)
    nid = f"n:import:{mod}"
    if nid not in nodes:
      add_node(nid, "Namespace", {"name": mod}, m.start(), m.end(), symbol="cp:Namespace")
    add_edge(f"e:imports:{mod}:{m.start()}", "Imports", module_id, nid, {})

  for m in re.finditer(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:extends\s+([A-Za-z_][A-Za-z0-9_]*))?", source, re.M):
    name = m.group(1)
    ext = m.group(2)
    cid = f"n:class:{name}"
    add_node(cid, "Class", {"name": name}, m.start(), m.end())
    add_edge(f"e:defines:class:{name}", "Defines", module_id, cid, {})
    if ext:
      tid = f"n:typeref:{ext}"
      if tid not in nodes:
        add_node(tid, "TypeRef", {"name": ext}, m.start(), m.end())
      add_edge(f"e:extends:{name}:{ext}", "Extends", cid, tid, {})

  for m in re.finditer(r"^\s*(?:export\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", source, re.M):
    name = m.group(1)
    fid = f"n:function:{name}"
    add_node(fid, "Function", {"name": name}, m.start(), m.end())
    add_edge(f"e:defines:function:{name}", "Defines", module_id, fid, {})

  for m in re.finditer(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*{", source, re.M):
    name = m.group(1)
    if name in {"if", "for", "while", "switch", "catch"}:
      continue
    # Heuristic: treat methods only when not already a function definition.
    if re.search(rf"^\s*(?:export\s+)?function\s+{name}\s*\(", source[m.start() : m.end() + 40], re.M):
      continue
    mid = f"n:method:{name}"
    if mid not in nodes:
      add_node(mid, "Method", {"name": name}, m.start(), m.end())
      add_edge(f"e:defines:method:{name}:{m.start()}", "Defines", module_id, mid, {})

  for m in re.finditer(r"([A-Za-z_][A-Za-z0-9_\.]*)\s*\(", source):
    callee = m.group(1)
    if callee in {"if", "for", "while", "switch", "catch", "function"}:
      continue
    tid = f"n:typeref:{callee}"
    if tid not in nodes:
      add_node(tid, "TypeRef", {"name": callee}, m.start(), m.end())
    add_edge(f"e:calls:{callee}:{m.start()}", "Calls", module_id, tid, {})

  frame = {
    "v": "ak.asg.v0",
    "authority": "advisory",
    "language": "typescript",
    "namespace": namespace,
    "nodes": [nodes[k] for k in sorted(nodes.keys())],
    "edges": [edges[k] for k in sorted(edges.keys())],
    "provenance": {
      "source_path": source_path,
      "parser": "typescript-regex",
      "parser_version": "v0",
    },
    "graph_hash": "",
  }
  frame["graph_hash"] = _hash_frame_without_hash(frame)
  return frame


def ingest_mjs_to_asg(source: str, source_path: str, namespace: str) -> dict[str, Any]:
  facts = _run_mjs_estree_parse(source, source_path)
  nodes: dict[str, dict[str, Any]] = {}
  edges: dict[str, dict[str, Any]] = {}

  def add_node(node_id: str, kind: str, attrs: dict[str, Any], start: int, end: int, symbol: str | None = None) -> None:
    if kind not in NODE_KINDS:
      raise AsgError(f"invalid node kind: {kind}")
    nodes[node_id] = {
      "id": node_id,
      "symbol": symbol or f"cp:{kind}",
      "kind": kind,
      "attrs": attrs,
      "source": _ts_span(source, source_path, start, end),
    }

  def add_edge(edge_id: str, kind: str, frm: str, to: str, attrs: dict[str, Any], symbol: str | None = None) -> None:
    if kind not in EDGE_KINDS:
      raise AsgError(f"invalid edge kind: {kind}")
    edges[edge_id] = {
      "id": edge_id,
      "symbol": symbol or f"cp:{kind}",
      "kind": kind,
      "from": frm,
      "to": to,
      "attrs": attrs,
    }

  module_id = "n:module"
  add_node(module_id, "Module", {"name": source_path}, 0, max(0, len(source) - 1))

  for rec in facts.get("imports", []):
    mod = rec.get("module", "")
    start = int(rec.get("start", 0))
    end = int(rec.get("end", start))
    if not isinstance(mod, str) or not mod:
      continue
    import_id = f"n:import:{mod}"
    if import_id not in nodes:
      add_node(import_id, "Import", {"module": mod}, start, end)
    ns_id = f"n:namespace:{mod}"
    if ns_id not in nodes:
      add_node(ns_id, "Namespace", {"name": mod}, start, end, symbol="cp:Namespace")
    add_edge(f"e:imports:{mod}:{start}", "Imports", module_id, ns_id, {"import_id": import_id})

  classes: dict[str, dict[str, Any]] = {}
  for rec in facts.get("classes", []):
    name = rec.get("name", "")
    ext = rec.get("extends", "")
    start = int(rec.get("start", 0))
    end = int(rec.get("end", start))
    if not isinstance(name, str) or not name:
      continue
    cid = f"n:class:{name}"
    add_node(cid, "Class", {"name": name}, start, end)
    add_edge(f"e:defines:class:{name}", "Defines", module_id, cid, {})
    classes[name] = {"id": cid, "start": start, "end": end}
    export_id = f"n:export:{name}"
    if export_id not in nodes:
      add_node(export_id, "Export", {"name": name, "kind": "class"}, start, end)
    add_edge(f"e:exports:class:{name}:{start}", "Exports", module_id, cid, {"export_node": export_id})
    if isinstance(ext, str) and ext:
      tid = f"n:typeref:{ext}"
      if tid not in nodes:
        add_node(tid, "TypeRef", {"name": ext}, start, end)
      add_edge(f"e:extends:{name}:{ext}", "Extends", cid, tid, {})

  functions: dict[str, dict[str, Any]] = {}
  for rec in facts.get("functions", []):
    name = rec.get("name", "")
    start = int(rec.get("start", 0))
    end = int(rec.get("end", start))
    if not isinstance(name, str) or not name:
      continue
    fid = f"n:function:{name}"
    add_node(fid, "Function", {"name": name}, start, end)
    add_edge(f"e:defines:function:{name}", "Defines", module_id, fid, {})
    functions[name] = {"id": fid, "start": start}

  for rec in facts.get("exports", []):
    name = rec.get("name", "")
    kind = rec.get("kind", "named")
    start = int(rec.get("start", 0))
    end = int(rec.get("end", start))
    if not isinstance(name, str) or not name:
      continue
    export_id = f"n:export:{name}:{start}"
    add_node(export_id, "Export", {"name": name, "kind": kind}, start, end)
    target = ""
    if name in classes:
      target = classes[name]["id"]
    elif name in functions:
      target = functions[name]["id"]
    if target:
      add_edge(f"e:exports:{name}:{start}", "Exports", module_id, target, {"export_node": export_id})

  for rec in facts.get("methods", []):
    owner = rec.get("owner", "")
    name = rec.get("name", "")
    kind = rec.get("kind", "method")
    start = int(rec.get("start", 0))
    end = int(rec.get("end", start))
    if not isinstance(owner, str) or not owner or not isinstance(name, str) or not name:
      continue
    mid = f"n:method:{owner}.{name}:{start}"
    if mid not in nodes:
      add_node(mid, "Method", {"name": name, "owner": owner, "kind": kind}, start, end)
      owner_id = classes.get(owner, {}).get("id", module_id)
      add_edge(f"e:defines:method:{owner}.{name}:{start}", "Defines", owner_id, mid, {})

  for rec in facts.get("variables", []):
    name = rec.get("name", "")
    vkind = rec.get("kind", "let")
    start = int(rec.get("start", 0))
    end = int(rec.get("end", start))
    if not isinstance(name, str) or not name:
      continue
    nkind = "Constant" if vkind == "const" else "Variable"
    vid = f"n:var:{name}:{start}"
    add_node(vid, nkind, {"name": name, "decl": vkind}, start, end)
    add_edge(f"e:defines:var:{name}:{start}", "Defines", module_id, vid, {})

  for rec in facts.get("object_literals", []):
    start = int(rec.get("start", 0))
    end = int(rec.get("end", start))
    oid = f"n:obj:{start}"
    add_node(oid, "ObjectLiteral", {"shape": "object"}, start, end)
    add_edge(f"e:defines:obj:{start}", "Defines", module_id, oid, {})

  for rec in facts.get("calls", []):
    callee = rec.get("callee", "")
    start = int(rec.get("start", 0))
    end = int(rec.get("end", start))
    if not isinstance(callee, str) or not callee:
      continue
    call_id = f"n:call:{callee}:{start}"
    if call_id not in nodes:
      add_node(call_id, "Call", {"name": callee}, start, end)
    tid = f"n:typeref:{callee}"
    if tid not in nodes:
      add_node(tid, "TypeRef", {"name": callee}, start, end)
    add_edge(f"e:calls:{callee}:{start}", "Calls", module_id, tid, {"call_node": call_id})

  frame = {
    "v": "ak.asg.v0",
    "authority": "advisory",
    "language": "mjs",
    "namespace": namespace,
    "nodes": [nodes[k] for k in sorted(nodes.keys())],
    "edges": [edges[k] for k in sorted(edges.keys())],
    "provenance": {
      "source_path": source_path,
      "parser": "mjs-acorn-estree",
      "parser_version": "v0",
    },
    "graph_hash": "",
  }
  frame["graph_hash"] = _hash_frame_without_hash(frame)
  return frame


def validate_asg_frame(frame: dict[str, Any]) -> None:
  if not isinstance(frame, dict):
    raise AsgError("frame must be object")
  keys = set(frame.keys())
  if keys != TOP_KEYS:
    raise AsgError(f"top-level key mismatch missing={sorted(TOP_KEYS-keys)} extra={sorted(keys-TOP_KEYS)}")
  if frame["v"] != "ak.asg.v0":
    raise AsgError("v invalid")
  if frame["authority"] != "advisory":
    raise AsgError("authority invalid")
  if frame["language"] not in LANGUAGES:
    raise AsgError("language invalid")
  if not isinstance(frame["namespace"], str) or not frame["namespace"]:
    raise AsgError("namespace invalid")

  prov = frame["provenance"]
  if not isinstance(prov, dict) or set(prov.keys()) != PROVENANCE_KEYS:
    raise AsgError("provenance invalid")
  if prov["parser"] not in PARSERS:
    raise AsgError("provenance.parser invalid")
  if frame["language"] == "python" and prov["parser"] != "python-ast":
    raise AsgError("language/parser mismatch")
  if frame["language"] == "typescript" and prov["parser"] != "typescript-regex":
    raise AsgError("language/parser mismatch")
  if frame["language"] == "mjs" and prov["parser"] != "mjs-acorn-estree":
    raise AsgError("language/parser mismatch")

  node_ids: set[str] = set()
  for i, node in enumerate(frame["nodes"]):
    if not isinstance(node, dict):
      raise AsgError(f"nodes[{i}] must be object")
    if set(node.keys()) != NODE_KEYS:
      raise AsgError(f"nodes[{i}] key mismatch")
    nid = node["id"]
    if not isinstance(nid, str) or not nid:
      raise AsgError(f"nodes[{i}].id invalid")
    if nid in node_ids:
      raise AsgError(f"duplicate node id: {nid}")
    node_ids.add(nid)
    if node["kind"] not in NODE_KINDS:
      raise AsgError(f"nodes[{i}].kind invalid")
    src = node["source"]
    if not isinstance(src, dict) or set(src.keys()) != SOURCE_KEYS:
      raise AsgError(f"nodes[{i}].source invalid")

  edge_ids: set[str] = set()
  for i, edge in enumerate(frame["edges"]):
    if not isinstance(edge, dict):
      raise AsgError(f"edges[{i}] must be object")
    if set(edge.keys()) != EDGE_KEYS:
      raise AsgError(f"edges[{i}] key mismatch")
    eid = edge["id"]
    if not isinstance(eid, str) or not eid:
      raise AsgError(f"edges[{i}].id invalid")
    if eid in edge_ids:
      raise AsgError(f"duplicate edge id: {eid}")
    edge_ids.add(eid)
    if edge["kind"] not in EDGE_KINDS:
      raise AsgError(f"edges[{i}].kind invalid")
    if edge["from"] not in node_ids or edge["to"] not in node_ids:
      raise AsgError(f"edges[{i}] references missing nodes")

  expected = _hash_frame_without_hash(frame)
  if frame["graph_hash"] != expected:
    raise AsgError("graph_hash mismatch")
