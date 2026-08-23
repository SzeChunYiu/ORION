"""Build SixLCU per-column primitives from origin/main's qg4_second_family cost model.
Type universe {I,X,Y,Z}^6 = 4096 (same as TARE); choice set = 2430 (part,phi) pairs."""
import sys, json, itertools, random
import numpy as np
sys.path.insert(0, "/Users/billy/Desktop/projects/ORION-claude/research/extensions/orion-qg")
import qg4_second_family as qg4

OUT="/private/tmp/claude-501/-Users-billy/07b03b4b-2ab6-48a7-92ed-098b720c327b/scratchpad/broadclass"
PARTS=qg4.PARTITIONS; assert len(PARTS)==203

COLS=list(itertools.product(range(4),repeat=6)); assert len(COLS)==4096
COL_INDEX={c:i for i,c in enumerate(COLS)}
A=np.array(COLS,dtype=np.int64)
POW=np.array([4**(5-j) for j in range(6)],dtype=np.int64)
assert (A@POW == np.arange(4096)).all(), "column indexing convention"
NZ=(A!=0)

# ---- choices and response tensor ----
CHOICES=[]
for pi,part in enumerate(PARTS):
    for phi in itertools.product((0,1),repeat=len(part)): CHOICES.append((pi,phi))
CH_INDEX={c:i for i,c in enumerate(CHOICES)}; NC=len(CHOICES); assert NC==2430

K=np.zeros((4096,NC),dtype=np.int16); ci=0
for pi,part in enumerate(PARTS):
    k=len(part); flag=1 if k>=2 else 0; c0=[];c1=[]
    for block in part:
        m=len(block); b=qg4.bbits(m)
        nq=NZ[:,list(block)].sum(axis=1).astype(np.int16)
        first=A[:,block[0]]; F=(first!=0)
        for i in block[1:]: F&=(A[:,i]==first)
        F=F.astype(np.int16)
        c0.append(((flag+b+1)*nq).astype(np.int16))
        c1.append(((flag+1)*F+(flag+b+1)*(nq-m*F)).astype(np.int16))
    for phi in itertools.product((0,1),repeat=k):
        tot=np.zeros(4096,dtype=np.int16)
        for bi in range(k): tot+=c1[bi] if phi[bi] else c0[bi]
        K[:,ci]=tot; ci+=1
assert ci==NC

def const_part(part,shared):
    k=len(part); flag=1 if k>=2 else 0
    prep=(0 if k==1 else 2*k-3)+sum((len(b)-1)*(1+flag)+qg4.DS[len(b)] for b in part if len(b)>=2)
    bs=[qg4.bbits(len(b)) for b in part]
    return prep+(k if k>=2 else 0)+((max(bs) if bs else 0) if shared else sum(bs))

# ---- V1: K against qg4.member_cost at n=1 ----
random.seed(1); bad=0
for _ in range(500):
    col=random.choice(COLS); pi,phi=random.choice(CHOICES); part=PARTS[pi]; sh=random.choice([True,False])
    ref=qg4.member_cost(list(col),1,part,phi,sh)-const_part(part,sh)
    bad += (ref != K[COL_INDEX[col],CH_INDEX[(pi,phi)]])
print(f"V1 response tensor vs qg4.member_cost: {bad} mismatches / 500")

# ---- group actions ----
LETTER=[(0,)+p for p in itertools.permutations((1,2,3))]          # 6
SLOT=list(itertools.permutations(range(6)))                        # 720
def canon_part(blocks):
    bl=sorted(tuple(sorted(b)) for b in blocks); return tuple(sorted(bl,key=lambda b:b[0]))
# choice action: part -> sigma^{-1}(part) so that {col[sigma[j]]: j in B'} = {col[i]: i in B}
PART_MAP=np.zeros((720,203),dtype=np.int32); PHI_MAP={}
for si,sg in enumerate(SLOT):
    inv=[0]*6
    for j,v in enumerate(sg): inv[v]=j
    for pi,part in enumerate(PARTS):
        img=[tuple(sorted(inv[i] for i in b)) for b in part]
        new=canon_part(img); PART_MAP[si,pi]=qg4.PART_INDEX[new]
        order=sorted(range(len(part)),key=lambda bi:min(img[bi]))
        PHI_MAP[(si,pi)]=order                # new block pos p holds old block order[p]
CH_MAP=np.zeros((720,NC),dtype=np.int32)
for si in range(720):
    for c,(pi,phi) in enumerate(CHOICES):
        npi=PART_MAP[si,pi]; order=PHI_MAP[(si,pi)]
        CH_MAP[si,c]=CH_INDEX[(int(npi),tuple(phi[order[p]] for p in range(len(phi))))]

def act(si,li):
    """index map on columns: (g.col)[j] = tau[col[sigma[j]]]"""
    tau=np.array(LETTER[li]); return (tau[A[:,list(SLOT[si])]]@POW)

# ---- V2: equivariance  K[g.t][g.c] == K[t][c] ----
random.seed(2); bad=0
for _ in range(200):
    si=random.randrange(720); li=random.randrange(6)
    img=act(si,li); t=random.randrange(4096); c=random.randrange(NC)
    bad += (K[img[t],CH_MAP[si,c]] != K[t,c])
print(f"V2 equivariance K[g.t][g.c]==K[t][c]: {bad} mismatches / 200")

# ---- V3: orbit counts ----
canonL=np.arange(4096)
for li in range(6): canonL=np.minimum(canonL,act(0,li))
nL=len(set(canonL.tolist()))
canonF=np.arange(4096)
for si in range(720):
    for li in range(6): canonF=np.minimum(canonF,act(si,li))
nF=len(set(canonF.tolist()))
print(f"V3 letter-orbits (S_3): {nL}  (Burnside (4096+3*64+2)/6 = {(4096+3*64+2)//6})")
print(f"V3 full orbits (S_3 x S_6): {nF}  (hand count 23)")

np.savez_compressed(f"{OUT}/sixlcu_prims.npz",K=K,canonL=canonL,canonF=canonF,
                    CH_MAP=CH_MAP,PART_MAP=PART_MAP,A=A)
json.dump({"choices":[[pi,list(phi)] for pi,phi in CHOICES],
           "parts":[[list(b) for b in p] for p in PARTS],
           "const_shared":[const_part(p,True) for p in PARTS],
           "const_dedicated":[const_part(p,False) for p in PARTS]},
          open(f"{OUT}/sixlcu_meta.json","w"))
print("saved.")
