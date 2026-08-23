import json, collections, itertools, subprocess
raw=json.load(open("zsf12_classes.json"))
CLS={tuple(x["seq"]):x for x in raw}
V={c:(c//25,(c//5)%5,c%5) for c in range(125)}
def add(a,b): return 25*((V[a][0]+V[b][0])%5)+5*((V[a][1]+V[b][1])%5)+((V[a][2]+V[b][2])%5)
NEG={c:25*((5-V[c][0])%5)+5*((5-V[c][1])%5)+((5-V[c][2])%5) for c in range(125)}
def tj(cs): return "["+",".join("[%d,%d,%d]"%(c//25,(c//5)%5,c%5) for c in cs)+"]"
def canon(seqs,L):
    r=subprocess.run(["./canon2","canon",str(L)],input="\n".join(tj(s) for s in seqs)+"\n",
                     capture_output=True,text=True); assert r.returncode==0,r.stderr[:300]
    return [tuple(int(x) for x in l.split()) for l in r.stdout.strip().split("\n")]

# ---- (A) close the open item: which ZSF-12 classes are D_2-witness complements? ----
comp=json.load(open("complements.json"))["complement_classes"]      # from canon.c
recan=canon([c["seq"] for c in comp],12)                            # re-canonicalize with canon2
agree=sum(1 for c,r in zip(comp,recan) if tuple(c["seq"])==r)
print("(A) canon.c vs canon2.c agree on the %d complement reps: %d"%(len(comp),agree))
S_comp=set(recan)
print("    distinct ZSF-12 classes arising as D_2-witness complements :",len(S_comp))
print("    total ZSF-12 classes                                       :",len(CLS))
print("    ALL complements are genuine ZSF-12 classes                 :",S_comp<=set(CLS))
w=sum(CLS[c]["orbit"] for c in S_comp)
print("    fraction of classes  : %d / %d = %.4f%%"%(len(S_comp),len(CLS),100*len(S_comp)/len(CLS)))
print("    fraction of sequences: %d / %d = %.4f%%"%(w,sum(x['orbit'] for x in raw),100*w/sum(x['orbit'] for x in raw)))
# separating criterion?
print()
print("    invariant contrasts (complement-classes vs the rest):")
for key in ["k","maxmult","maxline","mb","ext_maxmult"]:
    a=collections.Counter(CLS[c][key] for c in S_comp)
    b=collections.Counter(x[key] for x in raw if tuple(x["seq"]) not in S_comp)
    ks=sorted(set(a)|set(b))
    print("      %-12s complements %s"%(key,{k:a.get(k,0) for k in ks}))
    print("      %-12s others      %s"%("",{k:b.get(k,0) for k in ks}))

# ---- (B) inductive structure theorem via an element of multiplicity 4 ----
R2=json.load(open("rank2_C5x2.json"))
R2CLS={tuple(c["seq"]):c for c in R2["classes"]}
def canon2d(seq):     # GL(2,5) canonical form, same scheme
    cnt=collections.Counter(seq); sup=sorted(cnt); best=None
    W={c:(c//5,c%5) for c in range(25)}; INV=[0,1,3,2,4]
    for i in sup:
        for j in sup:
            if i==j: continue
            (a,b),(c,d)=W[i],W[j]; det=(a*d-b*c)%5
            if not det: continue
            iv=INV[det]; M=(((d*iv)%5,(-b*iv)%5),((-c*iv)%5,(a*iv)%5))
            pm=sorted((5*((W[s][0]*M[0][0]+W[s][1]*M[1][0])%5)+((W[s][0]*M[0][1]+W[s][1]*M[1][1])%5),cnt[s]) for s in sup)
            e=tuple(cc for cc,m in pm for _ in range(m))
            if best is None or e<best: best=e
    return best
def quotient(seq,g):
    """image of seq in G/<g> ~= C_5^2, coordinates via a complement basis"""
    gv=V[g]
    # find two vectors completing g to a basis
    basis=None
    for u in range(1,125):
        for w in range(1,125):
            a,b,c=gv; d,e,f=V[u]; h,i,j=V[w]
            if (a*(e*j-f*i)-b*(d*j-f*h)+c*(d*i-e*h))%5:
                basis=(u,w); break
        if basis: break
    u,w=basis
    # solve x = alpha*g + beta*u + gamma*w ; quotient coord = (beta,gamma)
    tbl={}
    for al in range(5):
        for be in range(5):
            for ga in range(5):
                x=0
                for _ in range(al): x=add(x,g)
                for _ in range(be): x=add(x,u)
                for _ in range(ga): x=add(x,w)
                tbl.setdefault(x,(be,ga))
    return [5*tbl[c][0]+tbl[c][1] for c in seq]
def is_zsf2(codes):
    W={c:(c//5,c%5) for c in range(25)}
    def a2(x,y): return 5*((W[x][0]+W[y][0])%5)+((W[x][1]+W[y][1])%5)
    R=set()
    for v in codes:
        R = R|{a2(s,v) for s in R}|{v}
        if 0 in R: return False
    return True
m4=[x for x in raw if x["maxmult"]==4]
print()
print("(B) inductive reduction:  m(g)=4  =>  S = g^4 * T  and  T mod <g>  is ZSF of length 8 over C_5^2")
print("    classes with an element of multiplicity 4 :",len(m4),"/",len(raw))
import random
rng=random.Random(11); test=[m4[rng.randrange(len(m4))] for _ in range(300)]
bad=0; shapes=collections.Counter()
for x in test:
    cnt=collections.Counter(x["seq"]); g=[c for c,m in cnt.items() if m==4][0]
    T=list(x["seq"]);
    for _ in range(4): T.remove(g)
    Q=quotient(T,g)
    if 0 in Q or not is_zsf2(Q) or len(Q)!=8: bad+=1; continue
    shapes[canon2d(Q)]+=1
print("    300 sampled classes: quotient FAILS to be a maximal ZSF-8 over C_5^2 in",bad,"cases (expect 0)")
print("    the quotients land in",len(shapes),"of the 18 rank-2 classes")
print()
print("    OBSTRUCTION: classes with NO element of multiplicity 4 =",len(raw)-len(m4),
      "(%.1f%% of classes, %d sequences)"%(100*(len(raw)-len(m4))/len(raw),
      sum(x['orbit'] for x in raw if x['maxmult']<4)))
json.dump({"complement_classes":len(S_comp),"total_zsf12_classes":len(CLS),
           "complement_sequence_weight":w,"total_sequence_weight":sum(x['orbit'] for x in raw),
           "classes_with_mult4":len(m4),"quotient_test_failures":bad,
           "rank2_classes_hit":len(shapes)},open("zsf12_structure.json","w"),indent=1)
