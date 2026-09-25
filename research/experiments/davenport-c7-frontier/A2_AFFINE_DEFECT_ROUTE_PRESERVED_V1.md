# Preserved route: integer linearization of the type-two quotient defect — V1

Preserved proof route from quotient_structure, building on root's affine-potential proposal and proof_audit's elementary consecutive-determinant theorem. The subsequent rectangular charge theorem eliminates the entire type-two submaximal family; the potential below is therefore a valid intermediate implication, not an active restriction on a surviving family.

## 1. Hypotheses

Use the canonical type-two rank-two light-share hypotheses of `A2_RANK2_EXACT_QUOTIENT_DEFECT_BUDGET_V1.md`. Put

\[
p=2H+1,\qquad 1\le c<H,\qquad d=H-c,\qquad a=d+1\le H,
\]

and let `R=x^r y^t` be the two-value cyclic quotient, of length `p+a-1`, with distinct nonzero values and `r,t<p`.

Every atomic divisor has an integer defect `D` in `[1,a-1]`. All atomizations have total defect `a`. The actual count vectors obey

\[
(A,B)\equiv D a^{-1}(r,t)\pmod p,
\qquad D\equiv A+B\pmod2.
\tag{1}
\]

Assume the quotient has at least two distinct atomic divisors. The existing rigid-power and saturated-boundary results already eliminate the alternative in the type-two setting.

The conclusion below needs no square-root condition on `d`.

## 2. Elementary lattice facts

The relation lattice

\[
\mathcal L=\{(A,B)\in\mathbb Z^2:Ax+By=0\}
\]

has index `p`. Atomic count vectors form a strictly decreasing Pareto frontier, and the atomic divisors of the occurrence rectangle `[0,r]×[0,t]` form a contiguous segment of it.

The elementary determinant theorem in `TWO_VALUE_LATTICE_ATOMS_AND_LENGTH_GCD_DICHOTOMY_V1.md` says that consecutive global atoms have determinant `p` when ordered by decreasing first coordinate and increasing second coordinate. Thus for three consecutive actual atoms `P,Q,E`,

\[
P+E=kQ\qquad\text{for an integer }k\ge2.
\tag{2}
\]

Indeed, `P,Q` form a basis of the relation lattice. Equality of the consecutive determinants forces the coefficient of `P` in `E` to be minus one. The first-coordinate ordering forces `k>1`.

## 3. Define an integer functional on one adjacent pair

Choose two consecutive actual atoms `P=(A,B)` and `Q=(C,E)` with

\[
AE-BC=p.
\]

Let their defects be `D_P,D_Q`. The unique rational linear functional taking those values is

\[
f(X,Y)=uX+vY,
\]

where

\[
u=\frac{D_PE-D_QB}{p},\qquad
v=\frac{AD_Q-CD_P}{p}.
\tag{3}
\]

Both coefficients are integers: the numerators vanish modulo `p` by the count congruences (1).

Both coefficients are odd. Reduce the first numerator modulo two and use `D_P==A+B`, `D_Q==C+E`:

\[
D_PE-D_QB\equiv(A+B)E-(C+E)B=AE-BC=p\equiv1\pmod2.
\]

Division by odd `p` preserves parity. The second numerator has the same parity by the symmetric calculation.

Consequently, for every atomic count vector `Z`,

\[
f(Z)\equiv D_Z\pmod{2p}.
\tag{4}
\]

For the congruence modulo `p`, (1) gives `f(Z)==D_Z a^{-1}f(r,t)`. Using either defining atom, whose defect is nonzero modulo `p`, yields `f(r,t)==a`. Congruence modulo two follows from the odd coefficients and (1).

This establishes (4) without yet assuming equality of the actual integer values or the ordinary equality `f(r,t)=a`.

## 4. Propagate exactness through every adjacent atom

Suppose exactness is already known on two consecutive atoms `P,Q`. Let `E` be the next atom in the actual contiguous segment, so (2) holds.

Put `m=floor(k/2)`. Since both outer atoms fit the occurrence rectangle,

