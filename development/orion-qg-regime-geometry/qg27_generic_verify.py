#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-27 bulk-defect theorem."""
import argparse,hashlib,itertools,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/"artifacts/orion-qg-qg27-bulk-defect.json";QG23=ROOT/"research/extensions/orion-qg/QG23_AUX_SUPPORT_COMPACTNESS_RESULTS.json";QG26=ROOT/"research/extensions/orion-qg/QG26_PARIKH_HISTOGRAM_RESULTS.json";OUT=ROOT/"artifacts/orion-qg-qg27-generic-verification.json";TOKEN="ORIONQG_QG27_GENERIC=";POS="QG27_TARE_BULK_DEFECT_LAW_AND_EXACT_ASYMPTOTIC_COST_DENSITY_ALL_N_MACHINE_CHECKED";BITS=((0,0),(1,0),(1,1),(0,1));CODE={b:i for i,b in enumerate(BITS)}
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(v):return hashlib.sha256(canon(v).encode()).hexdigest()
def valid(r):u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def mul(a,b):ax,az=BITS[a];bx,bz=BITS[b];return CODE[(ax^bx,az^bz)]
def sy(a,b):ax,az=BITS[a];bx,bz=BITS[b];return (ax*bz+az*bx)&1
def wt(a):return int(a!=0)
def f3(a,b,c):return 1 if a==b==c!=0 else wt(a)+wt(b)+wt(c)
def perm(t,p):
 o=[]
 for j in range(3):a,b=t[2*j],t[2*j+1];o.extend((a,b) if p[j]==0 else (b,a))
 return tuple(o)
def base(t,p):q=perm(t,p);return f3(q[0],q[2],q[4])+f3(q[1],q[3],q[5])
def vectors():
 ts=list(itertools.product(range(4),repeat=6));ps=list(itertools.product((0,1),repeat=3));vs=[[base(t,p) for t in ts] for p in ps];return ts,ps,vs
def branch():
 av=[];dv=[]
 for t in itertools.product(range(4),repeat=3):
  b=f3(*t)
  for fr in itertools.product(range(4),repeat=3):
   a=f3(*(mul(t[i],fr[i]) for i in range(3)));av.append(a);dv.append(a-b)
 return {"active":[min(av),max(av)],"corr":[min(dv),max(dv)],"rows":len(av)}
def aux48():
 pairs=[(a,b) for a in range(1,4) for b in range(1,4) if sy(a,b)==1];rows=[]
 for ps in itertools.product(pairs,repeat=3):
  fr=tuple(x for z in ps for x in z)
  for tag in range(4):
   l0,l1=sy(tag,fr[0]),sy(tag,fr[1]);ok=l0!=l1 and all(sy(tag,fr[2*j])==l0 and sy(tag,fr[2*j+1])==l1 for j in (1,2))
   if ok:rows.append((fr,tag))
 return rows
def struct(fr,tag,c):
 raw=0
 for j in range(3):raw+=(2 if c[j]==0 else 4)*int(fr[2*j]!=0)+(2 if c[j]==1 else 4)*int(fr[2*j+1]!=0)
 return raw+2*int(tag!=0)-18
