#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PAPERS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PAPERS / "publication_closure"))
from tier_a_analysis_common_v1 import bootstrap_mean_interval, mean  # noqa: E402

ARMS=("ADAPTIVE","ONE_SIGNAL_STATE","ONE_SIGNAL_REASON")
ONE_SIGNAL=("ONE_SIGNAL_STATE","ONE_SIGNAL_REASON")

def validate_family(r:dict[str,Any], model_set:set[str])->None:
    for k in ("family_id","domain"):
        if not isinstance(r.get(k),str) or not r[k]: raise ValueError(f"{k} missing")
    scores=r.get("scores_by_model")
    oracle=r.get("hindsight_oracle_by_model")
    if not isinstance(scores,dict) or set(scores)!=model_set: raise ValueError("family scores do not use exact frozen model set")
    if not isinstance(oracle,dict) or set(oracle)!=model_set: raise ValueError("oracle scores do not use exact frozen model set")
    for mid in model_set:
        arm_scores=scores[mid]
        if not isinstance(arm_scores,dict) or set(arm_scores)!=set(ARMS): raise ValueError("model arm scores incomplete")
        for v in list(arm_scores.values())+[oracle[mid]]:
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(float(v)): raise ValueError("scores must be finite numeric")
        if float(oracle[mid])+1e-12 < float(arm_scores["ADAPTIVE"]): raise ValueError("hindsight oracle below adaptive score")

def analyze(p:dict[str,Any],resamples:int=10000)->dict[str,Any]:
    if p.get("schema")!="ORION.A2.P12StopGoResultInput.v1": raise ValueError("wrong schema")
    if p.get("protected_outcomes_unsealed") is not True: raise ValueError("result analyzer requires explicit post-run unseal flag")
    selected=p.get("selected_one_signal_arm")
    if selected not in ONE_SIGNAL: raise ValueError("selected one-signal arm invalid/unfrozen")
    if p.get("one_signal_selected_before_protected_evaluation") is not True: raise ValueError("one-signal comparator was not selected before protected evaluation")
    models=p.get("model_family_ids")
    if not isinstance(models,list) or len(models)<2 or len(set(models))!=len(models) or not all(isinstance(x,str) and x for x in models): raise ValueError("need >=2 unique frozen model-family ids")
    model_set=set(models)
    rows=p.get("families")
    if not isinstance(rows,list): raise ValueError("families must be list")
    seen=set(); domains=Counter(); family_gain=[]; max_regret=0.0; by_domain=defaultdict(list)
    for r in rows:
        if not isinstance(r,dict): raise ValueError("family must be object")
        validate_family(r,model_set)
        fid=r["family_id"]
        if fid in seen: raise ValueError(f"duplicate family: {fid}")
        seen.add(fid); domains[r["domain"]]+=1
        adaptive=mean(float(r["scores_by_model"][m]["ADAPTIVE"]) for m in models)
        comp=mean(float(r["scores_by_model"][m][selected]) for m in models)
        gain=adaptive-comp; family_gain.append(gain); by_domain[r["domain"]].append(gain)
        for m in models:
            regret=float(r["hindsight_oracle_by_model"][m])-float(r["scores_by_model"][m]["ADAPTIVE"])
            max_regret=max(max_regret,regret)
    D=len(domains); scope_ok=len(rows)>=20 and D>=3 and len(models)>=2
    if not rows:
        lo=hi=avg=0.0
    else:
        avg=mean(family_gain); lo,hi=bootstrap_mean_interval(family_gain,"A2|P12|family-gain",resamples)
    domain_direction={d:mean(v) for d,v in sorted(by_domain.items())}
    required_positive=math.ceil(2*D/3) if D else 0
    positive_domains=sum(v>0 for v in domain_direction.values())
    loo={}
    for held in sorted(by_domain):
        kept=[g for d,vals in by_domain.items() if d!=held for g in vals]
        loo[held]=mean(kept) if kept else 0.0
    if not scope_ok:
        terminal="CANNOT_CHECK_SCOPE_OR_BINDING"
    elif avg<3.0:
        terminal="NOT_SUPPORTED_GAIN_LT_3"
    elif lo<=0:
        terminal="NOT_SUPPORTED_BOOTSTRAP"
    elif positive_domains<required_positive:
        terminal="HETEROGENEOUS_DOMAIN_FAILURE"
    elif any(v<=0 for v in loo.values()):
        terminal="LEAVE_ONE_DOMAIN_OUT_FAILURE"
    elif max_regret>2.0+1e-12:
        terminal="NOT_SUPPORTED_MAX_REGRET"
    else:
        terminal="SUPPORTED_FROZEN_P12_STOPGO_GATE"
    return {"schema":"ORION.A2.P12StopGoFinalAnalysisResult.v1","selected_one_signal_arm":selected,"task_families":len(rows),"domains":D,"model_families":len(models),"scope_ok":scope_ok,"mean_family_gain_normalized_points":avg,"family_gain_ci95":[lo,hi],"domain_direction":domain_direction,"positive_domains":positive_domains,"required_positive_domains":required_positive,"leave_one_domain_out_direction":loo,"maximum_hindsight_regret":max_regret,"terminal":terminal}

def fixture()->dict[str,Any]:
    models=["model-a","model-b"]; rows=[]
    for d in range(3):
        for i in range(7):
            scores={m:{"ADAPTIVE":10.0,"ONE_SIGNAL_STATE":6.0,"ONE_SIGNAL_REASON":5.0} for m in models}
            rows.append({"family_id":f"d{d}-f{i}","domain":f"domain-{d}","scores_by_model":scores,"hindsight_oracle_by_model":{m:11.0 for m in models}})
    return {"schema":"ORION.A2.P12StopGoResultInput.v1","protected_outcomes_unsealed":True,"selected_one_signal_arm":"ONE_SIGNAL_STATE","one_signal_selected_before_protected_evaluation":True,"model_family_ids":models,"families":rows}
def self_test()->dict[str,Any]:
    good=analyze(fixture(),128); assert good["terminal"]=="SUPPORTED_FROZEN_P12_STOPGO_GATE"
    bad=fixture();
    for r in bad["families"]: r["scores_by_model"]["model-a"]["ADAPTIVE"]=8.0; r["scores_by_model"]["model-b"]["ADAPTIVE"]=8.0
    fail=analyze(bad,64); assert fail["terminal"]=="NOT_SUPPORTED_GAIN_LT_3"
    bad2=fixture(); bad2["one_signal_selected_before_protected_evaluation"]=False
    try: analyze(bad2,16)
    except ValueError as e: assert "before protected" in str(e)
    else: raise AssertionError("post-outcome comparator selection accepted")
    return {"decision":"GREEN","positive_terminal":good["terminal"],"negative_terminal":fail["terminal"]}
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",type=Path); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    if a.self_test: print(json.dumps(self_test(),indent=2,sort_keys=True)); return 0
    if a.input is None: ap.error("input required unless --self-test")
    print(json.dumps(analyze(json.loads(a.input.read_text())),indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
