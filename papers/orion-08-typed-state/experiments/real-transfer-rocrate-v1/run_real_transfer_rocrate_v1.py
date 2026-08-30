#!/usr/bin/env python3
"""ORION-08 third family: RO-Crate workflow applicability. Protocol real-transfer-rocrate-v1."""
from __future__ import annotations
import json, os, random
from collections import defaultdict

U={(1,1):1.0,(1,0):-0.25,(0,1):-1.0,(0,0):0.0}
TH=0.25/2.25
MIN_MASS=1
DEGEN=0.5
SEED=20260830

d=json.load(open(os.path.expanduser("~/wh_records.json")))
recs=[r for r in d["records"] if "error" not in r]

def opt(v): return 1 if sum(v)/len(v)>TH else 0
def regret(by):
    tot=n=0
    for vs in by.values():
        a=opt(vs)
        for c in vs: tot+=U[(c,c)]-U[(a,c)]; n+=1
    return tot/n if n else 0.0

def band(n):
    return "0" if n==0 else ("1-2" if n<=2 else ("3-5" if n<=5 else "6+"))
rows=[(r["license"] or "NONE", r["workflow_class"] or "UNKNOWN",
       1 if r["internals_nonempty"] else 0, band(r.get("n_tags",0)))
      for r in recs]
rnd=random.Random(SEED); idx=list(range(len(rows))); rnd.shuffle(idx)
h=len(idx)//2; tr=[rows[i] for i in idx[:h]]; te=[rows[i] for i in idx[h:]]

co=defaultdict(list); re_=defaultdict(list); sub=defaultdict(lambda: defaultdict(list))
for lic,wc,y,_b in tr:
    co[lic].append(y); re_[(lic,wc)].append(y); sub[lic][(lic,wc)].append(y)

sing=sum(1 for v in re_.values() if len(v)==1); frac=sing/max(len(re_),1)

impure=[]
for cf,ss in sub.items():
    if len(co[cf])<MIN_MASS: continue
    acts={k:opt(v) for k,v in ss.items() if len(v)>=MIN_MASS}
    if len(set(acts.values()))>1:
        impure.append({"coarse_fibre":cf,"sub_actions":{str(k):v for k,v in acts.items()}})
predicted=len(impure)>0
r_co,r_re=regret(co),regret(re_)
observed=(r_co-r_re)>1e-12

# strata by workflow class: predict/observe within each class's records
strata={}
byclass=defaultdict(list)
for lic,wc,y,b in tr: byclass[b].append((lic,wc,y))
for wc,rs in byclass.items():
    if len(rs)<10: continue
    c2=defaultdict(list); r2=defaultdict(list); s2=defaultdict(lambda: defaultdict(list))
    for lic,w,y in rs: c2[lic].append(y); r2[(lic,w)].append(y); s2[lic][(lic,w)].append(y)
    pv=any(len({opt(v) for v in ss.values() if len(v)>=MIN_MASS})>1 for ss in s2.values())
    ov=(regret(c2)-regret(r2))>1e-12
    strata[wc]={"n":len(rs),"predicted_value":pv,"observed_value":ov,"agrees":pv==ov,
                "regret_coarse":round(regret(c2),6),"regret_refined":round(regret(r2),6)}

a_co={k:opt(v) for k,v in co.items()}; a_re={k:opt(v) for k,v in re_.items()}
g=opt([y for v in co.values() for y in v])
cot=defaultdict(list); ret=defaultdict(list)
for lic,wc,y,_b in te: cot[lic].append(y); ret[(lic,wc)].append(y)
def oos(by,acts,fb):
    tot=n=0
    for f,vs in by.items():
        a=acts.get(f,fb)
        for c in vs: tot+=U[(c,c)]-U[(a,c)]; n+=1
    return tot/n if n else 0.0
def arm_all(by):
    tot=n=0
    for vs in by.values():
        for c in vs: tot+=U[(c,c)]-U[(1,c)]; n+=1
    return tot/n if n else 0.0

out={"schema":"ORION08.REAL_TRANSFER_ROCRATE.v1","retrieved_utc":d["retrieved_utc"],
     "source":d["source"],"n_listed":d["n_listed"],"n_usable":len(recs),
     "utility":{str(k):v for k,v in U.items()},"threshold":round(TH,6),
     "split_seed":SEED,"train_n":len(tr),"test_n":len(te),
     "usable_rate_overall":round(sum(y for _,_,y,_b in rows)/max(len(rows),1),4),
     "coarse_fibres":len(co),"refined_fibres":len(re_),
     "refined_singleton_frac":round(frac,4),
     "predicted_value":predicted,"n_impure_coarse_fibres":len(impure),
     "impure_examples":impure[:3],
     "regret_coarse":round(r_co,6),"regret_refined":round(r_re,6),
     "observed_value":observed,"agrees":predicted==observed,
     "arms":{"coarse":round(r_co,6),"refined_typed":round(r_re,6),
             "attempt_all":round(arm_all(co),6),"oracle":0.0},
     "oos_regret_coarse":round(oos(cot,a_co,g),6),
     "oos_regret_refined":round(oos(ret,a_re,g),6),
     "strata":strata,"stratifier":"n_tags band (amendment 1)"}
val=[k for k,v in strata.items() if v["predicted_value"]]
nov=[k for k,v in strata.items() if not v["predicted_value"]]
dis=[k for k,v in strata.items() if not v["agrees"]]
out["strata_value"]=val; out["strata_no_value"]=nov; out["disagreements"]=dis
if frac>DEGEN: out["terminal"]="CANNOT_CHECK_DEGENERATE_BINDING"
elif not val or not nov: out["terminal"]="CANNOT_CHECK_NO_CONTRAST"
elif dis: out["terminal"]="THEOREM_FAILS_ON_REAL_DATA_ROCRATE"
else: out["terminal"]="THEOREM_PREDICTS_REAL_TRANSFER_ROCRATE"
json.dump(out,open(os.path.expanduser("~/roc_RESULTS_V1.json"),"w"),indent=1,sort_keys=True)

print(f"records usable {len(recs)}/{d['n_listed']}  usable-rate {out['usable_rate_overall']:.4f}")
print(f"coarse fibres {len(co)}  refined {len(re_)}  singleton frac {frac:.3f}")
print(f"regret coarse {r_co:.4f} -> refined {r_re:.4f}   attempt_all {out['arms']['attempt_all']:.4f}")
print(f"predicted value {predicted}  observed {observed}  agrees {predicted==observed}")
print(f"oos coarse {out['oos_regret_coarse']:.4f} -> refined {out['oos_regret_refined']:.4f}")
print(f"\n{'class':<14}{'n':>5}{'pred':>6}{'obs':>6}{'agree':>7}{'r_co':>9}{'r_re':>9}")
for k,v in sorted(strata.items(), key=lambda x:-x[1]['n']):
    print(f"{k:<14}{v['n']:>5}{str(v['predicted_value'])[0]:>6}{str(v['observed_value'])[0]:>6}"
          f"{str(v['agrees']):>7}{v['regret_coarse']:>9.4f}{v['regret_refined']:>9.4f}")
print(f"\nvalue strata: {val}\nno-value strata: {nov}\ndisagreements: {dis}")
print("TERMINAL:", out["terminal"])