def motifs(ts,ps,vs):
 idx={t:i for i,t in enumerate(ts)};reps=ps[:4];data={"unary_tie":([(1,1,1,1,1,1)],[2,2,2,2]),"strict_000":([(0,0,0,0,0,0),(1,2,1,2,1,2)],[2,6,6,6]),"strict_001":([(0,0,0,0,0,0),(1,2,1,2,2,1)],[6,2,6,6]),"strict_010":([(0,0,0,0,0,0),(1,2,2,1,1,2)],[6,6,2,6]),"strict_011":([(0,0,0,0,0,0),(1,2,2,1,2,1)],[6,6,6,2]),"two_way_tie":([(0,0,0,0,0,0),(1,1,1,2,1,2)],[4,6,6,4])};out={}
 for n,(cols,e) in data.items():v=[sum(vs[ps.index(p)][idx[t]] for t in cols) for p in reps];out[n]={"slopes":v,"match":v==e,"valid":all(any(t[i]!=0 for t in cols) for i in range(6))}
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();s=json.loads(x.input.read_text());ts,ps,vs=vectors();vh=[sha(v) for v in vs];br=branch();aux=aux48();sv=[struct(fr,t,c) for fr,t in aux for c in itertools.product((0,1),repeat=3)];mc=motifs(ts,ps,vs)
 q23=json.loads(QG23.read_text());q26=json.loads(QG26.read_text());parents={"qg23":q23.get("both_accept") is True and q23.get("maximum_auxiliary_support")==6,"qg26":q26.get("both_accept") is True and q26.get("FINITE_GUARDED_TROPICAL_TEMPLATE_REPRESENTATION") is True,"baselines":len(set(vh))==4 and set(vh)==set(q26.get("spectator_baselines",{}).get("pairing",{}).values())}
 derived={"spectator_range":[min(z for v in vs for z in v),max(z for v in vs for z in v)],"branch_rows":br["rows"],"branch_active_range":br["active"],"two_branch_active_range":[2*br["active"][0],2*br["active"][1]],"two_branch_correction_range":[2*br["corr"][0],2*br["corr"][1]],"aux_rows":len(aux),"one_active_struct_values":sorted(set(sv)),"lower_defect":2+6*(2*br["corr"][0]),"frozen_lower":-34,"frozen_upper":8,"motifs":mc}
 checks={"source_digest":valid(s),"source_positive":s.get("terminal")==POS,"parents":all(parents.values()),"spectator_0_6":derived["spectator_range"]==[0,6],"active_0_6":derived["two_branch_active_range"]==[0,6],"correction_m6_p6":derived["two_branch_correction_range"]==[-6,6],"aux48":len(aux)==48,"struct2":set(sv)=={2},"band":derived["lower_defect"]==-34 and s.get("local_bounds",{}).get("lower_defect_constant")==-34 and s.get("local_bounds",{}).get("upper_defect_constant")==8,"motifs":all(v["match"] and v["valid"] for v in mc.values()),"asymptotic":s.get("proof_audit",{}).get("eventual_period_one_affinity") is True and s.get("proof_audit",{}).get("scaling_ray_slope_equals_B_min") is True,"stronger_false":all(s.get(k) is False for k in ("DEFECT_CONSTANTS_SHARP","FINITE_N_GLOBAL_PHASE_BOUNDARY","PHYSICAL_PHASE_TRANSITION","CHAIN_ALL_N","CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS","novelty_authority","r6_authority","physical_quantum_advantage_claim"))};ok=all(checks.values())
 out={"schema":"ORIONQG.QG27.GenericVerification.v1","decision":"ACCEPT_BULK_DEFECT_THERMODYNAMIC_LIMIT" if ok else "REJECT","all_checks":bool(ok),"checks":checks,"parent_checks":parents,"derived":derived,"baseline_sha256":vh,"source_result_digest":s.get("result_digest"),"BULK_DEFECT_UNIFORM_BOUND_ALL_N":bool(ok),"ASYMPTOTIC_COST_DENSITY_EXACT":bool(ok),"PURE_SCALING_RAY_EVENTUALLY_AFFINE":bool(ok),"ASYMPTOTIC_COUNT_SPACE_PHASE_GEOMETRY":bool(ok),"DEFECT_CONSTANTS_SHARP":False,"FINITE_N_GLOBAL_PHASE_BOUNDARY":False,"PHYSICAL_PHASE_TRANSITION":False,"CHAIN_ALL_N":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"all_checks":ok,"band":[derived["lower_defect"],8],"correction":derived["two_branch_correction_range"],"bulk_forms":len(set(vh))}));return 0
if __name__=="__main__":raise SystemExit(main())
"""Independent from-primitives verifier for QG-27 (protocol gate G7).

Independent of `qg27_cost_minimality`: it imports the committed DP and re-derives
the cost table, the letter span, the structural conclusion, the counterexample
that refutes the lane's own frozen criterion, and the exhibited rejection that
`criterion_binding` demanded. It never reads a number out of the receipt and
checks it against itself.

Usage: qg27_generic_verify.py [results.json]   Exit 0 ACCEPT, 1 REJECT.
"""


import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "research" / "extensions" / "orion-q"))

import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402

DEFAULT = REPO / "research" / "extensions" / "orion-qg" / "QG27_COST_MINIMALITY_RESULTS.json"
PROTOCOL = HERE / "QG27_COST_MINIMALITY_PROTOCOL_V1.md"
INF = 1 << 40
CB_VERDICTS = {"PASS", "FAIL", "INDETERMINATE"}

FROZEN_CRITERION = (
    "QG27_COST_DP_IS_ALREADY_MINIMAL - 1024 classes at every R examined. "
    "The committed DP is tight for cost as well as feasibility."
)


