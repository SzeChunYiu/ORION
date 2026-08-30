#!/usr/bin/env python3
"""ORION-19 failure diagnosis. Protocol smt-failure-diagnosis-v1 + AMENDMENT_V1_MEASURED_ENCODINGS."""
from __future__ import annotations
import json, os, platform, random, statistics, sys, time
import z3

BUDGET_MS = 5000
LOW_FRACTION = 0.9          # hostile: budget just below what the reference needs
SPLIT_SEED = 20260830

def php_bv(n):
    W=max(3,(n).bit_length()+1); s=z3.Solver(); h=[z3.BitVec(f"v{i}",W) for i in range(n+1)]
    for x in h: s.add(z3.ULT(x,n))
    s.add(z3.Distinct(h)); return s
def php_int(n):
    s=z3.Solver(); h=[z3.Int(f"h{i}") for i in range(n+1)]
    for x in h: s.add(x>=0,x<n)
    s.add(z3.Distinct(h)); return s
def php_noinfo(n):
    W=max(3,(n).bit_length()+1); s=z3.Solver(); h=[z3.BitVec(f"v{i}",W) for i in range(n+1)]
    for x in h: s.add(z3.ULT(x,n))
    return s
def col_bv(k):
    W=max(3,(k).bit_length()+1); s=z3.Solver(); c=[z3.BitVec(f"c{i}",W) for i in range(k+1)]
    for x in c: s.add(z3.ULT(x,k))
    for a in range(k+1):
        for b in range(a+1,k+1): s.add(c[a]!=c[b])
    return s
def col_int(k):
    s=z3.Solver(); c=[z3.Int(f"c{i}") for i in range(k+1)]
    for x in c: s.add(x>=0,x<k)
    for a in range(k+1):
        for b in range(a+1,k+1): s.add(c[a]!=c[b])
    return s
def col_noinfo(k):
    W=max(3,(k).bit_length()+1); s=z3.Solver(); c=[z3.BitVec(f"c{i}",W) for i in range(k+1)]
    for x in c: s.add(z3.ULT(x,k))
    return s
def fac_bv(N):
    W=2*N.bit_length()+2; s=z3.Solver(); x=z3.BitVec("x",W); y=z3.BitVec("y",W)
    s.add(z3.UGT(x,1), z3.UGT(y,1), z3.ULE(x,y), z3.BVMulNoOverflow(x,y,False))
    s.add(x*y==N, z3.ULE(x,int(N**0.5)+1), z3.ULE(y,N)); return s
def fac_int(N):
    s=z3.Solver(); x=z3.Int("x"); y=z3.Int("y")
    s.add(x>1,y>1,x<=y,x*y==N,x<=int(N**0.5)+1,y<=N); return s
def fac_noinfo(N):          # drop x>1 -> x=1,y=N is a model -> sat
    W=2*N.bit_length()+2; s=z3.Solver(); x=z3.BitVec("x",W); y=z3.BitVec("y",W)
    s.add(z3.UGT(y,1), z3.ULE(x,y), z3.BVMulNoOverflow(x,y,False))
    s.add(x*y==N, z3.ULE(y,N)); return s

FAM = {
 "pigeonhole": (php_bv, php_int, php_noinfo, [6,7,8,9,10,11]),
 "colouring":  (col_bv, col_int, col_noinfo, [6,7,8,9,10]),
 "factoring":  (fac_bv, fac_int, fac_noinfo, [65537,1000003,15485863,179424673]),
}

def run(b,p,ms):
    s=b(p); s.set("timeout",ms); t=time.time(); r=s.check(); dt=time.time()-t
    st={}
    try:
        for k,v in s.statistics(): st[k]=v
    except Exception: pass
    return {"verdict":str(r),"wall_s":round(dt,4),
            "conflicts":int(st.get("conflicts",0) or 0),
            "decisions":int(st.get("decisions",0) or 0),
            "propagations":int(st.get("propagations",0) or 0)}

