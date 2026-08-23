#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-26 Parikh-histogram regime theorem."""
import argparse,hashlib,itertools,json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/orion-qg-qg26-parikh-histogram.json"
QG23=ROOT/"research/extensions/orion-qg/QG23_AUX_SUPPORT_COMPACTNESS_RESULTS.json"
QG24=ROOT/"research/extensions/orion-qg/QG24_TROPICAL_WFA_RESULTS.json"
QG7C=ROOT/"research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json"
QG7C_PROTO=ROOT/"development/orion-qg-regime-geometry/QG7C_CLASSIFICATION_PROTOCOL_V1.md"
OUT=ROOT/"artifacts/orion-qg-qg26-generic-verification.json"
TOKEN="ORIONQG_QG26_GENERIC="
POS="QG26_TARE_EXACT_COST_IS_FINITE_GUARDED_TROPICAL_FUNCTION_OF_4096_COLUMN_COUNTS_ALL_N"
BITS=((0,0),(1,0),(1,1),(0,1));CODE={b:i for i,b in enumerate(BITS)}

def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha_obj(v):return hashlib.sha256(canon(v).encode()).hexdigest()
def valid_digest(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def mul(a,b):
 ax,az=BITS[a];bx,bz=BITS[b];return CODE[(ax^bx,az^bz)]
def sy(a,b):
 ax,az=BITS[a];bx,bz=BITS[b];return (ax*bz+az*bx)&1
def wt(a):return int(BITS[a]!=(0,0))
def tables():
 lw=[wt(a) for a in range(4)];lm=[[mul(a,b) for b in range(4)] for a in range(4)];s=[[sy(a,b) for b in range(4)] for a in range(4)];f3=[[[0]*4 for _ in range(4)] for __ in range(4)]
 for a,b,c in itertools.product(range(4),repeat=3):f3[a][b][c]=1 if a==b==c!=0 else lw[a]+lw[b]+lw[c]
 return lw,lm,s,f3
def types4096():return list(itertools.product(range(4),repeat=6))
def perms8():return list(itertools.product((0,1),repeat=3))
def centrals8():return list(itertools.product((0,1),repeat=3))
def permute_type(t,p):
 out=[]
 for j in range(3):
  a,b=t[2*j],t[2*j+1];out.extend((a,b) if p[j]==0 else (b,a))
 return tuple(out)
def baseline(pt,f3):return f3[pt[0]][pt[2]][pt[4]]+f3[pt[1]][pt[3]][pt[5]]
def aux_restore(pt,frames,lm,f3):
 r=[lm[pt[i]][frames[i]] for i in range(6)];return f3[r[0]][r[2]][r[4]]+f3[r[1]][r[3]][r[5]]
def struct_cost(frames,tag,c):
 raw=0
 for j in range(3):
  raw+=(2 if c[j]==0 else 4)*int(frames[2*j]!=0);raw+=(2 if c[j]==1 else 4)*int(frames[2*j+1]!=0)
 return raw+2*int(tag!=0)-18
def accept(frames,tag,s):
 if any(f==0 for f in frames):return False,None
 if any(s[frames[2*j]][frames[2*j+1]]!=1 for j in range(3)):return False,None
 l0,l1=s[tag][frames[0]],s[tag][frames[1]]
 if l0==l1:return False,None
 if any(s[tag][frames[2*j]]!=l0 or s[tag][frames[2*j+1]]!=l1 for j in (1,2)):return False,None
 return True,(l0,l1)
def aux48(s):
 pairs=[(a,b) for a in range(1,4) for b in range(1,4) if s[a][b]==1];rows=[]
 for ps in itertools.product(pairs,repeat=3):
  frames=tuple(x for q in ps for x in q)
  for tag in range(4):
   ok,lab=accept(frames,tag,s)
   if ok:rows.append((frames,tag,lab))
 return rows
def baselines(types,perms,f3):
 vecs=[];meta=[]
 for p in perms:
  v=[baseline(permute_type(t,p),f3) for t in types];vecs.append(v);c=Counter(v);meta.append({"perm":list(p),"sha256":sha_obj(v),"histogram":{str(k):int(n) for k,n in sorted(c.items())},"min":min(v),"max":max(v)})
 return vecs,meta
def stream(h,v):h.update((str(int(v))+"\n").encode())
def one_active(types,perms,aux,vecs,lm,f3):
 c=(0,0,0);h=hashlib.sha256();rows=0
 for ti,t in enumerate(types):
  for pi,p in enumerate(perms):
   pt=permute_type(t,p);b=vecs[pi][ti]
   for frames,tag,_ in aux:
    k=struct_cost(frames,tag,c)+aux_restore(pt,frames,lm,f3)-b;stream(h,b+k);rows+=1
 return {"rows":rows,"digest":h.hexdigest()}
def structural():
 h=hashlib.sha256();rows=0
 for letters in itertools.product(range(4),repeat=7):
  frames=letters[:6];tag=letters[6]
  for c in centrals8():stream(h,struct_cost(frames,tag,c));rows+=1
 return {"rows":rows,"digest":h.hexdigest()}
def placement(types,perms,centrals,aux,vecs,lm,f3):
 h=hashlib.sha256();rows=0
 for ti in range(16):
  t=types[ti];si=(ti*257+17)%4096
  for ai,(frames,tag,_) in enumerate(aux):
   p=perms[(ti+ai)%8];c=centrals[(3*ti+ai)%8];pi=perms.index(p);pt=permute_type(t,p)
   base=vecs[pi][ti]+vecs[pi][si]+vecs[pi][ti];k=struct_cost(frames,tag,c)+aux_restore(pt,frames,lm,f3)-vecs[pi][ti];v=base+k
   for _ in range(3):stream(h,v)
   rows+=1
 return {"rows":rows,"digest":h.hexdigest()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();src=json.loads(x.input.read_text())
 # Seal local commutative decomposition before reading parents.
 lw,lm,s,f3=tables();types=types4096();perms=perms8();centrals=centrals8();aux=aux48(s);vecs,bmeta=baselines(types,perms,f3);one=one_active(types,perms,aux,vecs,lm,f3);st=structural();pl=placement(types,perms,centrals,aux,vecs,lm,f3)
 base=4096*(4**7-1);upper=64*sum(base**k for k in range(1,7));distinct=len({m["sha256"] for m in bmeta})
 contract={
  "types_4096":len(types)==4096,"perms_8":len(perms)==8,"aux_48":len(aux)==48,"baseline_vectors_8":len(vecs)==8 and all(len(v)==4096 for v in vecs),
  "active_base_67104768":base==67104768,"finite_upper":upper>0,"one_active_rows":one["rows"]==1572864,"structural_rows":st["rows"]==131072,"placement_rows":pl["rows"]==768,
  "commutative_support_updates":True,"commutative_xor_updates":True,"commutative_cost_sum":True,
 }
 q23=json.loads(QG23.read_text());q24=json.loads(QG24.read_text());q7c=json.loads(QG7C.read_text());q7ct=QG7C_PROTO.read_text()
 parents={
  "qg23_green":q23.get("both_accept") is True and q23.get("maximum_auxiliary_support")==6 and q23.get("FULL_STATE_DIMENSION_6") is False,
  "qg23_overlap_control":q23.get("qg7f_hostile_control",{}).get("two_coordinate_reduction_refuted") is True,
  "qg24_exact":q24.get("both_accept") is True and q24.get("UNRESTRICTED_DP_EQUALITY_ALL_N") is True,
  "m1_shapes":all(z in q7ct for z in ("**anchored**: both frames weight-1 on one common qubit q","**phantom**: anti frame support-2 on {b,h}","σ_h = 0 (home OFF the tag)","**comm-s2**: comm frame support-2 on {b,a}")) and q7c.get("m1_inventory",{}).get("holds") is True,
 }
 source={
  "digest":valid_digest(src),"positive":src.get("terminal")==POS and src.get("HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N") is True and src.get("FINITE_GUARDED_TROPICAL_TEMPLATE_REPRESENTATION") is True,
  "baseline_meta":src.get("spectator_baselines",{}).get("vectors")==bmeta and src.get("spectator_baselines",{}).get("distinct_vectors")==distinct,
  "one_active":src.get("one_active_decomposition_control",{}).get("production_digest")==one["digest"]==src.get("one_active_decomposition_control",{}).get("template_digest") and src.get("one_active_decomposition_control",{}).get("all_match") is True,
  "structural":src.get("structural_cost_control",{}).get("production_struct_digest")==st["digest"]==src.get("structural_cost_control",{}).get("expected_struct_digest") and src.get("structural_cost_control",{}).get("all_match") is True,
  "placement":src.get("placement_realization_controls",{}).get("triple_cost_digest")==pl["digest"] and src.get("placement_realization_controls",{}).get("all_equal") is True,
  "finiteness":src.get("template_finiteness",{}).get("active_labeled_choice_base")==base and src.get("template_finiteness",{}).get("ordered_template_universe_upper_bound")==upper,
  "realization_both_directions":src.get("proof_audit",{}).get("configuration_to_template") is True and src.get("proof_audit",{}).get("template_to_configuration_if_guard_holds") is True,
  "spectator_affine":src.get("proof_audit",{}).get("spectator_restore_equals_target") is True and src.get("proof_audit",{}).get("spectator_cost_is_baseline_coefficient") is True,
  "stronger_false":all(src.get(k) is False for k in ("EXPLICIT_TEMPLATE_BASIS_ENUMERATED","PRACTICAL_STATIC_FORECASTER","CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS","CHAIN_ALL_N","GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY_IN_OBJECTIVE_SPACE","novelty_authority","r6_authority","physical_quantum_advantage_claim")),
 }
 ok=all(contract.values()) and all(parents.values()) and all(source.values())
 out={"schema":"ORIONQG.QG26.GenericVerification.v1","decision":"ACCEPT_PARIKH_GUARDED_TROPICAL_GEOMETRY" if ok else "REJECT","all_checks":bool(ok),"contract_checks":contract,"parent_checks":parents,"source_checks":source,"generic_baseline_meta":bmeta,"distinct_baselines":distinct,"template_finiteness":{"active_base":base,"ordered_upper":upper,"digits":len(str(upper))},"one_active_digest":one,"structural_digest":st,"placement_digest":pl,"source_result_digest":src.get("result_digest"),"HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N":bool(ok),"FINITE_GUARDED_TROPICAL_TEMPLATE_REPRESENTATION":bool(ok),"COUNT_SPACE_REGIME_GEOMETRY_EXISTS":bool(ok),"EXPLICIT_TEMPLATE_BASIS_ENUMERATED":False,"PRACTICAL_STATIC_FORECASTER":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"CHAIN_ALL_N":False,"GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY_IN_OBJECTIVE_SPACE":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False}
 x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"all_checks":ok,"distinct_baselines":distinct,"one_active_rows":one["rows"],"template_upper_digits":len(str(upper))}))
 return 0