def canonical(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def sha_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def crit_digest(text: str) -> str:
    return hashlib.sha256(" ".join(str(text).split()).encode("utf-8")).hexdigest()


def rebuild_cost(key) -> list[int]:
    costs, _ = r6i._local_table(tuple(key))
    return [int(c) if int(c) < int(r6i.INF) else INF for c in costs]


def span_rank(cost: list[int]) -> tuple[int, set[int]]:
    basis: list[int] = []
    for d, c in enumerate(cost):
        if c >= INF:
            continue
        cur = d
        for b in basis:
            cur = min(cur, cur ^ b)
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    span = {0}
    for b in basis:
        span |= {e ^ b for e in span}
    return len(basis), span


def cost_to_go_first(cost: list[int], accepting: set[int]) -> list[int]:
    cur = [0 if s in accepting else INF for s in range(r6i.STATES)]
    return [min((c + cur[s ^ d] for d, c in enumerate(cost)
                 if c < INF and cur[s ^ d] < INF), default=INF)
            for s in range(r6i.STATES)]


def check_criterion_binding(records, frozen_texts) -> list:
    """Reimplemented, not imported: this verifier declares itself independent."""
    bad = []
    if not isinstance(records, list) or not records:
        return [[-1, "criterion_binding block missing or empty"]]
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            bad.append([i, "record is not an object"]); continue
        frozen = rec.get("frozen_criterion_digest")
        applied = rec.get("applied_criterion_digest")
        verdict = rec.get("reported_verdict")
        if not frozen:
            bad.append([i, "frozen_criterion_digest missing"]); continue
        if not applied:
            bad.append([i, "applied_criterion_digest missing -- silence is not sameness"]); continue
        if verdict not in CB_VERDICTS:
            bad.append([i, f"reported_verdict {verdict!r} invalid"]); continue
        text = frozen_texts.get(rec.get("criterion"))
        if text is None:
            bad.append([i, "criterion not one this verifier holds frozen text for"]); continue
        if crit_digest(text) != frozen:
            bad.append([i, "frozen_criterion_digest does not match the frozen protocol text"]); continue
        if applied == frozen:
            # Concealment is the cheapest bypass: set the applied digest equal to
            # the frozen one and none of the checks below ever run. This verifier
            # ACCEPTed exactly that tampered receipt until this existed.
            contradictions = [f for f in ("deviation", "verdict_under_frozen_criterion",
                                          "exhibited_rejection_ref") if rec.get(f)]
            if contradictions:
                bad.append([i, "declares the criterion unchanged yet carries "
                               f"{contradictions}; the change is being concealed"])
            continue
        if verdict != "PASS":
            continue
        dev = rec.get("deviation")
        if not isinstance(dev, dict) or not str(dev.get("description", "")).strip() \
                or not str(dev.get("rationale", "")).strip():
            bad.append([i, "PASS under a changed criterion without a full deviation"]); continue
        counter = rec.get("verdict_under_frozen_criterion")
        if counter not in CB_VERDICTS:
            bad.append([i, "PASS under a changed criterion without the counterfactual"]); continue
        if counter != "PASS" and not str(rec.get("exhibited_rejection_ref", "")).strip():
            bad.append([i, "frozen criterion would not have passed and no exhibited rejection is bound"])
    return bad


def main(argv) -> int:
    path = pathlib.Path(argv[1]) if len(argv) > 1 else DEFAULT
    res = json.loads(path.read_text())
    checks, failed = {}, []

    def record(name, ok, detail=None):
        checks[name] = {"ok": bool(ok), "detail": detail}
        if not ok:
            failed.append(name)

    record("protocol_sha256_recomputes", sha_file(PROTOCOL) == res.get("protocol_sha256"))
    record("result_digest_recomputes",
           hashlib.sha256(canonical({k: v for k, v in res.items()
                                     if k != "result_digest"}).encode()).hexdigest()
           == res.get("result_digest"))

    cost = rebuild_cost(res["frozen_key"])
    record("cost_table_rebuilt_from_the_committed_dp",
           sum(1 for c in cost if c < INF) == res["letters_with_finite_cost"]
           and len({c for c in cost if c < INF}) == res["distinct_finite_costs"],
           {"finite": sum(1 for c in cost if c < INF)})

    accepting = {int(p) for p, _ in r6i._accepting_states()}
    record("accepting_states_recomputed", sorted(accepting) == res["accepting_states"])

    rank, span = span_rank(cost)
    red = res["cost_mergeability_reduces_to_feasibility"]
    record("letters_span_rank_recomputed", rank == red["letters_span_rank"], {"recomputed": rank})
    record("subgroup_order_is_2_to_the_rank",
           len(span) == red["reachable_subgroup_order"] == 2 ** rank)
    # Recompute separation the way the CLAIM requires: the accepting set's
    # translation stabiliser must be trivial. Checking that every state reaches
    # one accepting state is implied by a full span and tests nothing.
    stabiliser = sorted(
        d for d in range(r6i.STATES) if {a ^ d for a in accepting} == accepting)
    separated = (len(span) == r6i.STATES) and stabiliser == [0]
    record("accepting_set_stabiliser_recomputed",
           stabiliser == red["accepting_set_translation_stabiliser"]
           and red["stabiliser_is_trivial"] == (stabiliser == [0]),
           {"recomputed": stabiliser})
    record("every_state_separated_recomputed",
           separated == red["every_state_separated_from_every_other"])

    record("costs_are_state_independent",
           len(r6i._local_table(tuple(res["frozen_key"]))[0]) == r6i.STATES
           and res["costs_are_state_independent"]["table_length"] == r6i.STATES)

    # the lane's own frozen criterion must really be refuted by the pair it names
    C1 = cost_to_go_first(cost, accepting)
    ref = res["frozen_criterion_refutation"]
    record("frozen_criterion_refutation_holds",
           bool(ref.get("refuted"))
           and C1[ref["state_a"]] == ref["optimal_cost_to_go_a"]
           and C1[ref["state_b"]] == ref["optimal_cost_to_go_b"]
           and C1[ref["state_b"]] != C1[ref["state_a"]],
           {"recomputed_a": C1[ref["state_a"]], "recomputed_b": C1[ref["state_b"]]})

    # and the exhibited rejection must really reject
    ex = res["exhibited_rejection"]
    deficient = [c if (d & 0b1111111000) == 0 and c < INF else INF
                 for d, c in enumerate(cost)]
    drank, dspan = span_rank(deficient)
    # Separation under the rank-deficient construction, recomputed the same way
    # the claim requires -- span full AND stabiliser trivial -- not by reachability.
    deficient_separated = (len(dspan) == r6i.STATES) and stabiliser == [0]
    record("exhibited_rejection_really_rejects",
           drank == ex["letters_span_rank"]
           and len(dspan) == ex["reachable_subgroup_order"]
           and deficient_separated is False
           and ex["every_state_separated"] is False,
           {"recomputed_rank": drank, "recomputed_order": len(dspan),
            "recomputed_separated": deficient_separated})

    bad = check_criterion_binding(res.get("criterion_binding"),
                                  {"protocol section 6, QG27_COST_DP_IS_ALREADY_MINIMAL":
                                   FROZEN_CRITERION})
    record("criterion_binding_gate_reimplemented", not bad, {"bad": bad})

    expected = ("QG27_COST_DP_IS_ALREADY_MINIMAL" if separated
                else "QG27_COST_REDUCTION_CANDIDATE__UNPROVEN_BEYOND_HORIZON")
    record("terminal_follows_from_the_recomputed_numbers",
           res["terminal"] == expected, {"expected": expected})

    record("no_efficiency_claim_g4",
           "no reduction is claimed" in res["g4_no_efficiency_claim"])
    record("timing_appears_in_no_argument_g3",
           "appears in no argument" in res["g3_timing_note"])
    record("scope_limit_declares_the_single_key",
           "ONE cost-table key" in res["scope_limit"]
           and res["frozen_key_is_the_only_key_used"] is True)
    record("authority_ceiling_not_r6",
           res["authority_ceiling"] == "NOT_R6"
           and res["novelty_authority"] is False
           and res["physical_quantum_advantage_claim"] is False
           and res["protected_subject_read"] is False
           and res["chemistry_sources_read"] is False)

    verdict = "ACCEPT" if not failed else "REJECT"
    out = {
        "verifier": "qg27_generic_verify",
        "independent_of": ["qg27_cost_minimality", "orion_research_harness"],
        "results_file": str(path),
        "results_sha256": sha_file(path),
        "terminal_under_review": res["terminal"],
        "check_count": len(checks),
        "checks": checks,
        "failed_checks": failed,
        "scope_note": (
            "establishes cost-minimality for the time-invariant automaton obtained "
            "by freezing ONE cost-table key. Says nothing about the key-varying DP "
            "the programme runs, and nothing about any algorithm's speed."
        ),
        "verdict": verdict,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    print(f"QG27_GENERIC_VERIFY={verdict}")
    return 0 if verdict == "ACCEPT" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
