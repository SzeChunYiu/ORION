"""Is the QG excess hardness real, or generic?

Referee's finding: the reported headline numbers are null-reproducible, but two
quantities were NOT -- the adaptive depth distribution and budget-2 regret.
This settles whether that residual survives a proper null distribution, and
tests the leading hypothesis against it (coverage-mask degeneracy)."""
import json, random, itertools
from collections import Counter, defaultdict
P=json.load(open("/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/qg34/primitives.json"))
K=P["K"]; joint=P["joint"]; NP=P["n_probes"]; n=len(K)

def depth_hist(rows):
    memo={}
    def parts(S):
        seen=set()
        for p in range(NP):
            g=defaultdict(list)
            for o in S: g[rows[o][p]].append(o)
            if len(g)>1: seen.add(tuple(sorted(tuple(v) for v in g.values())))
        return seen
    def feas(S,d):
        if len(S)<=1: return True
        if d<=0: return False
        k=(S,d)
        if k in memo: return memo[k]
        for b in sorted(parts(S),key=lambda x:max(len(y) for y in x)):
            if all(feas(t,d-1) for t in b): memo[k]=True; return True
        memo[k]=False; return False
    out=[]
    for c in joint:
        S=tuple(sorted(c))
        for d in range(0,5):
            if feas(S,d): out.append(d); break
    return Counter(out)

def masks(rows):
    pairs=[(a,b) for c in joint for a,b in itertools.combinations(sorted(c),2)]
    s=set()
    for p in range(NP):
        m=0
        for i,(a,b) in enumerate(pairs):
            if rows[a][p]!=rows[b][p]: m|=1<<i
        if m: s.add(m)
    return len(s), len(pairs)

real_h=depth_hist(K); real_m,npairs=masks(K)
print(f"REAL   depth histogram {dict(sorted(real_h.items()))}  depth3={real_h[3]}  masks={real_m}/{NP}")

print("\nNULL A -- independent row shuffle (destroys frame-index structure):")
d3=[]; mk=[]
for seed in range(40):
    rng=random.Random(1000+seed)
    NK=[]
    for r in K:
        rr=list(r); rng.shuffle(rr); NK.append(rr)
    h=depth_hist(NK); d3.append(h[3]); mk.append(masks(NK)[0])
print(f"  depth-3 count over 40 seeds: min={min(d3)} max={max(d3)} mean={sum(d3)/len(d3):.1f}   REAL={real_h[3]}")
print(f"  real above all {len(d3)} draws: {real_h[3]>max(d3)}")
print(f"  distinct coverage masks:     min={min(mk)} max={max(mk)} mean={sum(mk)/len(mk):.1f}   REAL={real_m}")

print("\nNULL B -- ONE global column permutation (keeps ALL inter-probe correlation):")
d3b=[]; mkb=[]
for seed in range(40):
    rng=random.Random(2000+seed)
    perm=list(range(NP)); rng.shuffle(perm)
    NK=[[r[perm[p]] for p in range(NP)] for r in K]
    h=depth_hist(NK); d3b.append(h[3]); mkb.append(masks(NK)[0])
print(f"  depth-3 count: min={min(d3b)} max={max(d3b)}   REAL={real_h[3]}   identical to real: {all(x==real_h[3] for x in d3b)}")
print(f"  masks:         min={min(mkb)} max={max(mkb)}   REAL={real_m}")
json.dump({"real_depth_hist":{str(k):v for k,v in real_h.items()},"real_masks":real_m,
 "nullA_depth3":{"min":min(d3),"max":max(d3),"mean":sum(d3)/len(d3)},
 "nullA_masks":{"min":min(mk),"max":max(mk),"mean":sum(mk)/len(mk)},
 "nullB_depth3":{"min":min(d3b),"max":max(d3b)},"nullB_masks":{"min":min(mkb),"max":max(mkb)},
 "seeds":40,"pairs":npairs}, open("/tmp/residual.json","w"), indent=2)
