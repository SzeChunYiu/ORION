# Cross-context reframe for the rank-three multiwise Davenport programme — V1

Status: **LLM-assisted research reframe with one new elementary structural lemma**. Donor ownership is retained; novelty/priority remains **CANNOT_CHECK**.

This note records the scene changes that currently look most likely to unlock the `C_p^3` multiwise problem. It does not claim that any imported language is itself new.

## 1. The same object in several mathematical scenes

### Block monoid / factorization theory

A zero-sum sequence is an element of the block monoid `B(G)`. Its atoms are minimal zero-sum sequences. The zero-sum packing number is the maximum factorization length. Thus a hypothetical `D_3` obstruction is not merely a sequence avoiding three disjoint zero sums: after zero-sum completion it is a block-monoid element whose factorization lengths stop at three.

This makes sets of lengths, products of atoms, catenary-style rigidity, and inverse factorization results natural donor languages.

### Polynomial invariant theory

For finite abelian groups the generalized Noether number satisfies donor equality

`beta_k(G) = D_k(G)`.

So a rank-three multiwise Davenport theorem is simultaneously a sharp degree statement for generalized polynomial invariants. Inductive inequalities for generalized Noether numbers and subquotients may therefore encode upper-bound mechanisms that are hard to see in zero-sum language alone.

### Affine semigroup / Hilbert-basis language

Fix support vectors as columns of a matrix `Q`. A zero-sum submultiset is a bounded nonnegative integer vector `x` satisfying

`Q x = 0 (mod p)`.

The block monoid is an affine semigroup; its atoms are the indecomposable nonnegative kernel vectors (the Hilbert-basis objects in the standard invariant-theory formulation). A four-pack asks whether the multiplicity vector decomposes into four nonzero bounded kernel vectors.

This suggests Graver-basis, toric-ideal, integer-decomposition, and augmentation methods as possible proof/search tools. At present this is a route proposal, not a theorem imported into the argument.

### Hypergraph matching

Take one vertex for every term occurrence and one hyperedge for every nonempty zero-sum subsequence. Then the packing number is the matching number of this highly algebraic hypergraph. Unlike a generic hypergraph, unions and complements of zero-sum blocks remain zero-sum whenever the ambient sequence is total-zero. This extra closure is exactly what made the support-seven exact search much smaller than a generic matching computation.

### Finite geometry / coding theory

Projectivizing support turns occupancy restrictions into weighted point-set restrictions in `PG(2,p)`. For `p=7`, support seven reduced to 54 projective `(7,3)`-arc types. The corresponding support matrix also defines a projective linear code, while its kernel controls total-zero scalar lifts. This remains the cleanest exact geometry lane.

### Additive-basis / restricted-sumset theory

This is the most promising new reframe for the length-19 corridor. A maximal zero-sum-free sequence has length `D(G)-1`, and its nonempty subsums cover every nonzero element of `G`. The proof is elementary: if `S` is zero-sum-free with `|S|=D(G)-1` and `g != 0`, then `S(-g)` has length `D(G)` and hence a zero-sum; that zero-sum must use `-g`, so a subsequence of `S` sums to `g`.

The unresolved issue is therefore not coverage but **disjoint / short / multiple representations**. That places the problem near additive-basis diameter, restricted sumsets and matching among representing subsets.

## 2. Maximal-atom / short-atom subsum-avoidance lemma

Let `G` be any finite abelian group. Let `U` be an atom with

`|U| = D(G)`,

and let `V` be another atom. Suppose `UV` cannot be factored into three nonempty zero-sum sequences.

Then for every term occurrence `u|U` there is **no** proper subsequence `W|V` satisfying

- `2 <= |W| <= |V|-1`, and
- `sigma(W)=u`.

Equivalently, writing `Sigma_{2..|V|-1}(V)` for sums of proper subsequences involving at least two terms,

`supp(U) cap Sigma_{2..|V|-1}(V) = emptyset`.

### Proof

Fix `u|U` and suppose such a `W` exists. Split `W=XY` with `X,Y` both nonempty. Since `V` is an atom and `X,Y` are proper nonempty subsequences,

`sigma(X) != 0` and `sigma(Y) != 0`.

Put `S=U u^{-1}`. Then `S` is zero-sum-free and has length `D(G)-1`. By the maximal zero-sum-free subsum-coverage observation above, there is a nonempty `T|S` with

`sigma(T) = -sigma(X)`.

Moreover `T != S`, because otherwise `sigma(X)=u`, forcing `sigma(Y)=0`, impossible. Since `sigma(S)=-u` and `u=sigma(X)+sigma(Y)`, the complement satisfies

`sigma(S T^{-1}) = -u + sigma(X) = -sigma(Y)`.

Hence

`TX` and `(S T^{-1})Y`

are two disjoint nonempty zero-sum sequences. The remaining sequence is

`u (V W^{-1})`,

which is nonempty because `W` is proper, and its sum is

`u + sigma(V)-sigma(W)=0`.

Thus `UV` has a three-factor zero-sum decomposition, contradiction.

## 3. Consequence for the two length-19 corridors in `C_7^3`

The corridor patterns

- `(8,10,19)`,
- `(9,9,19)`

contain a maximal atom `U` of length 19 and a short atom `V` of length 10 or 9. In a hypothetical length-37 obstruction, the product `UV` must have maximum factorization length exactly two; otherwise adjoining the third atom gives four factors.

Therefore the lemma forces

`supp(U) cap Sigma_{2..9}(V) = emptyset` for `|V|=10`,

or

`supp(U) cap Sigma_{2..8}(V) = emptyset` for `|V|=9`.

This is a much sharper residual than “classify all maximal atoms”. It asks whether a 9- or 10-term atom can have a proper-subsums avoidance set large/structured enough to contain the support of a length-19 maximal atom.

A length-19 atom has multiplicity at most six at every element, hence support size at least four. So at minimum the proper-subsums avoidance set of the short atom must contain four actual group elements arranged compatibly with a maximal atom.

## 4. Next donor / exact routes

The highest-value borrowed structures now are:

1. restricted-sumset lower bounds for zero-sum-free sequences and atoms;
2. additive-basis diameter / short representation results for maximal zero-sum-free sequences;
3. disjoint representation theorems, which translate directly into hypergraph matching;
4. generalized Noether-number induction and transfer inequalities for abelian groups;
5. Graver/Hilbert-basis augmentation bounds for bounded modular kernels;
6. inverse results for products of two atoms, but only where rank-three hypotheses are actually verified.

The main strategic change is to avoid a full classification of maximal length-19 atoms unless forced. The subsum-avoidance lemma permits attacking the **short atom** instead, where length 9 or 10 is far more tractable.