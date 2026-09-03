#!/usr/bin/env python3
from itertools import product

P = 7
V = [
    (1,0,0), (0,1,0), (0,0,1),
    (1,1,0), (1,0,1), (0,1,1),
    (1,1,1),
]
M = (5,5,5,6,6,6,4)

# Displayed four-factorization in support order
PARTS = [
    (0,1,1,0,0,6,0),
    (1,0,1,0,6,0,0),
    (1,1,0,6,0,0,0),
    (3,3,3,0,0,0,4),
]

def add(a,b):
    return tuple((x+y) % P for x,y in zip(a,b))

def mul(a,k):
    return tuple((k*x) % P for x in a)

def sigma(c):
    s=(0,0,0)
    for n,v in zip(c,V):
        s=add(s,mul(v,n))
    return s

assert sum(M) == 37
assert sigma(M) == (0,0,0)

short=[]
for c in product(*[range(x+1) for x in M]):
    L=sum(c)
    if 1 <= L <= 7 and sigma(c) == (0,0,0):
        short.append(c)
assert short == []

assert tuple(sum(c[i] for c in PARTS) for i in range(7)) == M
assert [sum(c) for c in PARTS] == [8,8,8,13]
assert all(sigma(c) == (0,0,0) for c in PARTS)

# 7-short-freeness makes five disjoint zero-sums impossible in length 37.
assert 5*8 > 37

print("FAN_LENGTH37_WITNESS_GREEN length=37 short_le_7=0 four_pack=8,8,8,13 packing_exact=4")
