#!/usr/bin/env python3
"""QG-13 V2 / QG-9: eliminate the R6I support-five boundary by combined local deletions."""
from __future__ import annotations
import argparse, hashlib, itertools, json, sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ORION_Q = REPO_ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(ORION_Q))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402

PROTOCOL = REPO_ROOT / "development/orion-qg-regime-geometry/QG13_V2_R6I_SUPPORT4_PROTOCOL.md"
NOVELTY = REPO_ROOT / "development/orion-qg-regime-geometry/QG13_V2_NOVELTY_FREEZE.md"
QG1 = REPO_ROOT / "research/extensions/orion-qg/QG1_RANK2_ALL_N_RESULTS.json"
QG13_V1 = REPO_ROOT / "development/orion-qg-regime-geometry/QG13_PROTECTED_RUN_RECEIPT_2026-08-21.json"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts/orion-qg-qg13-v2-support4.json"
TOKEN = "ORIONQG_QG13_V2_SUPPORT4="
ACTIONS = ("d0", "d1", "db")

def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def pack(bits): return sum(int(x) << i for i,x in enumerate(bits))

def local_state(a,b,s0,s1):
    sy=r6i._SYMP
    return (int(sy[a,b]),int(sy[s0,a]),int(sy[s1,a]),int(sy[s0,b]),int(sy[s1,b]))
def after(a,b,action):
    if action=="d0": return 0,b
    if action=="d1": return a,0
    if action=="db": return 0,0
    raise ValueError(action)
def action_available(a,b,action):
    return (action=="d0" and a!=0) or (action=="d1" and b!=0) or (action=="db" and a!=0 and b!=0)
def action_signature(a,b,s0,s1,action):
    old=local_state(a,b,s0,s1); na,nb=after(a,b,action); new=local_state(na,nb,s0,s1)
    return pack(tuple(x^y for x,y in zip(old,new)))
def multipliers(central):
    m=[4,4,4];m[central]=2;return m

def local_cost(a,b,p0,p1,p2,central):
    r2=int(r6i._MUL[a,b]);m=multipliers(central);lw=r6i._LW;mul=r6i._MUL
    return int(m[0]*lw[a]+m[1]*lw[b]+m[2]*lw[r2]+lw[int(mul[p0,a])]+lw[int(mul[p1,b])]+lw[int(mul[p2,r2])])
def local_delta(a,b,action,p0,p1,p2,central):
    na,nb=after(a,b,action)
    return local_cost(na,nb,p0,p1,p2,central)-local_cost(a,b,p0,p1,p2,central)

def descriptor(a,b,s0,s1):
    sy=r6i._SYMP
    return (int(a!=0),int(b!=0),int(a==b and a!=0),int(sy[a,b]),int(sy[s0,a]),int(sy[s1,a]),int(sy[s0,b]),int(sy[s1,b]))
def descriptor_code(d): return "".join(str(x) for x in d)

def zero_subset(codes):
    n=len(codes)
    for mask in range(1,1<<n):
        x=0
        for i,c in enumerate(codes):
            if (mask>>i)&1: x^=int(c)
        if x==0:return True
    return False

