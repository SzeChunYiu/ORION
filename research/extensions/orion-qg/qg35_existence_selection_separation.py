"""QG-35: the existence/selection separation for TARE frame choice.

Question: which regime predicates on TARE column types are decidable from the
cheap bulk+spectrum summary, and which are not -- unconditionally, at any
expressiveness, not merely within some frozen literal predicate family?

Criterion (immediate, and the whole point): a predicate B is A-determined iff B
is a union of blocks of A's partition. So the question is decided exactly by the
92 joint classes, which are recomputed from main."""
import json, itertools
from collections import Counter, defaultdict
PR=json.load(open("/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/qg34/primitives.json"))
K=PR["K"]; reps=PR["reps"]; joint=PR["joint"]; NP=PR["n_probes"]; n=len(K)
def T(i): return "".join("IXYZ"[x] for x in reps[i])
best=[min(K[i]) for i in range(n)]
argmin=[frozenset(p for p in range(NP) if K[i][p]==best[i]) for i in range(n)]
spec=[tuple(sorted(K[i])) for i in range(n)]

def determined(pred):
    return [c for c in joint if len({pred[i] for i in c})>1]

# ---- (a) EXISTENCE questions: proved determined, then verified ----
existence={}
for thr in range(-3,4):
    existence[f"improvement_available_at_level_{thr}  (min_p K <= {thr})"]=[best[i]<=thr for i in range(n)]
existence["optimal cost value itself (min_p K)"]=[best[i] for i in range(n)]
existence["number of optimal frames (|argmin|)"]=[len(argmin[i]) for i in range(n)]
existence["full multiset of achievable costs"]=[spec[i] for i in range(n)]
# ---- (b) SELECTION questions ----
selection={}
for p in range(0,NP,1):
    pass
sel_split={p:len(determined([p in argmin[i] for i in range(n)])) for p in range(NP)}
selection["is frame p optimal? (worst p)"]=max(sel_split.values())
selection["is frame p optimal? (# of p that are NOT determined)"]=sum(1 for v in sel_split.values() if v>0)
selection["identity of the optimal-frame SET"]=[argmin[i] for i in range(n)]
selection["lexicographically first optimal frame"]=[min(argmin[i]) for i in range(n)]

print("EXISTENCE questions -- decided by bulk+spectrum?")
for k,v in existence.items():
    s=determined(v); print(f"  {k:52s} classes split: {len(s):2d}  {'DETERMINED' if not s else 'NOT'}")
print()
print("SELECTION questions -- decided by bulk+spectrum?")
for k in ("identity of the optimal-frame SET","lexicographically first optimal frame"):
    s=determined(selection[k]); print(f"  {k:52s} classes split: {len(s):2d}  {'DETERMINED' if not s else 'NOT'}")
print(f"  individual frames p: {selection['is frame p optimal? (# of p that are NOT determined)']} of {NP} give a NON-determined predicate")
print(f"  worst single frame splits {selection['is frame p optimal? (worst p)']} of the 92 joint classes")
print()
# ---- sufficiency side: is selection determined at the 715 (letter-orbit) level? ----
print("SUFFICIENCY: cost is letter-S_3 invariant, so the 715 orbit types resolve everything.")
print("  distinct optimal-frame sets across the 715 types:", len(set(argmin)))
print()
# ---- explicit impossibility witnesses ----
wits=[]
for c in joint:
    if len(c)<2: continue
    for a,b in itertools.combinations(c,2):
        if argmin[a]!=argmin[b] and best[a]==best[b]:
            wits.append((a,b,len(c),best[a])); break
print(f"EXPLICIT WITNESS PAIRS (same joint class, same optimal VALUE, different optimal FRAMES): {len(wits)}")
for a,b,sz,v in wits[:5]:
    print(f"  {T(a)} vs {T(b)}   joint class size {sz}, both optimal value {v}, "
          f"|argmin| {len(argmin[a])} vs {len(argmin[b])}, disjointness {len(argmin[a]&argmin[b])} shared")
nsplit=len([c for c in joint if len({argmin[i] for i in c})>1])
print()
print(f"joint classes on which the optimal-frame set is NOT constant: {nsplit} of 92")
print(f"types living in such a class: {sum(len(c) for c in joint if len({argmin[i] for i in c})>1)} of 715")
json.dump({"existence_all_determined":all(not determined(v) for v in existence.values()),
 "selection_frame_set_split_classes":len(determined([argmin[i] for i in range(n)])),
 "selection_lexfirst_split_classes":len(determined([min(argmin[i]) for i in range(n)])),
 "individual_frames_not_determined":selection["is frame p optimal? (# of p that are NOT determined)"],
 "worst_frame_splits":selection["is frame p optimal? (worst p)"],
 "joint_classes_with_nonconstant_argmin":nsplit,
 "types_in_such_classes":sum(len(c) for c in joint if len({argmin[i] for i in c})>1),
 "distinct_argmin_sets_over_715":len(set(argmin)),
 "witness_pairs":len(wits),
 "witness_examples":[{"a":T(a),"b":T(b),"joint_class_size":sz,"shared_optimal_value":v,
   "argmin_a_size":len(argmin[a]),"argmin_b_size":len(argmin[b]),
   "shared_optimal_frames":len(argmin[a]&argmin[b])} for a,b,sz,v in wits[:10]]},
 open("/tmp/qg35_result.json","w"), indent=2)
