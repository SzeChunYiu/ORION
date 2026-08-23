"""Cache the QG-34 primitives, all recomputed from main: the 715 local-Clifford
orbit reps, their 384 indexed probe responses K_p, the 45-class bulk signature,
the 54-class unlabeled spectrum, and the 92 joint classes."""
import itertools, json, sys
from collections import defaultdict
from pathlib import Path
QDIR = Path("research/extensions/orion-q").resolve(); sys.path.insert(0, str(QDIR))
import max_r6_p10_candidate_blind_frame_optimizer as p10
import max_r6s_all_n_composition as r6s
BITS=((0,0),(1,0),(1,1),(0,1)); CODE={b:i for i,b in enumerate(BITS)}
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
aa=autos(); ps=list(itertools.product((0,1),repeat=3)); aux=aux48()
obs={}
for t in itertools.product(range(4),repeat=6):
    o=orbit(t,aa); obs.setdefault(min(o),set()).update(o)
reps=sorted(obs)
K=[]; bulk=[]; spec=[]
c=(0,0,0)
for r in reps:
    row=[]
    for p in ps:
        pt=perm(r,p); tkeys=tuple(key1(x) for x in pt); b=baseline(r,p)
        for fr,tag,fkeys,tkey in aux:
            row.append(int(r6s.config_cost(tkeys,fkeys,tkey,c,1))-b)
    K.append(row); spec.append(sorted(row))
    bulk.append([baseline(r,p) for p in ps[:4]])
jc=defaultdict(list)
for i,r in enumerate(reps): jc[(tuple(bulk[i]),tuple(spec[i]))].append(i)
joint=[sorted(v) for v in jc.values()]
out={"n_reps":len(reps),"n_probes":len(ps)*len(aux),
     "reps":[list(r) for r in reps],"K":K,
     "bulk_classes":len({tuple(b) for b in bulk}),
     "spectrum_classes":len({tuple(s) for s in spec}),
     "joint_classes":len(joint),
     "joint":sorted(joint,key=lambda s:(-len(s),s)),
     "joint_size_histogram":{str(k):v for k,v in sorted(
         __import__("collections").Counter(len(s) for s in joint).items())}}
json.dump(out,open("/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/qg34/primitives.json","w"))
print("reps",out["n_reps"],"probes",out["n_probes"],"bulk",out["bulk_classes"],
      "spectrum",out["spectrum_classes"],"joint",out["joint_classes"])
print("joint size histogram:",out["joint_size_histogram"])
print("largest joint class:",max(len(s) for s in joint))
