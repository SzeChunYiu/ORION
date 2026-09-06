#!/usr/bin/env python3
"""Self-contained verification of CODE_DICTIONARY_V7.md.

Nothing is imported from the other records and no compiled tool is required.  The two
descriptions of a block -- "zero-sum subsequence", found by brute-force subset sums, and
"nonzero binary codeword of ker M", found by Gaussian elimination over F_p followed by
code enumeration -- are written independently and compared against each other.

  Step 1  Theorem C  -- blocks <-> nonzero binary codewords of ker M, two ways
  Step 2  Theorem C(b) -- z(S) is the maximum number of pairwise disjoint binary codewords
  Step 3  Lemma A   -- z(S) <= 1 forces the block family to be an antichain
  Step 4  Corollary C1 -- z(S) <= 1 iff the atoms pairwise intersect
  Step 5  Theorem Y -- a position lying in every block forces n <= D(C_p^r) = r(p-1)+1
  Step 6  Theorem Y sharp -- n = D is attained, in four different groups
  Step 7  the C_3^5 length-16 witness read through the dictionary
"""
import random, itertools

D = lambda p, r: r * (p - 1) + 1


# ---------- path 1: blocks by brute-force subset sums ----------
def blocks(S, p, r):
    n = len(S)
    sums = [None] * (1 << n)
    sums[0] = (0,) * r
    out = []
    for m in range(1, 1 << n):
        lb = m & -m
        i = lb.bit_length() - 1
        prev = sums[m ^ lb]
        cur = tuple((prev[k] + S[i][k]) % p for k in range(r))
        sums[m] = cur
        if not any(cur):
            out.append(m)
    return out


# ---------- path 2: nonzero binary codewords of ker M, by linear algebra ----------
def kernel_binary(S, p, r):
    n = len(S)
    M = [[S[j][i] % p for j in range(n)] for i in range(r)]
    piv, row = [], 0
    for col in range(n):
        sel = next((k for k in range(row, r) if M[k][col] % p), None)
        if sel is None:
            continue
        M[row], M[sel] = M[sel], M[row]
        inv = pow(M[row][col], p - 2, p)
        M[row] = [(v * inv) % p for v in M[row]]
        for k in range(r):
            if k != row and M[k][col] % p:
                f = M[k][col]
                M[k] = [(M[k][c] - f * M[row][c]) % p for c in range(n)]
        piv.append(col)
        row += 1
        if row == r:
            break
    free = [c for c in range(n) if c not in piv]
    basis = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for i, c in enumerate(piv):
            v[c] = (-M[i][f]) % p
        basis.append(v)
    out = []
    for coef in itertools.product(range(p), repeat=len(basis)):
        if not any(coef):
            continue
        v = [0] * n
        for c, b in zip(coef, basis):
            if c:
                for j in range(n):
                    v[j] = (v[j] + c * b[j]) % p
        if all(x in (0, 1) for x in v):
            out.append(sum(1 << j for j in range(n) if v[j]))
    return sorted(out)


def atoms_of(bl):
    at = []
    for m in sorted(bl, key=lambda m: bin(m).count('1')):
        if not any((a & m) == a for a in at):
            at.append(m)
    return at


def packing(bl):
    """Max pairwise-disjoint blocks, exact."""
    bl = sorted(bl, key=lambda m: bin(m).count('1'))
    memo = {}

    def rec(used, start):
        key = (used, start)
        if key in memo:
            return memo[key]
        b = 0
        for idx in range(start, len(bl)):
            m = bl[idx]
            if m & used:
                continue
            b = max(b, 1 + rec(used | m, idx + 1))
        memo[key] = b
        return b

    return rec(0, 0)


def rand_seq(rng, p, r, n):
    return [tuple(rng.randrange(p) for _ in range(r)) for _ in range(n)]


def witness_c3_5():
    p, r = 3, 5
    e = [tuple(1 if k == i else 0 for k in range(r)) for i in range(r)]
    S = [e[i] for i in range(r) for _ in range(p - 1)]
    for i in range(1, r):
        for j in range(i + 1, r):
            S.append(tuple((e[0][k] + e[i][k] + e[j][k]) % p for k in range(r)))
    return p, r, S


def step1(rng):
    bad = t = 0
    for _ in range(60):
        p, r = rng.choice([2, 3, 5]), rng.choice([2, 3])
        S = rand_seq(rng, p, r, rng.randint(2, 11))
        t += 1
        if sorted(blocks(S, p, r)) != kernel_binary(S, p, r):
            bad += 1
    assert bad == 0, "block <-> binary codeword dictionary failed"
    print(f"1. Theorem C verified two independent ways on {t} random sequences: the nonempty")
    print("   zero-sum subsequences of S are exactly the nonzero binary codewords of ker M")


