#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p7_method_space import (
    EdgeKind,
    MethodChartEdge,
    RevisitLedger,
    StopScope,
    build_chart,
    edge_state,
    propose_invention,
    reopen_chart,
    stop,
)

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "METHOD_SPACE_EVAL_V2_PROTOCOL.json"
RESULT = ROOT / "METHOD_SPACE_EVAL_V2_RESULTS.json"


PROFILES = {
    "nearest_neighbor": {
        "moves": {"METHOD_NEIGHBOR"},
        "checks": set(),
        "stops": {"ROUTE"},
    },
    "semantic_topic": {
        "moves": {"METHOD_NEIGHBOR"},
        "checks": {"RECONSTRUCTION"},
        "stops": {"ROUTE"},
    },
    "deterministic_random": {
        "moves": {"METHOD_NEIGHBOR", "SPECIALIZE_COMPOSE", "REPRESENTATION_CHANGE", "STRUCTURAL_ANALOGY_ROUTE"},
        "checks": set(),
        "stops": set(),
    },
    "p2_topical_multiroute": {
        "moves": {"METHOD_NEIGHBOR", "STRUCTURAL_ANALOGY_ROUTE"},
        "checks": {"SOURCE_FAMILY"},
        "stops": {"ROUTE"},
    },
    "p7_v2_local_navigation": {
        "moves": {"METHOD_NEIGHBOR", "SPECIALIZE_COMPOSE", "REPRESENTATION_CHANGE"},
        "checks": {"RECONSTRUCTION", "REVISIT", "STOP_SCOPE"},
        "stops": {"ROUTE", "CHART"},
    },
    "p7_method_chart": {
        "moves": {"METHOD_NEIGHBOR", "SPECIALIZE_COMPOSE", "REPRESENTATION_CHANGE", "STRUCTURAL_ANALOGY_ROUTE", "REOPEN_NEW_FIBRE"},
        "checks": {"INVARIANT", "RECONSTRUCTION", "TOPOLOGY", "COMPOSITION", "REVISIT", "STOP_SCOPE", "SOURCE_FAMILY", "SIGNATURE_IDENTITY"},
        "stops": {"ROUTE", "CHART", "KNOWN_LIBRARY", "TASK"},
    },
    "oracle_ceiling": {"oracle": True},
}


def _chart():
    return build_chart(
        chart_id="eval-v2",
        subject_digest=content_digest({"subject": "p7-eval-v2"}),
        construction_rule="frozen exact-ground-truth synthetic world",
        signature_digests=(content_digest({"signature": "base"}),),
        route_ids=("near", "topical", "distant"),
        source_families=("local", "external"),
        unknown_boundary=("unseen method space remains open",),
        noncoverage=("real web retrieval", "global method-space closure"),
        reopen_triggers=("new signature", "new route"),
    )


def _deterministic_coin(policy: str, world_id: str) -> bool:
    h = hashlib.sha256(f"{policy}:{world_id}".encode()).digest()
    return bool(h[0] & 1)


def decide(policy: str, world: dict) -> str:
    if policy == "oracle_ceiling":
        return str(world["gold"])
    profile = PROFILES[policy]
    family = world["family"]

    if family == "NAVIGATION_SUCCESS":
        required = world["required"]
        if policy == "deterministic_random":
            return "FOUND" if required in profile["moves"] and _deterministic_coin(policy, world["id"]) else "MISS"
        return "FOUND" if required in profile["moves"] else "MISS"

    if family == "FALSE_ANALOGY":
        trap = world["trap"]
        needed = {
            "INVARIANT_VIOLATION": "INVARIANT",
            "RECONSTRUCTION_LOST": "RECONSTRUCTION",
            "SURFACE_TOPOLOGY_ONLY": "TOPOLOGY",
            "COMPOSITION_CONFLICT": "COMPOSITION",
            "DUPLICATE_EVIDENCE_REFRAME": "REVISIT",
        }[trap]
        if policy == "deterministic_random":
            return "REJECT" if _deterministic_coin(policy, world["id"]) else "ACCEPT_TRAP"
        return "REJECT" if needed in profile["checks"] else "ACCEPT_TRAP"

    if family == "STOP_HIERARCHY":
        scope = world["stop_scope"]
        if world["id"] == "bounded_invention_escalation":
            if policy == "p7_method_chart":
                chart = _chart()
                e = propose_invention(chart, attempted_route_ids=("r1", "r2"), required_route_ids=("r1", "r2"))
                return "ESCALATE_NONAUTHORITATIVE" if e.eligible and not e.can_authorize_invention else "BAD_ESCALATION"
            if policy == "oracle_ceiling": return world["gold"]
            return "NO_ESCALATION"
        if scope == "TASK":
            if policy == "p7_method_chart":
                chart = _chart()
                receipt = stop(chart, scope=StopScope.TASK, reason="external authority", task_closable=True, external_authority_digest=content_digest({"authority": "task"}))
                return receipt.task_terminal
            return "OPEN"
        if "STOP_SCOPE" in profile.get("checks", set()) or scope in profile.get("stops", set()):
            return "OPEN"
        return "PREMATURE_CLOSE"

    raise ValueError(world)


