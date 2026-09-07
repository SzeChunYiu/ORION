#!/usr/bin/env python3
import math

P=7
D=19

def zhao(N,k,i):
    return math.comb(N-k,k-i)+(-1)**i*math.comb(N-k+i-1,k-1)

assert zhao(37,11,2)%P == 6
assert zhao(29,11,2)%P == 4
assert zhao(27,11,2)%P == 4

triples=set()
triples.add((8,10,19))
for x in range(9,13):
    y=28-x
    if x<=y<=D:
        triples.add(tuple(sorted((9,x,y))))
triples.add((10,10,17))
expected={(8,10,19),(9,9,19),(9,10,18),(9,11,17),(9,12,16),(10,10,17)}
assert triples==expected
assert all(sum(t)==37 for t in triples)
print("ATOM_LENGTH_CORRIDOR_GREEN triples=6 zhao37=6 zhao29=4 zhao27=4")
