#!/usr/bin/env python3
"""Fail-closed validator for semantic contract v0 schemas and fixtures."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

STATE_MACHINE_KEYS = {
    "v",
    "authority",
    "machine_id",
    "machine_kind",
    "root_region",
    "regions",
    "states",
    "transitions",
    "extended_state_schema",
    "source_frame_hash",
}

REGION_KEYS = {"id", "parent_state_id", "orthogonal_index"}
STATE_KEYS = {"id", "name", "region_id", "state_kind", "entry_actions", "exit_actions", "internal_transitions"}
TRANS_KEYS = {"id", "source_state_id", "target_state_id", "event", "guard", "actions", "priority"}

PATTERN_KEYS = {
    "v",
    "authority",
    "pattern_type",
    "subject_nodes",
    "role_bindings",
    "evidence_edges",
    "constraints_passed",
    "confidence",
    "source_frame_hash",
    "alternates",
}

DIAGRAM_KEYS = {
    "v",
    "authority",
    "view_id",
    "view_type",
    "source_frame_hash",
    "elements",
    "relations",
    "layout",
    "annotations",
}

DIAG_ELEMENT_KEYS = {"id", "kind", "ref_kind", "ref_id", "label"}
DIAG_REL_KEYS = {"id", "kind", "from", "to", "ref_kind", "ref_id"}
DIAG_ANNOT_KEYS = {"kind", "target", "text"}

PATTERN_TYPES = {"Adapter", "Facade", "Strategy", "Observer", "Builder"}
EXT_TYPES = {"int", "float", "string", "bool", "json"}
STATE_KINDS = {"simple", "composite", "final"}
MACHINE_KINDS = {"behavioral", "protocol"}
DIAG_VIEW_TYPES = {"class", "component", "state"}
DIAG_ELEMENT_KINDS = {"class", "interface", "component", "state", "region", "note", "pattern_overlay"}
DIAG_ELEMENT_REF_KINDS = {"node", "state", "region", "pattern", "none"}
DIAG_REL_KINDS = {"association", "dependency", "composition", "transition", "implements", "extends"}
DIAG_REL_REF_KINDS = {"edge", "transition", "none"}
DIAG_ANNOT_KINDS = {"info", "warning", "pattern"}
EPI_KEYS = {
    "v",
    "authority",
    "assertion_id",
    "subject_kind",
    "subject_id",
    "status",
    "confidence",
    "evidence_refs",
    "source_frame_hash",
    "rationale",
    "constraints",
}
EPI_SUBJECT_KINDS = {"node", "edge", "state", "transition", "pattern", "diagram_element", "diagram_relation"}
EPI_STATUS = {"observed", "inferred", "validated", "projected", "rejected"}


def fail(msg: str) -> None:
    raise ValueError(msg)


def require_keys(obj: dict, allowed: set[str], required: set[str], ctx: str) -> None:
    got = set(obj.keys())
    extra = got - allowed
    missing = required - got
    if extra:
        fail(f"{ctx}: unknown keys: {sorted(extra)}")
    if missing:
        fail(f"{ctx}: missing keys: {sorted(missing)}")


def require_str(v: object, ctx: str) -> str:
    if not isinstance(v, str) or not v:
        fail(f"{ctx}: expected non-empty string")
    return v


def require_str_list(v: object, ctx: str, min_items: int = 0) -> list[str]:
    if not isinstance(v, list):
        fail(f"{ctx}: expected list")
    if len(v) < min_items:
        fail(f"{ctx}: expected at least {min_items} items")
    out: list[str] = []
    for i, item in enumerate(v):
        out.append(require_str(item, f"{ctx}[{i}]"))
    return out


def validate_state_machine(data: dict) -> None:
    require_keys(data, STATE_MACHINE_KEYS, STATE_MACHINE_KEYS, "state-machine")

    if data["v"] != "ak.state_machine.v0":
        fail("state-machine.v must be ak.state_machine.v0")
    if data["authority"] != "advisory":
        fail("state-machine.authority must be advisory")
    require_str(data["machine_id"], "state-machine.machine_id")

    if data["machine_kind"] not in MACHINE_KINDS:
        fail("state-machine.machine_kind invalid")

    root_region = require_str(data["root_region"], "state-machine.root_region")

    regions = data["regions"]
    if not isinstance(regions, list) or not regions:
        fail("state-machine.regions must be non-empty list")

    region_ids: set[str] = set()
    for i, r in enumerate(regions):
        if not isinstance(r, dict):
            fail(f"state-machine.regions[{i}] must be object")
        require_keys(r, REGION_KEYS, REGION_KEYS, f"state-machine.regions[{i}]")
        rid = require_str(r["id"], f"state-machine.regions[{i}].id")
        if rid in region_ids:
            fail(f"state-machine.regions[{i}]: duplicate region id {rid}")
        region_ids.add(rid)
        pid = r["parent_state_id"]
        if pid is not None and not isinstance(pid, str):
            fail(f"state-machine.regions[{i}].parent_state_id must be string|null")
        if not isinstance(r["orthogonal_index"], int) or r["orthogonal_index"] < 0:
            fail(f"state-machine.regions[{i}].orthogonal_index must be int >= 0")

    if root_region not in region_ids:
        fail("state-machine.root_region must reference existing region")

    states = data["states"]
    if not isinstance(states, list) or not states:
        fail("state-machine.states must be non-empty list")

    state_ids: set[str] = set()
    transition_ids_refd: set[str] = set()
    for i, s in enumerate(states):
        if not isinstance(s, dict):
            fail(f"state-machine.states[{i}] must be object")
        require_keys(s, STATE_KEYS, STATE_KEYS, f"state-machine.states[{i}]")
        sid = require_str(s["id"], f"state-machine.states[{i}].id")
        if sid in state_ids:
            fail(f"state-machine.states[{i}]: duplicate state id {sid}")
        state_ids.add(sid)
        require_str(s["name"], f"state-machine.states[{i}].name")
        rid = require_str(s["region_id"], f"state-machine.states[{i}].region_id")
        if rid not in region_ids:
            fail(f"state-machine.states[{i}].region_id references missing region")
        if s["state_kind"] not in STATE_KINDS:
            fail(f"state-machine.states[{i}].state_kind invalid")
        require_str_list(s["entry_actions"], f"state-machine.states[{i}].entry_actions")
        require_str_list(s["exit_actions"], f"state-machine.states[{i}].exit_actions")
        ints = require_str_list(s["internal_transitions"], f"state-machine.states[{i}].internal_transitions")
        transition_ids_refd.update(ints)

    transitions = data["transitions"]
    if not isinstance(transitions, list):
        fail("state-machine.transitions must be list")

    transition_ids: set[str] = set()
    for i, t in enumerate(transitions):
        if not isinstance(t, dict):
            fail(f"state-machine.transitions[{i}] must be object")
        require_keys(t, TRANS_KEYS, TRANS_KEYS, f"state-machine.transitions[{i}]")
        tid = require_str(t["id"], f"state-machine.transitions[{i}].id")
        if tid in transition_ids:
            fail(f"state-machine.transitions[{i}]: duplicate transition id {tid}")
        transition_ids.add(tid)

        src = require_str(t["source_state_id"], f"state-machine.transitions[{i}].source_state_id")
        if src not in state_ids:
            fail(f"state-machine.transitions[{i}].source_state_id references missing state")
        tgt = t["target_state_id"]
        if tgt is not None:
            tgt = require_str(tgt, f"state-machine.transitions[{i}].target_state_id")
            if tgt not in state_ids:
                fail(f"state-machine.transitions[{i}].target_state_id references missing state")

        require_str(t["event"], f"state-machine.transitions[{i}].event")
        guard = t["guard"]
        if guard is not None and not isinstance(guard, str):
            fail(f"state-machine.transitions[{i}].guard must be string|null")
        require_str_list(t["actions"], f"state-machine.transitions[{i}].actions")
        if not isinstance(t["priority"], int) or t["priority"] < 0:
            fail(f"state-machine.transitions[{i}].priority must be int >= 0")

    unknown_int_refs = transition_ids_refd - transition_ids
    if unknown_int_refs:
        fail(f"state-machine.internal_transitions references missing ids: {sorted(unknown_int_refs)}")

    ext = data["extended_state_schema"]
    if not isinstance(ext, dict):
        fail("state-machine.extended_state_schema must be object")
    for k, v in ext.items():
        require_str(k, "state-machine.extended_state_schema key")
        if v not in EXT_TYPES:
            fail(f"state-machine.extended_state_schema[{k}] invalid type")

    source_hash = require_str(data["source_frame_hash"], "state-machine.source_frame_hash")
    if not HEX64_RE.fullmatch(source_hash):
        fail("state-machine.source_frame_hash must be 64 lower-hex chars")


def validate_pattern_instance(data: dict) -> None:
    require_keys(data, PATTERN_KEYS, PATTERN_KEYS - {"alternates"}, "pattern-instance")

    if data["v"] != "ak.pattern.instance.v0":
        fail("pattern-instance.v must be ak.pattern.instance.v0")
    if data["authority"] != "advisory":
        fail("pattern-instance.authority must be advisory")
    if data["pattern_type"] not in PATTERN_TYPES:
        fail("pattern-instance.pattern_type invalid")

    require_str_list(data["subject_nodes"], "pattern-instance.subject_nodes", min_items=1)

    rb = data["role_bindings"]
    if not isinstance(rb, dict) or not rb:
        fail("pattern-instance.role_bindings must be non-empty object")
    for k, v in rb.items():
        require_str(k, "pattern-instance.role_bindings key")
        require_str(v, f"pattern-instance.role_bindings[{k}]")

    require_str_list(data["evidence_edges"], "pattern-instance.evidence_edges", min_items=1)
    require_str_list(data["constraints_passed"], "pattern-instance.constraints_passed")

    conf = data["confidence"]
    if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
        fail("pattern-instance.confidence must be in [0.0, 1.0]")

    alts = data.get("alternates", [])
    require_str_list(alts, "pattern-instance.alternates")

    source_hash = require_str(data["source_frame_hash"], "pattern-instance.source_frame_hash")
    if not HEX64_RE.fullmatch(source_hash):
        fail("pattern-instance.source_frame_hash must be 64 lower-hex chars")


def validate_diagram_view(data: dict) -> None:
    require_keys(data, DIAGRAM_KEYS, DIAGRAM_KEYS, "diagram-view")

    if data["v"] != "ak.diagram_view.v0":
        fail("diagram-view.v must be ak.diagram_view.v0")
    if data["authority"] != "advisory":
        fail("diagram-view.authority must be advisory")
    require_str(data["view_id"], "diagram-view.view_id")
    if data["view_type"] not in DIAG_VIEW_TYPES:
        fail("diagram-view.view_type invalid")
    source_hash = require_str(data["source_frame_hash"], "diagram-view.source_frame_hash")
    if not HEX64_RE.fullmatch(source_hash):
        fail("diagram-view.source_frame_hash must be 64 lower-hex chars")

    elements = data["elements"]
    if not isinstance(elements, list) or not elements:
        fail("diagram-view.elements must be non-empty list")
    element_ids: set[str] = set()
    for i, el in enumerate(elements):
        if not isinstance(el, dict):
            fail(f"diagram-view.elements[{i}] must be object")
        require_keys(el, DIAG_ELEMENT_KEYS, DIAG_ELEMENT_KEYS, f"diagram-view.elements[{i}]")
        eid = require_str(el["id"], f"diagram-view.elements[{i}].id")
        if eid in element_ids:
            fail(f"diagram-view.elements[{i}]: duplicate id {eid}")
        element_ids.add(eid)
        if el["kind"] not in DIAG_ELEMENT_KINDS:
            fail(f"diagram-view.elements[{i}].kind invalid")
        if el["ref_kind"] not in DIAG_ELEMENT_REF_KINDS:
            fail(f"diagram-view.elements[{i}].ref_kind invalid")
        require_str(el["ref_id"], f"diagram-view.elements[{i}].ref_id")
        require_str(el["label"], f"diagram-view.elements[{i}].label")

    relations = data["relations"]
    if not isinstance(relations, list):
        fail("diagram-view.relations must be list")
    rel_ids: set[str] = set()
    for i, rel in enumerate(relations):
        if not isinstance(rel, dict):
            fail(f"diagram-view.relations[{i}] must be object")
        require_keys(rel, DIAG_REL_KEYS, DIAG_REL_KEYS, f"diagram-view.relations[{i}]")
        rid = require_str(rel["id"], f"diagram-view.relations[{i}].id")
        if rid in rel_ids:
            fail(f"diagram-view.relations[{i}]: duplicate id {rid}")
        rel_ids.add(rid)
        if rel["kind"] not in DIAG_REL_KINDS:
            fail(f"diagram-view.relations[{i}].kind invalid")
        frm = require_str(rel["from"], f"diagram-view.relations[{i}].from")
        to = require_str(rel["to"], f"diagram-view.relations[{i}].to")
        if frm not in element_ids or to not in element_ids:
            fail(f"diagram-view.relations[{i}] references missing element id")
        if rel["ref_kind"] not in DIAG_REL_REF_KINDS:
            fail(f"diagram-view.relations[{i}].ref_kind invalid")
        require_str(rel["ref_id"], f"diagram-view.relations[{i}].ref_id")

    layout = data["layout"]
    if not isinstance(layout, dict):
        fail("diagram-view.layout must be object")
    for eid, box in layout.items():
        if eid not in element_ids:
            fail("diagram-view.layout references missing element id")
        if not isinstance(box, dict):
            fail(f"diagram-view.layout[{eid}] must be object")
        require_keys(box, {"x", "y", "w", "h"}, {"x", "y", "w", "h"}, f"diagram-view.layout[{eid}]")
        for key in ("x", "y", "w", "h"):
            if not isinstance(box[key], int):
                fail(f"diagram-view.layout[{eid}].{key} must be int")
        if box["w"] < 1 or box["h"] < 1:
            fail(f"diagram-view.layout[{eid}] dimensions must be >= 1")

    annotations = data["annotations"]
    if not isinstance(annotations, list):
        fail("diagram-view.annotations must be list")
    for i, ann in enumerate(annotations):
        if not isinstance(ann, dict):
            fail(f"diagram-view.annotations[{i}] must be object")
        require_keys(ann, DIAG_ANNOT_KEYS, DIAG_ANNOT_KEYS, f"diagram-view.annotations[{i}]")
        if ann["kind"] not in DIAG_ANNOT_KINDS:
            fail(f"diagram-view.annotations[{i}].kind invalid")
        target = require_str(ann["target"], f"diagram-view.annotations[{i}].target")
        if target not in element_ids:
            fail(f"diagram-view.annotations[{i}] target references missing element id")
        require_str(ann["text"], f"diagram-view.annotations[{i}].text")


def validate_epistemic_assertion(data: dict) -> None:
    require_keys(data, EPI_KEYS, EPI_KEYS - {"constraints"}, "epistemic-assertion")

    if data["v"] != "ak.epistemic_assertion.v0":
        fail("epistemic-assertion.v must be ak.epistemic_assertion.v0")
    if data["authority"] != "advisory":
        fail("epistemic-assertion.authority must be advisory")
    require_str(data["assertion_id"], "epistemic-assertion.assertion_id")
    if data["subject_kind"] not in EPI_SUBJECT_KINDS:
        fail("epistemic-assertion.subject_kind invalid")
    require_str(data["subject_id"], "epistemic-assertion.subject_id")
    if data["status"] not in EPI_STATUS:
        fail("epistemic-assertion.status invalid")

    conf = data["confidence"]
    if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
        fail("epistemic-assertion.confidence must be in [0.0, 1.0]")
    require_str_list(data["evidence_refs"], "epistemic-assertion.evidence_refs", min_items=1)
    source_hash = require_str(data["source_frame_hash"], "epistemic-assertion.source_frame_hash")
    if not HEX64_RE.fullmatch(source_hash):
        fail("epistemic-assertion.source_frame_hash must be 64 lower-hex chars")
    require_str(data["rationale"], "epistemic-assertion.rationale")
    require_str_list(data.get("constraints", []), "epistemic-assertion.constraints")


def load_json(path: Path) -> dict:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise ValueError(f"{path}: top-level value must be object")
    return obj


def validate_fixture_dir(kind: str, accept_dir: Path, reject_dir: Path) -> None:
    if kind == "state-machine":
        validator = validate_state_machine
    elif kind == "pattern-instance":
        validator = validate_pattern_instance
    elif kind == "diagram-view":
        validator = validate_diagram_view
    else:
        validator = validate_epistemic_assertion

    accept_files = sorted(accept_dir.glob("*.json"))
    reject_files = sorted(reject_dir.glob("*.json"))
    if not accept_files:
        fail(f"{kind}: no accept fixtures in {accept_dir}")
    if not reject_files:
        fail(f"{kind}: no must-reject fixtures in {reject_dir}")

    for path in accept_files:
        data = load_json(path)
        validator(data)

    for path in reject_files:
        data = load_json(path)
        try:
            validator(data)
        except ValueError:
            continue
        fail(f"{kind}: expected reject but accepted: {path}")


def validate_schemas_present() -> None:
    sm = ROOT / "runtime" / "atomic_kernel" / "schemas" / "state-machine.v0.schema.json"
    pi = ROOT / "runtime" / "atomic_kernel" / "schemas" / "pattern-instance.v0.schema.json"
    dv = ROOT / "runtime" / "atomic_kernel" / "schemas" / "diagram-view.v0.schema.json"
    ea = ROOT / "runtime" / "atomic_kernel" / "schemas" / "epistemic-assertion.v0.schema.json"
    for p, expected_id in [
        (sm, "ak.state_machine.v0"),
        (pi, "ak.pattern.instance.v0"),
        (dv, "ak.diagram_view.v0"),
        (ea, "ak.epistemic_assertion.v0"),
    ]:
        data = load_json(p)
        if data.get("$id") != expected_id:
            fail(f"schema {p} has wrong $id")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--kind",
        choices=["state-machine", "pattern-instance", "diagram-view", "epistemic-assertion", "all"],
        default="all",
    )
    args = parser.parse_args()

    validate_schemas_present()

    fixtures_root = ROOT / "runtime" / "atomic_kernel" / "fixtures"
    kinds = [args.kind] if args.kind != "all" else [
        "state-machine",
        "pattern-instance",
        "diagram-view",
        "epistemic-assertion",
    ]

    for kind in kinds:
        validate_fixture_dir(
            kind,
            fixtures_root / kind / "accept",
            fixtures_root / kind / "must-reject",
        )

    print(f"ok semantic contracts kind={args.kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
