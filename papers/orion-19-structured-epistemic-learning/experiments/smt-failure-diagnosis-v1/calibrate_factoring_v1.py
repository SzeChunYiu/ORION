#!/usr/bin/env python3
import time, z3
B=5000
def t(b,p,ms=B):
    s=b(p); s.set("timeout",ms); a=time.time(); r=s.check(); return str(r), round(time.time()-a,3)
PRIMES=[65537, 1000003, 15485863, 179424673, 2038074743]
COMPOSITES=[65536, 1000004, 15485864]
def fac_bv(N):
    W=2*N.bit_length()+2; s=z3.Solver()
    x=z3.BitVec("x",W); y=z3.BitVec("y",W)
    s.add(z3.UGT(x,1), z3.UGT(y,1), z3.ULE(x,y))
    s.add(z3.BVMulNoOverflow(x,y,False))          # no wraparound
    s.add(x*y==N)
    s.add(z3.ULE(x, int(N**0.5)+1), z3.ULE(y, N))
    return s
def fac_int(N):
    s=z3.Solver(); x=z3.Int("x"); y=z3.Int("y")
    s.add(x>1,y>1,x<=y,x*y==N, x<=int(N**0.5)+1, y<=N); return s
print("--- primes: MUST be unsat ---")
for N in PRIMES:
    r={n:t(b,N) for n,b in (("bv",fac_bv),("int",fac_int))}
    ok = "OK" if r["bv"][0] in ("unsat","unknown") else "*** WRONG ***"
    print(f"  N={N:<12} bits={N.bit_length():<3} " + "  ".join(f"{n}={v[0]}/{v[1]:.2f}s" for n,v in r.items()) + "  " + ok, flush=True)
print("--- composites: MUST be sat (control that the encoding can find factors) ---")
for N in COMPOSITES:
    r={n:t(b,N) for n,b in (("bv",fac_bv),("int",fac_int))}
    ok = "OK" if r["bv"][0]=="sat" else "*** WRONG ***"
    print(f"  N={N:<12} " + "  ".join(f"{n}={v[0]}/{v[1]:.2f}s" for n,v in r.items()) + "  " + ok, flush=True)
