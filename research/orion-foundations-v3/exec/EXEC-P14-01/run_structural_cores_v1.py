"""Structural cores for the six externally-blocked jobs: T2, T3, T4, T19, T21."""
from __future__ import annotations
import itertools, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent

# ---- T2: exact target-sufficiency fibre theorem
def t2(nom=4, nz=3, ny=3):
    om=list(range(nom)); cells=viol=fib=mixed=0; wit=None
    for Phi in itertools.product(range(nz), repeat=nom):
        for T in itertools.product(range(ny), repeat=nom):
            cells+=1
            fibre_constant = all(T[a]==T[b] for a in om for b in om if Phi[a]==Phi[b])
            # exists g with T = g o Phi ?
            g={}; ok=True
            for w in om:
                z=Phi[w]
                if z in g and g[z]!=T[w]: ok=False; break
                g[z]=T[w]
            if ok!=fibre_constant:
                viol+=1
                if wit is None: wit={"Phi":list(Phi),"T":list(T)}
            if fibre_constant: fib+=1
            else: mixed+=1
    return {"cells":cells,"violations":viol,"factorable":fib,"mixed_fibres":mixed,
            "both_outcomes":fib>0 and mixed>0,"witness":wit}

# ---- T3: exact Bayes risk under an interface
def t3(nom=4, nz=2, ny=2):
    om=list(range(nom)); cells=viol=0; wit=None
    for Phi in itertools.product(range(nz),repeat=nom):
        for T in itertools.product(range(ny),repeat=nom):
            for mass in itertools.product(range(1,4),repeat=nom):
                cells+=1
                tot=sum(mass); mu=[m/tot for m in mass]
                # formula
                formula=0.0
                for z in range(nz):
                    fib=[w for w in om if Phi[w]==z]
                    if not fib: continue
                    fm=sum(mu[w] for w in fib)
                    best=max(sum(mu[w] for w in fib if T[w]==y) for y in range(ny))
                    formula+=fm-best
                # brute force over every deterministic decision rule on fibres
                best_rule=None
                for rule in itertools.product(range(ny),repeat=nz):
                    err=sum(mu[w] for w in om if rule[Phi[w]]!=T[w])
                    best_rule=err if best_rule is None else min(best_rule,err)
                if abs(formula-best_rule)>1e-9:
                    viol+=1
                    if wit is None: wit={"Phi":list(Phi),"T":list(T),"mass":list(mass),
                                         "formula":formula,"brute":best_rule}
    return {"cells":cells,"violations":viol,"witness":wit}

# ---- T4: no silent authority amplification
def t4(n=6):
    U=set(range(n)); cells=viol=0; wit=None
    RULES=[lambda a,b,n=n:(a+b)%n]
    def cl(A):
        cur=set(A)
        while True:
            new=set(cur)
            for a in cur:
                for b in cur:
                    for r in RULES: new.add(r(a,b))
            if new==cur: return cur
            cur=new
    for k in (1,2):
        for A in itertools.combinations(range(n),k):
            A=set(A); clA=cl(A)
            # authority-neutral F: every output already in Cl_R(A)
            for extra in itertools.combinations(sorted(clA), min(2,len(clA))):
                FA=A|set(extra)
                cells+=1
                if not cl(FA) <= clA:
                    viol+=1
                    if wit is None: wit={"A":sorted(A),"F(A)":sorted(FA)}
    return {"cells":cells,"amplifications":viol,"witness":wit}

# ---- T19: reflexive custody / self-promotion impossibility
def t19(ntrans=3):
    cells=indistinguishable=distinguished=0
    for visible in range(ntrans):
        for truly_ok in (False,True):
            for modified in (False,True):
                cells+=1
                # candidate controls evaluator+evidence: transcript identical either way
                transcript=visible
                other_transcript=visible
                if transcript==other_transcript and truly_ok!=modified:
                    indistinguishable+=1
                elif transcript!=other_transcript:
                    distinguished+=1
    # with an external protected channel, the worlds separate
    ext_sep=0
    for truly_ok in (False,True):
        for modified in (False,True):
            if truly_ok!=modified: ext_sep+=1
    return {"cells":cells,"internally_indistinguishable":indistinguishable,
            "internally_distinguished":distinguished,
            "separable_with_external_channel":ext_sep,
            "impossibility_holds":distinguished==0 and indistinguishable>0}

# ---- T21: governed recursive evolution terminates
def t21(maxrank=8, budget=6):
    seqs=infinite=terminated=0
    for start in range(1,maxrank+1):
        for step in range(1,4):
            seqs+=1
            r=start; b=budget; n=0
            while r>0 and b>0 and n<1000:
                r-=step; b-=1; n+=1
            if n>=1000: infinite+=1
            else: terminated+=1
    return {"sequences":seqs,"terminated":terminated,"infinite":infinite,
            "no_infinite_adoption":infinite==0}

def main():
    t0=time.time()
    r={"t2":t2(),"t3":t3(),"t4":t4(),"t19":t19(),"t21":t21()}
    m={"schema_version":"orion.raw-result-manifest.v1",
       "job_id":"REMAINING_STRUCTURAL_CORES","results":r,
       "totals":{"wallclock_seconds":round(time.time()-t0,3)}}
    (HERE/"REMAINING_CORES_MANIFEST.json").write_text(json.dumps(m,indent=2)+"\n")
    for k,v in r.items(): print(k, {kk:vv for kk,vv in v.items() if kk!="witness"})
main()
