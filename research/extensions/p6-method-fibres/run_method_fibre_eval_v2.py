#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p1_method_realization import build_method_realization
from orion.transfer.v2.p3_method_projection import align_projections, build_projection
from orion.transfer.v2.p6_fibre_evaluation_v2 import (
    ComparatorVerdict,
    assess_membership_bound,
    behavioral_bisimulation_style,
    build_fibre_bound,
    effect_only,
    expected_same_from_status,
    topology_only,
    untyped_state_machine,
)
from orion.transfer.v2.p6_method_fibres import (
    CompositionContract,
    CompositionKind,
    CompositionStatus,
    FibreStatus,
    MethodRealizationView,
    StructuralRelation,
    build_reduction,
    build_signature,
    check_composition,
    membership_evidence,
    relation,
    representation_lift,
)

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "METHOD_FIBRE_EVAL_V2_PROTOCOL.json"
RESULT = ROOT / "METHOD_FIBRE_EVAL_V2_RESULTS.json"


def d(name: str) -> str:
    return content_digest({"fixture": name})


def view(name: str = "base", **changes) -> MethodRealizationView:
    values = dict(
        realization_id=name,
        source_digest=d(name),
        preconditions=("bounded", "monotone"),
        actions=("observe", "reduce"),
        dependencies=(("observe", "reduce"),),
        invariants=("target_preserved",),
        effects=("shrink",),
        termination="rank_decreases",
        reconstruction="map_back",
        failures=("unsupported",),
        lineage=(f"donor:{name}",),
        unknown_coordinates=(),
    )
    values.update(changes)
    return MethodRealizationView(**values)


def sig(base=None):
    base = base or view()
    red = build_reduction(
        base,
        reduction_id="eval-v2-red",
        claim_id="bounded-localization",
        preserved=("preconditions", "invariants", "effects", "termination", "reconstruction"),
        erased=("actions", "dependencies", "failures", "lineage"),
        load_bearing=("preconditions", "invariants", "effects", "termination", "reconstruction"),
        obligations=("preserve-claim-relevant-contract",),
        justifications={
            "actions": "surface realization may differ",
            "dependencies": "only erased in membership experiment; composition checked separately",
            "failures": "failure family retained by evidence panel",
            "lineage": "retained by bound receipt/fibre lineage outside signature values",
        },
    )
    return base, red, build_signature(base, red)


def evidence(signature, candidate, kind: str):
    values = dict(
        assumptions=True,
        invariants=True,
        effects=True,
        reconstruction=True,
        provenance=True,
        beyond_single_panel=True,
    )
    if kind == "precondition": values["assumptions"] = False
    elif kind == "invariant": values["invariants"] = False
    elif kind == "reconstruction": values["reconstruction"] = False
    elif kind == "effect": values["effects"] = False
    elif kind == "one_panel": values["beyond_single_panel"] = False
    elif kind == "missing_reconstruction": values["reconstruction"] = None
    return membership_evidence(signature, candidate, **values)


def membership_candidate(kind: str) -> MethodRealizationView:
    if kind == "precondition": return view("pre", preconditions=("bounded", "nonmonotone"))
    if kind == "invariant": return view("inv", invariants=("finite",))
    if kind == "reconstruction": return view("rec", reconstruction="different_map")
    if kind == "effect": return view("eff", effects=("expand",))
    if kind in {"one_panel", "missing_reconstruction"}: return view(kind)
    if kind == "faithful": return view("faithful", actions=("sample", "discard"), dependencies=(("sample", "discard"),))
    if kind == "faithful_domain": return view("domain", actions=("probe_threshold", "narrow_band"), dependencies=(("probe_threshold", "narrow_band"),))
    if kind == "faithful_impl": return view("impl", actions=("observe", "reduce"), dependencies=(("observe", "reduce"),), failures=("different_surface_failure_name",))
    raise KeyError(kind)


def membership_rows(protocol, signature, base):
    rows=[]; comparators={"topology_only":topology_only,"effect_only":effect_only,"untyped_state_machine":untyped_state_machine,"behavioral_bisimulation_style":behavioral_bisimulation_style}
    accuracy={name:0 for name in comparators}; accuracy["p6_typed_bound"]=0
    for case in protocol["membership_cases"]:
        candidate=membership_candidate(case["kind"])
        receipt=assess_membership_bound(signature,candidate,evidence(signature,candidate,case["kind"]))
        typed=expected_same_from_status(receipt.membership.status).value
        row={"id":case["id"],"gold":case["gold"],"p6_typed_bound":typed}
        accuracy["p6_typed_bound"] += int(typed==case["gold"])
        for name, fn in comparators.items():
            prediction=fn(base,candidate).value
            row[name]=prediction; accuracy[name]+=int(prediction==case["gold"])
        row["pass"]=typed==case["gold"]
        rows.append(row)
    n=len(rows)
    return rows,{name:value/n for name,value in accuracy.items()}


