"""EXEC-P10-01 v2 -- frozen grid: 5-var CNF with 3-literal clauses, UNSAT reachable."""
from __future__ import annotations
import itertools, json, time, random
from pathlib import Path
HERE = Path(__file__).resolve().parent

def closure(seeds, ops, U):
    cur=set(seeds)
    while True:
        new=set(cur)
        for a in cur:
            for b in cur:
                for op in ops:
                    v=op(a,b)
                    if v in U: new.add(v)
        if new==cur: return cur
        cur=new

def run(n=8, nvars=5, nclauses=4):
    U=set(range(n)); OPS=[lambda a,b,n=n:(a+b)%n, lambda a,b,n=n:(a*b)%n]
    checked=genuine=macro=viol=0; w=None
    for k in (1,2):
        for S in itertools.combinations(range(n),k):
            S=frozenset(S); cl=closure(S,OPS,U)
            for t in U-cl:
                for e in U:
                    checked+=1
                    cle=closure(S|{e},OPS,U)
                    if (t not in cl) and (e not in cl) and (t in cle): genuine+=1
                    if e in cl:
                        macro+=1
                        if cle!=cl:
                            viol+=1
                            if w is None: w={"seeds":sorted(S),"target":t,"ext":e}
    # T22: 3-literal clauses over 5 vars -- UNSAT is reachable
    lits=[l for v in range(1,nvars+1) for l in (v,-v)]
    trips=list(itertools.combinations(lits,3))
    random.seed(20260825)
    sample=random.sample(trips, min(len(trips), 60))
    def sat(a,cs): return all(any(a[abs(l)-1]==(l>0) for l in c) for c in cs)
    formulas=satn=unsatn=search=check=0
    worst_search=0
    for cs in itertools.combinations(sample, nclauses):
        formulas+=1
        if formulas>4000: break
        found=None; steps=0
        for bits in itertools.product((False,True),repeat=nvars):
            steps+=1
            if sat(list(bits),cs): found=list(bits); break
        search+=steps; worst_search=max(worst_search,steps)
        if found is not None:
            satn+=1; check+=1
            assert sat(found,cs)
        else:
            unsatn+=1
    return {"t15":{"checked":checked,"genuine_extensions":genuine,"macros":macro,
                   "macro_extended_closure_violations":viol,"minimal_witness":w},
            "t22":{"formulas":formulas,"sat":satn,"unsat":unsatn,"total_search_steps":search,
                   "worst_case_search_steps":worst_search,"checks":check,
                   "max_possible_assignments":2**nvars,
                   "unsat_present":unsatn>0}}

def main():
    t0=time.time(); grid={"universe":8,"cnf_vars":5,"cnf_clauses":4,"seed":20260825}
    r=run(grid["universe"],grid["cnf_vars"],grid["cnf_clauses"])
    m={"schema_version":"orion.raw-result-manifest.v1","job_id":"EXEC-P10-01","grid":grid,**r,
       "totals":{"cells_enumerated":r["t15"]["checked"]+r["t22"]["formulas"],
                 "wallclock_seconds":round(time.time()-t0,3)}}
    (HERE/"RAW_RESULT_MANIFEST.json").write_text(json.dumps(m,indent=2)+"\n")
    print("t15 checked",r["t15"]["checked"],"genuine",r["t15"]["genuine_extensions"],
          "macro_viol",r["t15"]["macro_extended_closure_violations"])
    print("t22 formulas",r["t22"]["formulas"],"sat",r["t22"]["sat"],"UNSAT",r["t22"]["unsat"],
          "worst_search",r["t22"]["worst_case_search_steps"],"of",r["t22"]["max_possible_assignments"])
main()
