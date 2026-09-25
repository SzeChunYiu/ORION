# Cross-context frontier checkpoint — V1

Status: **research route map / non-authorizing synthesis**.

The current target is not to keep brute-forcing `C_7^3` in isolation. The aim is to use `C_7^3` as the first nontrivial test case for a broader mechanism for multiwise Davenport constants of `C_p^3`, while borrowing mature structure from neighboring subjects.

## Current proved compression

For a hypothetical zero-sum length-37 obstruction `B` with `z(B)<=3`:

- `B` is 7-short-zero-free;
- `|supp(B)|>=8` by the complete support-7 closure;
- a shortest-first three-atom factorization exists with one of six candidate length triples:
  `(8,10,19)`, `(9,9,19)`, `(9,10,18)`, `(9,11,17)`, `(9,12,16)`, `(10,10,17)`;
- a length-19 atom has projectively separated support by the Gao--Geroldinger maximal zero-sumfree theorem;
- the support-8 layer now has the projective deficit reduction in `SUPPORT8_PROJECTIVE_DEFICIT_REDUCTION_V1.md`.

## Scene 1: affine semigroups / Graver and Hilbert bases

Fix projective support vectors as columns of a matrix `Q`. A zero-sum submultiset is a bounded nonnegative integer vector `x` satisfying

`Qx = 0 (mod p)`.

The set of all such nonnegative solutions is an affine semigroup. Minimal zero-sum sequences are exactly its indecomposable elements (Hilbert-basis atoms in the fixed-support model). Four-pack existence asks whether the ambient multiplicity vector decomposes conformally into four nonzero semigroup elements.

This reframes the exact problem as an **integer-decomposition / factorization-length** question, suggesting tools from:

- Hilbert bases and Graver bases;
- toric ideals and primitive conformal relations;
- integer decomposition properties of bounded fibers;
- normality/saturation phenomena of zero-sum semigroups.

Research discriminator: determine whether the bounded fibers arising from projective `(r,t)`-arc supports satisfy a low-degree integer-decomposition property strong enough to force four factors at total degree 37.

## Scene 2: coding theory / projective geometry

Projectivized support gives a finite projective code. Zero-sum submultisets become positive kernel words after diagonal scaling. Short-zero-freeness becomes exclusion of low-weight positive kernel vectors, while packing asks for several coordinatewise-disjoint positive kernel words.

The support-7 closure succeeded precisely because projective normalization compressed arbitrary vectors to 54 finite-geometry types. The support-8 deficit lemma continues this route:

- one collision -> the same 54 seven-point `(7,3)`-arc classes plus one scalar split;
- eight directions -> `(8,4)`-arc classification in `PG(2,7)`.

Research discriminator: finish support 8 before attempting any global 343-element search.

## Scene 3: block monoids / factorization theory

The six atom-length triples form a list containing an available shortest-first factorization in the block monoid `B(C_7^3)`; they are not proved to describe every factorization. See `CORRIDOR_FACTORIZATION_QUANTIFIER_AUDIT_V1.md` for this correction. A counterexample is a block with a length-3 factorization but no length-4 factorization. Products of two atoms inside the selected three-atom factorization must avoid any refactorization into three atoms.

This is the natural home for:

- sets of lengths;
- catenary/elasticity constraints;
- products of two atoms;
- local tameness and refactorization lemmas.

The present literature search did not produce a rank-three theorem that kills the `(8,10,19)` or `(9,9,19)` corridors, so this remains a donor-search lane rather than a claimed proof.

## Scene 4: additive bases / restricted subset-sum diameter

If `U` is an atom of length 19 and `x|U`, then `S=Ux^{-1}` is zero-sumfree of maximal length 18. By the definition of `D(C_7^3)=19`, for every target `g in C_7^3`, the sequence `S(-g)` has a zero-sum; since `S` itself is zero-sumfree, this zero-sum must use `-g`. Therefore **every group element occurs as a subsequence sum of `S`**.

What is missing is a cardinality bound: how small can the representing subsequence always be chosen? This turns the length-19 corridors into a restricted additive-basis diameter problem.

Research discriminator: search for or prove a uniform radius bound for maximal zero-sumfree sequences in `C_p^3`. A sufficiently small bound (roughly 8--9 in the `p=7` case, depending on the mixing target) could force a mixed zero-sum between the maximal atom and the companion atom and hence a forbidden refactorization.

No such radius theorem is claimed here.

## Scene 5: hypergraph matching / covering

Take term occurrences as vertices and nonempty zero-sum subsequences as hyperedges. Then `D_k` is a matching threshold. The current reductions impose strong lower bounds on edge sizes and strong geometric restrictions on which edges exist.

Potential borrowed tools include matching-cover duality, fractional matching bounds, and bounded-rank matching theorems. This lane is currently heuristic because the zero-sum hypergraph is highly structured and nonuniform; any theorem must be checked against that structure before use.

## Prime-uniform objective

The existing `GENERAL_CP3_MULTIWISE_MASTER_REDUCTION_V1.md` records the candidate formula

`D_k(C_p^3) = (9p-5)/2 + (k-2)p` for `p>=5`, `k>=2`,

as the Freeze--Schmid lower-bound line to test, not as a theorem.

The immediate program is:

1. finish `p=7,k=3` structurally rather than by raw search;
2. identify which borrowed mechanism actually closes it;
3. test that mechanism at another prime (`p=11` is the clean next stress test);
4. only then formulate a general theorem/conjecture with a mechanism, rather than extrapolating from numerology.

## Claim boundary

This file records research translations and route selection. It does not claim a new general Davenport theorem, a classification of maximal atoms, an additive-basis radius theorem, or novelty over the donor literature.
