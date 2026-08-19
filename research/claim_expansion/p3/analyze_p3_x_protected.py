from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict

from research.claim_expansion.p3.generate_p3_x_dev_cases import generate
from research.claim_expansion.p3.p3_x_execution import p3_x, b1_strong_semantic_product, b2_canonical_match, b3_ideal_typed_product

BOOTSTRAP_REPS=20000
BOOTSTRAP_SEED=20260819

def q(xs,p):
    xs=sorted(xs); pos=(len(xs)-1)*p; lo=int(pos); hi=min(lo+1,len(xs)-1); w=pos-lo
    return xs[lo]*(1-w)+xs[hi]*w

def canonical_rows(cases):
    rows=[]
    for c in cases:
        gold=c["protected_gold"]["terminal"]
        dec={"P3_X":p3_x(c),"B1":b1_strong_semantic_product(c),"B2":b2_canonical_match(c),"B3":b3_ideal_typed_product(c)}
        rows.append({"case_id":c["case_id"],"domain":c["domain"],"archetype":c["archetype"],"gold":gold,"decisions":dec})
    return rows

def main_result():
    cases=generate(n_variants=10, authority="PROTECTED_V1")
    rows=canonical_rows(cases)
    counts={arm:sum(r["decisions"][arm]==r["gold"] for r in rows) for arm in ("P3_X","B1","B2","B3")}
    by_domain=defaultdict(list)
    for r in rows: by_domain[r["domain"]].append(r)
    diffs=[]; rng=random.Random(BOOTSTRAP_SEED)
    domains=sorted(by_domain)
    for _ in range(BOOTSTRAP_REPS):
        num=den=0
        for d in domains:
            rr=by_domain[d]
            for _ in range(len(rr)):
                r=rr[rng.randrange(len(rr))]
                num += int(r["decisions"]["P3_X"]==r["gold"])-int(r["decisions"]["B1"]==r["gold"])
                den += 1
        diffs.append(num/den)
    effect=(counts["P3_X"]-counts["B1"])/len(rows)
    discord_b=sum(r["decisions"]["P3_X"]==r["gold"] and r["decisions"]["B1"]!=r["gold"] for r in rows)
    discord_c=sum(r["decisions"]["P3_X"]!=r["gold"] and r["decisions"]["B1"]==r["gold"] for r in rows)
    false_glue=sum(r["decisions"]["P3_X"]=="GLUE" and r["gold"]!="GLUE" for r in rows)
    clean=[r for r in rows if r["archetype"]=="CLEAN_IDENTITY"]
    per_domain={d:(sum(r["decisions"]["P3_X"]==r["gold"] for r in rr)-sum(r["decisions"]["B1"]==r["gold"] for r in rr))/len(rr) for d,rr in by_domain.items()}
    canonical=json.dumps(rows,sort_keys=True,separators=(",",":"))
    return {
      "authority":"PROTECTED_RESULT_V1",
      "case_count":len(rows),
      "counts":counts,
      "p3_x_minus_b1":effect,
      "bootstrap_95":[q(diffs,.025),q(diffs,.975)],
      "mcnemar_discordance":{"b":discord_b,"c":discord_c},
      "p3_x_false_glue":false_glue,
      "p3_x_clean_glue_rate":sum(r["decisions"]["P3_X"]==r["gold"] for r in clean)/len(clean),
      "b3_decision_mismatches":sum(r["decisions"]["P3_X"]!=r["decisions"]["B3"] for r in rows),
      "per_domain_effect":per_domain,
      "canonical_rows_sha256":hashlib.sha256(canonical.encode()).hexdigest(),
    }

if __name__=="__main__": print(json.dumps(main_result(),sort_keys=True,indent=2))
