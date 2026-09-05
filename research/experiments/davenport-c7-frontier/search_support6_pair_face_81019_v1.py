#!/usr/bin/env python3
"""Exact support-six-face classifier for the frozen p=7 (19,10) pair universe.

This implementation mirrors the validated incremental stage-one predicate but uses
Python sets rather than the C++ bitset representation.  It must reproduce the frozen
538/24/0 pair totals before its support-face output is trusted.
"""
from collections import Counter

P = 7
VEC = [(x, y, z) for x in range(P) for y in range(P) for z in range(P)]
IDX = {v: i for i, v in enumerate(VEC)}
N = len(VEC)
ADD = [[0] * N for _ in range(N)]
NEG = [0] * N
for i, a in enumerate(VEC):
    NEG[i] = IDX[tuple((-x) % P for x in a)]
    for j, b in enumerate(VEC):
        ADD[i][j] = IDX[tuple((a[k] + b[k]) % P for k in range(3))]


def inv(a: int) -> int:
    return pow(a, -1, P)


def make_u(a: int) -> list[int]:
    u = inv(a)
    c = [0] * N
    for g, m in [
        ((1, 0, 0), 6),
        ((0, 1, 0), 6),
        ((0, 0, 1), a),
        (((-u) % P, (-u) % P, 1), P - a),
    ]:
        c[IDX[g]] = m
    return c


def subset_sums(c: list[int], h: int) -> list[set[int]]:
    dp = [set() for _ in range(h + 1)]
    dp[0].add(0)
    for g, cnt in enumerate(c):
        if not cnt:
            continue
        old = [set(s) for s in dp]
        for k in range(h + 1):
            if not old[k]:
                continue
            cur = 0
            for take in range(1, min(cnt, h - k) + 1):
                cur = ADD[cur][g]
                dp[k + take].update(ADD[s][cur] for s in old[k])
    return dp


def enumerate_companions(base: list[int], m: int = 10, h: int = 9):
    dp = subset_sums(base, h)
    forb = [set() for _ in range(h + 1)]
    for j in range(h + 1):
        for k in range(h - j + 1):
            forb[j].update(NEG[s] for s in dp[k])

    allowed = [x for x in range(N) if x not in forb[1] and base[x] < 6]
    allowed_set = set(allowed)
    ss = [set() for _ in range(m + 1)]
    ss[0].add(0)
    mult = [0] * N
    chosen: list[int] = []

    def valid_add(x: int, depth: int):
        news = [set() for _ in range(depth + 2)]
        for k in range(1, depth + 2):
            news[k] = {ADD[s][x] for s in ss[k - 1]}
            if k <= h and news[k] & forb[k]:
                return None
        return news

    def dfs(start: int, depth: int, total: int):
        if depth == m - 1:
            x = NEG[total]
            if x not in allowed_set:
                return
            if chosen and x < chosen[-1]:
                return
            if mult[x] >= 6 - base[x]:
                return
            if valid_add(x, depth) is None:
                return
            yield chosen + [x]
            return

        for pos in range(start, len(allowed)):
            x = allowed[pos]
            if mult[x] >= 6 - base[x]:
                continue
            news = valid_add(x, depth)
            if news is None:
                continue
            old = [None] * (depth + 2)
            for k in range(1, depth + 2):
                old[k] = ss[k]
                ss[k] = ss[k] | news[k]
            mult[x] += 1
            chosen.append(x)
            yield from dfs(pos, depth + 1, ADD[total][x])
            chosen.pop()
            mult[x] -= 1
            for k in range(1, depth + 2):
                ss[k] = old[k]

    yield from dfs(0, 0, 0)


def rank_mod7(elems: list[int]) -> int:
    rows = [list(VEC[q]) for q in elems]
    rank = 0
    for col in range(3):
        piv = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        q = inv(rows[rank][col])
        rows[rank] = [(q * x) % P for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][col]:
                f = rows[i][col]
                rows[i] = [
                    (rows[i][c] - f * rows[rank][c]) % P for c in range(3)
                ]
        rank += 1
    return rank


def main() -> None:
    totals, faces = [], []
    categories, shared = {}, {}

    for a in (1, 2, 3):
        base = make_u(a)
        usupp = {g for g, c in enumerate(base) if c}
        light = IDX[(0, 0, 1)]
        u = inv(a)
        heavy = IDX[((-u) % P, (-u) % P, 1)]
        count = face = 0
        cats = Counter()
        mults = Counter()

        for seq in enumerate_companions(base):
            count += 1
            vc = Counter(seq)
            if len(usupp | set(vc)) != 6:
                continue
            face += 1
            r = rank_mod7(list(vc))
            cl, ch = vc[light], vc[heavy]
            cats[(len(vc), r, bool(cl), bool(ch))] += 1
            mults[(cl, ch)] += 1

        totals.append(count)
        faces.append(face)
        categories[a] = cats
        shared[a] = mults

    assert totals == [538, 24, 0], totals
    assert faces == [0, 0, 0], faces
    print(
        {
            "status": "SUPPORT6_PAIR_FACE_81019_GREEN",
            "pair_totals": totals,
            "support6_faces": faces,
            "categories": categories,
            "shared_multiplicities": shared,
        }
    )


if __name__ == "__main__":
    main()
