#!/usr/bin/env python3
"""Classify exact-support-six faces among the already frozen p=7 (19,10) pair candidates.

This is a bounded control. It independently reimplements the stage-one pair predicate with
cardinality-indexed subset sums, asserts the frozen 538/24/0 totals, then reports only
support/rank/overlap strata.
"""
from collections import Counter, defaultdict
from itertools import combinations_with_replacement

P=7
VEC=[(x,y,z) for x in range(P) for y in range(P) for z in range(P)]
IDX={v:i for i,v in enumerate(VEC)}
def add(a,b): return tuple((a[i]+b[i])%P for i in range(3))
def neg(a): return tuple((-x)%P for x in a)
def inv(a): return pow(a,-1,P)
def make_u(a):
    u=inv(a)
    return Counter({(1,0,0):6,(0,1,0):6,(0,0,1):a,((-u)%P,(-u)%P,1):P-a})

def zero_sum_short(base, extra, h):
    seq=[]
    for g,m in (base+extra).items(): seq += [g]*m
    dp=[set() for _ in range(h+1)]; dp[0].add((0,0,0))
    for g in seq:
        for k in range(h,0,-1):
            dp[k] |= {add(s,g) for s in dp[k-1]}
    return any((0,0,0) in dp[k] for k in range(1,h+1))

def rank_mod7(supp):
    rows=[list(v) for v in supp]; rank=0
    for col in range(3):
        piv=next((i for i in range(rank,len(rows)) if rows[i][col]),None)
        if piv is None: continue
        rows[rank],rows[piv]=rows[piv],rows[rank]
        q=inv(rows[rank][col]); rows[rank]=[(q*x)%P for x in rows[rank]]
        for i in range(len(rows)):
            if i!=rank and rows[i][col]:
                f=rows[i][col]; rows[i]=[(rows[i][c]-f*rows[rank][c])%P for c in range(3)]
        rank+=1
    return rank

def enumerate_v(base,m=10,h=9):
    # Simple bounded multiset DFS. The final term is forced by total sum.
    allowed=[g for g in VEC if g!=(0,0,0) and base[g]<6]
    out=[]; chosen=[]; mult=Counter(); total=(0,0,0)
    # A cheap exact filter is applied only at complete candidates; p=7 keeps this bounded enough.
    def rec(start,depth,total):
        if depth==m-1:
            x=neg(total)
            if x==(0,0,0) or x not in allowed: return
            if chosen and IDX[x] < IDX[chosen[-1]]: return
            if mult[x] >= 6-base[x]: return
            c=Counter(chosen+[x])
            if not zero_sum_short(base,c,h): out.append(c)
            return
        for pos in range(start,len(allowed)):
            x=allowed[pos]
            if mult[x] >= 6-base[x]: continue
            chosen.append(x); mult[x]+=1
            rec(pos,depth+1,add(total,x))
            mult[x]-=1; chosen.pop()
    # Use the exact old allowed ordering.
    allowed.sort(key=lambda g: IDX[g])
    rec(0,0,(0,0,0))
    return out

def main():
    totals=[]; faces=[]; cats={}; mults={}
    for a in (1,2,3):
        U=make_u(a); light=(0,0,1); u=inv(a); heavy=((-u)%P,(-u)%P,1)
        vs=enumerate_v(U)
        totals.append(len(vs)); fc=0; cc=Counter(); mm=Counter()
        for V in vs:
            union=set(U)|set(V)
            if len(union)!=6: continue
            fc+=1; supp=list(V); r=rank_mod7(supp); cl=V[light]; ch=V[heavy]
            cc[(len(supp),r,bool(cl),bool(ch))]+=1; mm[(cl,ch)]+=1
            assert len(supp) in (3,4)
            assert (len(supp)==3 and r==2) or (len(supp)==4 and r==3)
            assert int(cl>0)+int(ch>0)==len(supp)-2
        faces.append(fc); cats[a]=cc; mults[a]=mm
    assert totals==[538,24,0], totals
    print({'status':'SUPPORT6_PAIR_FACE_81019_GREEN','total':totals,'face':faces,
           'categories':{a:{str(k):v for k,v in cats[a].items()} for a in cats},
           'shared_multiplicities':{a:{str(k):v for k,v in mults[a].items()} for a in mults}})
if __name__=='__main__': main()
