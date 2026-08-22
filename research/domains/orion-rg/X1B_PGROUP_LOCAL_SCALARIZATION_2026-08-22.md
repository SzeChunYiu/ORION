# X1-B theorem — p-group missing-sum geometry locally scalarizes every legal block replacement

Parent: reopened #900. Committed before downstream use.

## Setup

Assume, for contradiction, that `S` is zero-sum-free over

`C_15^3 ≅ C_3^3 ⊕ C_5^3`

with `|S|=43`.

Choose any 12 pairwise-disjoint nonempty zero-sum blocks

`B_1,...,B_12`

in the `C_3^3` projection. Let their lifted sums in the kernel `K=C_5^3` be

`h_1,...,h_12`.

As already established in the X1-B setup, the induced kernel sequence

`H=h_1...h_12`

is zero-sum-free. Since `D(C_5^3)=13`, it has maximal zero-sum-free length 12.

Fix an index i and set

`T_i = H h_i^{-1}`,

so `|T_i|=11=d(C_5^3)-1`.

## Donor input: sharp p-group nu_5 theorem

Geroldinger--Yang, Theorem 3.5 (2026): for a finite abelian p-group G,

`nu(G)=nu_p(G)=d(G)-1`.

Specialized to `G=C_5^3`, every zero-sum-free sequence T of length 11 satisfies

`G^bullet \ Sigma(T) ⊆ alpha + L`

for some subgroup `L<G` of index 5 and some `alpha notin L`.

Equivalently, because `G/L ≅ C_5`, there is a nonzero homomorphism

`lambda_i : C_5^3 -> F_5`

and a nonzero scalar `rho_i in F_5^*` such that

`lambda_i(x)=rho_i`

for every nonzero value x missing from `Sigma(T_i)`.

Rescale lambda_i so that `rho_i=1`.

## Legal replacement correction

Call `C` a legal replacement of block `B_i` relative to the fixed other eleven blocks when:

1. C is a nonempty quotient-zero-sum block made from original indices not used by the other eleven fixed blocks;
2. replacing `B_i` by C leaves twelve pairwise-disjoint quotient-zero-sum blocks;
3. let `c in C_5^3` be the lifted sum of C.

If `-c` were a subsequence sum of `T_i`, then some subcollection of the other eleven lifted block sums would total `-c`; adding C would give a nonempty zero-sum subsequence of the original S. This contradicts the hypothetical zero-sum-free S.

Hence

`-c in C_5^3^bullet \ Sigma(T_i)`.

(The case c=0 is even more immediate: C itself is a zero-sum upstairs.)

Therefore the p-group theorem gives

`lambda_i(-c)=1`.

Likewise, since H itself is zero-sum-free,

`-h_i notin Sigma(T_i)`, so `lambda_i(-h_i)=1`.

Thus every legal replacement correction c satisfies

`lambda_i(c)=lambda_i(h_i)=-1`

after the above normalization.

## Local Scalarization Lemma

> **Fix eleven blocks of any maximal 12-block quotient packing arising from a hypothetical C15 counterexample. Then there exists a nonzero linear functional `lambda_i:C_5^3 -> F_5` such that the lifted sum of every legal twelfth replacement block has one common nonzero scalar image under `lambda_i`.**

Equivalently, the entire attainable replacement-correction set for block i is contained in one affine hyperplane of `C_5^3`, and applying `lambda_i` turns the vector-valued lift problem into a scalar equal-block-value constraint on that local replacement family.

## Relation to the 2007 cyclic donor proof

In the Bhowmik--Schlage-Puchta cyclic-kernel proof, a maximal zero-sum-free sequence of length n-1 in `C_n` is rigid: all induced block sums are equal to one generator. Consequently every alternative residual quotient-zero-sum block has the same scalar induced value.

The lemma above supplies a strict vector-kernel analogue:

- the C5^3 block sums need not be globally equal;
- but after fixing eleven blocks, **all admissible replacements of the twelfth become equal after a donor-generated linear functional**.

This is the exact structural bridge needed to test whether the donor residual impossibility arguments can be reused one block at a time.

## Next theorem question

For each donor residual size `3k+1` with `k=3,4,5`, determine whether one can select a distinguished block i such that **every quotient zero-sum subset used by the scalar donor contradiction is a legal replacement of that same block**.

If yes, composing the local scalarization lemma with the donor scalar contradiction over `F_5` may close the corresponding residual without classifying maximal zero-sum-free sequences in `C_5^3`.

If no, the first incompatible residual identifies exactly how many distinct hyperplane functionals must be coupled and becomes the next state coordinate.

## Claim boundary

- The p-group missing-sum theorem is donor mathematics.
- The local scalarization lemma is a derived application to the C15 block-lift interface.
- It does not yet prove `D(C_15^3)=43` or novelty authority.
- Any reuse of the 2007 scalar proof must be audited against the reconstructed/provenance-corrected source before promotion.
