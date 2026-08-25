"""EXEC-P13-01 v2 -- frozen grid: 5 elements, 6 tokens."""
from __future__ import annotations
import itertools, json, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
def parts(n):
    def h(e):
        if not e: yield []; return
        f,rest=e[0],e[1:]
        for sm in h(rest):
            for i in range(len(sm)): yield sm[:i]+[[f]+sm[i]]+sm[i+1:]
            yield [[f]]+sm
    for p in h(list(range(n))): yield tuple(frozenset(b) for b in p)
def refines(a,b): return all(any(x<=y for y in b) for x in a)
def run(n=5, ntok=6):
    allp=list(parts(n))
    cells=safe=unsafe=viol=fresh_wrong=0
    for pz in allp:
        for pr in allp:
            for pr2 in allp:
                cells+=1
                s=refines(pz,pr2)
                indep=all(any(x in bb and y in bb for bb in pr2) for b in pz for x in b for y in b)
                if s: safe+=1
                else: unsafe+=1
                if s!=indep: viol+=1
                if refines(pz,pr) and not s: fresh_wrong+=1
    toks=list(range(ntok)); fams=[frozenset(c) for c in itertools.combinations(toks,2)]
    tc=tv=surv=died=0
    for chosen in itertools.combinations(fams,3):
        ms=[f for f in chosen if not any(g<f for g in chosen)]
        for k in range(ntok+1):
            for R in itertools.combinations(toks,k):
                Rs=frozenset(R); tc+=1
                a=any(not (f&Rs) for f in ms); b=any(f<=(frozenset(toks)-Rs) for f in chosen)
                if a: surv+=1
                else: died+=1
                if a!=b: tv+=1
    return {"t18":{"cells":cells,"safe":safe,"unsafe":unsafe,"violations":viol,
                   "fresh_for_old_but_unsafe_for_new":fresh_wrong},
            "t11":{"cells":tc,"survived":surv,"died":died,"violations":tv}}
def main():
    t0=time.time(); grid={"n_elements":5,"n_tokens":6,"seed":20260825}
    r=run(grid["n_elements"],grid["n_tokens"])
    m={"schema_version":"orion.raw-result-manifest.v1","job_id":"EXEC-P13-01","grid":grid,**r,
       "totals":{"cells_enumerated":r["t18"]["cells"]+r["t11"]["cells"],
                 "wallclock_seconds":round(time.time()-t0,3)}}
    (HERE/"RAW_RESULT_MANIFEST.json").write_text(json.dumps(m,indent=2)+"\n")
    print("t18",r["t18"]["cells"],"safe",r["t18"]["safe"],"unsafe",r["t18"]["unsafe"],
          "viol",r["t18"]["violations"],"fresh_but_unsafe",r["t18"]["fresh_for_old_but_unsafe_for_new"])
    print("t11",r["t11"]["cells"],"surv",r["t11"]["survived"],"died",r["t11"]["died"],"viol",r["t11"]["violations"])
main()
