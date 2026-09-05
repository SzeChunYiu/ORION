# Type two: complete elimination of the first unsaturated rank-three face

Status: **proved for every prime p>=7 and every allowed shared multiplicity**. The entire face with high new multiplicity `p-2` is empty. The proof uses the all-prime unsaturated donor inverse and one exact mixed completion argument; it does not assume saturated new-value occurrences.

## 1. The theorem

Let `p=2H+1>=7`, `m=3H+1`, `u=H+1=2^{-1}`, and `s=(u,u,1)` in a basis `(e1,e2,g)`. Set

\[
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2.
\]

**Theorem.** For every `1<=c<=H`, put `r=H+1-c`. If

\[
\boxed{V=s^c g x^r y^{p-2},\qquad\sigma(V)=0,}
\tag{1}
\]

then `UV` contains a nonempty zero-sum of length at most `m-1`.

In particular this closes every rank-three type-two first-corridor row on the first unsaturated face `b=2`. The argument needs no additional rank or distinct-support hypothesis beyond the displayed group equation and actual occurrences.

## 2. Two endpoints and the exact donor inverse gate

The shared old donor is

\[
B_{c+2}=e_1^{p-1}e_2^{p-1}g^{p-1}s^{c+2}.
\]

If `c=1`, multiply (1)'s relation by three. The available sequence

\[
s^3g^3x^{H-1}y^{p-6}
\]

is zero-sum and has length `m-1`. Indeed `3H=p+H-1` and `3(p-2)=2p+p-6`; all four positive counts fit for every `p>=7`. This is the previously proved one-light-share certificate, included here to make the endpoint explicit.

If `c=H`, the all-prime first-unsaturated donor theorem rules out `B_{H+2} y^{p-2}` by itself: for odd `H` the donor already has a short zero-sum, and for even `H` its forced plane value exceeds the exact top-plane power capacity.

It remains to consider `2<=c<=H-1`. By `A2_FIRST_UNSATURATED_DONOR_INVERSE_ALL_PRIMES_V1.md`, short-freeness would force

\[
y=(A,-A,1),\quad A\ne0,
\tag{2}
\]

apart from the sole possible exception `(p,c)=(11,2)`, where `y=(4,7,2)` or its first-two-coordinate exchange. The `K=3` inverse exception cannot occur because `c>=2`. Section 5 handles the retained `p=11` exception directly.

## 3. The entire main face has coordinate sum two

From (1)--(2), the companion relation is

\[
rx=2y-cs-g,\qquad r=H+1-c.
\tag{3}
\]

Write `x=(X1,X2,C)`. Summing its three coordinates in the field gives

\[
r(X_1+X_2+C)=2-2c-1=1-2c=2r.
\]

The coefficient `r` is nonzero, so

\[
\boxed{X_1+X_2+C=2.}
\tag{4}
\]

This identity holds for every shared multiplicity in the face, not only `c=2`.

The third coordinate separately gives

\[
C=(1-c)/r.
\]

It is neither zero, one nor two:

- `C=0` would force `c=1`;
- `C=1` would force `1-c=r=H+1-c`, hence `H=0` in `F_p`;
- `C=2` would force `1-c=2r==1-2c`, hence `c=0` in `F_p`.

All are impossible in the present range. Therefore

\[
q=[-C]_p\in[1,p-3],\qquad M=p-2-q\ge1.
\tag{5}
\]

The actual product supplies one `x`, at least `q` copies of `y,g`, and at least `M` of each axis: `q<=p-3<p-2`, `r>=1`, and all basis donor counts are saturated. Thus every hypothesis of `CYCLIC_COMPLEMENT_INTERVAL_MIXED_RIGIDITY_V1.md` is satisfied.

## 4. Both possible progression steps contradict the companion relation

If an integer `0<=j<=q` has `P=[-X1-jA]_p<=M`, that lemma supplies the actual zero-sum

\[
\boxed{x\,y^j g^{q-j}e_1^P e_2^{M-P}}
\]

of length exactly `p-1<m`.

If no such short certificate exists, the same lemma forces either

`A=1,X1=1`, or `A=-1,X2=1`.

In the first case, the first coordinate of (3) reads

\[
r=2-c/2.
\]

Twice this equation, compared with `2r==1-2c`, gives

\[
4-c=1-2c,\qquad c+3=0\quad\text{in }\mathbb F_p.
\]

But `2<=c<=H-1<p-3`, so `c=p-3` is impossible. In the second case the second coordinate of (3) gives exactly the same contradiction. Thus one of the length-`p-1` mixed certificates must exist throughout the main family.

The rigidity step is an exact covering argument: the unavailable certificate indices would make a `q+1`-term arithmetic progression equal the complementary interval of exactly that size. Its translation boundary forces the two possible steps; the independent companion equation rules both out. No search over new values, primes, or multipliers supplies existence.

## 5. The genuine inverse exception at p = 11

For `(p,c)=(11,2)`, one has `H=5`, `r=4`, `s=(6,6,1)`. If `y=(4,7,2)`, equation (3), now with its actual third coordinate two, gives

\[
4x=2y-2s-g=(7,2,1),\qquad x=(10,6,3).
\]

The explicit available sequence

\[
\boxed{x s^2 e_2^4 g^6}
\]

has coordinate sum `(11,11,11)` and length `13<m=16`. Its light count is two of the four available; its other donor counts fit the saturated capacities. Exchanging the two axes handles `y=(7,4,2)`.

This treats the actual exception instead of imposing the main inverse form on it.

## 6. Complete scope and remaining frontier

Sections 2--5 cover every `1<=c<=H` and every prime `p>=7`. Consequently the entire first unsaturated rank-three face `t=p-2` is eliminated. Combined with the earlier saturated face `t=p-1` and the complete `c=1` layer, any remaining rank-three type-two row must satisfy

\[
\boxed{3\le b\le c+1,\qquad c\ge2,
\qquad V=s^c g x^{H+b-1-c}y^{p-b},}
\]

together with the previously proved quotient and overlap restrictions.

The theorem does not close those deeper unsaturated faces, every rank-two top-overlap row, the first corridor, or any unproved numerical Davenport constant. The proof was checked locally at the inverse-theorem exception, the nonzero denominator, the three excluded third coordinates, every completion capacity, and both progression-step contradictions. No separate external review is claimed.