\[
mQ\le \tfrac{k}{2}Q=\tfrac12(P+E)\le(r,t)
\]

coordinatewise. The sequence consisting of `m` copies of `Q` is therefore an actual zero-sum divisor of `R`. Factor its zero-sum complement if the complement is nonempty. The exact budget for the resulting atomization gives

\[
mD_Q\le a.
\tag{5}
\]

This also holds when the complement is empty.

By linearity and the known defects,

\[
f(E)=kD_Q-D_P.
\]

Since `k>=2`, `1<=D_P,D_Q<=a-1`, and `k<=2m+1`,

\[
3-a\le f(E)\le2a+(a-1)-1=3a-2.
\tag{6}
\]

But `D_E` belongs to `[1,a-1]`, and `p>=2a+1`. Its translates by `±2p` lie strictly outside (6):

\[
D_E+2p\ge4a+3>3a-2,
\]

\[
D_E-2p\le-3a-3<3-a.
\]

Together with the congruence (4), this forces

\[
f(E)=D_E.
\]

The same argument propagates to the other side of the initial adjacent pair, because the recurrence is symmetric in its two outer atoms. Therefore exactness holds for every actual atomic divisor of `R`.

## 5. Global conclusion and canonical light coefficients

Atomizing `R` now gives the ordinary identity

\[
\boxed{ur+vt=a.}
\tag{7}
\]

Because `u,v` are odd, neither is zero. They cannot both be positive, since then `ur+vt>=r+t=p+a-1>a`; they cannot both be negative because (7) is positive. Thus their signs are opposite. After interchanging the values, write

\[
\boxed{f(A,B)=uA-vB,\qquad u,v\text{ positive odd integers},
\qquad ur-vt=a.}
\tag{8}
\]

For every nonempty proper projected-zero occurrence part `Y=x^A y^B|R`, atomize `Y` and its complement. The zero-carry theorem shows that the proper part's defect is the sum of the defects of its factors. Hence

\[
\boxed{D(Y)=uA-vB.}
\tag{9}
\]

Since `D(Y)=2q(Y)-(A+B)`, its canonical light coefficient also becomes an ordinary integer linear functional:

\[
\boxed{q(Y)=\frac{u+1}{2}A-\frac{v-1}{2}B.}
\tag{10}
\]

In particular, all such actual lattice points satisfy the original parity-sensitive proper-part window with this exact integer potential; their coefficients are no longer merely modular representatives.

## 6. Why the carry step matters

Defining a functional on one adjacent pair does not by itself establish that all other defects equal its values. The adjacent-basis recurrence, the availability of `floor(k/2)` actual copies of the middle atom, and the modulus `2p` jointly eliminate that gap. Using only congruence modulo `p` would not justify (6)'s exclusion uniformly near the largest defects.

## 7. The formerly conjectured endpoint is now proved

The later general theorem in `CYCLIC_WEIGHTED_RECTANGLE_EXTREMAL_THEOREM_V1.md` proves the proposed extremal assertion in full: any integer functional positive on every atomic divisor has total value at least `|R|-p+1`. If its coefficients are odd, equality forces a rigid quotient, with an exact saturated endpoint classification. If there are at least two atomic-divisor types, its total is at least `|R|-p+3`.

Applied to the potential above, that strict bound would require `a>=a+2`, a contradiction. Thus this longer lattice route also closes every nonrigid type-two submaximal quotient; the established rigid/saturated theorem closes the alternative.

The direct `CYCLIC_RECTANGULAR_CHARGE_RIGIDITY_V1.md` argument reaches the complete conclusion more efficiently from the same count saturation and parity principle, without first constructing the affine functional. This note remains preserved because the recurrence and bounded-carry mechanism are independently reusable, and because it records the exact step that was initially conjectural and then resolved.

The full first corridor, the top overlap `c=H`, and the generalized Davenport numerical formula remain outside this theorem.

The proof-audit researcher independently checked the Cramer numerators, parity, consecutive-atom recurrence, actual middle-atom capacity, and exclusion of every nonzero carry. The coordinating researcher reviewed the saved route.
