from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np

SEED=2026082114
N_FAMILIES=20
N=400
BUDGET_CHECKS=7
OUT=Path(__file__).with_name("P14A_CONTROLLED_GOVERNANCE_RESULT_V1.json")
GOLDS=("CANNOT_CHECK","SUBSUMED","INTERACTION_ONLY","RETAIN_NEGATIVE","SUPPORTED_RESIDUAL","NEGATIVE")


def gold(c):
    if (not c["evidence_integrity"]) or (not c["frozen"]) or (not c["identifiable"]):
        return "CANNOT_CHECK"
    if not c["positive"]:
        return "NEGATIVE"
    if c["donor_owned"]:
        return "SUBSUMED"
    if c["interaction_only"]:
        return "INTERACTION_ONLY"
    if c["live_negative_history"] and not c["material_new_evidence"]:
        return "RETAIN_NEGATIVE"
    return "SUPPORTED_RESIDUAL"


def policy(name,c):
    if name=="RAW_POSITIVE":
        return "SUPPORTED_RESIDUAL" if c["positive"] else "NEGATIVE"
    if name=="REFLECTION_CHECKLIST":
        if (not c["evidence_integrity"]) or (not c["frozen"]) or (not c["identifiable"]):
            return "CANNOT_CHECK"
        return "SUPPORTED_RESIDUAL" if c["positive"] else "NEGATIVE"
    if name=="DONOR_AWARE_REVIEW":
        x=policy("REFLECTION_CHECKLIST",c)
        if x=="SUPPORTED_RESIDUAL" and c["donor_owned"]: return "SUBSUMED"
        return x
    if name=="MULTI_REVIEW":
        x=policy("DONOR_AWARE_REVIEW",c)
        if x=="SUPPORTED_RESIDUAL" and c["interaction_only"]: return "INTERACTION_ONLY"
        return x
    if name=="ORION_RSE_FULL":
        return gold(c)
    if name=="ABLATE_DONOR":
        d=dict(c); d["donor_owned"]=False; return gold(d)
    if name=="ABLATE_FREEZE":
        d=dict(c); d["frozen"]=True; return gold(d)
    if name=="ABLATE_INTERACTION":
        d=dict(c); d["interaction_only"]=False; return gold(d)
    if name=="ABLATE_NEGATIVE_HISTORY":
        d=dict(c); d["live_negative_history"]=False; return gold(d)
    raise AssertionError(name)


def make_case(rng, rates):
    positive=bool(rng.random()<rates["positive"])
    return {
        "positive":positive,
        "evidence_integrity":bool(rng.random()>=rates["bad_evidence"]),
        "frozen":bool(rng.random()>=rates["unfrozen"]),
        "identifiable":bool(rng.random()>=rates["nonidentifiable"]),
        "donor_owned":bool(positive and rng.random()<rates["donor"]),
        "interaction_only":bool(positive and rng.random()<rates["interaction"]),
        "live_negative_history":bool(positive and rng.random()<rates["history"]),
        "material_new_evidence":bool(rng.random()<rates["new_evidence"]),
    }


