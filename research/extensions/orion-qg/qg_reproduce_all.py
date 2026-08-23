#!/usr/bin/env python3
"""One-command regeneration and CHECK of every headline QG number, from main.

    python3 research/extensions/orion-qg/qg_reproduce_all.py

Recomputes each claim from the cost primitives and compares it to the committed
receipt.  Any mismatch is a FAIL and is printed.  This is the artifact that lets
a reader refute the work without talking to us: every number below is derived
here, not read from a stored result.
"""
import itertools, json, sys, os
from collections import defaultdict, Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"research/extensions/orion-q"))
import max_r6_p10_candidate_blind_frame_optimizer as p10
import max_r6s_all_n_composition as r6s

FAILS=[]
def check(name, got, want):
    ok = got==want
    print(f"  [{'OK ' if ok else 'FAIL'}] {name}: {got}" + ("" if ok else f"   expected {want}"))
    if not ok: FAILS.append((name,got,want))

def sy(a,b): return int(p10.h.local_symp(a,b))
def key1(c): return p10.key_from_codes([c])
def f3(a,b,c): return 1 if a==b==c!=0 else int(a!=0)+int(b!=0)+int(c!=0)
def perm(t,p):
    o=[]
    for j in range(3):
        a,b=t[2*j],t[2*j+1]; o.extend((a,b) if p[j]==0 else (b,a))
    return tuple(o)
def baseline(t,p):
    q=perm(t,p); return f3(q[0],q[2],q[4])+f3(q[1],q[3],q[5])
def aux48():
    pairs=[(a,b) for a in range(1,4) for b in range(1,4) if sy(a,b)==1]; rows=[]
    for ps in itertools.product(pairs,repeat=3):
        fr=tuple(x for z in ps for x in z)
        for tag in range(4):
            l0,l1=sy(tag,fr[0]),sy(tag,fr[1])
            if l0!=l1 and all(sy(tag,fr[2*j])==l0 and sy(tag,fr[2*j+1])==l1 for j in (1,2)):
                rows.append((fr,tag,tuple(key1(x) for x in fr),key1(tag)))
    return rows

print("== QG-28: local-Clifford orbit census ==")
AUTS=[(0,)+p for p in itertools.permutations((1,2,3))]
obs={}
for t in itertools.product(range(4),repeat=6):
    o={tuple(a[x] for x in t) for a in AUTS}; obs.setdefault(min(o),set()).update(o)
reps=sorted(obs)
check("orbit count", len(reps), 715)
check("orbit size histogram", dict(sorted(Counter(len(v) for v in obs.values()).items())), {1:1,3:63,6:651})

print("== responses, bulk, spectrum, joint ==")
AUX=aux48(); PS=list(itertools.product((0,1),repeat=3)); c0=(0,0,0)
K=[]; bulk=[]; spec=[]
for r in reps:
    row=[]
    for p in PS:
        pt=perm(r,p); tk=tuple(key1(x) for x in pt); b=baseline(r,p)
        for fr,tag,fk,tkey in AUX: row.append(int(r6s.config_cost(tk,fk,tkey,c0,1))-b)
    K.append(row); spec.append(tuple(sorted(row))); bulk.append(tuple(baseline(r,p) for p in PS[:4]))
check("probe count", len(K[0]), 384)
check("bulk classes", len(set(bulk)), 45)
check("spectrum classes", len(set(spec)), 54)
jc=defaultdict(list)
for i in range(len(reps)): jc[(bulk[i],spec[i])].append(i)
joint=[sorted(v) for v in jc.values()]
check("joint classes", len(joint), 92)

print("== C1: spectrum == maximal symmetry quotient ==")
def wreath():
    out=set()
    for bl in itertools.permutations(range(3)):
        for s in itertools.product((0,1),repeat=3):
            p=[]
            for bi in range(3):
                a,b=2*bl[bi],2*bl[bi]+1
                p += [b,a] if s[bi] else [a,b]
            out.add(tuple(p))
    return sorted(out)
W=wreath(); rep_of={t:r for r in reps for t in obs[r]}
sym=defaultdict(set); seen=set()
for r in reps:
    if r in seen: continue
    orb={rep_of[tuple(a[t[i]] for i in p)] for t in obs[r] for a in AUTS for p in W}
    seen|=orb
    for x in orb: sym[min(orb)].add(x)
Psym={frozenset(v) for v in sym.values()}
g=defaultdict(set)
for i,s in enumerate(spec): g[s].add(reps[i])
Ps={frozenset(v) for v in g.values()}
check("C1 spectrum partition == orbit partition", Ps==Psym, True)
badb=sum(1 for r in reps if any(bulk[reps.index(rep_of[tuple(r[i] for i in p)])]!=bulk[reps.index(r)] for p in W))
check("bulk reps changed by a wreath element", badb, 168)

print("== QG-35: existence free, selection impossible ==")
best=[min(K[i]) for i in range(len(K))]
argmin=[frozenset(p for p in range(384) if K[i][p]==best[i]) for i in range(len(K))]
def split(f): return sum(1 for c in joint if len({f[i] for i in c})>1)
check("existence (optimal value) classes split", split(best), 0)
check("existence (cost multiset) classes split", split(spec), 0)
check("selection (optimal-frame set) classes split", split(argmin), 85)
check("types in a split class", sum(len(c) for c in joint if len({argmin[i] for i in c})>1), 708)

print("== QG-32c: universal fixed minimum ==")
pairs=[(a,b) for c in joint for a,b in itertools.combinations(sorted(c),2)]
check("pairs needing separation", len(pairs), 5895)
masks=set()
for p in range(384):
    m=0
    for i,(a,b) in enumerate(pairs):
        if K[a][p]!=K[b][p]: m|=1<<i
    if m: masks.add(m)
check("distinct coverage masks", len(masks), 168)

print()
if FAILS:
    print(f"REPRODUCTION FAILED on {len(FAILS)} checks"); sys.exit(1)
print("ALL CHECKS REPRODUCED")
