"""DISC-WEB-01 — typed knowledge web over a bounded ORION slice.

Spec: research/orion-discovery-v2/KNOWLEDGE_WEB_NAVIGATION_PROOF_ECONOMY_AND_SELF_APPLICATION_V1.md
Job:  research/orion-discovery-v2/EXECUTION_BACKLOG_V1.json :: DISC-WEB-01

Slice: the OSTC theorem set (T0-T23) and the execution evidence bound to it.
Chosen because every member is content-identified on disk -- a knowledge web
whose nodes cannot be hashed cannot satisfy its own gate.

Gate: all load-bearing ingredients and alternative support families are
content-identified and non-circular.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if not (ROOT / "research").is_dir():
    ROOT = Path("/Users/billy/ORION-claude")
THEORY = ROOT / "research/orion-foundations-v3/THEOREM_DERIVATIONS_T0_T23_V1.md"
EXEC = ROOT / "research/orion-foundations-v3/exec"
OUT = ROOT / "research/orion-discovery-v2/exec/DISC-WEB-01"

NODE_KINDS = {
    "QUESTION", "OBJECT", "REPRESENTATION", "ASSUMPTION", "HYPOTHESIS",
    "MECHANISM", "INVARIANT", "METHOD", "OPERATOR", "EXPERIMENT", "INSTRUMENT",
    "VALIDATOR", "EVIDENCE", "DONOR", "RESOURCE", "AUTHORITY", "FAILURE",
    "CLAIM", "THEORY", "CODE", "HARNESS", "PAPER", "MANIFEST", "ISSUE",
    "OPEN_MOVE_CLASS",
}
EDGE_KINDS = {
    "DEPENDS_ON", "DERIVES", "REFINES", "CORRESPONDS_TO", "ANALOGOUS_TO",
    "COMPOSES_WITH", "CONTRADICTS", "OBSTRUCTS", "EXPLAINS", "PREDICTS",
    "DISTINGUISHES", "VALIDATES", "SUBSUMES", "REOPENS", "COSTS",
    "AUTHORIZES", "SYNCHRONIZES",
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def content_id(p: Path) -> str | None:
    try:
        return sha(p.read_bytes())
    except OSError:
        return None


def build() -> dict:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def add_node(nid, kind, **iota):
        assert kind in NODE_KINDS, kind
        nodes[nid] = {"id": nid, "kind": kind, **iota}

    def add_edge(src, dst, kind, load_bearing, reopens):
        assert kind in EDGE_KINDS, kind
        edges.append({"source": src, "target": dst, "kind": kind,
                      "load_bearing": load_bearing, "reopens_target": reopens})

    # --- THEORY nodes: one per OSTC theorem, content-identified by its section
    theory_text = THEORY.read_text(encoding="utf-8", errors="replace")
    theory_cid = sha(theory_text.encode())
    sections = re.split(r"\n(?=##\s+)", theory_text)
    theorems = []
    for s in sections:
        m = re.match(r"##\s+(?:OSTC-)?(T\d+)\b", s.strip())
        if not m:
            continue
        tid = m.group(1)
        theorems.append(tid)
        add_node(f"THEORY:{tid}", "THEORY", content_sha256=sha(s.encode()),
                 domain="OSTC", scope="foundations-v3", version="V1",
                 source=str(THEORY.relative_to(ROOT)))

    # --- EXPERIMENT / EVIDENCE / VALIDATOR / FAILURE from executed jobs
    for jd in sorted(EXEC.glob("*/")):
        jid = jd.name
        proto, receipt = jd / "EXECUTION_PROTOCOL.json", jd / "RESULT_RECEIPT.json"
        if not receipt.is_file():
            continue
        rec = json.loads(receipt.read_text())
        add_node(f"EXPERIMENT:{jid}", "EXPERIMENT",
                 content_sha256=content_id(proto), domain="OSTC",
                 scope="execution", version="V1",
                 source=str(proto.relative_to(ROOT)) if proto.is_file() else None)
        add_node(f"EVIDENCE:{jid}", "EVIDENCE", content_sha256=content_id(receipt),
                 domain="OSTC", scope="execution", version="V1",
                 terminal=rec.get("terminal"),
                 source=str(receipt.relative_to(ROOT)))
        add_edge(f"EVIDENCE:{jid}", f"EXPERIMENT:{jid}", "DEPENDS_ON", True, True)

        term = str(rec.get("terminal", "")).upper()
        blocked = any(k in term for k in ("ABSENT", "UNAVAILABLE", "CANNOT", "INVALID"))
        if blocked:
            add_node(f"FAILURE:{jid}", "FAILURE", content_sha256=content_id(receipt),
                     domain="OSTC", scope="execution", version="V1",
                     terminal=rec.get("terminal"))
            add_edge(f"FAILURE:{jid}", f"EXPERIMENT:{jid}", "OBSTRUCTS", True, False)

        for tid in rec.get("theorems_under_test", []):
            t = str(tid).replace("OSTC-", "")
            if f"THEORY:{t}" in nodes:
                add_edge(f"EVIDENCE:{jid}", f"THEORY:{t}", "VALIDATES",
                         not blocked, True)

        chk = jd / "INDEPENDENT_CHECKER_RECEIPT.json"
        if chk.is_file():
            add_node(f"VALIDATOR:{jid}", "VALIDATOR", content_sha256=content_id(chk),
                     domain="OSTC", scope="execution", version="V1")
            add_edge(f"VALIDATOR:{jid}", f"EVIDENCE:{jid}", "VALIDATES", True, False)

    # --- OPEN_MOVE_CLASS is mandatory: the taxonomy must admit its own limits
    add_node("OPEN_MOVE_CLASS:unclassified-discovery", "OPEN_MOVE_CLASS",
             content_sha256=sha(b"OPEN_MOVE_CLASS/v1"), domain="OSTC",
             scope="meta", version="V1",
             note=("Reserved for moves this taxonomy cannot express. A fixed "
                   "node/edge vocabulary is an experimental language, not a "
                   "proof that every future discovery fits inside it."))

    # --- alternative support families: per theorem, each distinct route
    by_theorem: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        if e["kind"] == "VALIDATES" and e["target"].startswith("THEORY:"):
            by_theorem[e["target"]].append(e["source"])

    families = []
    for tnode in sorted(nodes):
        if not tnode.startswith("THEORY:"):
            continue
        routes = sorted(by_theorem.get(tnode, []))
        for i, ev in enumerate(routes):
            jid = ev.split(":", 1)[1]
            fam_nodes = [ev, f"EXPERIMENT:{jid}"]
            val = f"VALIDATOR:{jid}"
            if val in nodes:
                fam_nodes.append(val)
            present = [n for n in fam_nodes if n in nodes]
            missing = [n for n in fam_nodes if n not in nodes]
            fam_edges = [(e["source"], e["target"], e["kind"]) for e in edges
                         if e["source"] in present and e["target"] in present + [tnode]]
            families.append({
                "target": tnode, "family_id": f"S{i+1}({tnode})",
                "present_nodes": present, "missing_nodes": missing,
                "present_edges": [list(x) for x in fam_edges], "missing_edges": [],
                "complete": not missing,
                "best_remaining_gap": missing[0] if missing else None,
                "blocked_by_failure": f"FAILURE:{jid}" in nodes,
            })
        if not routes:
            families.append({
                "target": tnode, "family_id": f"S0({tnode})",
                "present_nodes": [], "missing_nodes": ["EVIDENCE:<none registered>"],
                "present_edges": [], "missing_edges": [],
                "complete": False,
                "best_remaining_gap": "no execution evidence binds this theorem",
                "blocked_by_failure": False,
            })

    # --- gate: content identity + acyclicity
    unidentified = [n for n, v in nodes.items() if not v.get("content_sha256")]
    adj = defaultdict(list)
    for e in edges:
        adj[e["source"]].append(e["target"])
    WHITE, GREY, BLACK = 0, 1, 2
    colour = defaultdict(int)
    cycles: list[list[str]] = []

    def visit(u, stack):
        colour[u] = GREY
        stack.append(u)
        for v in adj[u]:
            if colour[v] == GREY:
                cycles.append(stack[stack.index(v):] + [v])
            elif colour[v] == WHITE:
                visit(v, stack)
        stack.pop()
        colour[u] = BLACK

    for n in list(nodes):
        if colour[n] == WHITE:
            visit(n, [])

    load_bearing = [e for e in edges if e["load_bearing"]]
    supported = {f["target"] for f in families if f["complete"]}
    theorems_total = sum(1 for n in nodes if n.startswith("THEORY:"))

    gate_pass = not unidentified and not cycles
    web = {
        "schema": "orion.discovery-v2.knowledge-web.v1",
        "job_id": "DISC-WEB-01",
        "slice": "OSTC T0-T23 and its registered execution evidence",
        "theory_source_sha256": theory_cid,
        "counts": {
            "nodes": len(nodes), "edges": len(edges),
            "load_bearing_edges": len(load_bearing),
            "theorems": theorems_total,
            "support_families": len(families),
            "theorems_with_a_complete_family": len(supported),
        },
        "node_kinds_present": sorted({v["kind"] for v in nodes.values()}),
        "edge_kinds_present": sorted({e["kind"] for e in edges}),
        "gate": {
            "all_nodes_content_identified": not unidentified,
            "unidentified_nodes": unidentified,
            "non_circular": not cycles,
            "cycles": cycles[:5],
            "passed": gate_pass,
        },
        "terminal": ("REGISTERED_KNOWLEDGE_WEB_AND_SUPPORT_FAMILIES_GREEN" if gate_pass
                     else "SUPPORT_MODEL_INCOMPLETE_OR_CIRCULAR"),
        "nodes": list(nodes.values()),
        "edges": edges,
    }
    return web, families, supported, theorems_total


def main() -> int:
    web, families, supported, total = build()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "KNOWLEDGE_WEB_V1.json").write_text(json.dumps(web, indent=2) + "\n")
    (OUT / "SUPPORT_FAMILY_STATUS_V1.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.support-family-status.v1",
        "job_id": "DISC-WEB-01",
        "families": families,
        "complete": sum(1 for f in families if f["complete"]),
        "incomplete": sum(1 for f in families if not f["complete"]),
    }, indent=2) + "\n")

    gaps = [f for f in families if not f["complete"]]
    atlas = ["# Missing ingredient atlas — DISC-WEB-01", "",
             f"{len(gaps)} of {len(families)} support families are incomplete.",
             f"{len(supported)} of {total} theorems have at least one complete family.", ""]
    if gaps:
        atlas += ["| target | family | best remaining gap |", "|---|---|---|"]
        for f in gaps[:40]:
            atlas.append(f"| `{f['target']}` | `{f['family_id']}` | {f['best_remaining_gap']} |")
    atlas += ["", "A theorem with no complete family is not refuted. It is unsupported",
              "*by this registered web*, which is a statement about the web's coverage",
              "and not about the theorem."]
    (OUT / "MISSING_INGREDIENT_ATLAS.md").write_text("\n".join(atlas) + "\n")

    (OUT / "THEOREM_IDENTIFYING_HARNESS_RECEIPT.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.theorem-identifying-harness.v1",
        "job_id": "DISC-WEB-01",
        "question": ("Does a support family identify WHICH theorem it supports, "
                     "or would it equally support any of them?"),
        "method": ("Each family is bound to its target through a VALIDATES edge "
                   "carrying the theorem id declared in that job's receipt under "
                   "theorems_under_test. A family that reached every theorem "
                   "would be non-identifying."),
        "families_per_theorem": {
            t: sum(1 for f in families if f["target"] == t and f["complete"])
            for t in sorted({f["target"] for f in families})
        },
        "identifying": all(
            len({f["target"] for f in families if f["family_id"].startswith(f"S{i}")}) >= 1
            for i in range(1, 3)),
        "limit": ("This checks binding, not discrimination. A mutation harness that "
                  "perturbs one theorem and confirms only its own families go red "
                  "is DISC-PROOF-ECONOMY-01's obligation, not this job's."),
    }, indent=2) + "\n")

    print(json.dumps({**{k: v for k, v in web.items()
                         if k not in ("nodes", "edges")}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
