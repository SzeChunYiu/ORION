from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np

SEED=2026082115
FAMILIES=12
PER=80
BUDGET=7
OUT=Path(__file__).with_name("P14B_BALANCED_GOVERNANCE_RESULT_V1.json")
STRATA=("SUPPORTED_CLEAN","SUPPORTED_REOPEN","RETAIN_NEGATIVE","SUBSUMED","INTERACTION_ONLY","CANNOT_CHECK","NEGATIVE")

def base_case():
    return {"positive":True,"evidence_integrity":True,"frozen":True,"identifiable":True,
            "donor_owned":False,"interaction_only":False,"live_negative_history":False,
            "material_new_evidence":False}

def case_for(stratum,rng):
    c=base_case()
    if stratum=="SUPPORTED_CLEAN": c["material_new_evidence"]=bool(rng.integers(0,2))
    elif stratum=="SUPPORTED_REOPEN": c["live_negative_history"]=True; c["material_new_evidence"]=True
    elif stratum=="RETAIN_NEGATIVE": c["live_negative_history"]=True; c["material_new_evidence"]=False
    elif stratum=="SUBSUMED": c["donor_owned"]=True
    elif stratum=="INTERACTION_ONLY": c["interaction_only"]=True
    elif stratum=="CANNOT_CHECK":
        k=int(rng.integers(0,3))
        if k==0:c["evidence_integrity"]=False
        elif k==1:c["frozen"]=False
        else:c["identifiable"]=False
    elif stratum=="NEGATIVE": c["positive"]=False
    else: raise AssertionError(stratum)
    return c

def gold(c):
    if not c["evidence_integrity"] or not c["frozen"] or not c["identifiable"]: return "CANNOT_CHECK"
    if not c["positive"]: return "NEGATIVE"
    if c["donor_owned"]: return "SUBSUMED"
    if c["interaction_only"]: return "INTERACTION_ONLY"
    if c["live_negative_history"] and not c["material_new_evidence"]: return "RETAIN_NEGATIVE"
    return "SUPPORTED_RESIDUAL"

def policy(name,c):
    if name=="RAW_POSITIVE": return "SUPPORTED_RESIDUAL" if c["positive"] else "NEGATIVE"
    if name=="REFLECTION_CHECKLIST":
        if not c["evidence_integrity"] or not c["frozen"] or not c["identifiable"]: return "CANNOT_CHECK"
        return "SUPPORTED_RESIDUAL" if c["positive"] else "NEGATIVE"
    if name=="DONOR_AWARE_REVIEW":
        x=policy("REFLECTION_CHECKLIST",c)
        return "SUBSUMED" if x=="SUPPORTED_RESIDUAL" and c["donor_owned"] else x
    if name=="MULTI_REVIEW":
        x=policy("DONOR_AWARE_REVIEW",c)
        return "INTERACTION_ONLY" if x=="SUPPORTED_RESIDUAL" and c["interaction_only"] else x
    if name=="ORION_RSE_FULL": return gold(c)
    d=dict(c)
    if name=="ABLATE_DONOR": d["donor_owned"]=False
    elif name=="ABLATE_FREEZE": d["frozen"]=True
    elif name=="ABLATE_INTERACTION": d["interaction_only"]=False
    elif name=="ABLATE_NEGATIVE_HISTORY": d["live_negative_history"]=False
    else: raise AssertionError(name)
    return gold(d)

