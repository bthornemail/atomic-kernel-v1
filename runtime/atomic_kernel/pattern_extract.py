"""Deterministic pattern extraction over ASG frames."""

from __future__ import annotations

from typing import Any

from .asg import AsgError, validate_asg_frame


class PatternExtractError(ValueError):
  """Pattern extraction failure."""


REQUIRED_PATTERN_KEYS = {
  "v",
  "authority",
  "pattern_id",
  "pattern_type",
  "subject_nodes",
  "role_bindings",
  "evidence_edges",
  "constraints_passed",
  "confidence",
  "source_frame_hash",
}


def _classify_arch_domain(s: str) -> str:
  s = s.lower()
  if "canbc" in s:
    return "abi"
  if any(tok in s for tok in ("canisa", "interpreter")):
    return "eabi"
  if any(tok in s for tok in ("control", "surface", "frame", "separator")):
    return "control"
  if any(tok in s for tok in ("waveform", "unicode", "carrier", "spherepack", "hw_canon", "hw_project", "validate_jsonl", "drift_scan")):
    return "carrier"
  if any(tok in s for tok in ("projection", "viewer", "portal", "obsidian", "esbuild")):
    return "projection"
  if any(tok in s for tok in ("runtime", "vm", "scheduler", "memory", "identity", "seed", "lane16")):
    return "runtime"
  if any(tok in s for tok in ("test", "verify", "witness", "conformance", "golden", "replay", "assert", "check", "run_all")):
    return "conformance"
  return "core"


def _strip_sha256_prefix(graph_hash: str) -> str:
  if not graph_hash.startswith("sha256:"):
    raise PatternExtractError("graph_hash must use sha256: prefix")
  return graph_hash.split(":", 1)[1]


def _validate_pattern_instance(pattern: dict[str, Any]) -> None:
  keys = set(pattern.keys())
  allowed = REQUIRED_PATTERN_KEYS | {"alternates"}
  extra = keys - allowed
  missing = REQUIRED_PATTERN_KEYS - keys
  if extra:
    raise PatternExtractError(f"pattern unknown keys: {sorted(extra)}")
  if missing:
    raise PatternExtractError(f"pattern missing keys: {sorted(missing)}")
  if pattern["v"] != "ak.pattern.instance.v0":
    raise PatternExtractError("pattern.v invalid")
  if pattern["authority"] != "advisory":
    raise PatternExtractError("pattern.authority invalid")
  if pattern["pattern_type"] not in {
    "Adapter",
    "Facade",
    "Observer",
    "Strategy",
    "Builder",
    "BoundarySplit",
    "ProjectionOnlySurface",
    "BridgeLayer",
    "CarrierLayer",
    "ConformanceSurface",
  }:
    raise PatternExtractError("pattern.pattern_type invalid")
  if not isinstance(pattern["subject_nodes"], list) or not pattern["subject_nodes"]:
    raise PatternExtractError("pattern.subject_nodes invalid")
  if not isinstance(pattern["role_bindings"], dict) or not pattern["role_bindings"]:
    raise PatternExtractError("pattern.role_bindings invalid")
  if not isinstance(pattern["evidence_edges"], list) or not pattern["evidence_edges"]:
    raise PatternExtractError("pattern.evidence_edges invalid")
  if not isinstance(pattern["constraints_passed"], list):
    raise PatternExtractError("pattern.constraints_passed invalid")
  conf = pattern["confidence"]
  if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
    raise PatternExtractError("pattern.confidence invalid")
  sfh = pattern["source_frame_hash"]
  if not isinstance(sfh, str) or len(sfh) != 64:
    raise PatternExtractError("pattern.source_frame_hash invalid")
  alts = pattern.get("alternates", [])
  if not isinstance(alts, list):
    raise PatternExtractError("pattern.alternates invalid")