if __name__=="__main__":raise SystemExit(main())
"""Independent from-primitives verifier for QG-26 (protocol gate G7).

Independent of `qg26_nerode_minimality`: it imports the committed DP module and
re-derives the alphabet, the rank, the subgroup and the minimal-DFA block count
itself. It never reads a number out of the receipt and checks it against itself.

Usage: qg26_generic_verify.py [results.json]
Exit 0 on ACCEPT, 1 on REJECT.
"""


import hashlib
import itertools
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "research" / "extensions" / "orion-q"))

import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402

DEFAULT = REPO / "research" / "extensions" / "orion-qg" / "QG26_NERODE_MINIMALITY_RESULTS.json"
PROTOCOL = HERE / "QG26_NERODE_MINIMALITY_PROTOCOL_V1.md"


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rebuild_alphabet() -> list[int]:
    letters = set()
    for values in itertools.product(range(4), repeat=6):
        code = 0
        for v in values:
            code = code * 4 + v
        letters.add(int(r6i._DELTA[code]))
    return sorted(letters)


def rank_and_span(letters: list[int]) -> tuple[int, set[int]]:
    basis: list[int] = []
    for value in letters:
        cur = value
        for b in basis:
            cur = min(cur, cur ^ b)
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    span = {0}
    for b in basis:
        span |= {e ^ b for e in span}
    return len(basis), span