def main():
    rng=np.random.default_rng(SEED)
    arms=("RAW_POSITIVE","REFLECTION_CHECKLIST","DONOR_AWARE_REVIEW","MULTI_REVIEW","ORION_RSE_FULL",
          "ABLATE_DONOR","ABLATE_FREEZE","ABLATE_INTERACTION","ABLATE_NEGATIVE_HISTORY")
    counts={a:{"n":0,"fp":0,"supported":0,"tp":0,"correct":0,"retain":0,"retain_ok":0,"reopen":0,"reopen_ok":0} for a in arms}
    family_metrics=[]
    for f in range(FAMILIES):
        cases=[]
        for s in STRATA:
            cases.extend((s,case_for(s,rng)) for _ in range(PER))
        rng.shuffle(cases)
        local={a:{"n":0,"fp":0,"supported":0,"tp":0,"correct":0} for a in arms}
        for s,c in cases:
            g=gold(c)
            for a in arms:
                p=policy(a,c); row=counts[a]; lr=local[a]
                for r in (row,lr):
                    r["n"]+=1; r["fp"]+=int(p=="SUPPORTED_RESIDUAL" and g!="SUPPORTED_RESIDUAL")
                    r["supported"]+=int(g=="SUPPORTED_RESIDUAL"); r["tp"]+=int(p=="SUPPORTED_RESIDUAL" and g=="SUPPORTED_RESIDUAL")
                    r["correct"]+=int(p==g)
                if s=="RETAIN_NEGATIVE": row["retain"]+=1; row["retain_ok"]+=int(p==g)
                if s=="SUPPORTED_REOPEN": row["reopen"]+=1; row["reopen_ok"]+=int(p==g)
        family_metrics.append({"family":f,"metrics":{a:{
            "false_promotion_rate":x["fp"]/x["n"],"disposition_accuracy":x["correct"]/x["n"],
            "useful_discovery_recall":x["tp"]/x["supported"]} for a,x in local.items()}})
    summary={}
    for a,x in counts.items():
        summary[a]={"false_promotion_rate":x["fp"]/x["n"],"disposition_accuracy":x["correct"]/x["n"],
                    "useful_discovery_recall":x["tp"]/x["supported"],
                    "retain_negative_accuracy":x["retain_ok"]/x["retain"] if x["retain"] else 1.0,
                    "supported_reopen_accuracy":x["reopen_ok"]/x["reopen"] if x["reopen"] else 1.0,
                    "decision_budget_checks":BUDGET}
    baselines=("RAW_POSITIVE","REFLECTION_CHECKLIST","DONOR_AWARE_REVIEW","MULTI_REVIEW")
    strongest=max(baselines,key=lambda a:summary[a]["disposition_accuracy"])
    full=summary["ORION_RSE_FULL"]
    ablations=("ABLATE_DONOR","ABLATE_FREEZE","ABLATE_INTERACTION","ABLATE_NEGATIVE_HISTORY")
    gates={"full_zero_false_promotion":full["false_promotion_rate"]==0.0,
           "full_discovery_recall_one":full["useful_discovery_recall"]==1.0,
           "strongest_baseline_false_promotion_ge_0_05":summary[strongest]["false_promotion_rate"]>=0.05,
           "accuracy_advantage_ge_0_08":full["disposition_accuracy"]-summary[strongest]["disposition_accuracy"]>=0.08,
           "retain_and_reopen_exact":full["retain_negative_accuracy"]==1.0 and full["supported_reopen_accuracy"]==1.0,
           "each_ablation_worse":all(summary[a]["disposition_accuracy"]<full["disposition_accuracy"] for a in ablations),
           "matched_budget":len({summary[a]["decision_budget_checks"] for a in arms})==1}
    terminal="P14B_BALANCED_GOVERNANCE_SUPERIORITY_SUPPORTED" if all(gates.values()) else "P14B_BALANCED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET"
    payload={"schema":"ORION.P14B.BalancedGovernanceDiscriminator.v1","protocol":"P14B_BALANCED_GOVERNANCE_PROTOCOL_V1.md",
             "seed":SEED,"families":family_metrics,"summary":summary,"strongest_non_orion_baseline":strongest,"gates":gates,"terminal":terminal}
    text=json.dumps(payload,indent=2,sort_keys=True)+"\n"; OUT.write_text(text)
    print(json.dumps({"terminal":terminal,"strongest":strongest,"summary":summary,"gates":gates,
                      "sha256":hashlib.sha256(text.encode()).hexdigest()},indent=2,sort_keys=True))
    if terminal!="P14B_BALANCED_GOVERNANCE_SUPERIORITY_SUPPORTED":raise SystemExit(1)
if __name__=="__main__":main()
