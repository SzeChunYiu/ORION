# An elementary extremal theorem for rigid powers of two-value cyclic atoms — V1

Status: **proved prime-uniform bound and exact equality classification**. The proof is a two-dimensional integer argument. It uses neither a long-atom index theorem nor a splitting theorem.

## 1. The theorem

Let `p` be prime, let `x,y` be distinct nonzero elements of `C_p`, and let

\[
Q=x^A y^B
\]

be an atom, where `A,B>=1`. Suppose `k>=2`, `kA,kB<=p-1`, and `Q` is the **only** atom dividing `Q^k`. Then

\[
\boxed{k|Q|\le p+k-1.}
\tag{1}
\]

Equality holds if and only if, after interchanging the two values,

\[
\boxed{Q=x^{(p-1)/k}y,\qquad
y=-\frac{p-1}{k}x.}
\tag{2}
\]

In particular, equality requires `k|(p-1)`. The hypothesis concerns all atomic divisors of the power, not merely one displayed factorization.

## 2. An integer certificate when both multiplicities exceed one

Suppose `A,B>=2` and, seeking a contradiction, assume

\[
k(A+B)\ge p+k-1,
\quad\text{or equivalently}\quad
p\le k(A+B)-k+1.
\tag{3}
\]

Atomicity implies `gcd(A,B)=1`. Indeed, if `h=gcd(A,B)>1`, then `h<p` and the relation `Ax+By=0` can be divided by the invertible scalar `h`, yielding a proper zero-sum divisor of `Q`.

Choose the unique `a_0` with

\[
1\le a_0\le A-1,\qquad B a_0\equiv p\pmod A,
\]

and put `b_0=(B a_0-p)/A`. Existence follows from `gcd(A,B)=1`; the residue is nonzero because the prime `p` is not divisible by `A`, where `2<=A<p`. We have `b_0<B`.

Moreover,

\[
\begin{aligned}
A\bigl(b_0+(k-1)B\bigr)
&=B a_0-p+(k-1)AB\\
&\ge ((k-1)A+1)B-p\\
&\ge (k-1)(A-1)(B-1)-A.
\end{aligned}
\tag{4}
\]

For `k>=3`, the last expression is at least

\[
(k-1)(A-1)-A=(k-2)A-k+1\ge k-3\ge0.
\]

For `k=2`, interchange `A,B` first so that `A<=B`. The coprimality and `A,B>=2` ensure `B>=3`. The last expression in (4) is then at least `2(A-1)-A=A-2>=0`.

Take the least nonnegative integer `j` for which `b_0+jB>=0`. Equation (4) gives `j<=k-1`. Define

\[
a=a_0+jA,\qquad b=b_0+jB.
\]

Then

\[
1\le a<kA<p,\qquad 0\le b<B,\qquad Ba-Ab=p.
\tag{5}
\]

In fact `b>0`: otherwise `Ba=p` would imply `p|a`, since `1<=B<p`, contradicting (5).

The zero-sum relation of `Q` gives `y=-AB^{-1}x`. Equation (5) therefore implies

\[
ax+by=B^{-1}(Ba-Ab)x=0\quad\text{in }C_p.
\]

Thus `x^a y^b` is a nonempty zero-sum divisor of `Q^k`, and it cannot contain `Q` because `b<B`. Any atom dividing it is different from `Q`. This contradicts rigidity. We have proved that, when both multiplicities exceed one,

\[
k|Q|\le p+k-2.
\tag{6}
\]

## 3. Singleton multiplicity and equality

If `B=1`, then `kA<=p-1` gives

\[
k|Q|=kA+k\le p+k-1.
\]

Equality forces `A=(p-1)/k`, and atomicity's zero-sum relation forces (2). The case `A=1` is symmetric. Together with (6), this proves the bound and its necessary equality form.

Conversely, take (2). The sequence `Q` is an atom: a zero-sum divisor with one `y` must have exactly `A` copies of `x`, and fewer than `p` copies of `x` alone cannot sum to zero. For any zero-sum divisor `x^a y^b|Q^k`,

\[
0\le a\le p-1,\quad 0\le b\le k,\quad
a\equiv Ab\pmod p.
\]

Since `0<=Ab<=Ak=p-1`, this congruence is the ordinary equality `a=Ab`. Every nonempty such divisor is `Q^b`, so `Q` is indeed the only atomic divisor of `Q^k`. This proves sufficiency.

## 4. Complete rigid-power reduction in the type-two overlap problem

Use the hypotheses and notation of `A2_RANK2_EXACT_QUOTIENT_DEFECT_BUDGET_V1.md`: `d=H-c>=1`, `|R|=p+d`. Suppose that

\[
\pi(R)=Q^k
\]

and `Q` is its only atomic divisor. Each occurrence copy of `Q` has the same integer defect `D>=1`. The exact budget gives

\[
kD=d+1.
\]

The multiplicity bound in (1) gives `p+d<=p+k-1`, so `d+1<=k`. Thus equality is necessary throughout:

\[
k=d+1,\qquad D=1.
\]

By (2), the original new multiplicities are, up to order,

\[
r=k,\qquad t=p-1,\qquad c=H+1-k.
\]

The quotient atom has length `(p-1)/k+1`. Defect one and the lower shifted-depth inequality force

\[
q=\frac{p-1}{2k}+1\quad\text{to be an odd integer}.
\]

Consequently

\[
\boxed{p=4kL+1,\quad
(c,r,t)=(2kL+1-k,\ k,\ p-1)}
\tag{7}
\]

for a positive integer `L`.

These are exactly the rigid quotient rows of the previously proved scalar barrier in `A2_RANK2_EXACT_SCALAR_BARRIER_V1.md`. The identification is structural. Indeed, for that row the quotient relation is `bar(y)=k bar(x)`; its atomic divisor is `Q=bar(x) bar(y)^{4L}`, and every proper projected-zero part is `Q^j`, `1<=j<=k-1`. Its light coefficient and defect are

\[
q_j=j(2L+1),\qquad D_j=j.
\]

They satisfy the entire shifted-depth window. The lower bound holds at `j=1` with equality, and automatically for `j>=2`; the upper bound is automatic for `j<=k-2`, while `j=k-1` gives `q_j+c` even and equality. Thus quotient rigidity alone cannot eliminate (7).

## 5. A shorter proof of the previous complete layer

For `c=H-1`, the existing argument establishes a rigid square `Q^2` of length `p+1`. Applying this theorem with `k=2` immediately gives `(r,t)=(2,p-1)` up to order. The established two-new-occurrence endpoint theorem then eliminates the row.

This replaces Sections 4–5 of `A2_RANK2_PENULTIMATE_OVERLAP_FULL_ELIMINATION_V1.md` with the elementary integer argument above. The earlier proof remains preserved and valid. Its Xia–Yuan splitting and Savchev–Chen index inputs are no longer needed for this reduction; the endpoint's separate Bhowmik–Halupczok–Schlage-Puchta dependency is unchanged.

## 6. Review and exact scope

The review checked coprimality, both `k=2` and `k>=3` inequalities, the nonzero modular residue `a_0`, the first admissible integer shift, the exclusion of `b=0`, and all occurrence capacities. The converse checks every zero-sum divisor, not only atoms.

There is no unproved index-one assertion in the proof. The result applies to powers with only one atomic divisor; it does not say that an arbitrary quotient has this form. The type-two scalar-barrier rows still require mixed geometry. No full first-corridor or generalized Davenport value is asserted. Review is internal by the producing researcher, with no independent audit or priority claim.
