#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json


def normalize(v,p):
    v=tuple(x%p for x in v)
    for x in v:
        if x:
            inv=pow(x,-1,p)
            return tuple(y*inv%p for y in v)
    raise ValueError


def cross(a,b,p):
    return normalize((a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]),p)


def dot(a,b,p):
    return sum(x*y for x,y in zip(a,b))%p


def data(p):
    pts=sorted({normalize((a,b,c),p) for a in range(p) for b in range(p) for c in range(p) if (a,b,c)!=(0,0,0)})
    conic=sorted({normalize((1,t,t*t),p) for t in range(p)}|{(0,0,1)})
    missing=conic[0]
    full=[x for x in conic if x!=missing]
    off=[x for x in pts if x not in set(conic)]
    return full,off


def compatible_pair(p,full,D,E):
    centers=[D,E]
    n=len(full)+2
    adj=[[] for _ in range(n)]
    for z,C in enumerate(centers):
        mu=len(full)+z
        for i,j in itertools.combinations(range(len(full)),2):
            line=cross(full[i],full[j],p)
            if dot(C,line,p):
                continue
            sol=[]
            for a in range(1,p):
                for b in range(1,p):
                    v=tuple((a*full[i][k]+b*full[j][k])%p for k in range(3))
                    if v==C:
                        sol.append((a,b))
            assert len(sol)==1
            a,b=sol[0]
            adj[mu].append((i,a)); adj[i].append((mu,pow(a,-1,p)))
            adj[mu].append((j,b)); adj[j].append((mu,pow(b,-1,p)))

    values=[None]*n
    for start in range(n):
        if values[start] is not None:
            continue
        values[start]=1
        stack=[start]
        while stack:
            u=stack.pop()
            for v,r in adj[u]:
                proposed=values[u]*r%p
                if values[v] is None:
                    values[v]=proposed
                    stack.append(v)
                elif values[v]!=proposed:
                    return False
    return True


def main()->int:
    expected={5:(125,175),7:(84,1092),11:(0,7260),13:(0,14196)}
    rows=[]
    for p in (5,7,11,13):
        full,off=data(p)
        assert len(full)==p and len(off)==p*p
        yes=no=0
        for i,j in itertools.combinations(range(len(off)),2):
            if compatible_pair(p,full,off[i],off[j]): yes+=1
            else: no+=1
        assert (yes,no)==expected[p],(p,yes,no)
        rows.append({'p':p,'full_arc_size':len(full),'compatible_distinct_offconic_pairs':yes,'incompatible_distinct_offconic_pairs':no})

    print(json.dumps({
        'status':'SATURATED_P_ARC_SCALAR_UNIQUENESS_INDEPENDENT_GREEN',
        'pair_replays':rows,
        'p5_compatible_pairs':125,
        'p7_compatible_pairs':84,
        'p_ge_11_compatible_pairs':0,
        'method':'delete one conic point and propagate saturated full-full secant gains',
    }, sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
