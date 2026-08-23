"""INDEPENDENT replay, written from primitive mod-5 addition with a different
state encoding (frozenset of (weight,sum) pairs) than the C searcher's bitboard.
Checks: (a) the f_7 witness has no zero-sum subsequence of length <=7;
        (b) the Freeze--Schmid 19-term witness has no TWO disjoint zero-sums;
        (c) the D_2 upper-bound argument on explicit random length-20 sequences."""
import random, itertools
P=5
def vadd(a,b): return ((a[0]+b[0])%P,(a[1]+b[1])%P,(a[2]+b[2])%P)

def min_zerosum_length(seq):
    """exact: smallest size of a nonempty subset summing to 0. brute DP by weight."""
    reach={0:{(0,0,0)}}
    for e in seq:
        new={}
        for w,S in reach.items():
            new.setdefault(w,set()).update(S)
            new.setdefault(w+1,set()).update(vadd(s,e) for s in S)
        reach=new
    for w in sorted(reach):
        if w>0 and (0,0,0) in reach[w]: return w
    return None

def has_k_disjoint(seq,k):
    """exact: can seq be split so that k disjoint nonempty parts each sum to 0?"""
    # state: tuple of k partial sums + tuple of k nonempty flags
    start=(((0,0,0),)*k,(False,)*k)
    states={start}
    for e in seq:
        new=set(states)
        for sums,flags in states:
            for i in range(k):
                s2=list(sums); f2=list(flags)
                s2[i]=vadd(sums[i],e); f2[i]=True
                new.add((tuple(s2),tuple(f2)))
        states=new
    tgt=(((0,0,0),)*k,(True,)*k)
    return tgt in states

W18=[(1,0,0),(0,1,0),(0,0,1),(0,1,4),(0,1,4),(1,0,4),(1,0,4),(1,0,4),(1,0,4),
     (1,4,1),(1,4,1),(1,4,1),(1,4,1),(4,1,0),(4,1,0),(4,1,0),(4,1,0),(4,2,0)]
e1,e2,e3=(1,0,0),(0,1,0),(0,0,1)
FS19=[e1]*4+[e2]*4+[e3]*4+[(1,1,0)]*2+[(1,0,1)]*2+[(0,1,1)]*3

print("f7 witness len          :",len(W18))
print("f7 witness min zero-sum :",min_zerosum_length(W18),"(must be >=8)")
print("f7 witness 2-disjoint?  :",has_k_disjoint(W18,2))
print("FS19 len                :",len(FS19))
print("FS19 min zero-sum       :",min_zerosum_length(FS19))
print("FS19 2-disjoint?        :",has_k_disjoint(FS19,2),"(must be False -> D2>=20)")
print("FS19 3-disjoint?        :",has_k_disjoint(FS19,3))

random.seed(11)
allv=[v for v in itertools.product(range(P),repeat=3) if v!=(0,0,0)]
bad=0
for _ in range(300):
    s=[random.choice(allv) for _ in range(20)]
    if not has_k_disjoint(s,2): bad+=1
print("random length-20 seqs without 2 disjoint zero-sums:",bad,"/300 (D2<=20 predicts 0)")
