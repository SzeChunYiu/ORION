"""X1-V: construct the [15,6,6] even-weight BCH subcode, verify it is intersecting,
and certify D_2(C_2^9) >= 16 via its parity-check columns.

g(x) = (x+1)(x^4+x+1)(x^4+x^3+x^2+x+1); codewords m(x)g(x), deg m <= 5.
Expected weight enumerator (Cohen-Lempel): 1 + 30x^6 + 15x^8 + 18x^10.
"""
from collections import Counter

def pmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
    return r

def main():
    g = pmul(pmul(0b11, 0b10011), 0b11111)
    assert g.bit_length() - 1 == 9
    C = [pmul(m, g) for m in range(64)]
    we = Counter(bin(c).count("1") for c in C)
    assert dict(we) == {0: 1, 6: 30, 8: 15, 10: 18}, we
    assert all((C[i] & C[j]) != 0 for i in range(1, 64) for j in range(i + 1, 64)), "not intersecting"
    gens, span = [], {0}
    for c in C:
        if c and c not in span:
            gens.append(c)
            span = {s ^ c for s in span} | span
    dual = [v for v in range(1 << 15) if all(bin(v & c).count("1") % 2 == 0 for c in gens)]
    assert len(dual) == 512
    H, span = [], {0}
    for v in dual:
        if v and v not in span:
            H.append(v)
            span = {s ^ v for s in span} | span
    W = [sum(((H[i] >> j) & 1) << i for i in range(9)) for j in range(15)]
    assert len(set(W)) == 15 and all(W)
    xr = [0] * (1 << 15)
    Z = []
    for s in range(1, 1 << 15):
        low = s & -s
        xr[s] = xr[s ^ low] ^ W[low.bit_length() - 1]
        if xr[s] == 0:
            Z.append(s)
    assert len(Z) == 63
    assert min(bin(s).count("1") for s in Z) == 6
    assert not any(not (Z[i] & Z[j]) for i in range(len(Z)) for j in range(i + 1, len(Z)))
    print("CERTIFIED: length-15 witness over C_2^9 ->  D_2(C_2^9) >= 16")
    print("witness:", sorted(W))

if __name__ == "__main__":
    main()