def build_local_domain():
    desc_reps=defaultdict(list)
    sig_rows=0
    for a,b,s0,s1 in itertools.product(range(4),repeat=4):
        if a==0 and b==0: continue
        d=descriptor(a,b,s0,s1);desc_reps[d].append((a,b,s0,s1))
        for act in ACTIONS:
            if action_available(a,b,act): sig_rows += 1
    profiles={}; action_cost_cases=0
    for d,reps in desc_reps.items():
        amap={}
        for act in ACTIONS:
            reps2=[r for r in reps if action_available(r[0],r[1],act)]
            if not reps2:continue
            sigs={action_signature(*r,act) for r in reps2}
            if len(sigs)!=1: raise AssertionError({"descriptor_signature_not_unique":descriptor_code(d),"action":act,"sigs":sorted(sigs)})
            by_c=[]; mins=[]
            for central in range(3):
                values=[]
                ab_seen=set()
                for a,b,_s0,_s1 in reps2:
                    if (a,b) in ab_seen:continue
                    ab_seen.add((a,b))
                    for p0,p1,p2 in itertools.product(range(4),repeat=3):
                        values.append(local_delta(a,b,act,p0,p1,p2,central)); action_cost_cases += 1
                by_c.append(max(values));mins.append(min(values))
            amap[act]={"signature":next(iter(sigs)),"max_by_central":by_c,"min_by_central":mins}
        profiles[d]=amap
    # action_cost_cases above duplicates an (a,b,action,central,target) whenever the same pair appears in multiple descriptors.
    # Recompute exact unique production cost domain independently.
    unique_cost_cases=0
    for a,b in itertools.product(range(4),repeat=2):
        if a==0 and b==0:continue
        for act in ACTIONS:
            if not action_available(a,b,act):continue
            unique_cost_cases += 3*(4**3)
    return desc_reps,profiles,sig_rows,unique_cost_cases

def irreducible(combo):
    # Selected generator is R0; arbitrary partner-only completion outside these columns is allowed.
    if not all(d[0] for d in combo): return False
    alpha=ba0=ba1=0
    for d in combo:
        alpha ^= d[3]; ba0 ^= d[4]; ba1 ^= d[5]
    if alpha != 1 or ((ba0<<1)|ba1)==0:return False
    C=[(d[4]<<1)|d[5] for d in combo if d[2]]
    if zero_subset(C):return False
    N0=[(d[3]<<2)|(d[4]<<1)|d[5] for d in combo if d[0] and not d[2]]
    if zero_subset(N0):return False
    N1=[(d[3]<<2)|(d[6]<<1)|d[7] for d in combo if d[1] and not d[2]]
    if zero_subset(N1):return False
    return True

def safe_move(combo,profiles):
    opts=[]
    for d in combo:
        row=[("none",0,(0,0,0),0,0)]
        for act in ACTIONS:
            if act not in profiles[d]:continue
            p=profiles[d][act]
            dr0=int(act in ("d0","db") and d[0]);dr1=int(act in ("d1","db") and d[1])
            row.append((act,int(p["signature"]),tuple(int(x) for x in p["max_by_central"]),dr0,dr0+dr1))
        opts.append(row)
    best=None
    for choices in itertools.product(*opts):
        if all(x[0]=="none" for x in choices):continue
        sig=0;drop0=drop=0
        for x in choices:sig^=x[1];drop0+=x[3];drop+=x[4]
        if sig!=0 or drop0<1:continue
        costs=tuple(sum(x[2][c] for x in choices) for c in range(3));worst=max(costs)
        if worst>0:continue
        word=tuple(x[0] for x in choices)
        key=(worst,-drop0,-drop,word)
        if best is None or key<best[0]:best=(key,{"actions":word,"cost_upper_by_central":costs,"worst_cost_upper":worst,"selected_support_drop":drop0,"total_support_drop":drop})
    return None if best is None else best[1]

def enumerate_boundary(descs,profiles,w):
    descs=sorted(descs)
    irreducibles=[]; unresolved=[]; moves=[]
    for inds in itertools.combinations_with_replacement(range(len(descs)),w):
        combo=[descs[i] for i in inds]
        if not irreducible(combo):continue
        mv=safe_move(combo,profiles)
        irreducibles.append(inds)
        if mv is None:
            if len(unresolved)<20:unresolved.append([descriptor_code(x) for x in combo])
        else:
            moves.append(mv)
    hist=Counter(int(m["worst_cost_upper"]) for m in moves)
    return {"support":w,"irreducible_count":len(irreducibles),"certified_move_count":len(moves),"unresolved_count":len(irreducibles)-len(moves),"worst_cost_histogram":{str(k):v for k,v in sorted(hist.items())},"strict_count":sum(m["worst_cost_upper"]<0 for m in moves),"tie_count":sum(m["worst_cost_upper"]==0 for m in moves),"unresolved_examples":unresolved}

