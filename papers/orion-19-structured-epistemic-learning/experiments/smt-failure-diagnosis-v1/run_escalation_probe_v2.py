#!/usr/bin/env python3
"""ORION-19 V2: budget-escalation probe. Protocol PROTOCOL_V2_ESCALATION_PROBE."""
from __future__ import annotations
import json, os, platform, sys, time
import z3

BUDGET_MS=5000; LOW_FRACTION=0.2; ESCALATION=2.0
V1_THRESHOLD=37361.25          # reused unchanged from V1's development half

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
    s.add(z3.UGT(x,1),z3.UGT(y,1),z3.ULE(x,y),z3.BVMulNoOverflow(x,y,False))
    s.add(x*y==N,z3.ULE(x,int(N**0.5)+1),z3.ULE(y,N)); return s
def fac_int(N):
    s=z3.Solver(); x=z3.Int("x"); y=z3.Int("y")
    s.add(x>1,y>1,x<=y,x*y==N,x<=int(N**0.5)+1,y<=N); return s
def fac_noinfo(N):
    W=2*N.bit_length()+2; s=z3.Solver(); x=z3.BitVec("x",W); y=z3.BitVec("y",W)
    s.add(z3.UGT(y,1),z3.ULE(x,y),z3.BVMulNoOverflow(x,y,False))
    s.add(x*y==N,z3.ULE(y,N)); return s

FAM={"pigeonhole":(php_bv,php_int,php_noinfo,[6,7,8,9,10,11]),
     "colouring":(col_bv,col_int,col_noinfo,[6,7,8,9,10]),
     "factoring":(fac_bv,fac_int,fac_noinfo,[65537,1000003,15485863,179424673])}

def run(b,p,ms):
    s=b(p); s.set("timeout",ms); t=time.time(); r=s.check(); dt=time.time()-t
    st={}
    try:
        for k,v in s.statistics(): st[k]=v
    except Exception: pass
    return {"verdict":str(r),"wall_s":round(dt,4),"conflicts":int(st.get("conflicts",0) or 0)}

def main():
    rows=[]; excluded=[]
    for fam,(ref,hard,noinfo,params) in FAM.items():
        for p in params:
            base=run(ref,p,BUDGET_MS)
            if base["verdict"]=="unknown":
                excluded.append({"family":fam,"param":p,"why":"reference did not solve"}); continue
            low=max(1,int(base["wall_s"]*1000*LOW_FRACTION))
            for truth,b,budget in (("INFORMATION",noinfo,BUDGET_MS),
                                   ("ACCESSIBILITY",hard,BUDGET_MS),
                                   ("COMPUTE",ref,low)):
                rec=run(b,p,budget)
                if rec["verdict"]==base["verdict"]:
                    excluded.append({"family":fam,"param":p,"truth":truth,
                                     "why":"injection did not change the verdict"}); continue
                esc=run(b,p,int(budget*ESCALATION))       # the V2 probe
                rows.append({"family":fam,"param":p,"truth":truth,
                             "reference_verdict":base["verdict"],"budget_ms":budget,
                             **rec,"escalated_budget_ms":int(budget*ESCALATION),
                             "escalated_verdict":esc["verdict"],"escalated_wall_s":esc["wall_s"]})
            print(f"  {fam} {p}: kept={sum(1 for r in rows if r['family']==fam and r['param']==p)}",flush=True)

    def always(r): return "COMPUTE"
    def verdict(r): return "INFORMATION" if r["verdict"]=="sat" else "COMPUTE"
    def vector(r):
        if r["verdict"]=="sat": return "INFORMATION"
        return "ACCESSIBILITY" if r["conflicts"]>V1_THRESHOLD else "COMPUTE"
    def escalate(r):
        if r["verdict"]=="sat": return "INFORMATION"
        return "COMPUTE" if r["escalated_verdict"]!="unknown" else "ACCESSIBILITY"
    COST={"always_compute":lambda r:0.0,"verdict_only":lambda r:0.0,
          "resource_vector":lambda r:0.0,"escalation_probe":lambda r:r["escalated_wall_s"],
          "oracle":lambda r:0.0}
    ARMS={"always_compute":always,"verdict_only":verdict,"resource_vector":vector,
          "escalation_probe":escalate,"oracle":lambda r:r["truth"]}

    out={"schema":"ORION19.SMT_FAILURE_DIAGNOSIS.v2","z3":z3.get_version_string(),
         "python":platform.python_version(),"budget_ms":BUDGET_MS,
         "escalation_factor":ESCALATION,"v1_threshold_reused":V1_THRESHOLD,
         "scored_on":"all instances (no split; see protocol)",
         "n_rows":len(rows),"n_excluded":len(excluded),"rows":rows,"excluded":excluded,"arms":{}}
    for name,fn in ARMS.items():
        preds=[(fn(r),r["truth"]) for r in rows]
        acc=sum(a==b for a,b in preds)/max(len(preds),1)
        nc=[(a,b) for a,b in preds if b!="COMPUTE"]
        fce=sum(1 for a,b in nc if a=="COMPUTE")/max(len(nc),1)
        cm={}
        for a,b in preds: cm[f"{b}->{a}"]=cm.get(f"{b}->{a}",0)+1
        fac=[(fn(r),r["truth"]) for r in rows if r["family"]=="factoring"]
        facacc=sum(a==b for a,b in fac)/max(len(fac),1)
        out["arms"][name]={"accuracy":round(acc,4),"false_compute_escalation":round(fce,4),
                           "factoring_accuracy":round(facacc,4),
                           "decision_solver_seconds":round(sum(COST[name](r) for r in rows),2),
                           "confusion":cm}
    A=out["arms"]
    resolved=sum(1 for r in rows if r["escalated_verdict"]!="unknown")
    if resolved==0: term="CANNOT_CHECK_NO_SEPARATION"
    elif (A["escalation_probe"]["false_compute_escalation"]<A["resource_vector"]["false_compute_escalation"]
          and A["escalation_probe"]["factoring_accuracy"]>=A["resource_vector"]["factoring_accuracy"]):
        term="ESCALATION_PROBE_SUPPORTED"
    else: term="ESCALATION_PROBE_NOT_SUPPORTED"
    out["terminal"]=term; out["escalation_resolved_n"]=resolved
    json.dump(out,open(os.path.expanduser("~/o19_V2_RESULTS.json"),"w"),indent=1,sort_keys=True)
    print(f"\nrows {len(rows)} excluded {len(excluded)}; doubling resolved {resolved}/{len(rows)}")
    print(f"{'arm':<19}{'acc':>8}{'FCE':>9}{'factoring':>11}{'decide_s':>10}")
    for k,v in out["arms"].items():
        print(f"{k:<19}{v['accuracy']:>8.4f}{v['false_compute_escalation']:>9.4f}"
              f"{v['factoring_accuracy']:>11.4f}{v['decision_solver_seconds']:>10.2f}")
    print("TERMINAL:",term)

if __name__=="__main__": sys.exit(main())
