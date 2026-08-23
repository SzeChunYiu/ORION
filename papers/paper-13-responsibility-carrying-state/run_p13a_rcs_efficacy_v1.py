from __future__ import annotations
import hashlib, itertools, json
from pathlib import Path
import numpy as np

SEED=2026082113
N_FAMILIES=24
N=512
RECOVER_P=0.95
CONF_T=0.80
OUT=Path(__file__).with_name("P13A_RCS_SAFETY_COST_RESULT_V1.json")
TASKS=("PREDICT","DECIDE","INTERVENE","VERIFY","REPAIR")
SUPPORT={
    "Z1":{"PREDICT","DECIDE"},
    "Z2":{"PREDICT","DECIDE","INTERVENE","VERIFY"},
    "Z3":set(TASKS),
}
COST={"REUSE":1.0,"REOPEN":6.0,"CANNOT_CHECK":0.5}


def truth(x,m,r,task):
    return {
        "PREDICT":x,"DECIDE":x,
        "INTERVENE":x*m,"VERIFY":x*m,
        "REPAIR":r,
    }[task]


def compact_pred(z,x,m,r,task,p_m,p_r):
    if task in SUPPORT[z]:
        return truth(x,m,r,task)
    map_m=1 if p_m>=0.5 else -1
    map_r=1 if p_r>=0.5 else -1
    if task in ("INTERVENE","VERIFY"):
        return x*map_m
    if task=="REPAIR":
        return map_r
    raise AssertionError(task)


def confidence(z,task,p_m,p_r):
    if task in SUPPORT[z]:
        return 1.0
    if task in ("INTERVENE","VERIFY"):
        return max(p_m,1-p_m)
    if task=="REPAIR":
        return max(p_r,1-p_r)
    return 1.0


def exact_matrix():
    support=list(itertools.product((-1,1),repeat=3))
    matrix={}
    for z in ("Z1","Z2","Z3"):
        if z=="Z1": key=lambda row:(row[0],)
        elif z=="Z2": key=lambda row:(row[0],row[1])
        else: key=lambda row:row
        matrix[z]={}
        for task in TASKS:
            groups={}
            for row in support:
                groups.setdefault(key(row),set()).add(truth(*row,task))
            matrix[z][task]=all(len(vals)==1 for vals in groups.values())
    return matrix


def action_for(arm,z,task,recover,p_m,p_r):
    supported=task in SUPPORT[z]
    if arm in ("UNQUALIFIED","PROVENANCE_ONLY"):
        return "REUSE"
    if arm=="CONFIDENCE_ONLY":
        if confidence(z,task,p_m,p_r)>=CONF_T:
            return "REUSE"
        return "REOPEN" if recover else "CANNOT_CHECK"
    if arm=="RCS":
        if supported:
            return "REUSE"
        return "REOPEN" if recover else "CANNOT_CHECK"
    if arm=="ALWAYS_RAW":
        return "REOPEN" if recover else "CANNOT_CHECK"
    raise AssertionError(arm)


