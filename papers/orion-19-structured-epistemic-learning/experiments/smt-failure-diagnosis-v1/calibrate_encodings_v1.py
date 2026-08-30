#!/usr/bin/env python3
"""Calibration for ORION-19: which encoding is fast, and where does the reference hold?
Measures only encoding cost. No diagnosis, no arms, no terminal."""
import time, z3, json, os
B = 5000
def t(build, p, ms=B):
    s = build(p); s.set("timeout", ms)
    a = time.time(); r = s.check(); return str(r), round(time.time()-a, 3)

def php_int(n):
    s=z3.Solver(); h=[z3.Int(f"h{i}") for i in range(n+1)]
    for x in h: s.add(x>=0, x<n)
    s.add(z3.Distinct(h)); return s
def php_bool(n):
    s=z3.Solver(); p=[[z3.Bool(f"p{i}_{j}") for j in range(n)] for i in range(n+1)]
    for i in range(n+1): s.add(z3.Or(p[i]))
    for j in range(n):
        for a in range(n+1):
            for b in range(a+1,n+1): s.add(z3.Or(z3.Not(p[a][j]), z3.Not(p[b][j])))
    return s
def php_bv(n):
    W=max(3,(n).bit_length()+1); s=z3.Solver(); h=[z3.BitVec(f"v{i}",W) for i in range(n+1)]
    for x in h: s.add(z3.ULT(x, n))
    s.add(z3.Distinct(h)); return s
def col_int(k):
    s=z3.Solver(); c=[z3.Int(f"c{i}") for i in range(k+1)]
    for x in c: s.add(x>=0, x<k)
    for a in range(k+1):
        for b in range(a+1,k+1): s.add(c[a]!=c[b])
    return s
def col_bool(k):
    s=z3.Solver(); v=[[z3.Bool(f"v{i}_{j}") for j in range(k)] for i in range(k+1)]
    for i in range(k+1):
        s.add(z3.Or(v[i]))
        for a in range(k):
            for b in range(a+1,k): s.add(z3.Or(z3.Not(v[i][a]), z3.Not(v[i][b])))
    for a in range(k+1):
        for b in range(a+1,k+1):
            for j in range(k): s.add(z3.Or(z3.Not(v[a][j]), z3.Not(v[b][j])))
    return s
def lin_int(m):
    s=z3.Solver(); x=[z3.Int(f"x{i}") for i in range(m)]
    for i in range(m): s.add(x[i]>=1, x[i]<=3)
    s.add(z3.Sum(x)<=m); s.add(z3.Sum([x[i]*(i+1) for i in range(m)])>=2*sum(range(1,m+1)))
    return s
def lin_bv(m):
    W=12; s=z3.Solver(); x=[z3.BitVec(f"b{i}",W) for i in range(m)]
    for i in range(m): s.add(z3.UGE(x[i],1), z3.ULE(x[i],3))
    tot=x[0]
    for i in range(1,m): tot=tot+x[i]
    s.add(z3.ULE(tot,m))
    w=x[0]*1
    for i in range(1,m): w=w+x[i]*(i+1)
    s.add(z3.UGE(w, 2*sum(range(1,m+1)))); return s

FAM={"pigeonhole":[("int",php_int),("bool",php_bool),("bv",php_bv)],
     "colouring":[("int",col_int),("bool",col_bool)],
     "linear":[("int",lin_int),("bv",lin_bv)]}
PAR={"pigeonhole":[6,7,8,9,10,11],"colouring":[6,8,10,12,14,16],"linear":[10,14,18,22,26,30]}
out={}
for fam,encs in FAM.items():
    print(f"--- {fam} ---")
    out[fam]={}
    for p in PAR[fam]:
        row={}
        for name,b in encs:
            v,dt=t(b,p); row[name]=(v,dt)
        out[fam][p]=row
        print("  p=%-3s " % p + "  ".join(f"{n}={row[n][0]}/{row[n][1]:.2f}s" for n,_ in encs), flush=True)
json.dump({f:{str(k):v for k,v in d.items()} for f,d in out.items()},
          open(os.path.expanduser("~/o19_CAL.json"),"w"), indent=1)
