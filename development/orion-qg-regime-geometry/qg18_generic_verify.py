#!/usr/bin/env python3
"""Independent generic-ORION verifier for QG-18 TARE intrinsic support."""
from __future__ import annotations

import hashlib, itertools, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "artifacts/orion-qg-qg18-tare-kappa2.json"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG18_TARE_KAPPA2_PROTOCOL_V1.md"
R6S = ROOT / "research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
OUT = ROOT / "artifacts/orion-qg-qg18-generic-verification.json"
TOKEN = "ORIONQG_QG18_GENERIC="


def canonical(v): return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)
def wt(a): return (a[0] | a[1]).bit_count()
def mul(a,b): return (a[0]^b[0], a[1]^b[1])
def symp(a,b): return (((a[0]&b[1]).bit_count() + (a[1]&b[0]).bit_count()) & 1)

def local(a,q): return ((a[0]>>q)&1, (a[1]>>q)&1)

def independent_cap1(target_pairs, n=3):
    keys=[(x,z) for x in range(1<<n) for z in range(1<<n)]
    small=[k for k in keys if k!=(0,0) and wt(k)==1]
    pairs=[(a,b) for a in small for b in small if symp(a,b)==1]
    assert len(pairs)==6*n
    tags=[k for k in keys if k!=(0,0)]
    best=None; best_id=None; examined=0
    for orient in ((0,1),(1,0)):
        l0,l1=orient
        for s in tags:
            opts=[]
            for tp in target_pairs:
                block=[]
                for pi,(a,b) in enumerate(pairs):
                    if symp(s,a)!=l0 or symp(s,b)!=l1: continue
                    for perm in (0,1):
                        t0,t1=tp if perm==0 else (tp[1],tp[0])
                        e0,e1=mul(t0,a),mul(t1,b)
                        block.append((wt(e0)+wt(e1),e0,e1,pi,perm))
                opts.append(block)
            if any(not x for x in opts): continue
            for A in opts[0]:
                for B in opts[1]:
                    for C in opts[2]:
                        examined+=1
                        match=0
                        for branch in (1,2):
                            ea=A[branch]; eb=B[branch]; ec=C[branch]
                            for q in range(n):
                                la,lb,lc=local(ea,q),local(eb,q),local(ec,q)
                                if la==lb==lc and la!=(0,0): match+=1
                        cost=A[0]+B[0]+C[0]-2*match+2*wt(s)
                        ident=(cost,orient,wt(s),s,A[3:],B[3:],C[3:])
                        if best is None or ident<best_id:
                            best=cost; best_id=ident
    if best is None: raise AssertionError("independent cap1 found no feasible point")
    return {"cost":int(best),"pair_count":len(pairs),"states_examined":examined,"best_identity":str(best_id[1:])}


def main():
    a=json.loads(RESULT.read_text()); r6s=json.loads(R6S.read_text())
    u=dict(a); observed=u.pop("result_digest",None)
    tp=tuple((tuple(x[0]),tuple(x[1])) for x in a["selected_witness"]["target_pairs"])
    brute=independent_cap1(tp,3)
    checks={
        "schema":a.get("schema")=="ORION.QG.QG18.TAREKappa.v1",
        "result_digest":observed==hashlib.sha256(canonical(u).encode()).hexdigest(),
        "protocol_hash":a.get("protocol_sha256")==hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "positive_terminal":a.get("terminal")=="QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS_MACHINE_VERIFIED",
        "independent_cap1_8":brute["cost"]==8,
        "production_cap1_8":a["selected_witness"]["cap1"]["C_Dxx"]==8,
        "dp_7":a["selected_witness"]["unrestricted_dp"]==7,
        "strict_gap":a["selected_witness"]["unrestricted_dp"]<brute["cost"],
        "r6s_bound":str(r6s.get("authority","")).startswith("MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED") and all(r6s.get("gates",{}).values()),
        "kappa_2":a.get("proof",{}).get("intrinsic_support_number")==2,
        "no_overclaim":a.get("novelty_authority") is False and a.get("physical_quantum_advantage_claim") is False and a.get("r6_authority") is False,
    }
    decision="ACCEPT_KAPPA2" if all(checks.values()) else "REJECT"
    out={"schema":"ORION.QG.QG18.GenericVerification.v1","issue":"SzeChunYiu/ORION#838","decision":decision,"checks":checks,"all_checks":all(checks.values()),"independent_cap1":brute,"terminal":a.get("terminal"),"novelty_authority":False}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(TOKEN+canonical(out)); return 0

if __name__=="__main__": raise SystemExit(main())