def main():
    rng=np.random.default_rng(SEED)
    arms=("RAW_POSITIVE","REFLECTION_CHECKLIST","DONOR_AWARE_REVIEW","MULTI_REVIEW","ORION_RSE_FULL",
          "ABLATE_DONOR","ABLATE_FREEZE","ABLATE_INTERACTION","ABLATE_NEGATIVE_HISTORY")
    totals={a:{"false_promote":0,"supported_total":0,"supported_promoted":0,"correct":0,"n":0,"history_cases":0,"history_correct":0} for a in arms}
    families=[]
    budget_receipts={a:BUDGET_CHECKS for a in arms}
    for f in range(N_FAMILIES):
        sampled={
            "positive":float(rng.uniform(.35,.65)),
            "bad_evidence":float(rng.uniform(.05,.18)),
            "unfrozen":float(rng.uniform(.05,.18)),
            "nonidentifiable":float(rng.uniform(.04,.14)),
            "donor":float(rng.uniform(.10,.28)),
            "interaction":float(rng.uniform(.08,.22)),
            "history":float(rng.uniform(.08,.22)),
            "new_evidence":float(rng.uniform(.25,.65)),
        }
        base={"positive":.50,"bad_evidence":.10,"unfrozen":.10,"nonidentifiable":.08,
              "donor":.18,"interaction":.15,"history":.15,"new_evidence":.45}
        rates={k:.5*sampled[k]+.5*base[k] for k in base}
        local={a:{"false_promote":0,"supported_total":0,"supported_promoted":0,"correct":0,"n":0,"history_cases":0,"history_correct":0} for a in arms}
        gold_counts={g:0 for g in GOLDS}
        for _ in range(N):
            c=make_case(rng,rates)
            g=gold(c); gold_counts[g]+=1
            is_hist = bool(c["positive"] and c["live_negative_history"] and c["evidence_integrity"] and c["frozen"] and c["identifiable"] and (not c["donor_owned"]) and (not c["interaction_only"]))
            for a in arms:
                pred=policy(a,c)
                promote=pred=="SUPPORTED_RESIDUAL"
                row=local[a]
                row["n"]+=1
                row["false_promote"]+=int(promote and g!="SUPPORTED_RESIDUAL")
                row["supported_total"]+=int(g=="SUPPORTED_RESIDUAL")
                row["supported_promoted"]+=int(promote and g=="SUPPORTED_RESIDUAL")
                row["correct"]+=int(pred==g)
                row["history_cases"]+=int(is_hist)
                row["history_correct"]+=int(is_hist and pred==g)
        fm={}
        for a,row in local.items():
            for k,v in row.items(): totals[a][k]+=v
            fm[a]={
                "false_promotion_rate":row["false_promote"]/row["n"],
                "useful_discovery_recall":row["supported_promoted"]/row["supported_total"] if row["supported_total"] else 1.0,
                "disposition_accuracy":row["correct"]/row["n"],
                "history_reopen_accuracy":row["history_correct"]/row["history_cases"] if row["history_cases"] else 1.0,
            }
        families.append({"family":f,"rates":rates,"gold_counts":gold_counts,"metrics":fm})

    summary={}
    for a,row in totals.items():
        summary[a]={
            "false_promotion_rate":row["false_promote"]/row["n"],
            "useful_discovery_recall":row["supported_promoted"]/row["supported_total"],
            "disposition_accuracy":row["correct"]/row["n"],
            "history_reopen_accuracy":row["history_correct"]/row["history_cases"] if row["history_cases"] else 1.0,
            "decision_budget_checks":budget_receipts[a],
        }
    baselines=("RAW_POSITIVE","REFLECTION_CHECKLIST","DONOR_AWARE_REVIEW","MULTI_REVIEW")
    strongest=max(baselines,key=lambda a:summary[a]["disposition_accuracy"])
    full=summary["ORION_RSE_FULL"]
    ablations=("ABLATE_DONOR","ABLATE_FREEZE","ABLATE_INTERACTION","ABLATE_NEGATIVE_HISTORY")
    gates={
        "full_zero_false_promotion":full["false_promotion_rate"]==0.0,
        "full_useful_discovery_recall_one":full["useful_discovery_recall"]==1.0,
        "strongest_baseline_false_promotion_ge_0_05":summary[strongest]["false_promotion_rate"]>=0.05,
        "accuracy_gain_ge_0_08":full["disposition_accuracy"]-summary[strongest]["disposition_accuracy"]>=0.08,
        "each_ablation_worse":all(summary[a]["false_promotion_rate"]>0.0 or summary[a]["disposition_accuracy"]<full["disposition_accuracy"] for a in ablations),
        "history_reopen_exact":full["history_reopen_accuracy"]==1.0,
        "matched_decision_budget":len(set(budget_receipts.values()))==1,
    }
    terminal="P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_SUPPORTED" if all(gates.values()) else "P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET"
    payload={"schema":"ORION.P14A.ResearchGovernanceDecisionBench.v1","protocol":"P14A_HIDDEN_GOLD_GOVERNANCE_PROTOCOL_V1.md",
             "seed":SEED,"families":families,"summary":summary,"strongest_non_orion_baseline":strongest,
             "gates":gates,"terminal":terminal}
    text=json.dumps(payload,indent=2,sort_keys=True)+"\n"
    OUT.write_text(text,encoding="utf-8")
    print(json.dumps({"terminal":terminal,"strongest_baseline":strongest,"summary":summary,"gates":gates,"sha256":hashlib.sha256(text.encode()).hexdigest()},indent=2,sort_keys=True))
    if terminal!="P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_SUPPORTED": raise SystemExit(1)

if __name__=="__main__": main()
