from itertools import product

Q = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 1, 0),
    (1, 0, 1),
    (0, 1, 1),
    (1, 1, 1),
)


def zsum(mult):
    return all(sum(mult[i] * Q[i][j] for i in range(7)) % 7 == 0 for j in range(3))


# Four orbit representatives and explicit four-block certificates from
# SUPPORT7_BINARY_CUBE_THEOREM_V1.md.
CERTIFICATES = {
    (5, 6, 6, 5, 5, 4, 6): (
        (0, 0, 1, 1, 0, 0, 6),
        (2, 0, 2, 0, 5, 0, 0),
        (0, 3, 3, 0, 0, 4, 0),
        (3, 3, 0, 4, 0, 0, 0),
    ),
    (4, 6, 6, 6, 6, 4, 5): (
        (0, 0, 0, 1, 1, 1, 5),
        (2, 0, 2, 0, 5, 0, 0),
        (2, 2, 0, 5, 0, 0, 0),
        (0, 4, 4, 0, 0, 3, 0),
    ),
    (5, 5, 6, 6, 5, 5, 5): (
        (0, 0, 0, 1, 1, 1, 5),
        (2, 2, 0, 5, 0, 0, 0),
        (0, 3, 3, 0, 0, 4, 0),
        (3, 0, 3, 0, 4, 0, 0),
    ),
    (5, 5, 5, 6, 6, 6, 4): (
        (0, 1, 1, 0, 0, 6, 0),
        (1, 0, 1, 0, 6, 0, 0),
        (1, 1, 0, 6, 0, 0, 0),
        (3, 3, 3, 0, 0, 0, 4),
    ),
}


def permute_profile(m, perm):
    # Q is the seven nonzero {0,1}^3 vectors; a coordinate permutation induces
    # a permutation of Q. Work it out from vector images rather than hard-code it.
    q_index = {v: i for i, v in enumerate(Q)}
    out = [0] * 7
    for i, v in enumerate(Q):
        image = tuple(v[perm[j]] for j in range(3))
        out[q_index[image]] = m[i]
    return tuple(out)


def orbit(rep):
    perms = (
        (0, 1, 2), (0, 2, 1), (1, 0, 2),
        (1, 2, 0), (2, 0, 1), (2, 1, 0),
    )
    return {permute_profile(rep, p) for p in perms}


def main():
    total_zero = []
    for d in product(range(6), repeat=7):
        if sum(d) != 5:
            continue
        m = tuple(6 - x for x in d)
        if zsum(m):
            total_zero.append(m)

    assert len(total_zero) == 10, total_zero
    covered = set().union(*(orbit(rep) for rep in CERTIFICATES))
    assert set(total_zero) == covered

    for rep, blocks in CERTIFICATES.items():
        assert all(any(block) and zsum(block) for block in blocks)
        assert tuple(sum(block[i] for block in blocks) for i in range(7)) == rep

    print('PASS: 10 labelled zero-sum profiles, 4 coordinate-permutation orbits, explicit four-pack certificates verified')


if __name__ == '__main__':
    main()
