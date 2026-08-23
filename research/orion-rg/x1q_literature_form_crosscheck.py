"""X1-Q: confirm the published form reproduces the enumerated extremal set.

Grynkiewicz-Liu arXiv:2109.10309 Conjecture 1.1 Part 4(a) at m=1,s=1 (a KNOWN case):
extremals for eta(C_n + C_n) are  e1^(n-1) e2^(n-1) (x*e1+e2)^(n-1),  gcd(x,n)=1.
Generating from that form must reproduce the X1-P enumeration exactly.
"""
from itertools import product
from math import gcd

def bases(n):
    return [(a, b) for a in product(range(n), repeat=2) for b in product(range(n), repeat=2)
            if gcd((a[0] * b[1] - a[1] * b[0]) % n, n) == 1]

def triples_from_literature_form(n):
    out = set()
    for e1, e2 in bases(n):
        for x in range(1, n):
            if gcd(x, n) != 1:
                continue
            c = ((x * e1[0] + e2[0]) % n, (x * e1[1] + e2[1]) % n)
            out.add(tuple(sorted([e1, e2, c])))
    return out

if __name__ == "__main__":
    # X1-P enumerated counts, from complete search
    enumerated = {3: 24, 4: 48, 5: 720, 6: 144, 7: 5040}
    for n in sorted(enumerated):
        got = len(triples_from_literature_form(n))
        print(f"n={n}: literature form {got:>5}   X1-P enumeration {enumerated[n]:>5}   "
              f"{'MATCH' if got == enumerated[n] else 'MISMATCH'}")
