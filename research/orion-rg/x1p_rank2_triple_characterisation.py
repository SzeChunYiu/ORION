"""X1-P: characterise and count the extremal triples for f_n(C_n + C_n).

An extremal sequence is a^(n-1) b^(n-1) c^(n-1) with {a,b} a basis and c = xa+yb;
it has no zero-sum of length <= n iff the min below is >= n+1.
Count of extremal sequences = |GL(2,Z_n)| * (phi(n)-1) / 2  for n >= 3.
"""
from fractions import Fraction

def valid_xy(n):
    return [(x, y) for x in range(n) for y in range(n)
            if min(((-g * x) % n) + ((-g * y) % n) + g for g in range(1, n)) >= n + 1]

def gl2_order(n):
    m, ps = n, set()
    p = 2
    while p * p <= m:
        if m % p == 0:
            ps.add(p)
            while m % p == 0:
                m //= p
        p += 1
    if m > 1:
        ps.add(m)
    r = Fraction(n ** 4)
    for p in ps:
        r *= (1 - Fraction(1, p)) * (1 - Fraction(1, p * p))
    return int(r)

def totient(n):
    return sum(1 for k in range(1, n + 1) if __import__("math").gcd(k, n) == 1)

if __name__ == "__main__":
    print(f"{'n':>3} {'V(n)':>5} {'3phi-3':>7} {'|GL2|':>7} {'N_extremal':>11}")
    for n in range(2, 16):
        v, t = len(valid_xy(n)), totient(n)
        N = 1 if n == 2 else gl2_order(n) * (t - 1) // 2
        print(f"{n:>3} {v:>5} {3*t-3:>7} {gl2_order(n):>7} {N:>11}")