def main():
    rng=np.random.default_rng(SEED)
    arms=("UNQUALIFIED","CONFIDENCE_ONLY","PROVENANCE_ONLY","RCS","ALWAYS_RAW")
    family_rows=[]
    aggregate={a:{"unsafe":0,"correct":0,"reopen_supported":0,"cost":0.0,"cannot_correct":0,"cannot_total":0} for a in arms}
    total=0
    unsupported_nonrecoverable=0
    for f in range(N_FAMILIES):
        p_m=float(rng.uniform(0.65,0.95)); p_r=float(rng.uniform(0.65,0.95))
        local={a:{k:0 for k in ("unsafe","correct","reopen_supported","cannot_correct","cannot_total")} | {"cost":0.0} for a in arms}
        for _ in range(N):
            x=int(rng.choice((-1,1)))
            m=1 if rng.random()<p_m else -1
            r=1 if rng.random()<p_r else -1
            z=str(rng.choice(("Z1","Z2")))
            task=str(rng.choice(TASKS))
            recover=bool(rng.random()<RECOVER_P)
            supported=task in SUPPORT[z]
            y=truth(x,m,r,task)
            if (not supported) and (not recover):
                unsupported_nonrecoverable+=1
            total+=1
            for arm in arms:
                a=action_for(arm,z,task,recover,p_m,p_r)
                if a=="REUSE":
                    pred=compact_pred(z,x,m,r,task,p_m,p_r)
                    local[arm]["correct"] += int(pred==y)
                    local[arm]["unsafe"] += int(not supported)
                elif a=="REOPEN":
                    local[arm]["correct"] += 1
                    local[arm]["reopen_supported"] += int(supported)
                else:
                    local[arm]["cannot_total"] += 1
                    local[arm]["cannot_correct"] += int((not supported) and (not recover))
                local[arm]["cost"] += COST[a]
        rates={}
        for arm in arms:
            row=local[arm]
            for k,v in row.items(): aggregate[arm][k]+=v
            rates[arm]={
                "unsafe_reuse_rate":row["unsafe"]/N,
                "verified_correct_rate":row["correct"]/N,
                "unnecessary_reopen_rate":row["reopen_supported"]/N,
                "mean_cost":row["cost"]/N,
                "correct_cannot_check_rate":(row["cannot_correct"]/row["cannot_total"] if row["cannot_total"] else 1.0),
            }
        family_rows.append({"family":f,"p_m":p_m,"p_r":p_r,"metrics":rates})

    summary={}
    for arm,row in aggregate.items():
        summary[arm]={
            "unsafe_reuse_rate":row["unsafe"]/total,
            "verified_correct_rate":row["correct"]/total,
            "unnecessary_reopen_rate":row["reopen_supported"]/total,
            "mean_cost":row["cost"]/total,
            "correct_cannot_check_rate":(row["cannot_correct"]/row["cannot_total"] if row["cannot_total"] else 1.0),
            "cannot_check_count":row["cannot_total"],
        }

    matrix=exact_matrix()
    expected={z:{t:(t in SUPPORT[z]) for t in TASKS} for z in SUPPORT}
    rcs=summary["RCS"]; conf=summary["CONFIDENCE_ONLY"]; prov=summary["PROVENANCE_ONLY"]; raw=summary["ALWAYS_RAW"]
    gates={
        "exact_responsibility_matrix":matrix==expected,
        "rcs_zero_unsafe_reuse":rcs["unsafe_reuse_rate"]==0.0,
        "confidence_unsafe_reuse_ge_0_10":conf["unsafe_reuse_rate"]>=0.10,
        "provenance_unsafe_reuse_ge_0_25":prov["unsafe_reuse_rate"]>=0.25,
        "rcs_correct_noninferior_0_01":rcs["verified_correct_rate"] >= conf["verified_correct_rate"]-0.01,
        "rcs_cost_at_least_30pct_below_always_raw":rcs["mean_cost"] <= 0.70*raw["mean_cost"],
        "rcs_zero_unnecessary_reopen":rcs["unnecessary_reopen_rate"]==0.0,
        "rcs_cannot_check_exact_for_unsupported_nonrecoverable":aggregate["RCS"]["cannot_correct"]==unsupported_nonrecoverable and aggregate["RCS"]["cannot_total"]==unsupported_nonrecoverable,
    }
    terminal="P13A_RCS_SAFETY_COST_SUPERIORITY_SUPPORTED" if all(gates.values()) else "P13A_RCS_SAFETY_COST_SUPERIORITY_GATE_NOT_MET"
    payload={
        "schema":"ORION.P13A.ResponsibilitySafeReuse.v1",
        "protocol":"P13A_INDEPENDENT_RCS_EFFICACY_PROTOCOL_V1.md",
        "seed":SEED,"families":family_rows,"summary":summary,
        "exact_matrix":matrix,"expected_matrix":expected,
        "unsupported_nonrecoverable_count":unsupported_nonrecoverable,
        "gates":gates,"terminal":terminal,
    }
    text=json.dumps(payload,indent=2,sort_keys=True)+"\n"
    OUT.write_text(text,encoding="utf-8")
    print(json.dumps({"terminal":terminal,"summary":summary,"gates":gates,"sha256":hashlib.sha256(text.encode()).hexdigest()},indent=2,sort_keys=True))
    if terminal!="P13A_RCS_SAFETY_COST_SUPERIORITY_SUPPORTED": raise SystemExit(1)

if __name__=="__main__": main()
