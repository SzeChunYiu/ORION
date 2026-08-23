"""Independent re-derivation of the QG-36 instance witness, recomputing every
response from the primitives rather than reading any cache."""
import itertools, sys
from pathlib import Path
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
def response(t):
    out=[]; c=(0,0,0)
    for p in PS:
        pt=perm(t,p); tk=tuple(key1(x) for x in pt); b=baseline(t,p)
        for fr,tag,fk,tkey in AUX:
            out.append(int(r6s.config_cost(tk,fk,tkey,c,1))-b)
    return out
L={"I":0,"X":1,"Y":2,"Z":3}
def parse(s): return tuple(L[ch] for ch in s)
A,B,X="IXIYXZ","IXIYYZ","IIIIIX"
ra,rb,rx=response(parse(A)),response(parse(B)),response(parse(X))
ba=[baseline(parse(A),p) for p in PS[:4]]; bb=[baseline(parse(B),p) for p in PS[:4]]
print("column-level:")
print(f"  bulk({A}) == bulk({B})        : {ba==bb}")
print(f"  spectrum({A}) == spectrum({B}): {sorted(ra)==sorted(rb)}")
print(f"  per-column optima            : {min(ra)}, {min(rb)}, {min(rx)}")
ca=min(ra[p]+rx[p] for p in range(len(ra)))
cb=min(rb[p]+rx[p] for p in range(len(rb)))
print("instance-level, shared frame:")
print(f"  cost({{{A},{X}}}) = {ca}")
print(f"  cost({{{B},{X}}}) = {cb}")
print(f"  DIFFER: {ca!=cb}   (aggregate cheap summaries are identical)")