def extract_patterns_from_asg(frame: dict[str, Any]) -> list[dict[str, Any]]:
  try:
    validate_asg_frame(frame)
  except AsgError as exc:
    raise PatternExtractError(str(exc)) from exc

  source_frame_hash = _strip_sha256_prefix(frame["graph_hash"])
  nodes = frame["nodes"]
  edges = frame["edges"]

  node_by_id = {n["id"]: n for n in nodes}
  calls_by_from: dict[str, list[dict[str, Any]]] = {}
  for e in edges:
    if e["kind"] == "Calls":
      calls_by_from.setdefault(e["from"], []).append(e)
  for k in list(calls_by_from.keys()):
    calls_by_from[k].sort(key=lambda e: e["id"])

  imports = sorted([e for e in edges if e["kind"] == "Imports"], key=lambda e: e["id"])
  extends_by_class: dict[str, list[dict[str, Any]]] = {}
  for e in edges:
    if e["kind"] == "Extends":
      extends_by_class.setdefault(e["from"], []).append(e)
  for k in list(extends_by_class.keys()):
    extends_by_class[k].sort(key=lambda e: e["id"])

  methods_by_owner: dict[str, list[dict[str, Any]]] = {}
  for n in nodes:
    if n["kind"] != "Method":
      continue
    owner = n.get("attrs", {}).get("owner")
    if isinstance(owner, str) and owner:
      methods_by_owner.setdefault(f"n:class:{owner}", []).append(n)
  for k in list(methods_by_owner.keys()):
    methods_by_owner[k].sort(key=lambda n: n["id"])

  source_path = str(frame.get("provenance", {}).get("source_path", ""))
  source_path_l = source_path.lower()

  out: list[dict[str, Any]] = []

  class_nodes = sorted([n for n in nodes if n["kind"] == "Class"], key=lambda n: n["id"])
  for cls in class_nodes:
    cid = cls["id"]
    class_name = cls.get("attrs", {}).get("name", cid)
    methods = methods_by_owner.get(cid, [])
    extends = extends_by_class.get(cid, [])
    method_calls: list[dict[str, Any]] = []
    for m in methods:
      method_calls.extend(calls_by_from.get(m["id"], []))
    method_calls.sort(key=lambda e: e["id"])

    if extends and method_calls:
      ext = extends[0]
      call = method_calls[0]
      adapter = {
        "v": "ak.pattern.instance.v0",
        "authority": "advisory",
        "pattern_id": f"pi.adapter.{class_name}",
        "pattern_type": "Adapter",
        "subject_nodes": [cid],
        "role_bindings": {
          "adapter": cid,
          "target_interface": ext["to"],
          "adaptee": call["to"],
        },
        "evidence_edges": [ext["id"], call["id"]],
        "constraints_passed": ["adapter-shape-v0", "delegation-present-v0"],
        "confidence": 0.91,
        "alternates": ["Facade"],
        "source_frame_hash": source_frame_hash,
      }
      _validate_pattern_instance(adapter)
      out.append(adapter)

    if len(methods) >= 2 and len(imports) >= 1:
      distinct_targets = sorted({e["to"] for e in method_calls})
      if len(distinct_targets) >= 2:
        evidence = [e["id"] for e in method_calls[:2]] + [imports[0]["id"]]
        facade = {
          "v": "ak.pattern.instance.v0",
          "authority": "advisory",
          "pattern_id": f"pi.facade.{class_name}",
          "pattern_type": "Facade",
          "subject_nodes": [cid],
          "role_bindings": {"facade": cid},
          "evidence_edges": evidence,
          "constraints_passed": ["facade-shape-v0", "multi-subsystem-dependency-v0"],
          "confidence": 0.83,
          "source_frame_hash": source_frame_hash,
        }
        _validate_pattern_instance(facade)
        out.append(facade)

    method_name_to_node = {m.get("attrs", {}).get("name", ""): m for m in methods}
    register_methods = sorted(
      [m for m in methods if any(tok in str(m.get("attrs", {}).get("name", "")).lower() for tok in ("register", "subscribe", "attach"))],
      key=lambda m: m["id"],
    )
    notify_methods = sorted(
      [m for m in methods if any(tok in str(m.get("attrs", {}).get("name", "")).lower() for tok in ("notify", "publish", "emit"))],
      key=lambda m: m["id"],
    )
    observer_calls: list[dict[str, Any]] = []
    for m in notify_methods:
      for call in calls_by_from.get(m["id"], []):
        callee = str(node_by_id.get(call["to"], {}).get("attrs", {}).get("name", ""))
        low = callee.lower()
        if any(tok in low for tok in ("update", "observer", "listener", "notify")):
          observer_calls.append(call)
    observer_calls.sort(key=lambda e: e["id"])

    if register_methods and notify_methods and observer_calls:
      reg = register_methods[0]
      notify = notify_methods[0]
      call = observer_calls[0]
      observer = {
        "v": "ak.pattern.instance.v0",
        "authority": "advisory",
        "pattern_id": f"pi.observer.{class_name}",
        "pattern_type": "Observer",
        "subject_nodes": [cid],
        "role_bindings": {
          "subject": cid,
          "observer": call["to"],
          "register_method": reg["id"],
          "notify_method": notify["id"],
        },
        "evidence_edges": [call["id"]],
        "constraints_passed": ["observer-shape-v0", "broadcast-update-v0"],
        "confidence": 0.84,
        "source_frame_hash": source_frame_hash,
      }
      _validate_pattern_instance(observer)
      out.append(observer)

    strategy_calls: list[dict[str, Any]] = []
    for m in methods:
      for call in calls_by_from.get(m["id"], []):
        callee = str(node_by_id.get(call["to"], {}).get("attrs", {}).get("name", "")).lower()
        if (".strategy." in callee) or callee.startswith("strategy.") or ".execute" in callee:
          strategy_calls.append(call)
    strategy_calls.sort(key=lambda e: e["id"])

    if strategy_calls:
      sc = strategy_calls[0]
      strategy = {
        "v": "ak.pattern.instance.v0",
        "authority": "advisory",
        "pattern_id": f"pi.strategy.{class_name}",
        "pattern_type": "Strategy",
        "subject_nodes": [cid],
        "role_bindings": {
          "context": cid,
          "strategy": sc["to"],
        },
        "evidence_edges": [sc["id"]],
        "constraints_passed": ["strategy-shape-v0", "delegated-algorithm-call-v0"],
        "confidence": 0.82,
        "source_frame_hash": source_frame_hash,
      }
      _validate_pattern_instance(strategy)
      out.append(strategy)

    build_methods = sorted(
      [m for m in methods if "build" in str(m.get("attrs", {}).get("name", "")).lower()],
      key=lambda m: m["id"],
    )
    configure_methods = sorted(
      [
        m
        for m in methods
        if any(tok in str(m.get("attrs", {}).get("name", "")).lower() for tok in ("set", "add", "with"))
      ],
      key=lambda m: m["id"],
    )
    builder_calls: list[dict[str, Any]] = []
    for m in build_methods:
      builder_calls.extend(calls_by_from.get(m["id"], []))
    builder_calls.sort(key=lambda e: e["id"])

    if build_methods and configure_methods:
      product_ref = builder_calls[0]["to"] if builder_calls else build_methods[0]["id"]
      evidence = [build_methods[0]["id"], configure_methods[0]["id"]]
      if builder_calls:
        evidence.append(builder_calls[0]["id"])
      builder = {
        "v": "ak.pattern.instance.v0",
        "authority": "advisory",
        "pattern_id": f"pi.builder.{class_name}",
        "pattern_type": "Builder",
        "subject_nodes": [cid],
        "role_bindings": {
          "builder": cid,
          "product": product_ref,
          "build_method": build_methods[0]["id"],
        },
        "evidence_edges": evidence,
        "constraints_passed": ["builder-shape-v0", "staged-construction-v0"],
        "confidence": 0.8,
        "source_frame_hash": source_frame_hash,
      }
      _validate_pattern_instance(builder)
      out.append(builder)

  # Repo-profile architecture detectors (MJS-first).
  if frame.get("language") == "mjs":
    module_id = "n:module"
    module_domain = _classify_arch_domain(source_path_l)
    import_edges = sorted([e for e in edges if e["kind"] == "Imports"], key=lambda e: e["id"])
    call_edges = sorted([e for e in edges if e["kind"] == "Calls"], key=lambda e: e["id"])
    import_targets = [
      str(node_by_id.get(e["to"], {}).get("attrs", {}).get("name", "")).lower()
      for e in import_edges
    ]

    import_domains = sorted({_classify_arch_domain(t) for t in import_targets if t})
    call_targets = [
      str(node_by_id.get(e["to"], {}).get("attrs", {}).get("name", "")).lower()
      for e in call_edges
    ]
    call_domains = sorted({_classify_arch_domain(t) for t in call_targets if t})

    # Topology grouping: domain -> supporting edges for this module.
    domain_edges: dict[str, list[dict[str, Any]]] = {}
    for e in import_edges:
      t = str(node_by_id.get(e["to"], {}).get("attrs", {}).get("name", "")).lower()
      d = _classify_arch_domain(t)
      domain_edges.setdefault(d, []).append(e)
    for e in call_edges:
      t = str(node_by_id.get(e["to"], {}).get("attrs", {}).get("name", "")).lower()
      d = _classify_arch_domain(t)
      domain_edges.setdefault(d, []).append(e)
    for d in list(domain_edges.keys()):
      domain_edges[d].sort(key=lambda x: x["id"])

    has_canbc = any("canbc" in t for t in import_targets)
    has_canisa = any("canisa" in t for t in import_targets)
    has_abi = ("abi" in source_path_l) or any("abi" in t for t in import_targets)
    has_eabi = ("eabi" in source_path_l) or any("eabi" in t for t in import_targets)
    if import_edges and ((has_abi and has_eabi) or (has_canbc and has_canisa)):
      be = import_edges[:2]
      boundary = {
        "v": "ak.pattern.instance.v0",
        "authority": "advisory",
        "pattern_id": f"pi.boundary_split.{source_path_l.replace('/', '.').replace(':', '.')}",
        "pattern_type": "BoundarySplit",
        "subject_nodes": [module_id],
        "role_bindings": {
          "module": module_id,
          "semantic_side": be[0]["to"],
          "invocation_side": be[-1]["to"],
        },
        "evidence_edges": [e["id"] for e in be],
        "constraints_passed": ["boundary-split-imports-v0"],
        "confidence": 0.86,
        "source_frame_hash": source_frame_hash,
      }
      _validate_pattern_instance(boundary)
      out.append(boundary)

    projection_path = any(tok in source_path_l for tok in ("wave32", "projection", "portal", "viewer", "obsidian", "trees/"))
    projection_import = any(
      tok in target
      for target in import_targets
      for tok in ("esbuild", "react", "viewer", "render", "projection", "obsidian")
    )
    if import_edges and (projection_path or projection_import):
      pe = import_edges[0]
      projection = {
        "v": "ak.pattern.instance.v0",
        "authority": "advisory",
        "pattern_id": f"pi.projection_only_surface.{source_path_l.replace('/', '.').replace(':', '.')}",
        "pattern_type": "ProjectionOnlySurface",
        "subject_nodes": [module_id],
        "role_bindings": {
          "surface_module": module_id,
          "projection_dep": pe["to"],
        },
        "evidence_edges": [pe["id"]],
        "constraints_passed": ["projection-surface-imports-v0"],
        "confidence": 0.8,
        "source_frame_hash": source_frame_hash,
      }
      _validate_pattern_instance(projection)
      out.append(projection)

    bridge_domains = {"control", "carrier", "abi", "eabi", "projection", "runtime"}
    connected_domains = sorted(d for d, es in domain_edges.items() if d in bridge_domains and es)
    # Topology-aware bridge rule:
    # - connects >=2 architecture domains
    # - includes both import and call participation in at least one connected domain
    has_import_in_bridge = any(
      any(e["kind"] == "Imports" for e in domain_edges[d]) for d in connected_domains
    )
    has_call_in_bridge = any(
      any(e["kind"] == "Calls" for e in domain_edges[d]) for d in connected_domains
    )
    if len(connected_domains) >= 2 and has_import_in_bridge and has_call_in_bridge:
      evidence: list[str] = []
      for d in connected_domains:
        for e in domain_edges[d][:2]:
          if e["id"] not in evidence:
            evidence.append(e["id"])
      evidence = evidence[:6]
      confidence = min(0.95, 0.74 + 0.04 * len(connected_domains))
      bridge = {
        "v": "ak.pattern.instance.v0",
        "authority": "advisory",
        "pattern_id": f"pi.bridge_layer.{source_path_l.replace('/', '.').replace(':', '.')}",
        "pattern_type": "BridgeLayer",
        "subject_nodes": [module_id],
        "role_bindings": {
          "bridge_module": module_id,
          "domain_a": connected_domains[0],
          "domain_b": connected_domains[1],
        },
        "evidence_edges": evidence,
        "constraints_passed": ["bridge-topology-domains-v1", "bridge-import-call-participation-v1"],
        "confidence": confidence,
        "source_frame_hash": source_frame_hash,
      }
      _validate_pattern_instance(bridge)
      out.append(bridge)

    carrier_path = any(
      tok in source_path_l
      for tok in ("waveform", "unicode", "carrier", "spherepack", "hw_canon", "hw_project", "validate_jsonl", "drift_scan")
    )
    carrier_import = any(_classify_arch_domain(t) == "carrier" for t in import_targets)
    carrier_call = any(
      any(tok in target for tok in ("canon", "project", "validate", "jsonl", "hash", "encode", "decode"))
      for target in call_targets
    )
    # Topology-aware carrier rule:
    # - carrier signal from path/import
    # - must have a carrier domain edge group and operational behavior signal
    has_carrier_domain_edges = bool(domain_edges.get("carrier")) or module_domain == "carrier"
    if (carrier_path or carrier_import) and has_carrier_domain_edges and (carrier_call or bool(call_edges)):
      evidence = []
      for e in domain_edges.get("carrier", [])[:2]:
        evidence.append(e["id"])
      for e in call_edges[:1]:
        if e["id"] not in evidence:
          evidence.append(e["id"])
      if not evidence:
        evidence = [f"edge:synthetic:path:{source_path_l}"]
      carrier = {
        "v": "ak.pattern.instance.v0",
        "authority": "advisory",
        "pattern_id": f"pi.carrier_layer.{source_path_l.replace('/', '.').replace(':', '.')}",
        "pattern_type": "CarrierLayer",
        "subject_nodes": [module_id],
        "role_bindings": {
          "carrier_module": module_id,
        },
        "evidence_edges": evidence,
        "constraints_passed": ["carrier-topology-domain-v1", "carrier-operational-signal-v1"],
        "confidence": 0.8,
        "source_frame_hash": source_frame_hash,
      }
      _validate_pattern_instance(carrier)
      out.append(carrier)

    conformance_path = any(tok in source_path_l for tok in ("test", "verify", "witness", "conformance", "golden", "replay"))
    conformance_import = any(_classify_arch_domain(t) == "conformance" for t in import_targets)
    conformance_call = any(
      any(tok in target for tok in ("assert", "verify", "check", "test", "run"))
      for target in call_targets
    )
    has_conformance_domain_edges = bool(domain_edges.get("conformance")) or module_domain == "conformance"
    if (conformance_path or conformance_import) and has_conformance_domain_edges and (conformance_call or bool(call_edges)):
      evidence = []
      for e in domain_edges.get("conformance", [])[:2]:
        evidence.append(e["id"])
      for e in call_edges[:1]:
        if e["id"] not in evidence:
          evidence.append(e["id"])
      if not evidence:
        evidence = [f"edge:synthetic:path:{source_path_l}"]
      conformance = {
        "v": "ak.pattern.instance.v0",
        "authority": "advisory",
        "pattern_id": f"pi.conformance_surface.{source_path_l.replace('/', '.').replace(':', '.')}",
        "pattern_type": "ConformanceSurface",
        "subject_nodes": [module_id],
        "role_bindings": {
          "conformance_module": module_id,
        },
        "evidence_edges": evidence,
        "constraints_passed": ["conformance-topology-domain-v1", "conformance-operational-signal-v1"],
        "confidence": 0.82,
        "source_frame_hash": source_frame_hash,
      }
      _validate_pattern_instance(conformance)
      out.append(conformance)

  out.sort(key=lambda p: (p["pattern_type"], p["pattern_id"]))
  return out