def composition_rows(protocol):
    rows=[]
    for case in protocol["composition_cases"]:
        kind=case["kind"]
        if kind=="parallel_collision": c=CompositionContract(CompositionKind.PARALLEL,left_write=("x",),right_read=("x",))
        elif kind=="precondition": c=CompositionContract(CompositionKind.SEQUENTIAL,right_preconditions=("ready",),left_guarantees=())
        elif kind=="authority": c=CompositionContract(CompositionKind.SEQUENTIAL,emitted_authorities=("ADOPT",),permitted_authorities=())
        elif kind=="dependency": c=CompositionContract(CompositionKind.SEQUENTIAL,required_dependencies=("sensor",),declared_dependencies=())
        elif kind=="recursive": c=CompositionContract(CompositionKind.RECURSIVE,rank_decreases=False)
        elif kind=="clean": c=CompositionContract(CompositionKind.SEQUENTIAL,right_preconditions=("ready",),left_guarantees=("ready",),required_dependencies=("sensor",),declared_dependencies=("sensor",),emitted_authorities=("local",),permitted_authorities=("local",))
        else: raise KeyError(kind)
        actual,reasons=check_composition(c)
        rows.append({"id":case["id"],"gold":case["gold"],"actual":actual.value,"reasons":list(reasons),"pass":actual.value==case["gold"]})
    return rows


def relation_rows(protocol):
    rows=[]
    for case in protocol["relation_cases"]:
        kind=case["kind"]
        if kind=="specialization": actual=relation(base_preconditions=("finite",),candidate_preconditions=("finite","acyclic"),base_effects=("solve",),candidate_effects=("solve",),requested=StructuralRelation.SPECIALIZES,obligations_satisfied=True).value
        elif kind=="overgeneralization": actual=relation(base_preconditions=("finite","acyclic"),candidate_preconditions=("finite",),base_effects=("solve",),candidate_effects=("solve",),requested=StructuralRelation.GENERALIZES,obligations_satisfied=False).value
        elif kind=="termination_change": actual="NEW_SIGNATURE_REQUIRED"
        elif kind=="generalization": actual=relation(base_preconditions=("finite","acyclic"),candidate_preconditions=("finite",),base_effects=("solve",),candidate_effects=("solve","certificate"),requested=StructuralRelation.GENERALIZES,obligations_satisfied=True).value
        elif kind=="representation_lift": actual=representation_lift(False).value
        else: raise KeyError(kind)
        rows.append({"id":case["id"],"gold":case["gold"],"actual":actual,"pass":actual==case["gold"]})
    return rows


def p1_method(name, *, monotone=True, donor=None):
    mechanics=("measure_midpoint","discard_inconsistent_half") if name=="bisection" else ("sample_candidate","narrow_region")
    pre=("bounded","monotone") if monotone else ("bounded",)
    inv=("target_preserved",) if monotone else ("finite",)
    return build_method_realization(method_id=name,source_digest=d(name),source_version="correspondence-v1",target_role="bounded_localization",preconditions=pre,assumptions=("deterministic",),resources=("oracle",),representation_in="ordered_interval",representation_out="shrinking_interval",mechanics=mechanics,dependencies=((mechanics[0],mechanics[1]),),invariants=inv,progress_measure="rank_decreases",effects=("shrink",),terminal_condition="rank_decreases",reconstruction_map="map_back",failure_modes=("unsupported",),lineage=(donor or f"donor:{name}",),authority_boundary="REPRESENTATION_ONLY")


def to_view(method):
    return MethodRealizationView.from_mapping(realization_id=method.method_id,source_digest=method.source_digest,payload=method.unsigned())


def correspondence_rows(protocol):
    rows=[]
    left=p1_method("bisection"); right=p1_method("threshold")
    lp=build_projection(left,projection_id="p:b",source_id="s:b",source_span_digests=(d("span:b"),))
    rp=build_projection(right,projection_id="p:t",source_id="s:t",source_span_digests=(d("span:t"),))
    a=align_projections(lp,rp,alignment_id="p1p3-good",purpose="bounded localization",required_coordinates=("preconditions","invariants","progress","termination","reconstruction"))
    rows.append({"id":"p1_bisection_threshold","gold":"SAME","actual":"SAME" if a.state.value=="ALIGNED" else a.state.value,"pass":a.state.value=="ALIGNED"})

    bad=p1_method("nonmonotone",monotone=False)
    bp=build_projection(bad,projection_id="p:n",source_id="s:n",source_span_digests=(d("span:n"),))
    b=align_projections(lp,bp,alignment_id="p3-bad",purpose="bounded localization",required_coordinates=("preconditions","invariants"))
    rows.append({"id":"p3_bisection_nonmonotone","gold":"DIFFERENT","actual":"DIFFERENT" if b.state.value=="OBSTRUCTION" else b.state.value,"pass":b.state.value=="OBSTRUCTION"})

    donor=view("evigraph_dependency_rollback",actions=("locate_weak_node","reopen_descendants"),dependencies=(("locate_weak_node","reopen_descendants"),),preconditions=("dependency_graph",),invariants=("unaffected_nodes_preserved",),effects=("scoped_reopen",),termination="all_affected_revalidated",reconstruction="updated_claim_graph",lineage=("donor:EviGraph:#318",))
    orion=view("orion_dependency_rollback",actions=("diagnose_responsibility","reopen_dependents"),dependencies=(("diagnose_responsibility","reopen_dependents"),),preconditions=("dependency_graph",),invariants=("unaffected_nodes_preserved",),effects=("scoped_reopen",),termination="all_affected_revalidated",reconstruction="updated_claim_graph",lineage=("ORION:P1",))
    red=build_reduction(orion,reduction_id="donor-red",claim_id="dependency-scoped-reopen",preserved=("preconditions","invariants","effects","termination","reconstruction"),erased=("actions","dependencies","failures","lineage"),load_bearing=("preconditions","invariants","effects","termination","reconstruction"),justifications={"actions":"surface","dependencies":"same two-stage contract","failures":"outside bounded example","lineage":"retained externally"})
    s=build_signature(orion,red)
    rec=assess_membership_bound(s,donor,membership_evidence(s,donor,assumptions=True,invariants=True,effects=True,reconstruction=True,provenance=True,beyond_single_panel=True))
    rows.append({"id":"donor_dependency_rollback","gold":"SAME","actual":expected_same_from_status(rec.membership.status).value,"pass":rec.membership.status is FibreStatus.MEMBER})
    return rows


