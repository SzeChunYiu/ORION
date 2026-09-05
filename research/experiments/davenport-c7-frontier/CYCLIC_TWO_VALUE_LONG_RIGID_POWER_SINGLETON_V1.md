# Long rigid powers of two-value cyclic atoms have a singleton multiplicity — V1

Status: **proved complete structural classification for rigid powers of length greater than the prime**. This strengthens the earlier extremal bound away from its equality case.

## 1. Statement

Let `p` be prime, let `x,y` be distinct nonzero elements of `C_p`, and let `Q=x^A y^B` be an atom. Suppose

\[
k\ge2,\qquad kA,kB<p,\qquad k(A+B)>p.
\]

Then `Q` is the only atomic count-vector type dividing `Q^k` if and only if

\[
\boxed{\min(A,B)=1.}
\]

The hypothesis concerns every atomic divisor within the actual capacity rectangle. A displayed power factorization alone is insufficient.

## 2. Necessity by an integer certificate

Suppose both multiplicities exceed one. After interchanging the values assume `2<=A<=B`. Atomicity gives `gcd(A,B)=1`: a common divisor less than `p` could be inverted modulo `p`, producing a proper zero-sum divisor. In particular `B>=3`.

Choose `1<=a_0<A` with `B a_0 == p (mod A)`, and set `b_0=(B a_0-p)/A<B`. The residue `a_0` is nonzero because `p` is prime and `1<A<p`. Since `p<=k(A+B)-1`,

\[
\begin{aligned}
A\bigl(b_0+(k-1)B\bigr)
&=Ba_0-p+(k-1)AB\\
&\ge(k-1)(A-1)(B-1)-A-k+2\\
&\ge(2k-3)A-3k+4\\
&\ge k-2\ge0.
\end{aligned}
\]

Let `j` be the least nonnegative integer with `b_0+jB>=0`. Then `j<=k-1`, and

\[
a=a_0+jA,\qquad b=b_0+jB
\]

satisfy

\[
1\le a<kA<p,\qquad 0\le b<B,\qquad Ba-Ab=p.
\]

Here `b` is positive: otherwise `Ba=p` would force `p|a`, impossible. From `y=-AB^{-1}x`, the last displayed equality gives `ax+by=0` in `C_p`. Thus `x^a y^b` is an actual nonempty zero-sum divisor of `Q^k` which cannot contain `Q`, because `b<B`. Any atomic divisor of it is a different atom type. This contradicts rigidity.

## 3. Sufficiency checks every divisor

If `B=1`, then `y=-Ax`. For any zero-sum divisor `x^a y^b|Q^k`,

\[
a\equiv Ab\pmod p,\qquad 0\le a,Ab\le kA<p.
\]

These bounds force the ordinary equality `a=Ab`. Every such nonempty divisor is `Q^b`, so its only atom type is `Q`. The case `A=1` is symmetric.

## 4. Review and boundary

The coordinating researcher derived the stronger inequality. The separate proof-audit researcher checked the entire certificate, the endpoint `k=2`, coprimality, positive occurrence counts, and the singleton converse. No external inverse theorem or enumeration is used.

The result does not apply when the power has length at most `p`; in particular, it does not eliminate the short rigid-square alternative in the rank-three quotient budget. The older `CYCLIC_TWO_VALUE_RIGID_POWER_BOUND_V1.md` remains valid and supplies a separate exact extremal bound and its Davenport application.
