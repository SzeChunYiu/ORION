#!/usr/bin/env python3
"""Independent QG-13 verifier: no production _DELTA imports."""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
ORION_Q = ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(ORION_Q))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402

ART = ROOT / "artifacts/orion-qg-qg13-theorem-miner.json"
OUT = ROOT / "artifacts/orion-qg-qg13-generic-verification.json"
TOKEN = "ORIONQG_QG13_GENERIC_VERIFY="
h = p10.h
LW = [h.local_wt(i) for i in range(4)]
LM = [[h.local_mul(a, b) for b in range(4)] for a in range(4)]
SY = [[h.local_symp(a, b) for b in range(4)] for a in range(4)]
F3 = [[[1 if a == b == c and a != 0 else LW[a] + LW[b] + LW[c] for c in range(4)] for b in range(4)] for a in range(4)]


def canonical(v): return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def basis(vals: Iterable[int]) -> list[int]:
    b = {}
    for raw in sorted(set(int(v) for v in vals)):
        x = raw
        while x:
            p = x.bit_length() - 1
            if p in b: x ^= b[p]
            else: b[p] = x; break
    return [b[p] for p in sorted(b, reverse=True)]


def r6m_delta(v):
    a0,a1,b0,b1,c0,c1,s=v
    return ((SY[a0][a1]<<0)|(SY[b0][b1]<<1)|(SY[c0][c1]<<2)|((SY[s][a0]^SY[s][b0])<<3)|((SY[s][a0]^SY[s][c0])<<4)|((SY[s][a1]^SY[s][b1])<<5)|((SY[s][a1]^SY[s][c1])<<6)|(SY[s][a0]<<7)|(SY[s][a1]<<8))


def r6i_delta(v):
    a0,a1,b0,b1,s0,s1=v
    return ((SY[a0][a1]<<0)|(SY[b0][b1]<<1)|((SY[s0][a0]^SY[s0][b0])<<2)|((SY[s1][a0]^SY[s1][b0])<<3)|((SY[s0][a1]^SY[s0][b1])<<4)|((SY[s1][a1]^SY[s1][b1])<<5)|(SY[s0][a0]<<6)|(SY[s1][a0]<<7)|(SY[s0][a1]<<8)|(SY[s1][a1]<<9))


def infer_changes():
    r6m = []
    for slot in range(6):
        ch=set()
        for vals in itertools.product(range(4), repeat=7):
            nv=list(vals); nv[slot]=0; ch.add(r6m_delta(vals)^r6m_delta(tuple(nv)))
        r6m.append({"rank":len(basis(ch)),"basis":basis(ch),"change_vectors":sorted(ch),"unique_change_count":len(ch)})
    r6i=[]
    for block in (0,1):
        ch=set()
        for vals in itertools.product(range(4), repeat=6):
            nv=list(vals); start=0 if block==0 else 2; nv[start]=0; nv[start+1]=0; ch.add(r6i_delta(vals)^r6i_delta(tuple(nv)))
        r6i.append({"rank":len(basis(ch)),"basis":basis(ch),"change_vectors":sorted(ch),"unique_change_count":len(ch)})
    return r6m,r6i


def r6m_resource():
    maxima={"central":-99,"noncentral":-99}; rows=0
    for kind in maxima:
        for slot in range(3):
            for f in (1,2,3):
                for partner,tag,target,u,v in itertools.product(range(4),repeat=5):
                    rows+=1; oldl=LM[target][f]
                    if slot==0: old,new=F3[oldl][u][v],F3[target][u][v]
                    elif slot==1: old,new=F3[u][oldl][v],F3[u][target][v]
                    else: old,new=F3[u][v][oldl],F3[u][v][target]
                    maxima[kind]=max(maxima[kind],new-old)
    return rows,maxima


def r6i_resource():
    rows=0; mx=-999; violations=0
    for central in range(3):
        mult=[4,4,4]; mult[central]=2
        for a,b in itertools.product(range(4),repeat=2):
            if a==0 and b==0: continue
            r2=LM[a][b]
            for p0,p1,p2,s0,s1 in itertools.product(range(4),repeat=5):
                rows+=1
                old=mult[0]*LW[a]+mult[1]*LW[b]+mult[2]*LW[r2]+LW[LM[p0][a]]+LW[LM[p1][b]]+LW[LM[p2][r2]]
                new=LW[p0]+LW[p1]+LW[p2]; d=new-old; mx=max(mx,d); violations += int(d>0)
    return rows,mx,violations


def main():
    a=json.loads(ART.read_text())
    copy=dict(a); observed=copy.pop("result_digest",None); digest=hashlib.sha256(canonical(copy).encode()).hexdigest()
    rm,ri=infer_changes(); rmrows,rmmax=r6m_resource(); rirows,rimax,riv=r6i_resource()
    prod_rm=[a["r6m_transition_inference"]["slots"][k] for k in ("A0","A1","B0","B1","C0","C1")]
    prod_ri=[a["r6i_transition_inference"]["blocks"][k] for k in ("A","B")]
    checks={
        "digest":observed==digest,
        "r6m_change_sets_exact":all(x["rank"]==y["rank"] and x["change_vectors"]==y["change_vectors"] for x,y in zip(rm,prod_rm)),
        "r6i_change_sets_exact":all(x["rank"]==y["rank"] and x["change_vectors"]==y["change_vectors"] for x,y in zip(ri,prod_ri)),
        "r6m_resource_domain":rmrows==18432==a["r6m_theorem_candidate"]["resource_cone"]["domain_rows"],
        "r6m_resource_max_exact":rmmax==a["r6m_theorem_candidate"]["resource_cone"]["max_delta_f3"],
        "r6i_resource_domain":rirows==46080==a["r6i_theorem_candidate"]["unit_objective_resource"]["domain_rows"],
        "r6i_resource_max_exact":rimax==a["r6i_theorem_candidate"]["unit_objective_resource"]["max_delta_c"],
        "r6i_no_positive_local_delta":riv==0,
        "authority_false":a["new_theorem_authority"] is False and a["novelty_authority"] is False,
    }
    decision="ACCEPT" if all(checks.values()) and a["terminal"]=="QG13_AUTOMATIC_THEOREM_MINER_RECOVERS_R6M_AND_R6I_PARENT_THEOREMS" else "REJECT"
    out={"schema":"ORION.QG.QG13.GenericVerification.v1","decision":decision,"checks":checks,"independent":{"r6m_ranks":[x["rank"] for x in rm],"r6i_ranks":[x["rank"] for x in ri],"r6m_max_delta_f3":rmmax,"r6i_max_delta_c":rimax},"novelty_authority":False}
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(TOKEN+canonical(out)); return 0

if __name__=="__main__": raise SystemExit(main())
