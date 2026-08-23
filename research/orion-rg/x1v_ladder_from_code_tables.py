"""X1-V: the D_2(C_2^r) ladder from the intersecting-code dictionary.

D_2(C_2^r) = 1 + r + K(r), K(r) = max{k : rho(k) <= r}, rho(k) = i(k,2) - k,
with i(k,2) = min length of a binary intersecting code of dimension k
(Borello-Schmid-Scotti Table 2 for k <= 9; Griesmer floor beyond).
Reproduces all eight known/certified values r = 2..9, then extends.
"""
I2 = {2: 3, 3: 6, 4: 9, 5: 13, 6: 15, 7: 20, 8: 24, 9: 26}
RHO = {k: n - k for k, n in I2.items()}
KNOWN = {2: 5, 3: 7, 4: 8, 5: 10, 6: 11, 7: 12, 8: 14, 9: 16}

def griesmer(k):
    return sum((k + (1 << j) - 1) // (1 << j) for j in range(k))

if __name__ == "__main__":
    for r in range(2, 19):
        K = max(k for k in RHO if RHO[k] <= r)
        cond = [k for k in (10, 11, 12) if griesmer(k) - k <= r]
        d2 = 1 + r + K
        fs_cap = (3 * r + 5) // 2
        assert d2 <= fs_cap
        if r in KNOWN:
            assert KNOWN[r] == d2, (r, d2)
            tag = "known/certified"
        elif r == 10:
            tag = "NEW, unconditional (padding + d_max(17,7)=6 proven + Griesmer)"
        elif not cond:
            tag = "NEW, conditional on BSS Table 2 exactness"
        else:
            tag = f"conditional on i({cond[0]},2)"
        print(f"r={r:>2}  K={K}  D_2={d2:>2}  [{tag}]")
