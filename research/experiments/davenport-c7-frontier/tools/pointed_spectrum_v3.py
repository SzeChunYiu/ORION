"""Pointed length-spectrum congruences.

Theorem 1 (SPECTRUM_CONGRUENCE_THEOREM_V2): for a sequence T = g_1..g_N over C_p^r and any
multilinear h of degree <= N - D,  sum_{I: sigma(I)=0} (-1)^{|I|} h(1_I) = 0 in F_p.

Symmetric instance  h = e_d(x)            -> sum_l (-1)^l C(l,d) N_l = 0,   d <= N-D.
Pointed instance    h = x_i e_d(x_{-i})   -> sum_l (-1)^l C(l-1,d) M_l = 0, d <= N-D-1,
where N_l = #{I : |I|=l, sigma(I)=0} and M_l = #{I : i in I, |I|=l, sigma(I)=0}.
Complementation (T zero-sum): N_l = N_{N-l} and M_l + M_{N-l} = N_l.

Solve the combined system mod p over the lengths NOT forbidden.
"""
import sys
from math import comb

def solve(rows, p, nvars):
    m=len(rows); A=[[0]*(nvars+1+m) for _ in rows]
    for i,(coef,rhs) in enumerate(rows):
        for v,c in coef.items(): A[i][v]=(A[i][v]+c)%p
        A[i][nvars]=rhs%p; A[i][nvars+1+i]=1
    r=0
    for col in range(nvars):
        piv=next((i for i in range(r,m) if A[i][col]),None)
        if piv is None: continue
        A[r],A[piv]=A[piv],A[r]
        inv=pow(A[r][col],p-2,p); A[r]=[(x*inv)%p for x in A[r]]
        for i in range(m):
            if i!=r and A[i][col]:
                f=A[i][col]; A[i]=[(A[i][j]-f*A[r][j])%p for j in range(nvars+1+m)]
        r+=1
        if r==m: break
    for i in range(m):
        if not any(A[i][:nvars]) and A[i][nvars]:
            return False, A[i][nvars+1:], r
    return True, None, r

def run(p, rdim, N, forbidden, pointed=True, verbose=True):
    D = rdim*(p-1)+1
    allowed = [l for l in range(N+1) if l not in forbidden]
    # variables: N_l for l in allowed, 0<l<N (symmetric: index by min(l,N-l));  M_l for l in allowed, l>0
    nidx = {}; midx = {}
    for l in allowed:
        if 0 < l < N: nidx.setdefault(min(l, N-l), len(nidx))
    off = len(nidx)
    if pointed:
        for l in allowed:
            if l > 0: midx[l] = off + len(midx)
    nvars = off + len(midx)
    rows = []
    # symmetric equations
    for d in range(N - D + 1):
        coef = {}; rhs = 0
        for l in allowed:
            c = ((-1)**l) * comb(l, d)
            if l in (0, N): rhs -= c
            else: coef[nidx[min(l, N-l)]] = coef.get(nidx[min(l, N-l)], 0) + c
        rows.append((coef, rhs))
    if pointed:
        # pointed equations (M_N = 1 known: the whole index set contains i)
        for d in range(N - D):
            coef = {}; rhs = 0
            for l in allowed:
                if l == 0: continue
                c = ((-1)**l) * comb(l-1, d)
                if l == N: rhs -= c
                else: coef[midx[l]] = coef.get(midx[l], 0) + c
            rows.append((coef, rhs))
        # complement relations M_l + M_{N-l} = N_l  (for 0 < l < N, both l and N-l allowed)
        for l in allowed:
            if not (0 < l < N): continue
            if (N - l) not in allowed: continue
            coef = {midx[l]: 1}
            coef[midx[N-l]] = coef.get(midx[N-l], 0) + 1
            coef[nidx[min(l, N-l)]] = coef.get(nidx[min(l, N-l)], 0) - 1
            rows.append((coef, 0))
    cons, cert, rank = solve(rows, p, nvars)
    if verbose:
        print(f"p={p} N={N} D={D} forbid {sorted(forbidden)[:6]}...  vars={nvars} eqs={len(rows)} "
              f"rank={rank} consistent={cons}{' (pointed)' if pointed else ' (symmetric only)'}")
    return cons

if __name__ == '__main__':
    print("=== control: the symmetric system reproduces the V2 results")
    run(7,3,30,set(range(1,11))|set(range(20,30)),pointed=False)
    run(7,3,37,set(range(1,11))|set(range(27,37)),pointed=False)
    run(7,3,37,set(range(1,8))|set(range(30,37)),pointed=False)
    print("=== pointed system at the D_3 target length 37 over C_7^3")
    for hi in (7,8,9,10):
        forb=set(range(1,hi+1))|set(range(37-hi,37))
        run(7,3,37,forb,pointed=True)
    print("=== pointed system, control at other lengths")
    for N,hi in ((29,9),(28,8),(27,7),(30,10),(36,7)):
        forb=set(range(1,hi+1))|set(range(N-hi,N))
        run(7,3,N,forb,pointed=True)
    print("=== p=5 analogue (D_3(C_5^3) = 25 is known exactly, so length 26 must be closable in principle)")
    for hi in (5,6,7):
        forb=set(range(1,hi+1))|set(range(26-hi,26))
        run(5,3,26,forb,pointed=True)
    print("=== p=3 analogue at the D_3 target length 15")
    for hi in (3,4):
        forb=set(range(1,hi+1))|set(range(15-hi,15))
        run(3,3,15,forb,pointed=True)
