# The weighted extremal theorem for two-value cyclic zero-sum rectangles — V1

Status: **proved for every odd prime, throughout the complete feasible length range `p<N<=2p-2`**. Integer weights give the sharp lower bound; odd weights give an exact equality classification and a strict gap for nonrigid sequences. The theorem does not assume the Davenport donor setup.

## 1. Statement

Let `p` be an odd prime, let `x,y` be distinct nonzero elements of `C_p`, and let

\[
S=x^r y^t,\qquad 1\le r,t\le p-1,\qquad
\sigma(S)=0,
\qquad N=r+t>p.
\]

Let

\[
f(A,B)=uA+vB
\]

have integer coefficients. Suppose `f` is strictly positive on every atomic divisor of `S`, and put `F=f(r,t)`.

Then

\[
\boxed{F\ge N-p+1.}
\tag{1}
\]

If both `u,v` are odd, put `a=N-p+1` (`2<=a<=p-1`). Equality in (1) holds if and only if, after interchanging the two values,

\[
\boxed{
r=a,\qquad t=p-1,\qquad y=a x,
\qquad 2a\mid(p-1),
\qquad f\bigl(1,(p-1)/a\bigr)=1.
}
\tag{2}
\]

In that case `S=Q^a` with `Q=x y^((p-1)/a)` its only atomic divisor.

Consequently, if `u,v` are odd and `S` has at least two distinct atomic divisors, then

\[
\boxed{F\ge N-p+3.}
\tag{3}
\]

The condition on `f(Q)` in (2) is essential for a fixed functional: the endpoint sequence alone does not force every positive odd functional to attain equality.

## 2. The lower bound by intersection counting

Every nonempty zero-sum divisor factors into atoms, so its `f` value is a positive integer. In particular `F>0`, and any nonempty proper zero-sum divisor has value in `[1,F-1]`, because its zero-sum complement also has positive value.

If `F>=p`, then (1) is immediate from `N<=2p-2`, which gives `N-p+1<=p-1`.

Suppose `1<=F<p`. Every zero-sum count vector `(A,B)` in the occurrence rectangle is congruent to `lambda(r,t)` for a unique scalar `lambda` in `F_p`. Its value satisfies

\[
f(A,B)\equiv\lambda F\pmod p.
\]

Since `F` is invertible modulo `p`, the actual integer value `f(A,B)` determines `lambda`. Since both coordinates are below `p`, that scalar determines at most one actual count vector.

Thus there are at most `F+1` zero-sum count vectors: the empty vector of value zero, at most one for each proper value `1,...,F-1`, and the full vector of value `F`.

On the other hand, those vectors correspond exactly to the intersection

\[
\{Ax:0\le A\le r\}\cap\{-By:0\le B\le t\}.
\]

Its cardinality is at least

\[
(r+1)+(t+1)-p=N-p+2.
\]

Therefore `N-p+2<=F+1`, proving (1).

## 3. Odd equality synchronizes the two residue progressions

Assume `u,v` are odd and `F=a=N-p+1`. The preceding two cardinality bounds are equal, so every level `D=0,...,a` is attained by a unique zero-sum count vector `Y_D`; the endpoint vectors are empty and full.

Let `P=Y_1=x^A y^B`. It is an atom: a factorization into two or more nonempty zero-sum parts would express its value one as a sum of at least two positive integers. It is mixed because the entire sequence has fewer than `p` copies of either value.

The unique relation scalar of `P` is `a^{-1}`, so every level has actual count vector

\[
Y_D=x^{[DA]_p}y^{[DB]_p}\qquad(0\le D\le a).
\tag{4}
\]

The odd coefficients imply

\[
|Y_D|\equiv f(Y_D)=D\pmod2.
\]

In particular `A+B` is odd. Combining this with (4),

\[
\left\lfloor DA/p\right\rfloor+
\left\lfloor DB/p\right\rfloor
\equiv0\pmod2
\qquad(0\le D\le a).
\tag{5}
\]

Each floor rises by zero or one in each step. Hence (5) forces every rise to occur in both coordinates simultaneously.

If `j<=a` were the first rise, the vector for `Y_j` would be `(jA-p,jB-p)`. Since `a<=p-1`, primality and `j<p` make both coordinates strictly positive. Absence of an earlier rise makes them strictly less than `A,B`. This produces a nonempty proper zero-sum divisor of the atom `P`, impossible.

Thus there are no rises through level `a`, and every zero-sum divisor is `P^D`. In particular

\[
S=P^a
\]

with `P` its only atomic divisor.

This argument does not require `a<=p/2`: positivity of the ordinary functional, rather than a small modular interval, proves level-one atomicity throughout `2<=a<=p-1`.

## 4. Exact normal form and converse

The equality `a|P|=N=p+a-1` is precisely equality in the elementary bound of `CYCLIC_TWO_VALUE_RIGID_POWER_BOUND_V1.md`. Its equality classification gives

\[
P=x\,y^{(p-1)/a}
\]

after a possible interchange, and consequently `(r,t)=(a,p-1)` and `y=a x`.

Oddness of `|P|` yields `2a|(p-1)`. Also `f(P)=1` by its definition as the level-one vector. This proves the necessity of (2).

Conversely, suppose (2) holds. The rigid-power theorem's elementary converse classifies every nonempty zero-sum divisor as `Q^D`, `1<=D<=a`. Thus `Q` is the only atomic divisor. The condition `f(Q)=1` ensures positivity on it, and

\[
F=f(Q^a)=a=N-p+1.
\]

This proves the exact equality criterion.

For every endpoint sequence allowed by (2), at least one such odd functional exists: writing `b=(p-1)/a`, which is even, the functional

\[
f(A,B)=(1-b)A+B
\]

has odd coefficients and satisfies `f(1,b)=1`.

## 5. The strict nonrigid gap

If `S` has more than one atomic-divisor type, equality in (1) is impossible by the preceding classification. Because both functional coefficients are odd,

\[
F\equiv r+t=N\equiv N-p+1\pmod2.
\]

The next possible integer above the lower bound is therefore `N-p+3`, proving (3).

## 6. Interpretation and audit

The first bound is a direct count of actual zero-sum vectors. Equality makes every intermediate functional value occur. Oddness then prevents one coordinate of the residue progression from wrapping alone; a simultaneous first wrap would split the value-one atom. This forces exact rigidity and its known endpoint normal form.

The theorem separates an arbitrary integer positive functional from the stronger odd-coefficient equality conclusion. It counts divisors by their actual occurrence vectors, and never applies an atomic length formula to a general divisor.

Root, quotient_structure, and proof_audit independently checked the lower bound, scalar injectivity, the full equality range `a<=p-1`, the endpoint normal form, the qualification `f(Q)=1`, and the parity gap. No finite search or external long-atom inverse theorem enters the proof. The only imported result for the last multiplicity classification is the existing elementary rigid-power equality theorem.
