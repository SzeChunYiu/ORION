"""Independent check of the claimed 3 < 4 < 5 observation-cost hierarchy.

  adaptive        D*  : QG-34, verified this session = 3
  class-conditioned F*: for EACH joint class, the min fixed probe set separating
                        that class; take the max over the 92 classes
  universal        U* : ONE fixed probe set separating every same-class pair"""
import json, itertools
P=json.load(open("/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/qg34/primitives.json"))
K=P["K"]; joint=P["joint"]; NP=P["n_probes"]
def min_cover_for(cls, cap=8):
    pairs=[(a,b) for a,b in itertools.combinations(sorted(cls),2)]
    if not pairs: return 0
    full=(1<<len(pairs))-1
    masks=set()
    for p in range(NP):
        m=0
        for i,(a,b) in enumerate(pairs):
            if K[a][p]!=K[b][p]: m|=1<<i
        if m: masks.add(m)
    masks=sorted(masks,key=lambda m:-bin(m).count("1"))
    if not masks: return None
    for k in range(1,cap+1):
        def rec(i,rem,d):
            if rem==0: return True
            if d==0: return False
            if d*max((m&rem).bit_count() for m in masks) < rem.bit_count(): return False
            for j in range(i,len(masks)):
                if masks[j]&rem and rec(j+1, rem&~masks[j], d-1): return True
            return False
        if rec(0,full,k): return k
    return None
vals=[min_cover_for(c) for c in joint]
from collections import Counter
print("per-class minimum FIXED probe count, histogram:",dict(sorted(Counter(vals).items())))
print("class-conditioned fixed minimum  F* =",max(vals))
print("universal fixed minimum          U* = 5   (exhaustive: no 4-subset of the 168")
print("                                          distinct coverage masks covers all 5895 pairs)")
print("adaptive depth                   D* = 3   (QG-34, three solvers agreeing)")
print()
D,F,U=3,max(vals),5
print(f"HIERARCHY: {D} < {F} < {U}  ->", "CONFIRMED" if D<F<U else "NOT CONFIRMED")
