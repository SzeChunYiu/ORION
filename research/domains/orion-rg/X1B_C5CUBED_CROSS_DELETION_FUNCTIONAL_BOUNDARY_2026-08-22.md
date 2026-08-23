# X1-B donor boundary — deletion hyperplanes need not share one functional in `C_5^3`

Parent: #900. Committed before downstream use.

## Donor statement actually available

Geroldinger--Yang, Theorem 3.5 (arXiv:2608.19090), proves for a finite abelian p-group `G` that

`nu(G)=nu_p(G)=d(G)-1`.

For each zero-sum-free sequence `T` of length `d(G)-1`, their group-algebra proof constructs a homomorphism

`lambda_T : G -> F_p`

such that all nonzero elements missing from `Sigma(T)` lie in one nonzero affine fiber of `lambda_T`.

The construction is indexed by `T`. The theorem does **not** state that the homomorphisms obtained from two different deletions of one maximal zero-sum-free sequence agree, are proportional, or satisfy another cross-deletion relation.

## Exact counterexample to a universal common deletion functional

Let

`G=C_5^3 = <e1> direct-sum <e2> direct-sum <e3>`

and take the standard maximal zero-sum-free sequence

`H = e1^4 e2^4 e3^4`.

It has length `12=d(G)` and is zero-sum free.

### Delete one `e1`

Let

`T1 = e1^3 e2^4 e3^4`.

Its subsequence sums have e1-coordinate in `{0,1,2,3}` and arbitrary e2/e3 coordinates in `F_5`. Hence the nonzero missing sums are exactly

`M1 = {4 e1 + b e2 + c e3 : b,c in F_5}`.

Thus the missing set is the affine hyperplane

`x1 = 4`,

with normal functional proportional to the first coordinate.

### Delete one `e2`

Similarly, for

`T2 = e1^4 e2^3 e3^4`,

the nonzero missing set is exactly

`M2 = {a e1 + 4 e2 + c e3 : a,c in F_5}`,

namely the affine hyperplane

`x2 = 4`,

whose normal is proportional to the second coordinate.

The two normals are linearly independent. Therefore there is no single nonzero functional whose one affine fiber equals both missing sets, and in particular no theorem of the form

> all deletion-induced exceptional hyperplanes of a maximal `C_5^3` zero-sum-free sequence share one common normal.

## Consequence for the k=4 reframe

The six committed 13-point quotient obstruction orbits cannot be eliminated merely by demanding that the local scalarizations attached to their two residual blocks use the same functional. That requirement is false even for the canonical maximal kernel sequence.

A valid successor must instead exploit a weaker but genuine coupling arising from the **same underlying maximal kernel sequence**, for example:

1. compatibility of two affine fibers with a common 12-term sequence of kernel block sums;
2. exchange-cycle identities that compare the two locally scalarized correction families;
3. direct vector-valued subsequence-sum constraints beyond independent affine-fiber containment.

## Claim boundary

This is an exact counterexample to one proposed proof strategy, not a counterexample to `D(C_15^3)=43`. The Geroldinger--Yang p-group theorem remains fully admitted; only an unjustified cross-deletion strengthening is ruled out.
