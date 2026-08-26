from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np

SEED = 2026082112
N_FAMILIES = 16
N_PER_FAMILY = 512
BUDGET = 2
BOOT = 20000
OUT = Path(__file__).with_name("P12A_MATCHED_BUDGET_RESULT_V1.json")
REGIMES = ("EASY","ACCESS","REASON","BOTH")
REQ = {"EASY":(0,0),"ACCESS":(2,0),"REASON":(0,2),"BOTH":(1,1)}
JOINT_OPTIONS = ((0,0),(1,1),(2,0),(0,2))


def success(alloc, req):
    return int(alloc[0] >= req[0] and alloc[1] >= req[1])


def joint_alloc(sc, sr):
    distances = [((sc-c)**2 + (sr-r)**2, i, (c,r)) for i,(c,r) in enumerate(JOINT_OPTIONS)]
    return min(distances)[2]


def main():
    rng=np.random.default_rng(SEED)
    families=[]
    budget_violations=0
    for f in range(N_FAMILIES):
        sigma=float(rng.uniform(0.30,0.80))
        raw=rng.dirichlet(np.ones(4))
        probs=0.5*raw + 0.5*np.ones(4)/4.0
        labels=rng.choice(4,size=N_PER_FAMILY,p=probs)
        rows={k:[] for k in ("FIXED_11","ADAPTIVE_STATE_ONLY","ADAPTIVE_REASON_ONLY","JOINT_FROZEN","ORACLE_JOINT")}
        regime_counts={k:0 for k in REGIMES}
        for idx in labels:
            reg=REGIMES[int(idx)]
            regime_counts[reg]+=1
            req=REQ[reg]
            sc=float(req[0] + rng.normal(0,sigma))
            sr=float(req[1] + rng.normal(0,sigma))
            allocations={
                "FIXED_11":(1,1),
                "ADAPTIVE_STATE_ONLY":(2,0) if sc>=1.0 else (0,0),
                "ADAPTIVE_REASON_ONLY":(0,2) if sr>=1.0 else (0,0),
                "JOINT_FROZEN":joint_alloc(sc,sr),
                "ORACLE_JOINT":req,
            }
            for arm,a in allocations.items():
                if a[0]+a[1] > BUDGET:
                    budget_violations += 1
                rows[arm].append(success(a,req))
        rates={arm:float(np.mean(v)) for arm,v in rows.items()}
        best_one=max(rates["ADAPTIVE_STATE_ONLY"],rates["ADAPTIVE_REASON_ONLY"])
        families.append({
            "family":f,
            "sigma":sigma,
            "regime_probs":[float(x) for x in probs],
            "regime_counts":regime_counts,
            "success_rate":rates,
            "joint_gain_vs_best_one_axis":rates["JOINT_FROZEN"]-best_one,
            "joint_gain_vs_fixed_11":rates["JOINT_FROZEN"]-rates["FIXED_11"],
        })

    gains=np.array([x["joint_gain_vs_best_one_axis"] for x in families])
    fixed_gains=np.array([x["joint_gain_vs_fixed_11"] for x in families])
    brng=np.random.default_rng(SEED+991)
    boot=np.empty(BOOT)
    for i in range(BOOT):
        boot[i]=np.mean(gains[brng.integers(0,N_FAMILIES,size=N_FAMILIES)])
    ci=[float(np.quantile(boot,0.025)),float(np.quantile(boot,0.975))]
    gates={
        "budget_respected":budget_violations==0,
        "signals_pre_outcome_by_construction":True,
        "mean_joint_gain_ge_0_15":float(np.mean(gains))>=0.15,
        "family_bootstrap_lower_gt_0":ci[0]>0.0,
        "mean_joint_minus_fixed_ge_0_10":float(np.mean(fixed_gains))>=0.10,
        "worst_family_joint_gain_ge_0_05":float(np.min(gains))>=0.05,
        "oracle_ceiling_holds":all(x["success_rate"]["ORACLE_JOINT"]+1e-12 >= x["success_rate"]["JOINT_FROZEN"] for x in families),
    }
    terminal="P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED" if all(gates.values()) else "P12A_JOINT_ALLOCATION_SUPERIORITY_GATE_NOT_MET"
    payload={
        "schema":"ORION.P12A.MatchedBudgetAllocation.v1",
        "protocol":"P12A_MATCHED_BUDGET_JOINT_ALLOCATION_PROTOCOL_V1.md",
        "seed":SEED,
        "n_families":N_FAMILIES,
        "n_per_family":N_PER_FAMILY,
        "budget":BUDGET,
        "families":families,
        "summary":{
            "mean_joint_success":float(np.mean([x["success_rate"]["JOINT_FROZEN"] for x in families])),
            "mean_state_only_success":float(np.mean([x["success_rate"]["ADAPTIVE_STATE_ONLY"] for x in families])),
            "mean_reason_only_success":float(np.mean([x["success_rate"]["ADAPTIVE_REASON_ONLY"] for x in families])),
            "mean_fixed_11_success":float(np.mean([x["success_rate"]["FIXED_11"] for x in families])),
            "mean_joint_gain_vs_best_one_axis":float(np.mean(gains)),
            "family_bootstrap_95ci_joint_gain":[*ci],
            "worst_family_joint_gain":float(np.min(gains)),
            "mean_joint_gain_vs_fixed_11":float(np.mean(fixed_gains)),
        },
        "gates":gates,
        "terminal":terminal,
    }
    text=json.dumps(payload,indent=2,sort_keys=True)+"\n"
    OUT.write_text(text,encoding="utf-8")
    print(json.dumps({"terminal":terminal,"summary":payload["summary"],"gates":gates,"sha256":hashlib.sha256(text.encode()).hexdigest()},indent=2,sort_keys=True))
    if terminal != "P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED":
        raise SystemExit(1)

if __name__=="__main__":
    main()
