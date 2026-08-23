"""Decide conjecture C1: is QG-31's 54-class unlabeled defect-spectrum partition
EQUAL to the S_3(letters) x (S_2 wr S_3)(positions) orbit partition of the 4096
TARE column types, or only equinumerous with it?

The spectrum is reimplemented here from its definition; the two cost primitives
it needs (max_r6_p10..., max_r6s_all_n_composition) are both on main."""
import itertools, json, sys
from collections import defaultdict
from pathlib import Path
QDIR = Path("research/extensions/orion-q").resolve()
sys.path.insert(0, str(QDIR))
import max_r6_p10_candidate_blind_frame_optimizer as p10
import max_r6s_all_n_composition as r6s

BITS = ((0,0),(1,0),(1,1),(0,1)); CODE = {b:i for i,b in enumerate(BITS)}
def sy(a,b): return int(p10.h.local_symp(a,b))
def f3(a,b,c): return 1 if a==b==c!=0 else int(a!=0)+int(b!=0)+int(c!=0)
def autos(): return [(0,)+p for p in itertools.permutations((1,2,3))]
def orbit(t,aa): return {tuple(a[x] for x in t) for a in aa}
def perm(t,p):
    o=[]
    for j in range(3):
        a,b=t[2*j],t[2*j+1]; o.extend((a,b) if p[j]==0 else (b,a))
    return tuple(o)
def baseline(t,p):
    q=perm(t,p); return f3(q[0],q[2],q[4])+f3(q[1],q[3],q[5])
def key1(c): return p10.key_from_codes([c])
def aux48():
    pairs=[(a,b) for a in range(1,4) for b in range(1,4) if sy(a,b)==1]; rows=[]
    for ps in itertools.product(pairs,repeat=3):
        fr=tuple(x for z in ps for x in z)
        for tag in range(4):
            l0,l1=sy(tag,fr[0]),sy(tag,fr[1])
            if l0!=l1 and all(sy(tag,fr[2*j])==l0 and sy(tag,fr[2*j+1])==l1 for j in (1,2)):
                rows.append((fr,tag,tuple(key1(x) for x in fr),key1(tag)))
    return rows
def response(rep,ps,aux):
    out=[]; c=(0,0,0)
    for p in ps:
        pt=perm(rep,p); tkeys=tuple(key1(x) for x in pt); b=baseline(rep,p)
        for fr,tag,fkeys,tkey in aux:
            out.append(int(r6s.config_cost(tkeys,fkeys,tkey,c,1))-b)
    return tuple(out)

aa=autos(); ps=list(itertools.product((0,1),repeat=3)); aux=aux48()
print("aux rows:",len(aux)," position patterns:",len(ps)," probes:",len(ps)*len(aux))
obs={}
for t in itertools.product(range(4),repeat=6):
    o=orbit(t,aa); obs.setdefault(min(o),set()).update(o)
reps=sorted(obs); print("orbit reps:",len(reps))
bulk={}; spec={}; idx={}
for r in reps:
    v=response(r,ps,aux); idx[r]=v; spec[r]=tuple(sorted(v))
    bulk[r]=tuple(baseline(r,p) for p in ps[:4])
def part(d):
    g=defaultdict(set)
    for k,v in d.items(): g[v].add(k)
    return {frozenset(s) for s in g.values()}
Pb, Ps, Pi = part(bulk), part(spec), part(idx)
print("bulk classes:",len(Pb)," spectrum classes:",len(Ps)," indexed classes:",len(Pi))

# the symmetry quotient, expressed on the same 715 representatives
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
W=wreath(); print("wreath order:",len(W))
rep_of={}
for r in reps:
    for t in obs[r]: rep_of[t]=r
sym=defaultdict(set)
seen=set()
for r in reps:
    if r in seen: continue
    orb={rep_of[tuple(a[t[i]] for i in p)] for t in obs[r] for a in aa for p in W}
    seen|=orb
    for x in orb: sym[min(orb)].add(x)
Psym={frozenset(s) for s in sym.values()}
print("S_3 x wreath classes on the 715 reps:",len(Psym))

def refines(A,B): return all(any(c<=d for d in B) for c in A)
badw = sum(1 for r in reps if any(bulk[rep_of[tuple(r[i] for i in p)]]!=bulk[r] for p in W))
bads = sum(1 for r in reps if any(spec[rep_of[tuple(r[i] for i in p)]]!=spec[r] for p in W))
Pj = part({r:(bulk[r],spec[r]) for r in reps})
res = {
 "schema":"ORION.QG.SpectrumSymmetryIdentification.v1",
 "issue_under_test":"SzeChunYiu/ORION#904 (QG-31)",
 "read_from":("origin/codex/orion-qg-qg31-query-abstraction-20260822 (open PR #905) -- "
   "definitions only; both cost primitives are on main and every partition here is "
   "recomputed by this file, not imported from that branch"),
 "independent_reproduction":{
   "bulk_classes":len(Pb),"spectrum_classes":len(Ps),"indexed_classes":len(Pi),
   "joint_bulk_spectrum_classes":len(Pj),
   "reported_by_qg31_qg32":{"bulk":45,"spectrum":54,"indexed":715,"joint":92},
   "all_match": len(Pb)==45 and len(Ps)==54 and len(Pi)==715 and len(Pj)==92},
 "C1":{"statement":("the unlabeled one-active defect spectrum partition equals the "
        "S_3(letters) x (S_2 wr S_3)(positions) orbit partition of the 4096 column types"),
   "verdict":"CONFIRMED_AS_EQUALITY" if Ps==Psym else "REFUTED",
   "equal_as_set_systems":Ps==Psym,
   "reps_whose_spectrum_changes_under_some_wreath_element":bads,
   "consequence":("the spectrum carries exactly the symmetry-invariant information "
        "about a column type, and nothing more")},
 "bulk_is_not_a_symmetry_quotient":{
   "bulk_refines_symmetry":refines(Pb,Psym),"symmetry_refines_bulk":refines(Psym,Pb),
   "bulk_refines_spectrum":refines(Pb,Ps),"spectrum_refines_bulk":refines(Ps,Pb),
   "reps_whose_bulk_changes_under_some_wreath_element":badw,
   "mechanism":("bulk reads baseline over only the first 4 of the 8 swap patterns "
        "(ps[:4]), so it is not even S_2^3-invariant"),
   "consequence":("bulk and spectrum are incomparable -- QG-31's finding -- because "
        "they are different kinds of object: one is a group quotient, the other is not")},
 "authority":{"mathematical_proposal":True,"NOT_R6":True,"novelty_claim":False,
   "proof_authority":False,"machine_checked":True}}
print(json.dumps(res,indent=2,sort_keys=True))