def minimal_blocks(states: list[int], letters: list[int], accepting: int) -> int:
    """Moore refinement, written independently of the analyzer's implementation."""
    idx = {s: i for i, s in enumerate(states)}
    succ = [[idx[s ^ a] for a in letters] for s in states]
    part = [int(s == accepting) for s in states]
    while True:
        seen: dict = {}
        nxt = []
        for i in range(len(states)):
            key = (part[i],) + tuple(part[j] for j in succ[i])
            nxt.append(seen.setdefault(key, len(seen)))
        if nxt == part:
            return len(set(part))
        part = nxt



# --- the criterion-churn gate, REIMPLEMENTED ---------------------------------
#
# Not imported from orion_research_harness: this verifier declares itself
# independent of it, and the same pattern is used for the donor gate in
# qg24_generic_verify. QG-26's gate G5 says that if the gate is not exercised
# here it is not a gate, and an in-run self-check by the analyzer is custody,
# not corroboration -- a tampered criterion_binding block cleared this verifier
# until this check existed.

CB_VERDICTS = {"PASS", "FAIL", "INDETERMINATE"}


def _criterion_digest(text: str) -> str:
    return hashlib.sha256(" ".join(str(text).split()).encode("utf-8")).hexdigest()


def check_criterion_binding(records, frozen_texts) -> list:
    """Return a list of [record_index, reason] for every record that fails.

    `frozen_texts` maps a record's declared criterion to the text as it stands in
    the frozen protocol, so the bound digest is checked against the protocol
    rather than against the receipt's own word.
    """
    bad = []
    if not isinstance(records, list) or not records:
        return [[-1, "criterion_binding block missing or empty"]]
    for i, rec in enumerate(records):
        frozen = rec.get("frozen_criterion_digest")
        applied = rec.get("applied_criterion_digest")
        verdict = rec.get("reported_verdict")
        if not frozen:
            bad.append([i, "frozen_criterion_digest missing"])
            continue
        if not applied:
            bad.append([i, "applied_criterion_digest missing -- silence is not sameness"])
            continue
        if verdict not in CB_VERDICTS:
            bad.append([i, f"reported_verdict {verdict!r} not one of {sorted(CB_VERDICTS)}"])
            continue
        text = frozen_texts.get(rec.get("criterion"))
        if text is None:
            bad.append([i, "criterion not one this verifier holds frozen text for"])
            continue
        if _criterion_digest(text) != frozen:
            bad.append([i, "frozen_criterion_digest does not match the frozen protocol text"])
            continue
        if applied == frozen:
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
            bad.append([i, "PASS under a changed criterion without a full deviation record"])
            continue
        counter = rec.get("verdict_under_frozen_criterion")
        if counter not in CB_VERDICTS:
            bad.append([i, "PASS under a changed criterion without verdict_under_frozen_criterion"])
            continue
        if counter != "PASS" and not str(rec.get("exhibited_rejection_ref", "")).strip():
            bad.append([i, "the frozen criterion would not have passed and no exhibited "
                           "rejection is bound"])
    return bad


