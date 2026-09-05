# Type two: an actual mixed circle selector for every deficit

Status: **proved prime-uniform mixed-subsequence theorem**. The full-companion certificate used on the first faces extends to every deficit with an explicit lower power bound and an adaptive parity choice. In the main inverse family it removes a general high-overlap band. The available inverse theorem makes that band unconditional when `p>=10b`.

## 1. The exact occurrence theorem

Let `p=2H+1>=7` be prime, `m=p+H`, `u=H+1`, `s=(u,u,1)` in a basis `(e1,e2,g)`, and

\[
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2,\qquad
V=s^c g x^r y^{p-b},\qquad r=H+b-1-c>0.
\]

Suppose `sigma(V)=0`, `2<=b<=c<=H`, and

\[
y=(A,-A,1),\qquad A\ne0.
\tag{1}
\]

If ordinary integers `j,n,v` satisfy

\[
b\le j\le n+1,\quad0\le n\le c,\quad
|v|\le n,\quad v\equiv n\pmod2,\quad v\equiv2jA\pmod p,
\tag{2}
\]

then

\[
\boxed{x^r y^{j-b}s^{c-n}g^{1+n-j}
e_1^{(n-v)/2}e_2^{(n+v)/2}}
\tag{3}
\]

is an actual zero-sum of length

\[
H+n\le H+c\le p-1<m.
\tag{4}
\]

Indeed `rx=by-cs-g`. The first four factors of (3) consequently sum to `(jA-nu,-jA-nu,0)`; the axis counts cancel this vector, using `2u=1` and the congruence for `v`. They are nonnegative integers by (2) and are each at most `n<=H`. The new `y` count satisfies `0<=j-b<=c+1-b<p-b`, and `0<=1+n-j<=c+1-b<=H-1` fits the actual shared `g` donor. The light and `x` counts fit by definition. Their ordinary length is `r+c+1-b+n=H+n`. Thus every needed occurrence, including the missing-power lower bound, is verified.

## 2. A stepped circle enforces the lower bound j >= b

Put `M=floor(c/b)` and `N=M+1`. The `N` points

\[
0,2bA,4bA,\ldots,2MbA
\]

are distinct on the residue circle. A cyclic gap has length at most `floor(p/N)`, so its endpoint indices give an integer `ell` in `[1,M]` with a centered representative `v` of `2b ell A` satisfying `|v|<=floor(p/N)`.

Assume

\[
\boxed{(c+1)(\lfloor c/b\rfloor+1)>p.}
\tag{5}
\]

Then `floor(p/N)<=c`. Set `j=b ell`, so `b<=j<=c`. Choose the least integer `n>=max(j-1,|v|)` having the parity of `v`. If `|v|=c`, the maximum is `c` and its parity is already correct. Otherwise both entries of that maximum are at most `c-1`, and adjusting by at most one still gives `n<=c`. Thus (2) holds and (3) is short.

**General selector theorem.** Every companion satisfying (1) and (5), in the stated range, is impossible. There is no parity hypothesis on `p` or `c`. The theorem remains conditional on (1) until an inverse theorem supplies it.

## 3. An unconditional band and its exact residual restriction

Let `b>=4` and `p>=10b`, within the standing rank-three multiplicity strip. The linear bounded-hole theorem and the half-power plane inverse force (1). One may take the light subdonor with `K=min(c+2,H+1)`; all its core and power hypotheses hold, and its exceptional prime eleven is outside the bound.

The minimal endpoint `c=b-1` is excluded by `PLANAR_HALF_POWER_INVERSE_AND_MINIMAL_OVERLAP_V1.md`. For all other rows, `c>=b`, and (5) is an unconditional exclusion. Therefore every surviving row with these `p,b` must satisfy

\[
\boxed{c\ge b,\qquad(c+1)(\lfloor c/b\rfloor+1)\le p.}
\tag{6}
\]

Since `floor(c/b)+1>=(c+1)/b`, this gives

\[
\boxed{(c+1)^2\le bp.}
\tag{7}
\]

There is also a useful combination with the earlier negative-even balanced-band theorem. If `b>=7` and `b<=c<=2b-2`, then `c>=7`, `p>=10b>3(c+1)`, and the old boundary coordinate `k=c+1-b` satisfies `2k<=c`. That theorem eliminates this entire range; the minimal endpoint was already excluded. Thus for `b>=7,p>=10b`, a survivor must satisfy the sharper joint restrictions

\[
\boxed{2b-1\le c,\qquad(c+1)(\lfloor c/b\rfloor+1)\le p.}
\tag{8}
\]

These bounds still leave an intermediate range. They do not close every larger deficit, nor assert any surviving row is realizable.

## 4. Relation to the earlier complete faces and proof checks

The whole faces `b=1,2,3` remain closed by their separate all-prime proofs. Formula (3) extends their mixed mechanism, while the stepped circle handles the new lower bound `j>=b`. A circle based on all consecutive indices would not itself ensure that bound. The parity adjustment explicitly handles the endpoint `|v|=c`.

The argument was checked locally for all capacities, signed gaps, ordinary length, exact floor inequalities, and the independent hypotheses of the balanced-band corollary. It is elementary and uses no enumeration. The inverse theorem's explicit prime threshold and the unresolved global first-corridor and Davenport-value gates remain in force.
