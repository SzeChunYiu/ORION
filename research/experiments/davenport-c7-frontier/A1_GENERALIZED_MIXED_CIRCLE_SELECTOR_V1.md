# Type one: a mixed circle selector for every high-power deficit

Status: **proved prime-uniform mixed-subsequence theorem**. The main type-one inverse family has an actual mixed certificate whenever one of a prescribed range of multiples is close to zero. A circular-gap argument supplies it above an explicit overlap threshold, for every deficit. On the newly classified `t=p-2` face this leaves only overlaps of order at most the square root of the prime.

## 1. Hypotheses and the exact certificate

Let `p=2H+1>=7` be prime, let `(f1,f2,f3)` be a basis, and put

\[
s=f_1+f_2+f_3,\quad m=p+H,\quad
U=f_1^{p-1}f_2^{p-1}f_3^{p-1}s.
\]

Suppose

\[
V=s^c x^r y^{p-d},\quad
y=(1,b,-b),\quad b\ne0,\quad
1\le d\le c\le H,\quad r=H+d-c>0,
\tag{1}
\]

and `sigma(V)=0`. The displayed inverse family is a hypothesis, and basis permutations are allowed.

If ordinary integers `k,n,v` satisfy

\[
d\le k\le n\le c,\qquad |v|\le n,\qquad v\equiv kb\pmod p,
\tag{2}
\]

then the actual occurrence sequence

\[
\boxed{x^r y^{k-d}s^{c-n}
f_1^{n-k}f_2^{n-v}f_3^{n+v}}
\tag{3}
\]

is zero-sum and has length

\[
H+2n\le3H=m-1.
\tag{4}
\]

For proof, the companion relation is `rx=dy-cs`. The first three factors in (3) sum to `ky-ns`, and the three displayed axis counts cancel its coordinates. The light count lies in `[0,c]`, the new `y` count is at most `c-d<p-d`, and the axis counts lie between zero and `2c<=p-1`. The `x` count is exactly its actual capacity `r`; thus no unprovided occurrence is used. The length identity follows from `r+c-d=H`. The certificate is nonempty because `r>0`.

## 2. A circle gap supplies the needed multiplier

Put

\[
M=\lfloor c/d\rfloor,\qquad N=M+1.
\]

The `N` points `0,db,2db,...,Mdb` are distinct modulo `p`. Place them on the circle of circumference `p`. A gap between cyclically consecutive points has length at most `floor(p/N)`. Its endpoint indices differ by an absolute amount `ell` in `[1,M]`. Consequently a centered representative `v` of `d ell b` has

\[
|v|\le\lfloor p/N\rfloor.
\]

Suppose

\[
\boxed{(c+1)(\lfloor c/d\rfloor+1)>p.}
\tag{5}
\]

This is exactly the integer condition `floor(p/N)<=c`. Set `k=d ell` and `n=max(k,|v|)`. Then (2) holds, so (3) is a short zero-sum.

**General theorem.** Every main-family companion (1) satisfying (5) is impossible. The proof is uniform in both the prime and deficit. In contrast to the type-two parity selector, the three saturated type-one axes permit either parity of `v` directly.

The main-family assumption has only been established on specified donor ranges elsewhere; (5) does not manufacture that inverse form for arbitrary deficits.

## 3. Unconditional consequence on the first unsaturated face

For `d=2`, the exact theorem in `A1_FIRST_UNSATURATED_DONOR_INVERSE_AND_AUGMENTATION_V1.md` applies to the actual donor with `K=c+1`, for every `c>=1`. It forces the displayed family under short-freeness. It also eliminates every

\[
c\ge\left\lfloor\frac{p+1}{4}\right\rfloor
\]

with `r>0`. Thus (5) gives an unconditional additional exclusion on the `t=p-2` face:

\[
c\ge2,\qquad(c+1)(\lfloor c/2\rfloor+1)>p.
\tag{6}
\]

Combine this with the already complete low-overlap results `c=1,2,3,4`. Every remaining type-one `t=p-2` companion must satisfy all of

\[
\boxed{5\le c<\left\lfloor\frac{p+1}{4}\right\rfloor,\qquad
(c+1)(\lfloor c/2\rfloor+1)\le p.}
\tag{7}
\]

In particular `(c+1)^2<=2p`, since `floor(c/2)+1>=(c+1)/2`. Hence the unclosed overlap range is at most of square-root size. This is a necessary residual restriction, not an existence assertion. The original type-one quotient and other proven bands continue to apply within it.

## 4. Checks and preserved gate

The lower bound `k>=d` is essential: it keeps `y^(k-d)` an actual subsequence rather than a formal negative count. The stepped set of circle points enforces that bound without assuming a favorable sign for the gap. All three axis capacities and the exact length in (4) were checked locally. The argument uses no enumeration or new external theorem. The small-overlap part of (7), other deficits without an inverse form, and the full first corridor remain open.
