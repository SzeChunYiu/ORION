# Type two: complete all-prime elimination of the second unsaturated face

Status: **proved for every prime p>=7**. The full face with high new multiplicity `p-3` is empty. This removes the small-prime inverse gate left in the preceding main-family theorem.

Let `p=2H+1>=7`, `m=3H+1`, `u=H+1`, and `s=(u,u,1)` in a basis `(e1,e2,g)`. Set

\[
U=e_1^{p-1}e_2^{p-1}g^{p-2}s^2.
\]

**Theorem.** If

\[
V=s^c g x^{H+2-c}y^{p-3},\qquad\sigma(V)=0,
\qquad2\le c\le H,
\]

then `UV` contains a nonempty zero-sum shorter than `m`.

Assume short-freeness toward contradiction. If `c=H`, the donor-capacity conclusion of `A2_SECOND_UNSATURATED_DONOR_INVERSE_ALL_PRIMES_V1.md` already contradicts the available subproduct

`e1^{p-1}e2^{p-1}g^{p-1}s^{H+2}y^{p-3}`.

For `2<=c<=H-1`, the same exact inverse theorem applies with `K=c+2>=4`. It forces `y=(A,-A,1)`, `A!=0`, apart from `(p,c)=(11,2)` and the two exceptional values below. The main family is completely eliminated, for every prime and every allowed overlap, by `A2_RANK3_SECOND_UNSATURATED_MAIN_FAMILY_ELIMINATION_V1.md`. Its auxiliary atomization, index-one alternative, exchanged occurrence vector, and final circle argument have no remaining small-prime assumption.

At the retained exception `p=11,c=2`, one has `H=5`, `r=H+2-c=5`, and `s=(6,6,1)`. For `y=(4,7,2)`, the actual companion relation gives

\[
5x=3y-2s-g=(0,9,3),\qquad x=(0,4,5).
\]

The sequence

\[
\boxed{x e_2^7 g^6}
\]

has coordinate sum `(0,11,11)` and length `14<m=16`. All counts fit the actual donor. Axis exchange gives the certificate for `y=(7,4,2)`.

These alternatives exhaust the inverse theorem, proving the complete face elimination. If an overlap violates the previously proved ceiling `c<=2 floor(H/2)`, its donor already supplies a short zero-sum; no such row is silently included in the main-family theorem's narrower standing range.

Combining the saturated face, the new `p-2` face, and this `p-3` face gives the exact surviving rank-three restriction

\[
\boxed{4\le b\le c+1,\qquad c\ge3,
\qquad V=s^c g x^{H+b-1-c}y^{p-b}.}
\]

In particular the entire rank-three light-overlap layer `c=2` is now eliminated: its only boundary deficits were `b=1,2,3`, and the earlier shared-donor argument had already removed its interior multiplicities. The old complete `c=1` elimination remains intact.

The same donor inverse also removes the full rank-two top-overlap case with smaller new multiplicity three. Together with the older saturated case and the new first-unsaturated inverse, every remaining type-two rank-two top row has `r>=4`, as well as `r>p/10` from the linear inverse band.

The proof was checked locally at the exact inverse ranges, the residual `p=11` coordinate calculation, and the assembly of all boundary deficits. The deeper faces `b>=4`, the remaining rank-two top rows, type-one high overlaps, the full first corridor, and unproved Davenport values remain outside this theorem.
