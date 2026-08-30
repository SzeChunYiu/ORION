#!/usr/bin/env python3
"""Does the frozen threshold's POSITION inside a project's fibre catch-rate range
predict whether typed state has value? Post-hoc mechanistic analysis of an
already-reported result; no parameter is fitted."""
from __future__ import annotations
import json, os, random
from collections import defaultdict
TH = 0.05/2.05
d = json.load(open(os.path.expanduser("~/d4j_data.json")))
def pkg(f): return ".".join(f.split(".")[:-1])
def nm(mods, t):
    ts = t.split(".")[-1]; s = {m.split(".")[-1] for m in mods}
    if any(ts == x+"Test" or ts == "Test"+x for x in s): return "exact"
    if any(x and x in ts for x in s): return "prefix"
    return "none"

print(f"{'proj':<12}{'|T|':>5}{'base_rate':>10}{'min_fib':>9}{'max_fib':>9}"
      f"  brackets_TH  observed_value  agree")
rows=[]
for proj, bugs in sorted(d.items()):
    ids=sorted(bugs); r=random.Random(20260830); sh=ids[:]; r.shuffle(sh)
    tr=sorted(sh[:len(sh)//2]); T=sorted({t for b in tr for t in bugs[b]["rels"]})
    if not T: continue
    co=defaultdict(list); sub=defaultdict(lambda: defaultdict(list))
    for b in tr:
        mods=bugs[b]["mods"]; trig=set(bugs[b]["trigs"])
        for t in T:
            c=1 if t in trig else 0
            cf=pkg(t); co[cf].append(c); sub[cf][nm(mods,t)].append(c)
    # value observed = some coarse fibre's sub-fibres take different optimal actions
    value=False
    for cf,ss in sub.items():
        acts={1 if sum(v)/len(v)>TH else 0 for v in ss.values()}
        if len(acts)>1: value=True; break
    rates=[sum(v)/len(v) for ss in sub.values() for v in ss.values()]
    lo,hi=min(rates),max(rates)
    brackets = lo <= TH <= hi
    base=sum(sum(v) for v in co.values())/sum(len(v) for v in co.values())
    rows.append((proj,len(T),base,lo,hi,brackets,value))
    print(f"{proj:<12}{len(T):>5}{base:>10.4f}{lo:>9.4f}{hi:>9.4f}"
          f"  {str(brackets):>11}  {str(value):>14}  {brackets==value}")
ag=sum(b==v for _,_,_,_,_,b,v in rows)
print(f"\nthreshold-bracketing predicts value on {ag}/{len(rows)} projects, no parameter fitted")
sm=[r for r in rows if not r[6]]; lg=[r for r in rows if r[6]]
print(f"no-value projects: |T| = {sorted(r[1] for r in sm)}")
print(f"value projects:    |T| = {sorted(r[1] for r in lg)}")
json.dump([{"project":p,"test_universe":n,"base_rate":round(b,6),
            "min_fibre_rate":round(l,6),"max_fibre_rate":round(h,6),
            "threshold":round(TH,6),"threshold_bracketed":br,"value_observed":v}
           for p,n,b,l,h,br,v in rows],
          open(os.path.expanduser("~/d4j_LAW_V1.json"),"w"), indent=1, sort_keys=True)
