"""For each GL-orbit of extremal sequences, decide whether its support contains / equals a
GL(3,n)-image of the nonzero binary cube Q = {e1,e2,e3,e12,e13,e23,e123}, and report the
multiplicity profile in cube coordinates when it does."""
import sys, re, itertools
from collections import Counter

def parse(line):
    items=re.findall(r'\((\d+),(\d+),(\d+)\)\^(\d+)', line)
    return {(int(a),int(b),int(c)):int(m) for a,b,c,m in items}

def det3(a,b,c,n):
    return (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0])) % n

def cube_images(ms, n):
    """Yield (basis triple, dict cube-point -> multiplicity) for every ordered independent triple
    (f1,f2,f3) of support points such that f1+f2, f1+f3, f2+f3, f1+f2+f3 are ALL in the support
    (projectively: exact vectors, since Q is a set of exact vectors)."""
    pts = set(ms)
    out=[]
    for f1,f2,f3 in itertools.permutations(pts,3):
        if det3(f1,f2,f3,n)==0: continue
        add=lambda *vs: tuple(sum(v[i] for v in vs)%n for i in range(3))
        img=[f1,f2,f3,add(f1,f2),add(f1,f3),add(f2,f3),add(f1,f2,f3)]
        if all(v in pts for v in img):
            out.append((("f1","f2","f3"), tuple(ms[v] for v in img), img))
    return out

if __name__=='__main__':
    n=int(sys.argv[1]); fn=sys.argv[2]
    tot=0; withcube=0; exact=0; profiles=Counter(); suppsizes=Counter()
    for line in open(fn):
        if not line.startswith('packing'): continue
        tot+=1
        ms=parse(line); suppsizes[len(ms)]+=1
        imgs=cube_images(ms,n)
        if imgs:
            withcube+=1
            if len(ms)==7: exact+=1
            best=max(imgs, key=lambda t: sum(t[1]))
            profiles[tuple(sorted(best[1],reverse=True))]+=1
    print(f"{fn}: {tot} sequences; support sizes {dict(sorted(suppsizes.items()))}")
    print(f"  contain a GL-image of the binary cube in their support: {withcube} ({100*withcube/tot:.1f}%)")
    print(f"  support IS exactly a cube image (7 points): {exact}")
    print("  cube-coordinate multiplicity profiles (sorted, top 12):")
    for k,v in profiles.most_common(12): print("   ", k, "->", v)
