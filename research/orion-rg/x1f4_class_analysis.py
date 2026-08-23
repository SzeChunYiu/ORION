import numpy as np, collections, json, pickle, itertools
A=np.load("wit.npy")
canon=[tuple(int(x) for x in l.split()) for l in open("canon_all.txt")]
assert len(canon)==A.shape[0]
pref=pickle.load(open("ext_prefixes.pkl","rb"))
# --- extension flag per witness (file order), then check class-constancy
ext=[tuple(r.tolist()) in pref for r in A]
print("witnesses with >=1 six-element zero-sum extension:",sum(ext),"(expect 45970)")
byclass=collections.defaultdict(lambda:[0,0])   # class -> [n, n_ext]
for c,e in zip(canon,ext):
    byclass[c][0]+=1; byclass[c][1]+= (1 if e else 0)
mixed=[c for c,(n,ne) in byclass.items() if ne not in (0,n)]
print("classes with MIXED extension flag:",len(mixed),"(must be 0 -- GL-invariance)")
print("classes:",len(byclass))

V={c:(c//25,(c//5)%5,c%5) for c in range(125)}
def add(a,b): return 25*((V[a][0]+V[b][0])%5)+5*((V[a][1]+V[b][1])%5)+((V[a][2]+V[b][2])%5)
def smul(t,c): return 25*((t*V[c][0])%5)+5*((t*V[c][1])%5)+((t*V[c][2])%5)

def zs_dist(codes):
    cnt=collections.Counter(codes)
    cur={(0,0):1}
    for code,m in cnt.items():
        nxt=collections.defaultdict(int)
        for (s,k),n in cur.items():
            t_s=s
            for t in range(m+1):
                nxt[(t_s,k+t)]+=n
                t_s=add(t_s,code)
        cur=nxt
    d=collections.Counter()
    for (s,k),n in cur.items():
        if s==0 and k>0: d[k]+=n
    return d

# ---- PG(2,5): 31 points, 31 lines
def proj(c):
    v=V[c]
    for i in range(3):
        if v[i]: 
            inv=[0,1,3,2,4][v[i]]
            return tuple((x*inv)%5 for x in v)
    return None
PTS=sorted({proj(c) for c in range(1,125)})
assert len(PTS)==31
def dot(u,v): return (u[0]*v[0]+u[1]*v[1]+u[2]*v[2])%5
LINES=[frozenset(p for p in PTS if dot(p,L)==0) for L in PTS]
assert all(len(l)==6 for l in LINES) and len(set(LINES))==31

classes=[]
for c,(n,ne) in byclass.items():
    cnt=collections.Counter(c)
    sup=sorted(cnt)
    k=len(sup)
    prof=tuple(sorted(cnt.values()))
    d=zs_dist(c)
    mn=min(d); tot=sum(d.values())
    dist=tuple(sorted(d.items()))
    # projective structure
    pmap=collections.defaultdict(list)
    for s in sup: pmap[proj(s)].append(s)
    ppts=set(pmap)
    npp=len(ppts)
    inter=sorted((len(ppts & L) for L in LINES), reverse=True)
    maxline=inter[0]
    n_lines_ge3=sum(1 for x in inter if x>=3)
    # "fiber profile": for each projective point, multiset of mults of its support elements
    fib=tuple(sorted(tuple(sorted(cnt[s] for s in pmap[p])) for p in pmap))
    classes.append(dict(seq=list(c),count=n,ext=(ne>0),k=k,prof=prof,npp=npp,
                        maxline=maxline,n_lines_ge3=n_lines_ge3,arc=(maxline<=2),
                        fib=fib,minzs=mn,nzs=tot,zsdist=dist))
# attach stab/orbit
raw={tuple(x["seq"]):x for x in json.load(open("classes_raw.json"))}
for cl in classes:
    r=raw[tuple(cl["seq"])]
    assert r["count"]==cl["count"]
    cl["stab"]=r["stab"]; cl["orbit"]=r["orbit"]; cl["N"]=r["N"]
classes.sort(key=lambda x:(-x["count"],x["seq"]))
json.dump(classes,open("classes.json","w"))
print()
print("=== summary ===")
print("total orbit size (all length-19 no-2-disjoint sequences):",sum(c["orbit"] for c in classes))
print("min zero-sum length across classes:",sorted(collections.Counter(c["minzs"] for c in classes).items()))
print("support size k:",sorted(collections.Counter(c["k"] for c in classes).items()))
print("#projective points:",sorted(collections.Counter(c["npp"] for c in classes).items()))
print("max line-intersection of proj. support:",sorted(collections.Counter(c["maxline"] for c in classes).items()))
print("arcs (no 3 collinear):",sum(1 for c in classes if c["arc"]))
print("stab:",sorted(collections.Counter(c["stab"] for c in classes).items()))
print("extendable classes:",sum(1 for c in classes if c["ext"]),"/",len(classes))
print("  -> normalized witnesses in extendable classes:",sum(c["count"] for c in classes if c["ext"]))
print("  -> orbit-weighted:",sum(c["orbit"] for c in classes if c["ext"]))
print("#distinct zero-sums, range:",min(c["nzs"] for c in classes),"-",max(c["nzs"] for c in classes))
print("distinct multiplicity profiles:",len({c["prof"] for c in classes}))
