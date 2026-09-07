"""Canonical form of a multiset over F_p^3 under GL(3,p): lex-min multiplicity vector over all
maps sending an ordered independent triple of support points to (e1,e2,e3)."""
import sys, re, itertools
from collections import Counter

def parse_line(line):
    pk = int(re.search(r'packing=(\d+)', line).group(1))
    items = re.findall(r'\((\d+),(\d+),(\d+)\)\^(\d+)', line)
    ms = {(int(a),int(b),int(c)): int(m) for a,b,c,m in items}
    return pk, ms

def det3(a,b,c,p):
    return (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0])) % p

def inv3(M, p):
    a,b,c = M
    d = det3(a,b,c,p); di = pow(d, p-2, p)
    # cofactor matrix transpose
    cof = [[(b[1]*c[2]-b[2]*c[1]), -(b[0]*c[2]-b[2]*c[0]), (b[0]*c[1]-b[1]*c[0])],
           [-(a[1]*c[2]-a[2]*c[1]), (a[0]*c[2]-a[2]*c[0]), -(a[0]*c[1]-a[1]*c[0])],
           [(a[1]*b[2]-a[2]*b[1]), -(a[0]*b[2]-a[2]*b[0]), (a[0]*b[1]-a[1]*b[0])]]
    # inverse = adj/det, adj = transpose of cofactor
    return [[(cof[j][i]*di) % p for j in range(3)] for i in range(3)]

def apply(Minv, v, p):
    # coordinates of v in basis (a,b,c): solve; Minv is inverse of matrix with ROWS a,b,c? we need v = x a + y b + z c
    # Let B = [a b c] as columns; v = B x => x = B^{-1} v. Build B^{-1} from rows-matrix inverse: rows-matrix R has rows a,b,c; B = R^T; B^{-1} = (R^{-1})^T
    return tuple(sum(Minv[j][i]*v[j] for j in range(3)) % p for i in range(3))

def canon(ms, p):
    pts = list(ms)
    best = None
    for a,b,c in itertools.permutations(pts, 3):
        if det3(a,b,c,p) == 0: continue
        Rinv = inv3((a,b,c), p)
        img = tuple(sorted((apply(Rinv, v, p), m) for v,m in ms.items()))
        if best is None or img < best: best = img
    return best

if __name__ == '__main__':
    p = int(sys.argv[1]); fn = sys.argv[2]
    seen = {}
    for line in open(fn):
        if not line.startswith('packing'): continue
        pk, ms = parse_line(line)
        key = canon(ms, p)
        if key not in seen: seen[key] = (pk, ms)
    print(f"{len(seen)} GL-orbits")
    # summarize by support size and multiplicity profile
    prof = Counter()
    for key,(pk,ms) in seen.items():
        prof[(len(ms), tuple(sorted(ms.values(), reverse=True)))] += 1
    for k,v in sorted(prof.items()): print("supp", k[0], "mults", k[1], "orbits", v)
    if len(sys.argv) > 3:
        for key,(pk,ms) in seen.items():
            print("packing", pk, " ".join(f"{v}^{m}" for v,m in key))
