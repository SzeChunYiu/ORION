#!/usr/bin/env python3
"""Does candidate-set size predict whether the typed binding transfers out-of-sample?
Post-hoc analysis of the already-reported ORION-08 Defects4J result. No parameter fitted."""
from __future__ import annotations
import json, os, random
from collections import defaultdict
U={(1,1):1.0,(1,0):-0.05,(0,1):-1.0,(0,0):0.0}
TH=0.05/2.05; SEED=20260830
d=json.load(open(os.path.expanduser("~/d4j_data.json")))
def pkg(f): return ".".join(f.split(".")[:-1])
def nm(mods,t):
    ts=t.split(".")[-1]; s={m.split(".")[-1] for m in mods}
    if any(ts==x+"Test" or ts=="Test"+x for x in s): return "exact"
    if any(x and x in ts for x in s): return "prefix"
    return "none"
def opt(v): return 1 if sum(v)/len(v)>TH else 0

rows=[]
for proj,bugs in sorted(d.items()):
    ids=sorted(bugs); r=random.Random(SEED); sh=ids[:]; r.shuffle(sh)
    h=len(sh)//2; tr,te=sorted(sh[:h]),sorted(sh[h:])
    T=sorted({t for b in tr for t in bugs[b]["rels"]})
    if not T or not te: continue
    def build(bs):
        co,re_=defaultdict(list),defaultdict(list)
        for b in bs:
            mods,trig=bugs[b]["mods"],set(bugs[b]["trigs"])
            for t in T:
                c=1 if t in trig else 0
                cf=pkg(t); co[cf].append(c); re_[(cf,nm(mods,t))].append(c)
        return co,re_
    co,re_=build(tr); cot,ret=build(te)
    a_co={k:opt(v) for k,v in co.items()}; a_re={k:opt(v) for k,v in re_.items()}
    g=opt([c for v in co.values() for c in v])
    def reg(rows_by,acts,fb):
        tot=n=0
        for f,vs in rows_by.items():
            a=acts.get(f,fb)
            for c in vs: tot+=U[(c,c)]-U[(a,c)]; n+=1
        return tot/n if n else 0.0
    oos_co,oos_re=reg(cot,a_co,g),reg(ret,a_re,g)
    # coverage: fraction of held-out rows whose refined fibre was seen in training
    seen=sum(len(v) for f,v in ret.items() if f in a_re); tot=sum(len(v) for v in ret.values())
    base=sum(sum(v) for v in co.values())/sum(len(v) for v in co.values())
    rows.append({"project":proj,"test_universe":len(T),"bugs_train":len(tr),"bugs_test":len(te),
                 "base_catch_rate":round(base,6),
                 "oos_regret_coarse":round(oos_co,6),"oos_regret_refined":round(oos_re,6),
                 "oos_refinement_helps":(oos_co-oos_re)>1e-12,
                 "refined_fibre_coverage":round(seen/tot,4) if tot else None,
                 "n_refined_fibres_train":len(a_re)})
print(f"{'project':<12}{'|T|':>5}{'base':>9}{'cover':>7}{'oos_co':>9}{'oos_re':>9}  helps")
for r in sorted(rows,key=lambda x:x["test_universe"]):
    print(f"{r['project']:<12}{r['test_universe']:>5}{r['base_catch_rate']:>9.4f}"
          f"{r['refined_fibre_coverage']:>7.3f}{r['oos_regret_coarse']:>9.4f}"
          f"{r['oos_regret_refined']:>9.4f}  {r['oos_refinement_helps']}")
helps=[r for r in rows if r["oos_refinement_helps"]]; fails=[r for r in rows if not r["oos_refinement_helps"]]
print(f"\nhelps out-of-sample: {len(helps)}/{len(rows)}")
print(f"  |T| where it helps : {sorted(r['test_universe'] for r in helps)}")
print(f"  |T| where it fails : {sorted(r['test_universe'] for r in fails)}")
if helps and fails:
    mh=min(r["test_universe"] for r in helps); Mf=max(r["test_universe"] for r in fails)
    print(f"  smallest helping |T| = {mh}; largest failing |T| = {Mf}; "
          f"separable by size: {Mf < mh}")
    print(f"  coverage where it helps: {sorted(round(r['refined_fibre_coverage'],3) for r in helps)}")
    print(f"  coverage where it fails: {sorted(round(r['refined_fibre_coverage'],3) for r in fails)}")
json.dump(rows,open(os.path.expanduser("~/d4j_OOS_V1.json"),"w"),indent=1,sort_keys=True)