def main():
    rows=[]; excluded=[]
    for fam,(ref,hard,noinfo,params) in FAM.items():
        for p in params:
            base=run(ref,p,BUDGET_MS)
            if base["verdict"]=="unknown":
                excluded.append({"family":fam,"param":p,"why":"reference did not solve"}); continue
            low=max(1,int(base["wall_s"]*1000*LOW_FRACTION))
            trio=[("INFORMATION",noinfo,BUDGET_MS),("ACCESSIBILITY",hard,BUDGET_MS),("COMPUTE",ref,low)]
            for truth,b,budget in trio:
                rec=run(b,p,budget); probe=run(b,p,budget)
                failed = (rec["verdict"]!=base["verdict"])
                if not failed:
                    excluded.append({"family":fam,"param":p,"truth":truth,
                                     "why":"injection did not change the verdict"}); continue
                rows.append({"family":fam,"param":p,"truth":truth,
                             "reference_verdict":base["verdict"],"reference_wall_s":base["wall_s"],
                             "low_budget_ms":low,**rec,
                             "probe_verdict":probe["verdict"],"probe_wall_s":probe["wall_s"]})
            print(f"  {fam} {p}: ref={base['verdict']}/{base['wall_s']:.2f}s low={low}ms "
                  f"kept={sum(1 for r in rows if r['family']==fam and r['param']==p)}",flush=True)

    rnd=random.Random(SPLIT_SEED); idx=list(range(len(rows))); rnd.shuffle(idx)
    h=len(idx)//2; dev=[rows[i] for i in idx[:h]]; held=[rows[i] for i in idx[h:]]
    acc=[r["conflicts"] for r in dev if r["truth"]=="ACCESSIBILITY"]
    cmp_=[r["conflicts"] for r in dev if r["truth"]=="COMPUTE"]
    thr=(statistics.median(acc)+statistics.median(cmp_))/2 if acc and cmp_ else 1.0

    A={"always_compute":lambda r:"COMPUTE",
       "verdict_only":lambda r:"INFORMATION" if r["verdict"]=="sat" else "COMPUTE",
       "resource_vector":lambda r:("INFORMATION" if r["verdict"]=="sat"
                                   else "ACCESSIBILITY" if r["conflicts"]>thr else "COMPUTE"),
       "oracle":lambda r:r["truth"]}
    out={"schema":"ORION19.SMT_FAILURE_DIAGNOSIS.v1","z3":z3.get_version_string(),
         "python":platform.python_version(),"budget_ms":BUDGET_MS,
         "low_fraction":LOW_FRACTION,"split_seed":SPLIT_SEED,
         "rows":rows,"excluded":excluded,"n_rows":len(rows),"n_excluded":len(excluded),
         "dev_n":len(dev),"held_n":len(held),
         "conflict_threshold_fitted_on_dev":thr,"arms":{}}
    for name,fn in A.items():
        preds=[(fn(r),r["truth"]) for r in held]
        acc_=sum(p==t for p,t in preds)/max(len(preds),1)
        nonc=[(p,t) for p,t in preds if t!="COMPUTE"]
        fce=sum(1 for p,t in nonc if p=="COMPUTE")/max(len(nonc),1)
        cm={}
        for p,t in preds: cm[f"{t}->{p}"]=cm.get(f"{t}->{p}",0)+1
        out["arms"][name]={"accuracy":round(acc_,4),"false_compute_escalation":round(fce,4),
                           "n_non_compute":len(nonc),"confusion":cm}
    R=out["arms"]
    truths={r["truth"] for r in held}
    if len(truths)<3 or len({r["verdict"] for r in rows})<2:
        term="CANNOT_CHECK_NO_SEPARATION"
    elif (R["resource_vector"]["false_compute_escalation"]<R["always_compute"]["false_compute_escalation"]
          and R["resource_vector"]["false_compute_escalation"]<R["verdict_only"]["false_compute_escalation"]
          and R["resource_vector"]["accuracy"]>=R["verdict_only"]["accuracy"]):
        term="RESOURCE_VECTOR_DIAGNOSIS_SUPPORTED"
    else: term="RESOURCE_VECTOR_DIAGNOSIS_NOT_SUPPORTED"
    out["terminal"]=term
    json.dump(out,open(os.path.expanduser("~/o19_RESULTS_HOSTILE09.json"),"w"),indent=1,sort_keys=True)
    print(f"\nrows {len(rows)}  excluded {len(excluded)}  dev {len(dev)} held {len(held)}")
    print(f"held-out truths: {sorted(truths)}   conflict threshold (dev): {thr:.1f}")
    print(f"{'arm':<18}{'accuracy':>10}{'false_compute_esc':>20}")
    for k,v in out["arms"].items():
        print(f"{k:<18}{v['accuracy']:>10.4f}{v['false_compute_escalation']:>20.4f}")
    print("TERMINAL:",term)

if __name__=="__main__": sys.exit(main())
