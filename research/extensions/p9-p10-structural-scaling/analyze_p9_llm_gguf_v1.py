from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

PRIMARY_BUDGET = 32
BOOTSTRAP_SEED = 914031
BOOTSTRAP_DRAWS = 10000
TARGETS = (0.50, 0.70, 0.85)


def q(values: list[float], p: float) -> float:
    values = sorted(values)
    pos = (len(values)-1)*p
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi: return values[lo]
    w = pos-lo
    return values[lo]*(1-w)+values[hi]*w


def acc(rows: list[dict[str, Any]]) -> float:
    return sum(bool(r["correct"]) for r in rows)/len(rows)


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--inputs",nargs=3,required=True); ap.add_argument("--output",required=True); a=ap.parse_args()
    runs=[json.loads(Path(p).read_text()) for p in a.inputs]
    runs=sorted(runs,key=lambda d:int(d["model_parameter_count"]))
    if [r["model_scale"] for r in runs] != ["0.5B","1.5B","3B"]: raise SystemExit("model family/scale mismatch")
    manifests={r["item_manifest_sha256"] for r in runs}; prompts={r["prompt_sha256"] for r in runs}
    if len(manifests)!=1 or len(prompts)!=1 or any(r["equivalence_failures"]!=0 for r in runs): raise SystemExit("identity/equivalence mismatch")

    cells=[]; by_key={}
    for run in runs:
        grouped=defaultdict(list)
        for row in run["records"]: grouped[(row["representation"],int(row["budget"]))].append(row)
        for rep in ("R1_SAME_INFO","R2_TYPED_STATE"):
            for budget in (8,32,96):
                rows=grouped[(rep,budget)]
                if len(rows)!=192: raise SystemExit("incomplete cell")
                cell={"model_scale":run["model_scale"],"params":run["model_parameter_count"],"representation":rep,"budget":budget,"accuracy":acc(rows)}
                cells.append(cell); by_key[(run["model_scale"],rep,budget)]=cell

    effects=[]
    for run in runs:
        scale=run["model_scale"]
        a1=by_key[(scale,"R1_SAME_INFO",PRIMARY_BUDGET)]["accuracy"]
        a2=by_key[(scale,"R2_TYPED_STATE",PRIMARY_BUDGET)]["accuracy"]
        effects.append({"model_scale":scale,"R1":a1,"R2":a2,"delta":a2-a1})

    largest=runs[-1]
    per_domain={}
    for domain in sorted({r["domain"] for r in largest["records"]}):
        vals={}
        for rep in ("R1_SAME_INFO","R2_TYPED_STATE"):
            rows=[x for x in largest["records"] if x["domain"]==domain and x["representation"]==rep and int(x["budget"])==PRIMARY_BUDGET]
            vals[rep]=acc(rows)
        per_domain[domain]=vals["R2_TYPED_STATE"]-vals["R1_SAME_INFO"]
    domains=sorted(per_domain)
    rng=random.Random(BOOTSTRAP_SEED); boots=[]
    for _ in range(BOOTSTRAP_DRAWS):
        draw=[rng.choice(domains) for _ in domains]
        boots.append(sum(per_domain[d] for d in draw)/len(draw))
    ci=[q(boots,0.025),q(boots,0.975)]

    substitutions=[]
    for target in TARGETS:
        for budget in (8,32,96):
            for i,small in enumerate(runs[:-1]):
                for large in runs[i+1:]:
                    s=by_key[(small["model_scale"],"R2_TYPED_STATE",budget)]["accuracy"]
                    l=by_key[(large["model_scale"],"R1_SAME_INFO",budget)]["accuracy"]
                    if s>=target and l>=target and s>=l:
                        substitutions.append({"target":target,"budget":budget,"smaller_structured":small["model_scale"],"smaller_structured_accuracy":s,"larger_same_info":large["model_scale"],"larger_same_info_accuracy":l})

    compute_sub=[]
    for run in runs:
        scale=run["model_scale"]
        for target in TARGETS:
            r1=next((b for b in (8,32,96) if by_key[(scale,"R1_SAME_INFO",b)]["accuracy"]>=target),None)
            r2=next((b for b in (8,32,96) if by_key[(scale,"R2_TYPED_STATE",b)]["accuracy"]>=target),None)
            if r1 is not None and r2 is not None and r2<r1: compute_sub.append({"model_scale":scale,"target":target,"R1_budget":r1,"R2_budget":r2})

    primary_checks={
        "positive_delta_every_size": all(e["delta"]>0 for e in effects),
        "largest_domain_bootstrap_lower_gt_zero": ci[0]>0,
        "largest_nonnegative_domain_fraction_ge_0_60": sum(v>=0 for v in per_domain.values())/len(per_domain)>=0.60,
        "observed_smaller_structured_substitution_exists": bool(substitutions),
        "equivalence_green": True,
    }
    terminal="LLM_STRUCTURE_SCALING_FRONTIER_SUPPORTED" if all(primary_checks.values()) else "LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED"
    out={"schema":"P9.LLMGGUFScalingAnalysis.v1","primary_budget":PRIMARY_BUDGET,"effects":effects,"largest_model_domain_deltas":per_domain,"domain_block_bootstrap_95pct":ci,"substitutions":substitutions,"compute_substitutions":compute_sub,"cells":cells,"checks":primary_checks,"terminal":terminal,"claim_boundary":"Exact Qwen2.5 Q4_K_M three-size family only; no full-precision or cross-family generalization."}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