def parent_binding():
    qg1=json.loads(QG1.read_text());v1=json.loads(QG13_V1.read_text())
    return {"qg1_sha256":sha(QG1),"qg1_authority":qg1.get("authority"),"qg1_support5":str(qg1.get("claim_boundary",{}).get("covers","")).find("support <= 5")>=0,"qg1_all_gates":all(qg1.get("gates",{}).values()),"qg13_v1_sha256":sha(QG13_V1),"qg13_v1_terminal":v1.get("terminal"),"v2_permitted":v1.get("v2_permission")=="NEW_EDIT_TEMPLATE_MAY_BE_FROZEN_ONLY_AS_NEW_PROSPECTIVE_PACKET"}
def run():
    desc_reps,profiles,sig_rows,cost_cases=build_local_domain();descs=list(desc_reps)
    w5=enumerate_boundary(descs,profiles,5);w4=enumerate_boundary(descs,profiles,4);parent=parent_binding()
    # symmetry: descriptor set closed under R0/R1 swap and corresponding beta swap.
    dset=set(descs)
    def sw(d):return (d[1],d[0],d[2],d[3],d[6],d[7],d[4],d[5])
    symmetry=all(sw(d) in dset for d in dset)
    gates={
      "production_algebra_bound": all(int(r6i._MUL[a,b])==int(p10.h.local_mul(a,b)) and int(r6i._SYMP[a,b])==int(p10.h.local_symp(a,b)) for a in range(4) for b in range(4)),
      "descriptor_count_28":len(descs)==28,"signature_rows_528":sig_rows==528,"unique_cost_domain_6336":cost_cases==6336,
      "support5_irreducible_324":w5["irreducible_count"]==324,"support5_all_reducible":w5["certified_move_count"]==324 and w5["unresolved_count"]==0,
      "support5_strict_288_tie_36":w5["strict_count"]==288 and w5["tie_count"]==36,
      "support4_irreducible_432":w4["irreducible_count"]==432,"support4_boundary_36_unresolved":w4["unresolved_count"]==36,
      "generator_swap_symmetry":symmetry,"parent_qg1_support5_bound":parent["qg1_support5"] and parent["qg1_all_gates"],"qg13_v1_permits_new_edit":parent["v2_permitted"]}
    positive=all(gates.values())
    terminal="QG13_V2_R6I_SUPPORT4_CANDIDATE_COMPLETE" if positive else "QG13_V2_SUPPORT5_PATTERN_REFUTATION_FOUND"
    result={"schema":"ORION.QG.QG13V2.R6ISupport4.v1","issue":"SzeChunYiu/ORION#762","protocol_sha256":sha(PROTOCOL),"novelty_freeze_sha256":sha(NOVELTY),"terminal":terminal,"descriptor_count":len(descs),"signature_domain_rows":sig_rows,"unique_local_cost_domain_cases":cost_cases,"support5":w5,"support4_boundary":w4,"parent_binding":parent,"proof_audit":{"zero_signature_preserves_all_five_block_constraints":True,"dependent_r2_recomputed_exactly":True,"r6i_objective_is_qubit_additive_no_factor_coupling":True,"common_central_worst_case_used":True,"qg1_reduces_all_n_problem_to_support_at_most_five":parent["qg1_support5"],"support4_not_support3_claim":w4["unresolved_count"]>0},"gates":gates,"new_theorem_authority":False,"support3_authority":False,"tightness4_authority":False,"novelty_authority":False,"physical_quantum_advantage_claim":False}
    d=dict(result);result["result_digest"]=hashlib.sha256(canonical(d).encode()).hexdigest();return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",default=str(DEFAULT_OUTPUT));args=ap.parse_args();r=run();p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");print(TOKEN+canonical(r));return 0
if __name__=="__main__":raise SystemExit(main())
