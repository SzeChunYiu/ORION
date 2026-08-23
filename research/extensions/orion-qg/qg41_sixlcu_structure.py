"""Verify the structural engine: argmin equivariance, and the exact boundary
between the determined (symmetry-blind) and undetermined (symmetry-moved) readouts."""
import json, itertools, random
from collections import defaultdict
import numpy as np
OUT="/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/broadclass"
D=np.load(f"{OUT}/sixlcu_prims.npz"); M=json.load(open(f"{OUT}/sixlcu_meta.json"))
K=D["K"]; CH_MAP=D["CH_MAP"]; canonF=D["canonF"]; A=D["A"]
CHOICES=[(pi,tuple(phi)) for pi,phi in M["choices"]]; PARTS=[tuple(tuple(b) for b in p) for p in M["parts"]]
SLOT=list(itertools.permutations(range(6))); LETTER=[(0,)+p for p in itertools.permutations((1,2,3))]
POW=np.array([4**(5-j) for j in range(6)],dtype=np.int64)
n=4096; best=K.min(axis=1); argmin=[frozenset(np.flatnonzero(K[i]==best[i]).tolist()) for i in range(n)]
SHAPE=[tuple(sorted((len(b) for b in PARTS[pi]),reverse=True)) for pi,_ in CHOICES]
def T(i): return "".join("IXYZ"[x] for x in A[i])

# ---- V5: argmin equivariance  argmin(g.t) = g.argmin(t) ----
random.seed(5); bad=0; trivial=0
for _ in range(300):
    si=random.randrange(720); li=random.randrange(6); t=random.randrange(n)
    tau=np.array(LETTER[li]); gt=int((tau[A[:,list(SLOT[si])]]@POW)[t])
    bad += (argmin[gt] != frozenset(int(CH_MAP[si,c]) for c in argmin[t]))
print(f"V5 argmin equivariance argmin(g.t)==g.argmin(t): {bad} mismatches / 300")
# letters act trivially on choices:
bad2=0
for _ in range(200):
    li=random.randrange(1,6); t=random.randrange(n)
    tau=np.array(LETTER[li]); gt=int((tau[A]@POW)[t])
    bad2 += not (K[gt]==K[t]).all()
print(f"V5 letter action is trivial on choices (K[tau.t]==K[t] pointwise): {bad2} mismatches / 200\n")

# ---- the exact boundary, orbit by orbit ----
orb=defaultdict(list)
for i in range(n): orb[int(canonF[i])].append(i)
const_argmin=sum(1 for g in orb.values() if len({argmin[i] for i in g})==1)
const_shape =sum(1 for g in orb.values() if len({frozenset(SHAPE[c] for c in argmin[i]) for i in g})==1)
const_part  =sum(1 for g in orb.values() if len({frozenset(CHOICES[c][0] for c in argmin[i]) for i in g})==1)
print(f"=== BOUNDARY over the {len(orb)} orbits (= spectrum classes) ===")
print(f"  orbits where optimal-CHOICE set is constant   : {const_argmin}/{len(orb)}   (determined here)")
print(f"  orbits where optimal-PARTITION set is constant: {const_part}/{len(orb)}")
print(f"  orbits where optimal-SHAPE set is constant    : {const_shape}/{len(orb)}   <- symmetry-blind readout")
print("\n  orbits where selection IS determined (argmin constant) -- the degenerate cases:")
for c,g in orb.items():
    if len({argmin[i] for i in g})==1:
        print(f"    orbit of {T(g[0]):8s} size {len(g):4d}  |argmin|={len(argmin[g[0]])}  "
              f"{'ALL choices optimal (cost constant)' if len(argmin[g[0]])==2430 else 'argmin is G-stable'}")
# stabiliser explanation
print("\n  => selection fails exactly on orbits where the group MOVES the optimal-choice set;")
print(f"     it holds on the {const_argmin} orbits where argmin is G-stable.")
json.dump({"orbits":len(orb),"orbits_argmin_constant":const_argmin,"orbits_shape_constant":const_shape,
           "orbits_partition_constant":const_part},open(f"{OUT}/structure.json","w"),indent=2)
