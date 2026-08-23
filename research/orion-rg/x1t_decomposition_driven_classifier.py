import sys
from itertools import combinations, permutations
from math import factorial

r=int(sys.argv[1]); m=int(sys.argv[2])
N=1<<r; V=list(range(1,N)); B0=[1<<i for i in range(r)]; B0set=set(B0)
GL=1
for i in range(r): GL*=(N-(1<<i))

pool=[v for v in V if v not in B0set]
if m==4:
    pool=[v for v in pool if bin(v).count('1')>=3]   # weight<=2 => 3-ZS with basis => min-ZS<4
poolset=set(pool)

cands=[]
for t in combinations(pool,m-1):
    x=0
    for e in t: x^=e
    if x==0 or x<=t[-1] or x not in poolset: continue
    cands.append(t+(x,))

def zs_masks(W):
    n=len(W); x=[0]*(1<<n)
    for s in range(1,1<<n):
        low=s&-s; i=low.bit_length()-1
        x[s]=x[s^low]^W[i]
    return [s for s in range(1,1<<n) if x[s]==0]

assert_fails=0; survivors=[]
for A in cands:
    W=sorted(B0)+list(A)
    Z=zs_masks(W)
    mn=min(bin(s).count('1') for s in Z)   # Z nonempty: A itself is a ZS
    bad=False
    for i in range(len(Z)):
        for j in range(i+1,len(Z)):
            if not(Z[i]&Z[j]): bad=True; break
        if bad: break
    if bad: continue
    if mn!=m: assert_fails+=1; print("THEOREM-VIOLATION candidate:",W); continue
    survivors.append(frozenset(W))

def rankfull(sub):
    span={0}
    for c in sub:
        if c in span: return False
        span|={s^c for s in span}
    return True

def decs(Wset):
    out=[]
    for sub in combinations(sorted(Wset),r):
        comp=Wset-set(sub)
        x=0
        for e in comp: x^=e
        if x: continue
        if rankfull(sub): out.append(sub)
    return out

def img(Wset,ordb):
    coord={0:0}
    for j,b in enumerate(ordb):
        for s,c in list(coord.items()):
            coord[s^b]=c|(1<<j)
    return frozenset(coord[w] for w in Wset)

def canon_stab(Wset):
    best=None; stab=0
    for sub in decs(Wset):
        for p in permutations(sub):
            I=img(Wset,p)
            t=tuple(sorted(I))
            if best is None or t<best: best=t
            if I==Wset: stab+=1
    return best,stab,len(decs(Wset))

classes={}
for Wset in survivors:
    c,st,dc=canon_stab(Wset)
    if c not in classes: classes[c]=(st,dc,Wset,0)
    st0,dc0,rep,cnt=classes[c]; classes[c]=(st0,dc0,rep,cnt+1)

print(f"r={r} m={m}  |GL|={GL}  candidates={len(cands)}  survivors(validA)={len(survivors)}  theorem-violations={assert_fails}")
total=0; ident=0
for c,(st,dc,rep,cnt) in sorted(classes.items()):
    assert GL%st==0
    orb=GL//st; total+=orb
    ident+=orb*dc
    A=sorted(rep-set(B0))
    colt=tuple(sorted(tuple(i for i,a in enumerate(A) if (a>>bit)&1) for bit in range(r)))
    print(f"  ORBIT size={orb}  |Stab|={st}  decomps={dc}  survivors-in-class={cnt}  A={A}  coltypes={colt}")
print(f"TOTAL witnesses = {total}")
ub=GL//factorial(r)
print(f"identity: survivors {len(survivors)} =?= sum(orbit*decomps)/#bases = {ident}/{ub} = {ident/ub}")
assert len(survivors)*ub==ident, "IDENTITY FAIL"
print("IDENTITY OK")
