# The full integer-functional equality classification — V1

Status: **proved complete equality classification for the integer-weighted bound**, including the essential zero-coefficient exception. This strengthens `CYCLIC_WEIGHTED_RECTANGLE_EXTREMAL_THEOREM_V1.md`. The coordinating researcher independently checked the quotient-structure proof.

## 1. Equality with two nonzero coefficients does not require parity

Keep the weighted theorem's hypotheses: `S=x^r y^t` is zero-sum over `C_p`, its distinct values are nonzero, `r,t<p`, `N=r+t>p`, and the integer functional

\[
f(A,B)=uA+vB
\]

is positive on every atomic divisor. Its total obeys `F>=N-p+1` by the previously proved intersection bound.

Suppose equality holds, and set `a=N-p+1`. As proved there, every level `D=0,...,a` occurs exactly once; the level-one vector `P=(A,B)` is an atom, and

\[
Y_D=([DA]_p,[DB]_p).
\]

Assume now only that both `u,v` are nonzero, with no parity assumption. Exact linearity gives

\[
D=f(Y_D)=D f(P)
-p\left(u\left\lfloor DA/p\right\rfloor
+v\left\lfloor DB/p\right\rfloor\right),
\]

so, since `f(P)=1`,

\[
u\left\lfloor DA/p\right\rfloor
+v\left\lfloor DB/p\right\rfloor=0.
\tag{1}
\]

At a first wrap, one floor alone cannot increase: equation (1) would force the corresponding coefficient to vanish. If both increase, the resulting actual vector is strictly positive and strictly smaller than `P` in both coordinates, contradicting atomicity exactly as in the earlier proof.

There is therefore no wrap, and `S=P^a` is rigid. The elementary rigid-power equality theorem yields, after swapping values,

\[
\boxed{(r,t)=(a,p-1),\quad y=a x,\quad a\mid(p-1),
\quad f\bigl(1,(p-1)/a\bigr)=1.}
\tag{2}
\]

Conversely, (2) gives a rigid sequence whose only atom has functional value one, so positivity and equality follow.

If the coefficients are additionally odd, the atom's value one forces its length odd and recovers `2a|(p-1)`.

## 2. A zero coefficient gives a different equality family

Suppose `v=0`. Positivity on mixed atoms implies `u>=1`. Equality reads

\[
ur=r+t-p+1,
\qquad (u-1)r=t-p+1.
\]

The left side is nonnegative and the right side is nonpositive. Thus `u=1` and `t=p-1`. The zero-sum relation then gives `y=r x`, and `a=r`.

Conversely, for every `2<=a<=p-1`, the endpoint

\[
S=x^a(a x)^{p-1}
\]

with `f(A,B)=A` has positive functional value on every atom: every atomic divisor is mixed because neither multiplicity reaches `p`. Its total value is `a=N-p+1`. No divisibility `a|(p-1)` is needed. The case `u=0` is symmetric.

This caveat is necessary. At `p=7`, let `y=4x` and

\[
S=x^4y^6,\qquad f(A,B)=A.
\]

It has `N=10`, `F=4=N-p+1`, but at least the distinct atoms

\[
x^3y,\qquad x^2y^3,\qquad xy^5
\]

divide it. To verify all three are atoms without a search, use `y` as generator; then `x=2y`, and their positive representative sums are respectively `3\cdot2+1`, `2\cdot2+3`, and `2+5`, each equal to seven. Thus the equality sequence is not rigid.

## 3. Full integer-functional equality theorem

Under the lower-bound hypotheses, equality always forces at least one original multiplicity to be `p-1`.

- If both functional coefficients are nonzero, equality is exactly the rigid endpoint (2).
- If one coefficient is zero, the other is one, and the opposite value has multiplicity `p-1`; this coordinate-projection endpoint may be nonrigid.

For two nonzero coefficients and a nonrigid sequence,

\[
F\ge N-p+2.
\]

For two odd coefficients and a nonrigid sequence, the earlier parity argument strengthens this to

\[
F\ge N-p+3.
\]

## 4. Proof authority and boundary

The quotient-structure researcher derived the strengthening and the coordinating researcher independently checked its first-wrap argument, every coefficient case, the exact normal form, and the analytic nonrigid equality example. No prime, support-value, or subsequence enumeration was used. The lower bound and rigid-power equality classification are the already proved elementary results cited in `CYCLIC_WEIGHTED_RECTANGLE_EXTREMAL_THEOREM_V1.md`.

The example preserves a failed overgeneralization: equality does not imply rigidity when a functional coefficient vanishes. The hypothesis of strict positivity applies to every atomic count-vector type in the actual occurrence rectangle. These results do not establish an unproved generalized Davenport equality.
