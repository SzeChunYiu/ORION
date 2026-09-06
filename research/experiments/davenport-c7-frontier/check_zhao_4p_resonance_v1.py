#!/usr/bin/env python3
import math

PRIMES=(5,7,11,13,17,19,23,29,31,37,41,43)

def a(N,k,i):
    return math.comb(N-k,k-i)+(-1)**i*math.comb(N-k+i-1,k-1)

for p in PRIMES:
    D=3*p-2
    N=4*p
    for k in range((3*p+1)//2,2*p+1):
        assert N>=2*k and 2*k>=D+2
        for i in range(1,2*k-D+1):
            assert a(N,k,i)%p==0, (p,k,i,a(N,k,i)%p)
print(f"ZHAO_4P_RESONANCE_GREEN primes={len(PRIMES)}")
