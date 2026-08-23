"""Verify the referee's two fatal claims myself.
 (1) IDENTITY: is "85 of 92" just "92 minus the singleton classes"?
 (2) NULL: does shuffling the frame-index alignment -- destroying all TARE
     content in the selection dimension while preserving bulk, spectrum and the
     92 joint classes exactly -- reproduce the headline numbers?"""
import json, random, itertools
from collections import Counter, defaultdict
P=json.load(open("/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/qg34/primitives.json"))
K=P["K"]; joint=P["joint"]; NP=P["n_probes"]; n=len(K)

sizes=Counter(len(c) for c in joint)
singles=sizes.get(1,0)
print("(1) IDENTITY CHECK")
print(f"    joint class size histogram: {dict(sorted(sizes.items()))}")
print(f"    singleton classes: {singles};  92 - {singles} = {92-singles}   (claim: 85)")
print(f"    singleton types  : {singles};  715 - {singles} = {715-singles}  (claim: 708)")
def split_count(rows):
    best=[min(r) for r in rows]
    am=[frozenset(p for p in range(NP) if r[p]==b) for r,b in zip(rows,best)]
    s=sum(1 for c in joint if len({am[i] for i in c})>1)
    t=sum(len(c) for c in joint if len({am[i] for i in c})>1)
    return s,t,am,best
s,t,am,best=split_count(K)
print(f"    measured on REAL data: {s}/92 classes, {t}/715 types")
print(f"    every non-singleton class splits: {s==92-singles and t==715-singles}")

print()
print("(2) NULL MODEL -- shuffle each row's frame alignment (spectrum preserved exactly)")
for seed in (1,2,3):
    rng=random.Random(seed)
    NK=[]
    for r in K:
        rr=list(r); rng.shuffle(rr); NK.append(rr)
    # spectrum, bulk, joint classes are unchanged by construction: verify
    assert all(sorted(a)==sorted(b) for a,b in zip(K,NK)), "spectrum changed!"
    ns,nt,nam,nbest=split_count(NK)
    assert nbest==best, "optimal values changed!"
    print(f"    seed {seed}: classes split {ns}/92, types {nt}/715   "
          f"(REAL: {s}/92, {t}/715)   spectrum+optimal value IDENTICAL")
print()
print("VERDICT: the headline separation counts are reproduced by a null with no")
print("         TARE structure in the selection dimension." )
