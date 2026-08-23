"""CHECK B: is the spectrum's 54-completeness BY CONSTRUCTION or a genuine fact?
Split the two questions that 'it is the maximal symmetry quotient' conflates:
  (a) INVARIANCE  -- is spec(g.t) = spec(t) forced by how spec is defined?
  (b) COMPLETENESS -- does spec separate ALL 54 orbits, rather than merging some?
(a) can be by-construction; (b) cannot."""
import itertools, sys
from pathlib import Path
from collections import defaultdict
QDIR=Path("research/extensions/orion-q").resolve(); sys.path.insert(0,str(QDIR))
import max_r6_p10_candidate_blind_frame_optimizer as p10
import max_r6s_all_n_composition as r6s
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
AUX=aux48(); PS=list(itertools.product((0,1),repeat=3))
AUTS=[(0,)+p for p in itertools.permutations((1,2,3))]

# --- (a) is the aux row set closed under the group? if so invariance is structural
frtags={(fr,tag) for fr,tag,_,_ in AUX}
def blockperm(x,bl): return tuple(y for b in bl for y in (x[2*b],x[2*b+1]))
closed_letters = all(( tuple(phi[c] for c in fr), phi[tag]) in frtags
                     for fr,tag,_,_ in AUX for phi in AUTS)
closed_blocks  = all((blockperm(fr,bl),tag) in frtags
                     for fr,tag,_,_ in AUX for bl in itertools.permutations(range(3)))
closed_swaps   = all((perm(fr,p),tag) in frtags for fr,tag,_,_ in AUX for p in PS)
print("aux row set closed under letter S_3 :", closed_letters)
print("aux row set closed under block S_3  :", closed_blocks)
print("aux row set closed under swaps S_2^3:", closed_swaps)
print("  -> if all three are True, sorting the 384-tuple makes INVARIANCE structural")

# --- (b) completeness is the part that could have failed: does spec separate all 54?
def response(rep):
    out=[]; c=(0,0,0)
    for p in PS:
        pt=perm(rep,p); tkeys=tuple(key1(x) for x in pt); b=baseline(rep,p)
        for fr,tag,fkeys,tkey in AUX:
            out.append(int(r6s.config_cost(tkeys,fkeys,tkey,c,1))-b)
    return tuple(out)
obs={}
for t in itertools.product(range(4),repeat=6):
    o={tuple(a[x] for x in t) for a in AUTS}; obs.setdefault(min(o),set()).update(o)
reps=sorted(obs)
spec={r:tuple(sorted(response(r))) for r in reps}
def W():
    out=set()
    for bl in itertools.permutations(range(3)):
        for s in itertools.product((0,1),repeat=3):
            p=[]
            for bi in range(3):
                a,b=2*bl[bi],2*bl[bi]+1
                p += [b,a] if s[bi] else [a,b]
            out.add(tuple(p))
    return sorted(out)
WG=W(); rep_of={t:r for r in reps for t in obs[r]}
sym=defaultdict(set); seen=set()
for r in reps:
    if r in seen: continue
    orb={rep_of[tuple(a[t[i]] for i in p)] for t in obs[r] for a in AUTS for p in WG}
    seen|=orb
    for x in orb: sym[min(orb)].add(x)
Psym={frozenset(v) for v in sym.values()}
g=defaultdict(set)
for r,v in spec.items(): g[v].add(r)
Ps={frozenset(v) for v in g.values()}
print()
print("orbit classes (S_3 x wreath):", len(Psym))
print("spectrum classes            :", len(Ps))
print("spectrum == orbits          :", Ps==Psym)
# a shuffled control: does an ARBITRARY invariant summary also hit 54?
ctrl={r: tuple(sorted(response(r)[:48])) for r in reps}   # only the first aux block
gc=defaultdict(set)
for r,v in ctrl.items(): gc[v].add(r)
print()
print("CONTROL -- sorting only the first 48 of the 384 coordinates:")
print("  classes:", len({frozenset(v) for v in gc.values()}), "(if < 54, completeness was NOT automatic)")
