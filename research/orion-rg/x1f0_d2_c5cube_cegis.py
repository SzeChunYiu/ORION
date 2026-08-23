#!/usr/bin/env python3
"""Prospectively frozen positive-search CEGIS for D_2(C_5^3)>20.

A positive terminal is a length-20 multiset over C_5^3 with no two disjoint
nonempty zero-sum submultisets.  Master infeasibility is only a solver/bounded
certificate until independently proved.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

P = 5
N = 125
TARGET = 20
VECTORS = tuple((i // 25, (i // 5) % 5, i % 5) for i in range(N))
BASIS_INDEX = (25, 5, 1)  # e1,e2,e3 in the encoding above


def solve_oracle(counts: tuple[int, ...], time_limit: float):
    active = tuple(g for g, c in enumerate(counts) if c)
    m = len(active)
    zc = 2 * m
    qoff = zc
    nvar = zc + 6
    integrality = np.ones(nvar, dtype=int)
    lb = np.zeros(nvar)
    ub = np.zeros(nvar)
    for j in range(2):
        for a, g in enumerate(active):
            ub[j * m + a] = counts[g]
    ub[qoff:] = 16
    objective = np.zeros(nvar)
    objective[:zc] = 1.0

    rows=[]; cols=[]; data=[]; lo=[]; hi=[]; row=0
    for a,g in enumerate(active):
        for j in range(2):
            rows.append(row); cols.append(j*m+a); data.append(1.0)
        lo.append(-np.inf); hi.append(float(counts[g])); row += 1
    for j in range(2):
        for a in range(m):
            rows.append(row); cols.append(j*m+a); data.append(1.0)
        lo.append(1.0); hi.append(np.inf); row += 1
    for j in range(2):
        for c in range(3):
            for a,g in enumerate(active):
                coeff = VECTORS[g][c]
                if coeff:
                    rows.append(row); cols.append(j*m+a); data.append(float(coeff))
            rows.append(row); cols.append(qoff+3*j+c); data.append(-5.0)
            lo.append(0.0); hi.append(0.0); row += 1
    A=coo_matrix((data,(rows,cols)),shape=(row,nvar)).tocsr()
    res=milp(c=objective, integrality=integrality, bounds=Bounds(lb,ub),
             constraints=LinearConstraint(A,np.asarray(lo),np.asarray(hi)),
             options={"time_limit":time_limit,"mip_rel_gap":0.0})
    if not res.success:
        return res, None
    raw=np.rint(res.x[:zc]).astype(int)
    blocks=[]; usage=[0]*N
    for j in range(2):
        block=[0]*N
        for a,g in enumerate(active):
            v=int(raw[j*m+a]); block[g]=v; usage[g]+=v
        blocks.append(tuple(block))
    return res,(tuple(usage),tuple(blocks))


def solve_master(cuts, time_limit: float):
    blockers=[]
    for ci,(usage,_) in enumerate(cuts):
        for g,need in enumerate(usage):
            if need: blockers.append((ci,g))
    yoff=N; nvar=N+len(blockers)
    integrality=np.ones(nvar,dtype=int)
    lb=np.zeros(nvar); ub=np.full(nvar,TARGET,dtype=float)
    if blockers: ub[yoff:]=1.0
    objective=np.zeros(nvar); objective[:N]=np.arange(N)/(N*N)
    rows=[];cols=[];data=[];lo=[];hi=[];row=0
    for g in range(N):
        rows.append(row);cols.append(g);data.append(1.0)
    lo.append(TARGET);hi.append(TARGET);row+=1
    for g in BASIS_INDEX:
        rows.append(row);cols.append(g);data.append(1.0)
        lo.append(1.0);hi.append(np.inf);row+=1
    bycut={ci:[] for ci in range(len(cuts))}
    for pos,(ci,g) in enumerate(blockers):
        bycut[ci].append(pos); need=cuts[ci][0][g]
        rows.extend((row,row)); cols.extend((g,yoff+pos)); data.extend((1.0,float(TARGET)))
        lo.append(-np.inf); hi.append(float(need-1+TARGET)); row+=1
    for ci in range(len(cuts)):
        for pos in bycut[ci]:
            rows.append(row);cols.append(yoff+pos);data.append(1.0)
        lo.append(1.0);hi.append(np.inf);row+=1
    A=coo_matrix((data,(rows,cols)),shape=(row,nvar)).tocsr()
    return milp(c=objective,integrality=integrality,bounds=Bounds(lb,ub),
                constraints=LinearConstraint(A,np.asarray(lo),np.asarray(hi)),
                options={"time_limit":time_limit,"mip_rel_gap":0.0})


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--max-iterations",type=int,default=5000)
    ap.add_argument("--master-time-limit",type=float,default=60.0)
    ap.add_argument("--oracle-time-limit",type=float,default=60.0)
    ap.add_argument("--receipt",type=Path)
    args=ap.parse_args()
    cuts=[]; candidate=None; terminal="CANNOT_CHECK_RESOURCE_BOUND"; detail="iteration cap"
    for it in range(args.max_iterations):
        master=solve_master(cuts,args.master_time_limit)
        if master.status==2:
            terminal="MASTER_INFEASIBLE_NEEDS_INDEPENDENT_PROOF"; detail=f"cuts={len(cuts)}"; break
        if not master.success:
            detail=f"master status={master.status}: {master.message}"; break
        counts=tuple(int(round(v)) for v in master.x[:N])
        oracle,cut=solve_oracle(counts,args.oracle_time_limit)
        if cut is None:
            if oracle.status==2:
                terminal="LENGTH20_OBSTRUCTION_CANDIDATE_FOUND"
                candidate=[{"vector":list(VECTORS[g]),"multiplicity":c} for g,c in enumerate(counts) if c]
                detail="independent replay required"
            else:
                detail=f"oracle status={oracle.status}: {oracle.message}"
            break
        cuts.append(cut)
    out={"schema":"ORION.RG.X1F0.C5CubeD2CEGIS.v1","terminal":terminal,
         "detail":detail,"packing_cuts":len(cuts),"candidate":candidate,
         "claim_ceiling":"POSITIVE_CANDIDATE_OR_BOUNDED_NEGATIVE_ONLY",
         "exact_D2_authority":False,"novelty_authority":False}
    text=json.dumps(out,sort_keys=True,separators=(",", ":"))
    if args.receipt: args.receipt.write_text(text+"\n")
    print(text)

if __name__=="__main__":
    main()
