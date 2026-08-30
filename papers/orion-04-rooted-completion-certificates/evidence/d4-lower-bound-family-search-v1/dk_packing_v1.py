"""Max disjoint nontrivial zero-sum subsequences over C_p^r, on MULTIPLICITY vectors.

A sequence is a multiset {g: m_g}. A sub-multiset is c=(c_1..c_d) with 0<=c_i<=m_i.
It is zero-sum iff sum c_i*g_i = 0 in C_p^r. We enumerate the inclusion-MINIMAL
nontrivial zero-sum vectors, then maximise the number of pairwise "disjoint" ones
(vectors summing componentwise to <= m). Exponential only in d = #distinct
elements, which is small for every construction of interest.
"""
from itertools import product

def zero(r): return (0,)*r

def minimal_zs_vectors(elems, mult, p, r):
    d=len(elems); out=[]
    ranges=[range(m+1) for m in mult]
    for c in product(*ranges):
        if not any(c): continue
        s=[0]*r
        for ci,g in zip(c,elems):
            if ci:
                for j in range(r): s[j]+=ci*g[j]
        if all(x%p==0 for x in s): out.append(c)
    out.sort(key=sum)
    keep=[]
    for c in out:
        if not any(all(k[i]<=c[i] for i in range(d)) for k in keep): keep.append(c)
    return keep

def max_disjoint(elems, mult, p, r, cap=99):
    d=len(elems)
    mz=minimal_zs_vectors(elems,mult,p,r)
    best=0
    def rec(i, rem, cnt):
        nonlocal best
        if cnt>best: best=cnt
        if best>=cap: return True
        for j in range(i,len(mz)):
            c=mz[j]
            if all(c[t]<=rem[t] for t in range(d)):
                if rec(j, tuple(rem[t]-c[t] for t in range(d)), cnt+1): return True
        return False
    rec(0, tuple(mult), 0)
    return best, len(mz)

def basis(r): return [tuple(1 if j==i else 0 for j in range(r)) for i in range(r)]
