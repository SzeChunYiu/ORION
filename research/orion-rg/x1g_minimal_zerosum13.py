"""Every minimal zero-sum sequence U of length D(C_5^3)=13 satisfies U = S*(-sigma(S))
for S = U minus any one element, and every such S is ZSF of length 12.  So the
26369 ZSF-12 classes surject onto ALL classes of maximal-length minimal zero-sum
sequences.  Validation identity:
      #ZSF-12 sequences  =  sum over minimal zero-sum U of |supp(U)|
(the S's with S*(-sigma(S)) = U are exactly U\\{u}, u in supp(U))."""
import json, collections, subprocess
raw=json.load(open("zsf12_classes.json"))
V={c:(c//25,(c//5)%5,c%5) for c in range(125)}
def add(a,b): return 25*((V[a][0]+V[b][0])%5)+5*((V[a][1]+V[b][1])%5)+((V[a][2]+V[b][2])%5)
NEG={c:25*((5-V[c][0])%5)+5*((5-V[c][1])%5)+((5-V[c][2])%5) for c in range(125)}
def tj(cs): return "["+",".join("[%d,%d,%d]"%(c//25,(c//5)%5,c%5) for c in cs)+"]"
Us=[]
for x in raw:
    s=0
    for c in x["seq"]: s=add(s,c)
    assert s!=0
    Us.append(sorted(x["seq"]+[NEG[s]]))
r=subprocess.run(["./canon2","canon","13"],input="\n".join(tj(u) for u in Us)+"\n",capture_output=True,text=True)
assert r.returncode==0, r.stderr[:300]
cans=[tuple(int(y) for y in l.split()) for l in r.stdout.strip().split("\n")]
uc=collections.Counter(cans)
print("GL(3,5)-classes of MINIMAL ZERO-SUM sequences of length D(C_5^3)=13 :",len(uc))
reps=list(uc)
r=subprocess.run(["./canon2","stab","13"],input="\n".join(tj(u) for u in reps)+"\n",capture_output=True,text=True)
st=[int(l.split()[0]) for l in r.stdout.strip().split("\n")]
GL=1488000
tot=0; chk=0; rows=[]
for u,s in zip(reps,st):
    assert GL%s==0
    orb=GL//s; k=len(set(u))
    tot+=orb; chk+=orb*k
    rows.append({"seq":list(u),"stab":s,"orbit":orb,"k":k,"maxmult":max(collections.Counter(u).values())})
print("total minimal zero-sum sequences of length 13 :",tot)
print("VALIDATION  sum over U of |supp(U)| = %d"%chk)
print("            #ZSF-12 sequences       = %d"%sum(x['orbit'] for x in raw))
print("            MATCH                   =",chk==sum(x['orbit'] for x in raw))
print()
print("max multiplicity of U  (the rank-3 analogue of Property B would force 4):")
t=collections.defaultdict(lambda:[0,0])
for x in rows: t[x["maxmult"]][0]+=1; t[x["maxmult"]][1]+=x["orbit"]
for k in sorted(t): print("   maxmult=%d : %6d classes, %14d sequences"%(k,t[k][0],t[k][1]))
print()
print("support size of U:")
t=collections.Counter(x["k"] for x in rows); print("  ",sorted(t.items()))
print("stabilizers:",sorted(collections.Counter(x["stab"] for x in rows).items()))
def fmt(seq):
    c=collections.Counter(seq); return " ".join("(%d%d%d)^%d"%(V[k][0],V[k][1],V[k][2],m) for k,m in sorted(c.items()))
print()
print("most symmetric classes:")
for x in sorted(rows,key=lambda y:-y["stab"])[:5]:
    print("   |Stab|=%3d orbit=%8d maxmult=%d  %s"%(x["stab"],x["orbit"],x["maxmult"],fmt(x["seq"])))
json.dump({"n_classes":len(uc),"n_sequences":tot,"validation_sum_supp":chk,
           "classes":[{**x,"pretty":fmt(x["seq"])} for x in rows]},open("mzs13_classes.json","w"))
