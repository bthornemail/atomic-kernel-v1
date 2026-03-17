#!/usr/bin/env python3
"""Deterministic RDF projection exporter (core-minimal v0)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

NAMESPACES = {
    "ak": "https://atomic-kernel.dev/ns#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
}

SOURCE_TOP_KEYS = {
    "source_frame_hash",
    "ontology_nodes",
    "topology_edges",
    "epistemic_assertions",
    "pattern_instances",
    "state_machines",
    "diagram_views",
}
ONTO_KEYS = {"node_id", "class", "label", "properties", "source_frame_hash"}
TOPO_KEYS = {"edge_id", "kind", "from_id", "to_id", "confidence", "source_frame_hash"}
EPI_KEYS = {
    "assertion_id",
    "subject_id",
    "status",
    "confidence",
    "rationale",
    "evidence_refs",
    "source_frame_hash",
}
PATTERN_KEYS = {
    "pattern_id",
    "pattern_type",
    "subject_nodes",
    "role_bindings",
    "evidence_edges",
    "constraints_passed",
    "confidence",
    "alternates",
    "source_frame_hash",
}
SM_KEYS = {
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
SM_REGION_KEYS = {"id", "parent_state_id", "orthogonal_index"}
SM_STATE_KEYS = {"id", "name", "region_id", "state_kind", "entry_actions", "exit_actions", "internal_transitions"}
SM_TRANS_KEYS = {"id", "source_state_id", "target_state_id", "event", "guard", "actions", "priority"}
DV_KEYS = {"v", "authority", "view_id", "view_type", "source_frame_hash", "elements", "relations", "layout", "annotations"}
DV_ELEMENT_KEYS = {"id", "kind", "ref_kind", "ref_id", "label"}
DV_REL_KEYS = {"id", "kind", "from", "to", "ref_kind", "ref_id"}


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("input must be object")
    return data


def iri(s: str) -> str:
    return s


def lit(v: object) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def add(triples: list[dict], s: str, p: str, o: str, o_kind: str) -> None:
    triples.append({"s": s, "p": p, "o": o, "o_kind": o_kind})


def require_keys(obj: dict, allowed: set[str], required: set[str], ctx: str) -> None:
    keys = set(obj.keys())
    extra = keys - allowed
    missing = required - keys
    if extra:
        raise ValueError(f"{ctx}: unknown keys: {sorted(extra)}")
    if missing:
        raise ValueError(f"{ctx}: missing keys: {sorted(missing)}")


def validate_source(data: dict) -> None:
    require_keys(data, SOURCE_TOP_KEYS, {"source_frame_hash"}, "source")
    if not isinstance(data["source_frame_hash"], str) or len(data["source_frame_hash"]) != 64:
        raise ValueError("source.source_frame_hash invalid")

    for list_key in (
        "ontology_nodes",
        "topology_edges",
        "epistemic_assertions",
        "pattern_instances",
        "state_machines",
        "diagram_views",
    ):
        lv = data.get(list_key, [])
        if not isinstance(lv, list):
            raise ValueError(f"source.{list_key} must be list")

    for i, on in enumerate(data.get("ontology_nodes", [])):
        if not isinstance(on, dict):
            raise ValueError(f"ontology_nodes[{i}] must be object")
        require_keys(on, ONTO_KEYS, ONTO_KEYS - {"properties"}, f"ontology_nodes[{i}]")

    for i, te in enumerate(data.get("topology_edges", [])):
        if not isinstance(te, dict):
            raise ValueError(f"topology_edges[{i}] must be object")
        require_keys(te, TOPO_KEYS, TOPO_KEYS, f"topology_edges[{i}]")

    for i, ea in enumerate(data.get("epistemic_assertions", [])):
        if not isinstance(ea, dict):
            raise ValueError(f"epistemic_assertions[{i}] must be object")
        require_keys(ea, EPI_KEYS, EPI_KEYS, f"epistemic_assertions[{i}]")

    for i, pi in enumerate(data.get("pattern_instances", [])):
        if not isinstance(pi, dict):
            raise ValueError(f"pattern_instances[{i}] must be object")
        require_keys(pi, PATTERN_KEYS, PATTERN_KEYS - {"alternates"}, f"pattern_instances[{i}]")

    for i, sm in enumerate(data.get("state_machines", [])):
        if not isinstance(sm, dict):
            raise ValueError(f"state_machines[{i}] must be object")
        require_keys(sm, SM_KEYS, SM_KEYS, f"state_machines[{i}]")
        if sm["v"] != "ak.state_machine.v0":
            raise ValueError(f"state_machines[{i}].v invalid")
        if sm["authority"] != "advisory":
            raise ValueError(f"state_machines[{i}].authority invalid")
        if sm["machine_kind"] not in {"behavioral", "protocol"}:
            raise ValueError(f"state_machines[{i}].machine_kind invalid")

        regions = sm["regions"]
        states = sm["states"]
        transitions = sm["transitions"]
        if not isinstance(regions, list) or not regions:
            raise ValueError(f"state_machines[{i}].regions invalid")
        if not isinstance(states, list) or not states:
            raise ValueError(f"state_machines[{i}].states invalid")
        if not isinstance(transitions, list):
            raise ValueError(f"state_machines[{i}].transitions invalid")

        region_ids: set[str] = set()
        state_ids: set[str] = set()
        trans_ids: set[str] = set()
        internal_refs: set[str] = set()

        for j, r in enumerate(regions):
            if not isinstance(r, dict):
                raise ValueError(f"state_machines[{i}].regions[{j}] must be object")
            require_keys(r, SM_REGION_KEYS, SM_REGION_KEYS, f"state_machines[{i}].regions[{j}]")
            rid = r["id"]
            if not isinstance(rid, str) or not rid:
                raise ValueError(f"state_machines[{i}].regions[{j}].id invalid")
            if rid in region_ids:
                raise ValueError(f"state_machines[{i}] duplicate region id: {rid}")
            region_ids.add(rid)

        if sm["root_region"] not in region_ids:
            raise ValueError(f"state_machines[{i}].root_region missing")

        for j, s in enumerate(states):
            if not isinstance(s, dict):
                raise ValueError(f"state_machines[{i}].states[{j}] must be object")
            require_keys(s, SM_STATE_KEYS, SM_STATE_KEYS, f"state_machines[{i}].states[{j}]")
            sid = s["id"]
            if not isinstance(sid, str) or not sid:
                raise ValueError(f"state_machines[{i}].states[{j}].id invalid")
            if sid in state_ids:
                raise ValueError(f"state_machines[{i}] duplicate state id: {sid}")
            state_ids.add(sid)
            if s["region_id"] not in region_ids:
                raise ValueError(f"state_machines[{i}].states[{j}].region_id missing")
            for tid in s.get("internal_transitions", []):
                if not isinstance(tid, str) or not tid:
                    raise ValueError(f"state_machines[{i}].states[{j}].internal_transitions invalid")
                internal_refs.add(tid)

        for j, t in enumerate(transitions):
            if not isinstance(t, dict):
                raise ValueError(f"state_machines[{i}].transitions[{j}] must be object")
            require_keys(t, SM_TRANS_KEYS, SM_TRANS_KEYS, f"state_machines[{i}].transitions[{j}]")
            tid = t["id"]
            if not isinstance(tid, str) or not tid:
                raise ValueError(f"state_machines[{i}].transitions[{j}].id invalid")
            if tid in trans_ids:
                raise ValueError(f"state_machines[{i}] duplicate transition id: {tid}")
            trans_ids.add(tid)
            if t["source_state_id"] not in state_ids:
                raise ValueError(f"state_machines[{i}].transitions[{j}].source_state_id missing")
            tgt = t["target_state_id"]
            if tgt is not None and tgt not in state_ids:
                raise ValueError(f"state_machines[{i}].transitions[{j}].target_state_id missing")

        unknown_internal = internal_refs - trans_ids
        if unknown_internal:
            raise ValueError(f"state_machines[{i}] unknown internal transition refs: {sorted(unknown_internal)}")

    for i, dv in enumerate(data.get("diagram_views", [])):
        if not isinstance(dv, dict):
            raise ValueError(f"diagram_views[{i}] must be object")
        require_keys(dv, DV_KEYS, DV_KEYS, f"diagram_views[{i}]")
        if dv["v"] != "ak.diagram_view.v0":
            raise ValueError(f"diagram_views[{i}].v invalid")
        if dv["authority"] != "advisory":
            raise ValueError(f"diagram_views[{i}].authority invalid")
        if dv["view_type"] not in {"class", "component", "state"}:
            raise ValueError(f"diagram_views[{i}].view_type invalid")

        elements = dv["elements"]
        relations = dv["relations"]
        layout = dv["layout"]
        if not isinstance(elements, list) or not elements:
            raise ValueError(f"diagram_views[{i}].elements invalid")
        if not isinstance(relations, list):
            raise ValueError(f"diagram_views[{i}].relations invalid")
        if not isinstance(layout, dict):
            raise ValueError(f"diagram_views[{i}].layout invalid")

        element_ids: set[str] = set()
        for j, el in enumerate(elements):
            if not isinstance(el, dict):
                raise ValueError(f"diagram_views[{i}].elements[{j}] must be object")
            require_keys(el, DV_ELEMENT_KEYS, DV_ELEMENT_KEYS, f"diagram_views[{i}].elements[{j}]")
            eid = el["id"]
            if not isinstance(eid, str) or not eid:
                raise ValueError(f"diagram_views[{i}].elements[{j}].id invalid")
            if eid in element_ids:
                raise ValueError(f"diagram_views[{i}] duplicate element id: {eid}")
            element_ids.add(eid)

        for j, rel in enumerate(relations):
            if not isinstance(rel, dict):
                raise ValueError(f"diagram_views[{i}].relations[{j}] must be object")
            require_keys(rel, DV_REL_KEYS, DV_REL_KEYS, f"diagram_views[{i}].relations[{j}]")
            if rel["from"] not in element_ids or rel["to"] not in element_ids:
                raise ValueError(f"diagram_views[{i}].relations[{j}] references missing element")

        for key in layout.keys():
            if key not in element_ids:
                raise ValueError(f"diagram_views[{i}].layout references missing element")


def export_payload(data: dict) -> dict:
    validate_source(data)
    source_hash = data["source_frame_hash"]
    triples: list[dict] = []

    for on in data.get("ontology_nodes", []):
        sid = iri(f"ak:node/{on['node_id']}")
        add(triples, sid, "rdf:type", iri(f"ak:{on['class']}"), "iri")
        add(triples, sid, "rdfs:label", lit(on["label"]), "literal")
        add(triples, sid, "ak:sourceFrameHash", lit(on["source_frame_hash"]), "literal")
        for k, v in sorted(on.get("properties", {}).items()):
            pred = iri(f"ak:prop/{k}")
            add(triples, sid, pred, lit(v), "literal")

    for te in data.get("topology_edges", []):
        frm = iri(f"ak:node/{te['from_id']}")
        to = iri(f"ak:node/{te['to_id']}")
        add(triples, frm, iri(f"ak:{te['kind']}"), to, "iri")
        eid = iri(f"ak:topology/{te['edge_id']}")
        add(triples, eid, "rdf:type", iri("ak:TopologyEdge"), "iri")
        add(triples, eid, "ak:from", frm, "iri")
        add(triples, eid, "ak:to", to, "iri")
        add(triples, eid, "ak:confidence", lit(te["confidence"]), "literal")
        add(triples, eid, "ak:sourceFrameHash", lit(te["source_frame_hash"]), "literal")

    for ea in data.get("epistemic_assertions", []):
        aid = iri(f"ak:assert/{ea['assertion_id']}")
        add(triples, aid, "rdf:type", iri("ak:EpistemicAssertion"), "iri")
        add(triples, aid, "ak:asserts", iri(f"ak:node/{ea['subject_id']}"), "iri")
        add(triples, aid, "ak:status", iri(f"ak:{ea['status']}"), "iri")
        add(triples, aid, "ak:confidence", lit(ea["confidence"]), "literal")
        add(triples, aid, "ak:rationale", lit(ea["rationale"]), "literal")
        add(triples, aid, "ak:sourceFrameHash", lit(ea["source_frame_hash"]), "literal")
        for ev in ea.get("evidence_refs", []):
            add(triples, aid, "ak:evidenceRef", lit(ev), "literal")

    for pi in data.get("pattern_instances", []):
        pid = iri(f"ak:pattern/{pi['pattern_id']}")
        add(triples, pid, "rdf:type", iri("ak:PatternInstance"), "iri")
        add(triples, pid, "ak:patternType", iri(f"ak:{pi['pattern_type']}"), "iri")
        add(triples, pid, "ak:confidence", lit(pi["confidence"]), "literal")
        add(triples, pid, "ak:sourceFrameHash", lit(pi["source_frame_hash"]), "literal")
        for sid in pi["subject_nodes"]:
            add(triples, pid, "ak:subject", iri(f"ak:node/{sid}"), "iri")
        for role, nid in sorted(pi["role_bindings"].items()):
            add(triples, pid, iri(f"ak:role/{role}"), iri(f"ak:node/{nid}"), "iri")
        for edge in pi["evidence_edges"]:
            add(triples, pid, "ak:evidenceEdge", lit(edge), "literal")
        for constraint in pi["constraints_passed"]:
            add(triples, pid, "ak:constraintPassed", lit(constraint), "literal")
        for alt in pi.get("alternates", []):
            add(triples, pid, "ak:alternatePattern", iri(f"ak:{alt}"), "iri")

    for sm in data.get("state_machines", []):
        mid = iri(f"ak:machine/{sm['machine_id']}")
        add(triples, mid, "rdf:type", iri("ak:StateMachine"), "iri")
        mk = "BehavioralMachine" if sm["machine_kind"] == "behavioral" else "ProtocolMachine"
        add(triples, mid, "ak:machineKind", iri(f"ak:{mk}"), "iri")
        add(triples, mid, "ak:sourceFrameHash", lit(sm["source_frame_hash"]), "literal")
        add(triples, mid, "ak:rootRegion", iri(f"ak:region/{sm['machine_id']}/{sm['root_region']}"), "iri")

        for r in sm["regions"]:
            rid = iri(f"ak:region/{sm['machine_id']}/{r['id']}")
            add(triples, rid, "rdf:type", iri("ak:Region"), "iri")
            add(triples, mid, "ak:hasRegion", rid, "iri")

        for s in sm["states"]:
            sid = iri(f"ak:state/{sm['machine_id']}/{s['id']}")
            rid = iri(f"ak:region/{sm['machine_id']}/{s['region_id']}")
            add(triples, sid, "rdf:type", iri("ak:State"), "iri")
            add(triples, sid, "rdfs:label", lit(s["name"]), "literal")
            add(triples, sid, "ak:inRegion", rid, "iri")
            add(triples, rid, "ak:hasState", sid, "iri")
            add(triples, mid, "ak:hasState", sid, "iri")

        for t in sm["transitions"]:
            tid = iri(f"ak:transition/{sm['machine_id']}/{t['id']}")
            src = iri(f"ak:state/{sm['machine_id']}/{t['source_state_id']}")
            tgt = t["target_state_id"]
            add(triples, tid, "rdf:type", iri("ak:Transition"), "iri")
            add(triples, tid, "ak:sourceState", src, "iri")
            if tgt is not None:
                add(triples, tid, "ak:targetState", iri(f"ak:state/{sm['machine_id']}/{tgt}"), "iri")
            add(triples, tid, "ak:trigger", lit(t["event"]), "literal")
            add(triples, tid, "ak:hasGuard", lit(t["guard"] is not None), "literal")
            add(triples, tid, "ak:hasAction", lit(bool(t["actions"])), "literal")
            add(triples, mid, "ak:hasTransition", tid, "iri")

    for dv in data.get("diagram_views", []):
        vid = iri(f"ak:diagram/{dv['view_id']}")
        add(triples, vid, "rdf:type", iri("ak:DiagramView"), "iri")
        add(triples, vid, "ak:viewType", iri(f"ak:{dv['view_type']}"), "iri")
        add(triples, vid, "ak:sourceFrameHash", lit(dv["source_frame_hash"]), "literal")

        for el in dv["elements"]:
            eid = iri(f"ak:diagram/{dv['view_id']}/element/{el['id']}")
            add(triples, eid, "rdf:type", iri("ak:DiagramElement"), "iri")
            add(triples, eid, "ak:elementKind", iri(f"ak:{el['kind']}"), "iri")
            add(triples, eid, "rdfs:label", lit(el["label"]), "literal")
            add(triples, vid, "ak:hasElement", eid, "iri")
            rk = el["ref_kind"]
            rv = el["ref_id"]
            if rk == "node":
                add(triples, eid, "ak:refNode", iri(f"ak:node/{rv}"), "iri")
            elif rk == "state":
                add(triples, eid, "ak:refState", iri(f"ak:state/{rv}"), "iri")
            elif rk == "region":
                add(triples, eid, "ak:refRegion", iri(f"ak:region/{rv}"), "iri")
            elif rk == "pattern":
                add(triples, eid, "ak:refPattern", iri(f"ak:pattern/{rv}"), "iri")
            else:
                add(triples, eid, "ak:refNone", lit("true"), "literal")

        for rel in dv["relations"]:
            rid = iri(f"ak:diagram/{dv['view_id']}/relation/{rel['id']}")
            from_e = iri(f"ak:diagram/{dv['view_id']}/element/{rel['from']}")
            to_e = iri(f"ak:diagram/{dv['view_id']}/element/{rel['to']}")
            add(triples, rid, "rdf:type", iri("ak:DiagramRelation"), "iri")
            add(triples, rid, "ak:relationKind", iri(f"ak:{rel['kind']}"), "iri")
            add(triples, rid, "ak:fromElement", from_e, "iri")
            add(triples, rid, "ak:toElement", to_e, "iri")
            add(triples, vid, "ak:hasRelation", rid, "iri")

    triples.sort(key=lambda t: (t["s"], t["p"], t["o"], t["o_kind"]))

    return {
        "v": "ak.rdf_export.v0",
        "authority": "advisory",
        "export_profile": "core-minimal",
        "source_frame_hash": source_hash,
        "namespaces": NAMESPACES,
        "triples": triples,
    }


def escape_ttl(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def to_turtle(envelope: dict) -> str:
    lines = [
        f"@prefix ak: <{envelope['namespaces']['ak']}> .",
        f"@prefix rdf: <{envelope['namespaces']['rdf']}> .",
        f"@prefix rdfs: <{envelope['namespaces']['rdfs']}> .",
        "",
    ]
    for t in envelope["triples"]:
        s = t["s"]
        p = t["p"]
        if t["o_kind"] == "iri":
            o = t["o"]
        else:
            o = f'"{escape_ttl(t["o"])}"'
        lines.append(f"{s} {p} {o} .")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--ttl-out", required=True)
    args = parser.parse_args()

    source = load_json(Path(args.input))
    envelope = export_payload(source)

    Path(args.json_out).write_text(
        json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    Path(args.ttl_out).write_text(to_turtle(envelope), encoding="utf-8")

    print(f"ok rdf export json={args.json_out} ttl={args.ttl_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
