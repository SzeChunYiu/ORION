#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-22.

No imports from QG-7/QG-22 analyzers. Rebuilds phase-free Pauli/F3 semantics,
feature partitions, the full subset lattice, and the 4096-state composition.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "artifacts/orion-qg-qg22-hidden-home-state.json"
DEFAULT_OUTPUT = ROOT / "artifacts/orion-qg-qg22-generic-verification.json"
TOKEN = "ORIONQG_QG22_GENERIC="
POSITIVE = "QG22_HIDDEN_HOME_J5_DELTA_EXACTLY_DETERMINED_BY_MINIMAL_5_PREDICATE_STATE"
PREDICATES = ("a0","b0","c0","ab","ac","bc","am","bm0","cm","a_bm","c_bm")
SELECTED = ("b0","ab","ac","bm0","a_bm")
X, Z = 1, 3


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def verify_digest(raw: dict[str,Any]) -> bool:
    unsigned = {k:v for k,v in raw.items() if k != "result_digest"}
    return raw.get("result_digest") == hashlib.sha256(canon(unsigned).encode()).hexdigest()


def mul(a: int, b: int) -> int:
    if a == 0: return b
    if b == 0: return a
    if a == b: return 0
    return 6 - a - b


def f3(a: int, b: int, c: int) -> int:
    if a == b == c != 0:
        return 1
    return int(a != 0) + int(b != 0) + int(c != 0)


def delta(a: int, b: int, c: int, m: int) -> int:
    return f3(a,b,c) - f3(a,mul(b,m),c)


def features(a: int, b: int, c: int, m: int) -> dict[str,bool]:
    bm = mul(b,m)
    return {
        "a0":a==0,"b0":b==0,"c0":c==0,
        "ab":a==b,"ac":a==c,"bc":b==c,
        "am":a==m,"bm0":bm==0,"cm":c==m,
        "a_bm":a==bm,"c_bm":c==bm,
    }


def branch_rows(m: int):
    return [(a,b,c,delta(a,b,c,m),features(a,b,c,m)) for a,b,c in itertools.product(range(4),repeat=3)]


def cells(rows, subset):
    out = defaultdict(set)
    examples = defaultdict(dict)
    for a,b,c,d,f in rows:
        sig = tuple(int(f[n]) for n in subset)
        out[sig].add(d)
        examples[sig].setdefault(d,[a,b,c])
    return out, examples


def determines(rows, subset):
    c,_ = cells(rows,subset)
    return all(len(ds)==1 for ds in c.values())


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,default=DEFAULT_INPUT)
    ap.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    args=ap.parse_args()
    raw=json.loads(args.input.read_text())
    by_m={Z:branch_rows(Z),X:branch_rows(X)}

    selected_tables={}
    selected_counts={}
    selected_mixed={}
    for m,rr in by_m.items():
        cc,ex=cells(rr,SELECTED)
        selected_counts[str(m)]=len(cc)
        selected_tables[str(m)]={"".join(str(x) for x in sig):next(iter(ds)) for sig,ds in sorted(cc.items()) if len(ds)==1}
        bad=[]
        for sig,ds in sorted(cc.items()):
            if len(ds)>1:
                vals=sorted(ds)
                bad.append({"signature":list(sig),"deltas":vals,"examples":{str(d):ex[sig][d] for d in vals[:2]}})
        selected_mixed[str(m)]=bad

    minimum_k=None
    minima=[]
    smaller_counterexample_count=0
    for k in range(len(PREDICATES)+1):
        found=[]
        for sub in itertools.combinations(PREDICATES,k):
            if all(determines(rr,sub) for rr in by_m.values()):
                found.append(list(sub))
            elif k==4:
                smaller_counterexample_count += 1
        if found:
            minimum_k=k
            minima=found
            break

    paircells=defaultdict(set)
    hist=Counter()
    for a0,b0,c0,a1,b1,c1 in itertools.product(range(4),repeat=6):
        f0=features(a0,b0,c0,Z); f1=features(a1,b1,c1,X)
        sig=(tuple(int(f0[n]) for n in SELECTED),tuple(int(f1[n]) for n in SELECTED))
        d=delta(a0,b0,c0,Z)+delta(a1,b1,c1,X)
        paircells[sig].add(d); hist[d]+=1

    checks={
        "source_schema":raw.get("schema")=="ORIONQG.QG22.HiddenHomeState.v1",
        "source_digest":verify_digest(raw),
        "source_positive":raw.get("terminal")==POSITIVE and raw.get("all_gates") is True,
        "frozen_predicates_exact":raw.get("frozen_predicates")==list(PREDICATES),
        "selected_exact":raw.get("selected_signature")==list(SELECTED),
        "branch_domain_64":all(len(rr)==64 for rr in by_m.values()),
        "branch_values":all(set(x[3] for x in rr)=={-2,-1,0,1,2} for rr in by_m.values()),
        "selected_counts_18":all(v==18 for v in selected_counts.values()),
        "selected_no_mixed":all(not v for v in selected_mixed.values()),
        "selected_table_invariant":selected_tables[str(Z)]==selected_tables[str(X)],
        "selected_tables_match":selected_tables==raw.get("selected_signature_tables"),
        "minimum_k_5":minimum_k==5==raw.get("minimum_determining_cardinality"),
        "minimum_subsets_match":minima==raw.get("minimum_determining_subsets"),
        "four_subsets_all_refuted":smaller_counterexample_count==330,
        "pair_domain_4096":sum(hist.values())==4096,
        "pair_range_all_nine":set(hist)==set(range(-4,5)),
        "pair_cells_324":len(paircells)==324==raw.get("paired",{}).get("signature_cells"),
        "pair_no_mixed":all(len(ds)==1 for ds in paircells.values()),
        "pair_hist_match":{str(k):v for k,v in sorted(hist.items())}==raw.get("paired",{}).get("delta_histogram"),
        "scope_bounded":raw.get("all_n_theorem_authority") is False and raw.get("novelty_authority") is False and raw.get("r6_authority") is False,
        "protected_subject_not_read":raw.get("protected_subject_read") is False,
    }
    decision="ACCEPT_STATE_QUOTIENT" if all(checks.values()) else "REJECT"
    out={
        "schema":"ORIONQG.QG22.GenericVerification.v1",
        "decision":decision,
        "all_checks":all(checks.values()),
        "checks":checks,
        "source_result_digest":raw.get("result_digest"),
        "minimum_determining_cardinality":minimum_k,
        "minimum_determining_subsets":minima,
        "selected_cell_counts":selected_counts,
        "selected_signature_tables":selected_tables,
        "paired_signature_cells":len(paircells),
        "paired_delta_histogram":{str(k):v for k,v in sorted(hist.items())},
        "all_n_theorem_authority":False,
        "novelty_authority":False,
        "physical_quantum_advantage_claim":False,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(TOKEN+canon({"decision":decision,"all_checks":out["all_checks"],"minimum_k":minimum_k,"minimum_subset_count":len(minima),"branch_cells":selected_counts,"pair_cells":len(paircells)}))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
