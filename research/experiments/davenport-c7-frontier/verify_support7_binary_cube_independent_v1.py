from functools import lru_cache
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


def total_zero_profiles():
    out = []
    for d in product(range(6), repeat=7):
        if sum(d) != 5:
            continue
        m = tuple(6 - x for x in d)
        if zsum(m):
            out.append(m)
    return tuple(sorted(out))


@lru_cache(maxsize=None)
def packing_witness(mult, k):
    if k == 1:
        return (mult,) if sum(mult) > 0 and zsum(mult) else None
    first = next((i for i, x in enumerate(mult) if x), None)
    if first is None:
        return None

    ranges = [range(x + 1) for x in mult]
    # Every unordered partition has a block containing the first occupied support
    # point. Requiring the chosen block to contain one such copy removes only block
    # permutation symmetry, not scientific candidates.
    ranges[first] = range(1, mult[first] + 1)

    for block in product(*ranges):
        if block == mult or not zsum(block):
            continue
        rest = tuple(mult[i] - block[i] for i in range(7))
        tail = packing_witness(rest, k - 1)
        if tail is not None:
            return (block,) + tail
    return None


def main():
    profiles = total_zero_profiles()
    assert len(profiles) == 10

    for mult in profiles:
        w4 = packing_witness(mult, 4)
        w5 = packing_witness(mult, 5)
        assert w4 is not None, mult
        assert w5 is None, mult
        assert tuple(sum(block[i] for block in w4) for i in range(7)) == mult
        assert all(zsum(block) and any(block) for block in w4)
        print('profile', mult, 'packing_number=4', 'witness=', w4)

    print('PASS: all 10 profiles have exact zero-sum packing number 4')


if __name__ == '__main__':
    main()
