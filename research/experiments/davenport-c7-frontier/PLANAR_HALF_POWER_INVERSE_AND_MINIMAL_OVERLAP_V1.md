# An exact planar inverse theorem at half the power range

Status: **proved elementary prime-uniform inverse theorem**. A saturated plane together with `H=(p-1)/2` copies of one value is short-free at the first-corridor threshold exactly for the sum of its two basis values. Applied to the main type-two inverse family, it removes every minimal-overlap endpoint, uniformly in the deficit.

## 1. The planar theorem

Let `p=2H+1>=7` be prime, let `e1,e2` be independent in an elementary abelian group of exponent `p`, and let `x` lie in their span. Set `m=p+H`.

**Theorem.** The sequence

\[
e_1^{p-1}e_2^{p-1}x^H
\tag{1}
\]

contains no nonempty zero-sum of length below `m` if and only if

\[
\boxed{x=e_1+e_2.}
\tag{2}
\]

The ambient rank is irrelevant; the proof uses only this plane and the actual `H` copies.

## 2. Reduce to small positive coordinate representatives

Write `x=Ae1+Be2`, and set `K=[A+B]_p`. If `K=0`, the singleton's saturated completion has length at most `p+1<m`. If `K=1`, it has length `p<m`. These include zero-coordinate cases.

If `K=2`, the two completion counts sum to either `p-2` or `2p-2`. The first gives a zero-sum of length `p-1`. The second requires both counts to equal `p-1`, giving `A=B=1`, precisely (2).

It remains to consider `3<=K<=p-1`. Put `P=[-A]_p`. If `P<=p-K`, then

\[
xe_1^P e_2^{p-K-P}
\]

is a zero-sum of length `p-K+1<m`. Otherwise `P>p-K` forces the ordinary integer representatives

\[
1\le A\le K-1,\qquad B=K-A\ge1.
\tag{3}
\]

Thus both coordinates are positive, their ordinary sum is `K<=p-1`, and they are not both one. Let `M=max(A,B)>=2`.

## 3. Every remaining coordinate maximum has an available short completion

If `M=2`, the only unordered pairs are `(1,2)` and `(2,2)`. The `H`th power has completed lengths `p+1` and `H+2`, respectively, both below `m`.

Suppose `M>=3` and `M!=H+1`. Write

\[
p=qM+R,\qquad q=\lfloor p/M\rfloor,\qquad1\le R<M.
\]

The elementary division estimate from `A2_HALF_POWER_PLANE_INVERSE_CLASSIFICATION_V1.md`, Section 2, gives

\[
q\le H-1,\qquad q+R\le H.
\tag{4}
\]

Here is its short proof. If `M>=H+2`, then `q=1,R<=H-1`. For `3<=M<=H`, one has `(q-1)M>=2q`, except possibly `q=2,M=3`. Since `p+1<=(q+1)M`, the inequality yields `p+1<=2q(M-1)`, equivalent to `q+R<=H`. The omitted pair forces `p=7`, where the estimate is equality. The power bound follows from `q<=floor(p/3)<=H-1`, with seven checked by the same division.

Complete `x^q` by the two saturated axes. The coordinate at `M` requires exactly `R` basis copies, and the other requires at most `p-1`. Its length is consequently at most

\[
q+R+p-1\le p+H-1=m-1.
\]

All counts fit (1).

Finally suppose `M=H+1`. If the other coordinate is at least two, the singleton completion has length at most `1+H+p-2=m-1`. If the other coordinate is one, use the third power. Its two completion counts are `H-1` and `p-3`, so its length is again `m-1`. This power is available because `H>=3`.

This eliminates every value except (2).

## 4. Complete converse

For `x=e1+e2`, a zero-sum using `1<=j<=H` copies of `x` must use `p-j` copies of each axis. Its length is

\[
2p-j\ge2p-H=m+1.
\]

A zero-sum using no `x` must be empty, by independence and the axis capacities below `p`. Thus every subsequence is accounted for and (2) really is short-free.

## 5. All minimal-overlap endpoints in the type-two main family

Use the standing type-two coordinates

\[
s=(u,u,1),\quad u=H+1,\quad
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2,
\]

and suppose the main inverse family and minimal-overlap companion relation hold:

\[
V=s^c g x^H y^{p-c-1},\qquad
y=(A,-A,1),\quad A\ne0,\quad2\le c\le H.
\tag{5}
\]

Equivalently the deficit is `b=c+1` and `r=H`. From `sigma(V)=0`,

\[
Hx=(c+1)y-cs-g.
\]

The third coordinate of `x` is zero. The sum of its first two coordinates is

\[
-c/H=2c\quad\text{in }\mathbb F_p.
\]

Since `2<=c<=H`, this is never two. In particular `x!=e1+e2`. The actual product contains the planar donor (1), so the theorem supplies a short zero-sum.

**Main-family corollary.** Every endpoint `b=c+1>=3` in (5) is empty, for every prime, with no deficit-dependent threshold.

The inverse-family hypothesis remains essential to this corollary. It is established without that hypothesis when `p>=10(c+1)`: the linear half-interval theorem forces the opposite-coordinate plane, and the half-power plane theorem leaves only the main family. Its isolated exceptional prime eleven cannot occur under this bound. All required core and power inequalities follow from `p>=10b`; the actual light count is `c+2`.

In particular, at `c=3`, the endpoint `b=4` is completely eliminated for every prime `p>=41`. Together with the already complete faces `b=1,2,3`, this closes the whole rank-three layer `c=3` for those primes. The smaller-prime `c=3,b=4` inverse gate is not claimed here.

## 6. Scope and verification

The theorem and its main-family corollary are elementary and use no enumeration or external inverse theorem. Each power is at most `H`; both exceptional coordinate maxima are treated explicitly; and the converse checks every possible zero-sum. These points were checked locally. No independently tasked review or full first-corridor conclusion is asserted.