def step2(rng):
    t = 0
    for _ in range(120):
        p, r = rng.choice([2, 3]), rng.choice([2, 3])
        S = rand_seq(rng, p, r, rng.randint(2, 10))
        bl = blocks(S, p, r)
        if not bl:
            continue
        kb = kernel_binary(S, p, r)
        assert packing(bl) == packing(kb)
        t += 1
    print(f"2. Theorem C(b) verified on {t} sequences: z(S) computed from the zero-sum")
    print("   subsequences equals z(S) computed from the binary codewords")


def step3(rng):
    low = high = viol = 0
    for _ in range(400):
        p, r = rng.choice([2, 3, 5]), rng.choice([2, 3])
        S = rand_seq(rng, p, r, rng.randint(2, 12))
        bl = blocks(S, p, r)
        if not bl:
            continue
        if packing(bl) <= 1:
            low += 1
            if len(atoms_of(bl)) != len(bl):
                viol += 1
        else:
            high += 1
    assert viol == 0, "antichain lemma failed"
    print(f"3. Lemma A verified: of {low} sequences with z(S)<=1, {viol} had a block that was")
    print(f"   not an atom -- the block family is an antichain ({high} with z>=2 as control)")


def step4(rng):
    agree = both = 0
    for _ in range(400):
        p, r = rng.choice([2, 3, 5]), rng.choice([2, 3])
        S = rand_seq(rng, p, r, rng.randint(2, 11))
        bl = blocks(S, p, r)
        if not bl:
            continue
        at = atoms_of(bl)
        inter = all((a & b) for a in at for b in at)
        if (packing(bl) <= 1) == inter:
            agree += 1
        both += 1
    assert agree == both, "Corollary C1 failed"
    print(f"4. Corollary C1 verified on {both} sequences: z(S)<=1 exactly when the atoms")
    print("   pairwise intersect, i.e. when the atom family is an intersecting family")


def step5(rng):
    hits = viol = t = 0
    for _ in range(4000):
        p, r = rng.choice([2, 3, 5]), rng.choice([1, 2, 3])
        n = rng.randint(1, 10)
        S = rand_seq(rng, p, r, n)
        bl = blocks(S, p, r)
        if not bl:
            continue
        t += 1
        common = bl[0]
        for m in bl:
            common &= m
        if common:
            hits += 1
            if n > D(p, r):
                viol += 1
    assert viol == 0, "Theorem Y failed"
    print(f"5. Theorem Y verified: of {t} sequences with a block, {hits} had a position lying")
    print(f"   in every block; {viol} of those exceeded n <= D(C_p^r) = r(p-1)+1")


def step6():
    rows = []
    for p, r in [(3, 3), (3, 5), (5, 3), (7, 2)]:
        e = [tuple(1 if k == i else 0 for k in range(r)) for i in range(r)]
        T = [x for x in e for _ in range(p - 1)]
        s = [sum(v[k] for v in T) % p for k in range(r)]
        S = T + [tuple((-x) % p for x in s)]
        bl = blocks(S, p, r)
        common = bl[0]
        for m in bl:
            common &= m
        assert len(S) == D(p, r) and common, f"sharpness failed at C_{p}^{r}"
        rows.append(f"C_{p}^{r}: n={len(S)}=D")
    print("6. Theorem Y is sharp -- n = D attained with a block-covering position at " + ", ".join(rows))


def step7():
    p, r, S = witness_c3_5()
    n = len(S)
    bl = blocks(S, p, r)
    assert sorted(bl) == kernel_binary(S, p, r)
    at = atoms_of(bl)
    assert len(at) == len(bl) == 289
    assert packing(bl) == 1
    sizes = sorted({bin(a).count('1') for a in at})
    floor, ceil = n - r * (p - 1), D(p, r)
    assert sizes == list(range(floor, ceil + 1)), sizes
    assert all((a & b) for a in at for b in at)
    core = at[0]
    for a in at:
        core &= a
    assert core == 0
    print(f"7. the C_3^5 witness (n={n}, z=1) read through the dictionary: {len(bl)} blocks, all")
    print(f"   atoms; sizes fill [{floor}, {ceil}] exactly -- the complement-lemma floor and the")
    print("   Olson ceiling are both attained; intersecting; and the common core is empty")


if __name__ == "__main__":
    rng = random.Random(20260906)
    step1(rng); step2(rng); step3(rng); step4(rng); step5(rng); step6(); step7()
    print()
    print("THEOREM C, LEMMA A, COROLLARY C1 and THEOREM Y verified.  D_k(C_p^r) is the")
    print("extremal problem for binary codewords of an F_p code of codimension <= r.")
