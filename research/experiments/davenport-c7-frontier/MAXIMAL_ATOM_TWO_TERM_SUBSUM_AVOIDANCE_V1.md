# Maximal-atom two-term subsum avoidance from the van-Emde-Boas invariant — V1

Status: **proved analytic p-group lemma with donor input and independent finite quotient checks**. No corridor elimination or novelty claim is made here.

## 1. Donor input

Let `G` be a nontrivial finite abelian `p`-group. Write `d(G)=D(G)-1` for the small Davenport constant and `Sigma(T)` for the set of nonempty subsequence sums of a zero-sumfree sequence `T`.

Geroldinger--Yang, *On a classical zero-sum invariant* (arXiv:2608.19090, 2026), Theorem 3.5 proves the refined p-group identity

`nu(G)=nu_p(G)=d(G)-1`.

Thus every zero-sumfree sequence `T` with

`|T|>=d(G)-1`

has all its missing nonzero subsequence sums contained in one nonzero affine coset

`alpha+H`,

where `H<G` has index `p` and `alpha notin H`.

The same paper's Lemma 2.4 records the especially relevant two-deletion structure for maximal atoms. The p-group value of `nu` itself was already known in earlier group-algebra literature; donor ownership and priority remain `CANNOT_CHECK` here.

## 2. Two-term avoidance theorem

Let

- `U` be a maximal atom over `G`, so `|U|=D(G)=d(G)+1`;
- `V` be another atom; and
- assume `UV` cannot be factored into three nonempty zero-sum sequences, equivalently `z(UV)=2`.

Choose any two term occurrences `u_1 u_2 | U`.

> **Theorem.** There is no proper subsequence `W|V` satisfying
>
> `3<=|W|<=|V|-1`
>
> and
>
> `sigma(W)=u_1+u_2`.

Equivalently, with occurrence-respecting fixed-cardinality subsum sets,

`Sigma_2(U) cap Sigma_{3..|V|-1}(V) = emptyset`.

### Proof

Put

`S=U (u_1 u_2)^(-1)`.

Since `U` is an atom, `S` is zero-sumfree, and

`|S|=D(G)-2=d(G)-1=nu(G)`.

Hence there are a proper subgroup `H<G` and `alpha notin H` such that

`G^bullet \ Sigma(S) subset alpha+H`.

Assume for contradiction that `W|V` is proper, has `|W|>=3`, and

`sigma(W)=u_1+u_2`.

We first show that for **every** nonempty proper subsequence `X|W`,

`-sigma(X) notin Sigma(S)`.

Indeed, suppose instead that `T|S` is nonempty with

`sigma(T)=-sigma(X)`.

Then the following three disjoint sequences are all nonempty and zero-sum:

1. `T X`;
2. `(S T^(-1))(W X^(-1))`;
3. `u_1 u_2 (V W^(-1))`.

The first is zero-sum by construction. For the second, use

`sigma(S)=-(u_1+u_2)=-sigma(W)`;

for the third, use `sigma(V)=0` and `sigma(W)=u_1+u_2`. Nonemptiness of the second follows because `X` is proper in `W`, and the third is nonempty because `W` is proper in `V` (in fact it already contains `u_1,u_2`). Thus `UV` would have a three-factorization, contradiction.

Therefore every `-sigma(X)`, for `emptyset != X proper W`, is a missing nonzero subsum of `S` and hence lies in the same affine coset `alpha+H`.

Because `|W|>=3`, choose two term occurrences `x,y|W` such that `xy` is still a proper subsequence of `W`. Since `V` is an atom, the sums of `x`, `y`, and `xy` are all nonzero. Applying the preceding conclusion to `X=x`, `X=y`, and `X=xy` gives

`-x, -y, -(x+y) in alpha+H`.

Subtracting the first from the third yields

`-y in H`.

But also `-y in alpha+H`, so `H` meets `alpha+H`; hence `alpha in H`, contradicting the choice of a nonzero coset.

This proves the theorem.

## 3. Complement form

Let `m=|V|`. If `Y|V` is nonempty with `|Y|<=m-3`, then

`W=V Y^(-1)`

is proper and has `|W|>=3`, with

`sigma(W)=-sigma(Y)`.

The theorem therefore gives

`Sigma_2(U) cap (-Sigma_{1..m-3}(V)) = emptyset`.

Combining this with the previously proved one-term proper-subsum avoidance gives the useful depth statement

`(Sigma_1(U) union Sigma_2(U)) cap (-Sigma_{1..m-3}(V)) = emptyset`.

Now fix any occurrence `u|U`. The sequence `Uu^(-1)` is zero-sumfree of maximal length `d(G)`, so its nonempty subsums cover every nonzero element of `G`. Hence every element of

`-Sigma_{1..m-3}(V)`

has a representation by terms of `U`, but the displayed exclusion says **every such representation has length at least three**.

This is an additive-basis depth constraint rather than a support-only constraint.

## 4. The two `C_7^3` maximal-atom corridors

For `C_7^3`, a maximal atom has length 19.

### `(8,10,19)`

With `|V|=10`, non-refactorability of the `19+10` product implies

`Sigma_2(U) cap Sigma_{3..9}(V) = emptyset`

and

`(Sigma_1(U) union Sigma_2(U)) cap (-Sigma_{1..7}(V)) = emptyset`.

Thus every nonzero negative V-subsum using at most seven terms has U-representation depth at least three.

### `(9,9,19)`

With `|V|=9`, one obtains

`Sigma_2(U) cap Sigma_{3..8}(V) = emptyset`

and

`(Sigma_1(U) union Sigma_2(U)) cap (-Sigma_{1..6}(V)) = emptyset`.

In particular, in either corridor,

`-supp(V) cap Sigma_2(U) = emptyset`.

This is strictly stronger than projective separation of `supp(U)` and the earlier one-term proper-subsum avoidance.

## 5. General mechanism and next extension

The proof isolates a reusable pattern. If deleting `t` specified terms from a maximal atom leaves a zero-sumfree sequence whose missing sums are forced into a sufficiently rigid family of affine cosets, then a V-subsum matching those `t` deleted terms is incompatible with non-refactorability.

For p-groups, the global van-Emde-Boas threshold lands **exactly** at two deletions, which is why the theorem above is uniform. Geroldinger--Yang also introduce local variants of `nu`; no three-deletion theorem for arbitrary `C_p^3` is imported here without a verified local hypothesis.

The next high-value route is therefore either:

1. obtain a local-`nu` bound for maximal zero-sumfree sequences in `C_p^3` that survives three deletions; or
2. combine the new U-representation-depth >=3 condition with additive-basis diameter / restricted-sum lower bounds to force a three-factorization directly.

## Computational receipt

`check_maximal_atom_two_term_avoidance_v1.py` checks the quotient-coset obstruction symbolically for all primes through 401 and freezes the exact `p=7` corridor ranges.

`verify_maximal_atom_two_term_avoidance_independent_v1.py` independently reconstructs all projective index-p hyperplanes and every nonzero affine coset in `F_p^3` for `p=3,5,7`, then exhaustively verifies that no two elements of one nonzero coset can have their sum in the same coset. This is the finite quotient obstruction used in the proof.

## Boundary

- Neither length-19 corridor is eliminated by this file alone.
- No three-deletion analogue is claimed.
- Geroldinger--Yang and the earlier p-group `nu` theorem are donor-owned.
- Priority/novelty remains `CANNOT_CHECK`.