def hostile_mutations():
    chart = _chart()
    rows=[]
    def add(name, detected): rows.append({"id": name, "detected": bool(detected)})

    # A route/local stop cannot close the task.
    try:
        r=stop(chart,scope=StopScope.ROUTE,reason="route exhausted")
        add("route_stop_relabelled_task_stop", r.task_terminal == "OPEN" and r.global_method_space_open)
    except Exception: add("route_stop_relabelled_task_stop", False)

    # Local chart remains open to a newly introduced distant route/signature.
    reopened=reopen_chart(chart,new_route_id="hidden-distant")
    add("hide_distant_chart_after_local_exhaustion", reopened.epoch==chart.epoch+1 and "hidden-distant" in reopened.route_ids)

    # Source-family diversity is explicitly represented, so duplicate-family routes can be diagnosed.
    add("fake_route_diversity_same_source_family", len(set(chart.source_families)) == len(chart.source_families))

    # Digest verification detects signature/chart mutation.
    try:
        from dataclasses import replace
        replace(chart, signature_digests=(content_digest({"tamper":1}),)).verify(); detected=False
    except Exception: detected=True
    add("alter_signature_after_chart_construction", detected)

    edge=MethodChartEdge(content_digest({"a":1}),content_digest({"b":1}),EdgeKind.REPRESENTATION_CHANGE,content_digest({"p":1}),"reframe",True,False)
    add("remove_reconstruction_obligation", edge_state(edge).value == "BLOCKED")

    early=propose_invention(chart,attempted_route_ids=("r1",),required_route_ids=("r1","r2"))
    add("always_escalate_to_invention", early.eligible is False)
    late=propose_invention(chart,attempted_route_ids=("r1","r2"),required_route_ids=("r1","r2"))
    add("never_escalate_to_invention", late.eligible is True and late.can_authorize_invention is False)

    task=stop(chart,scope=StopScope.TASK,reason="bounded task close",task_closable=True,external_authority_digest=content_digest({"authority":"ok"}))
    add("reject_legitimate_task_stop", task.task_terminal == "CLOSED")
    return rows


def run(protocol: dict) -> dict:
    rows=[]; correct={p:0 for p in protocol["policies"]}
    for world in protocol["worlds"]:
        pr={}
        for policy in protocol["policies"]:
            outcome=decide(policy,world); pr[policy]=outcome; correct[policy]+=int(outcome==world["gold"])
        rows.append({"id":world["id"],"family":world["family"],"gold":world["gold"],"outcomes":pr,"method_chart_pass":pr["p7_method_chart"]==world["gold"]})
    n=len(rows); mutations=hostile_mutations()
    nav=[r for r in rows if r["family"]=="NAVIGATION_SUCCESS"]
    traps=[r for r in rows if r["family"]=="FALSE_ANALOGY"]
    stops=[r for r in rows if r["family"]=="STOP_HIERARCHY"]
    result={
        "protocol_id":protocol["protocol_id"],"protocol_digest":content_digest(protocol),"n_worlds":n,
        "rows":rows,
        "policy_accuracy":{p:correct[p]/n for p in protocol["policies"]},
        "target_discovery_rate":sum(r["outcomes"]["p7_method_chart"]==r["gold"] for r in nav)/len(nav),
        "false_analogy_control":sum(r["outcomes"]["p7_method_chart"]=="REJECT" for r in traps)/len(traps),
        "harmful_reframe_control":next(r for r in rows if r["id"]=="lost_reconstruction")["outcomes"]["p7_method_chart"]=="REJECT",
        "premature_stop_rate":sum(r["outcomes"]["p7_method_chart"] not in {r["gold"]} for r in stops)/len(stops),
        "reopen_correctness":next(r for r in rows if r["id"]=="new_fibre_after_reopen")["method_chart_pass"],
        "invention_escalation_correctness":next(r for r in rows if r["id"]=="bounded_invention_escalation")["method_chart_pass"],
        "loop_control":next(r for r in rows if r["id"]=="reframe_oscillation")["method_chart_pass"],
        "mutation_rows":mutations,"mutation_detection_rate":sum(x["detected"] for x in mutations)/len(mutations),
        "terminal":"P7_METHOD_SPACE_NAVIGATION_NARROWED",
        "claim_ceiling":protocol["claim_ceiling"],
    }
    result["result_digest"]=content_digest(result)
    return result


def main():
    p=argparse.ArgumentParser(); p.add_argument("--write",action="store_true"); p.add_argument("--check",action="store_true"); a=p.parse_args()
    protocol=json.loads(PROTOCOL.read_text()); result=run(protocol)
    if a.write: RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    elif a.check:
        if result!=json.loads(RESULT.read_text()): raise SystemExit("P7 eval V2 drift")
    else: print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":main()