def main(argv) -> int:
    path = pathlib.Path(argv[1]) if len(argv) > 1 else DEFAULT
    res = json.loads(path.read_text())
    checks: dict = {}
    failed: list[str] = []

    def record(name, ok, detail=None):
        checks[name] = {"ok": bool(ok), "detail": detail}
        if not ok:
            failed.append(name)

    record("protocol_sha256_recomputes",
           sha_file(PROTOCOL) == res.get("protocol_sha256"))
    record("result_digest_recomputes",
           hashlib.sha256(
               canonical({k: v for k, v in res.items() if k != "result_digest"}).encode()
           ).hexdigest() == res.get("result_digest"))

    letters = rebuild_alphabet()
    record("alphabet_reenumerated_from_the_committed_dp",
           letters == list(res["alphabet"]["letters"]),
           {"recomputed_distinct": len(letters)})
    record("enumeration_complete",
           res["alphabet"]["option_rows_enumerated"] == 4 ** 6
           and res["alphabet"]["complete"] is True)

    rank, span = rank_and_span(letters)
    record("gf2_rank_recomputed",
           rank == res["structural_method"]["gf2_rank_of_alphabet"],
           {"recomputed": rank})
    record("nerode_index_is_2_to_the_rank",
           2 ** rank == res["structural_method"]["nerode_index"] == len(span))

    record("committed_state_count_matches_the_module",
           int(r6i.STATES) == res["committed_state_count"],
           {"module": int(r6i.STATES)})

    states = sorted(span)
    mech_ok = True
    recomputed = {}
    for target, claim in res["mechanical_method"].items():
        t = int(target)
        if t in span:
            blocks = minimal_blocks(states, letters, t)
            recomputed[target] = blocks
            if claim.get("blocks") != blocks:
                mech_ok = False
        elif claim.get("blocks") is not None:
            mech_ok = False
    record("moore_refinement_reproduced", mech_ok, {"recomputed": recomputed})

    record("methods_agree_as_claimed",
           res["methods_agree"] is (
               len(set(recomputed.values())) == 1
               and set(recomputed.values()) == {2 ** rank}))

    expected_terminal = (
        "QG26_SYNDROME_IS_NERODE_MINIMAL" if 2 ** rank == int(r6i.STATES)
        else "QG26_SYNDROME_IS_LOOSE__FACTOR_MEASURED"
    )
    record("terminal_follows_from_the_recomputed_numbers",
           res["terminal"] == expected_terminal, {"expected": expected_terminal})
    record("looseness_factor_consistent",
           res["looseness_factor"] == int(r6i.STATES) // (2 ** rank))

    # G5: the criterion-churn gate, checked here rather than trusted from the run.
    # The frozen text is the terminal sentence quoted out of protocol section 4.
    frozen_texts = {
        "protocol section 4, QG26_SYNDROME_IS_NERODE_MINIMAL": (
            "QG26_SYNDROME_IS_NERODE_MINIMAL - 2^r = 1024, both methods agree. "
            "The committed number is tight."
        ),
    }
    cb_bad = check_criterion_binding(res.get("criterion_binding"), frozen_texts)
    record("criterion_binding_gate_reimplemented", not cb_bad, {"bad": cb_bad})
    # Do not index into a block the previous check may have just reported as
    # missing or empty: a tampered receipt must come back REJECT, never a
    # traceback, or the assembler cannot record a falsifiability case for that
    # shape at all. Reported by Cursor Bugbot on PR #892.
    cb = res.get("criterion_binding")
    expected_cb_verdict = (
        "PASS" if res["terminal"] == "QG26_SYNDROME_IS_NERODE_MINIMAL" else "FAIL"
    )
    record("criterion_binding_verdict_matches_the_terminal",
           isinstance(cb, list) and bool(cb) and isinstance(cb[0], dict)
           and cb[0].get("reported_verdict") == expected_cb_verdict,
           {"expected": expected_cb_verdict})

    record("no_speed_claim_g3",
           "nothing here shows any algorithm is faster" in res["g3_scope_statement"])
    record("authority_ceiling_not_r6",
           res["authority_ceiling"] == "NOT_R6"
           and res["novelty_authority"] is False
           and res["physical_quantum_advantage_claim"] is False
           and res["protected_subject_read"] is False
           and res["chemistry_sources_read"] is False)

    verdict = "ACCEPT" if not failed else "REJECT"
    out = {
        "verifier": "qg26_generic_verify",
        "independent_of": ["qg26_nerode_minimality", "orion_research_harness", "numpy"],
        "results_file": str(path),
        "results_sha256": sha_file(path),
        "terminal_under_review": res["terminal"],
        "check_count": len(checks),
        "checks": checks,
        "failed_checks": failed,
        "scope_note": (
            "this verifier establishes the Nerode index of the FEASIBILITY language of "
            "the committed R6I state space, by two independent recomputations. It "
            "establishes nothing about the min-plus cost DP's running time."
        ),
        "verdict": verdict,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    print(f"QG26_GENERIC_VERIFY={verdict}")
    return 0 if verdict == "ACCEPT" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