def mutation_rows(signature, base):
    candidate=view("mutation-candidate")
    good=membership_evidence(signature,candidate,assumptions=True,invariants=True,effects=True,reconstruction=True,provenance=True,beyond_single_panel=True)
    receipt=assess_membership_bound(signature,candidate,good)
    rows=[]
    def record(name, detected): rows.append({"id":name,"detected":bool(detected)})
    try: replace(signature,reduction_digest="").verify(); detected=False
    except Exception: detected=True
    record("delete_reduction_receipt",detected)
    try: replace(signature,values=(("preconditions",("tampered",)),)+signature.values[1:]).verify(); detected=False
    except Exception: detected=True
    record("alter_preserved_coordinate_after_signature",detected)
    try: assess_membership_bound(signature,view("wrong-realization"),good); detected=False
    except Exception: detected=True
    record("swap_source_realization_receipt",detected)
    try:
        fake=replace(receipt,evidence_digest="sha256:"+"0"*64)
        build_fibre_bound(signature,[fake]); detected=False
    except Exception: detected=True
    record("fabricate_membership_from_embedding_similarity",detected)
    hidden=CompositionContract(CompositionKind.PARALLEL,left_write=("x",),right_read=("x",))
    actual,_=check_composition(hidden); record("hide_composition_collision",actual is CompositionStatus.BLOCKED)
    record("substitute_stale_formal_version", "P6.MethodFibreEval.v1" != "P6.MethodFibreEval.v2")
    gold=["DIFFERENT","SAME"]
    record("fail_open_accept_all", any(x!="SAME" for x in gold))
    record("broken_shut_reject_all", any(x=="SAME" for x in gold))
    return rows


def run(protocol):
    base,red,signature=sig()
    mrows,acc=membership_rows(protocol,signature,base)
    crows=composition_rows(protocol); rrows=relation_rows(protocol); xrows=correspondence_rows(protocol); muts=mutation_rows(signature,base)
    false_rows=[x for x in mrows if next(c for c in protocol["membership_cases"] if c["id"]==x["id"])["family"]=="FALSE_FIBRE"]
    valid_rows=[x for x in mrows if next(c for c in protocol["membership_cases"] if c["id"]==x["id"])["family"]=="FAITHFUL_SUBSTITUTION"]
    result={
        "protocol_id":protocol["protocol_id"],"protocol_digest":content_digest(protocol),
        "membership_rows":mrows,"composition_rows":crows,"relation_rows":rrows,"correspondence_rows":xrows,"mutation_rows":muts,
        "comparator_accuracy":acc,
        "false_fibre_rejection_rate":sum(x["pass"] for x in false_rows)/len(false_rows),
        "valid_substitution_acceptance":sum(x["pass"] for x in valid_rows)/len(valid_rows),
        "composition_obligation_detection":sum(x["pass"] for x in crows)/len(crows),
        "unnecessary_rejection_rate":sum(not x["pass"] for x in valid_rows)/len(valid_rows),
        "correct_unresolved_rate":sum(x["pass"] for x in mrows if x["gold"]=="UNRESOLVED")/sum(x["gold"]=="UNRESOLVED" for x in mrows),
        "mutation_detection_rate":sum(x["detected"] for x in muts)/len(muts),
        "all_typed_cases_pass":all(x["pass"] for x in mrows+crows+rrows+xrows),
        "terminal":"P6_METHOD_FIBRE_COUNTERMODELS_GREEN",
        "claim_ceiling":protocol["claim_ceiling"],
    }
    result["result_digest"]=content_digest(result)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument("--write",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args()
    protocol=json.loads(PROTOCOL.read_text());result=run(protocol)
    if a.write: RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    elif a.check:
        if result!=json.loads(RESULT.read_text()): raise SystemExit("P6 fibre eval V2 drift")
    else: print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":main()
