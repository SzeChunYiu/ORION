"""X1-U: independent verification of the D_2(C_2^7) = 12 negative, plus certificates.

The negative: no 5-subset of the 64 weight->=4 vectors of F_2^7 satisfies
|S| + wt(xor_S) >= 5 for every nonempty S of size <= 4 -- hence no 12-element
witness (which must contain a basis and have min-ZS >= 5). Written from the
definition, independently of the C hunter's prune logic.
"""
from itertools import combinations

def negative_r7():
    pool = [v for v in range(1, 128) if bin(v).count("1") >= 4]
    count = 0
    def ok_add(ch, a):
        for sz in (0, 1, 2, 3):
            for c in combinations(ch, sz):
                x = a
                for e in c:
                    x ^= e
                if sz + 1 + bin(x).count("1") < 5:
                    return False
        return True
    def dfs(start, ch):
        nonlocal count
        if len(ch) == 5:
            count += 1
            return
        for i in range(start, len(pool)):
            if ok_add(ch, pool[i]):
                dfs(i + 1, ch + [pool[i]])
    dfs(0, [])
    return count

def analyse(W, label):
    n = len(W)
    xr = [0] * (1 << n)
    Z = []
    for s in range(1, 1 << n):
        low = s & -s
        xr[s] = xr[s ^ low] ^ W[low.bit_length() - 1]
        if xr[s] == 0:
            Z.append(s)
    two = any(not (Z[i] & Z[j]) for i in range(len(Z)) for j in range(i + 1, len(Z)))
    mz = min(bin(s).count("1") for s in Z)
    print(f"{label}: len={n} #ZS={len(Z)} minZS={mz} witness={not two}")
    return not two

if __name__ == "__main__":
    c = negative_r7()
    print("min-ZS>=5 five-sets over C_2^7:", c, "(0 => D_2(C_2^7) = 12 and f_4(C_2^7) = 11)")
    assert c == 0
    B7 = [1, 2, 4, 8, 16, 32, 64]
    B8 = B7 + [128]
    assert analyse(B7 + [7, 11, 21, 25], "C_2^7 len-11 lower-bound cert")
    assert analyse(B7 + [15, 120, 51, 85], "C_2^7 len-11 min-ZS-5 stratum cert")
    assert analyse(B8 + [15, 51, 85, 169, 205], "C_2^8 len-13 cert (D_2 >= 14)")
    assert analyse(B8 + [15, 51, 85, 169, 205, 256], "C_2^9 len-14 padded cert (D_2 >= 15)")
