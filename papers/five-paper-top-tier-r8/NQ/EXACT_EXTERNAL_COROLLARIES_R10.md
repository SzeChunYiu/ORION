# Exact External Corollaries of the C5^3 Generalized Davenport Programme — R10

Date: 2026-08-26

Status: translation/corollary note. The numerical statements below are **conditional on the independent replay authority required by issue #1383**. Generic links between generalized Davenport constants, generalized Noether numbers, factorization theory, and coding theory are donor-owned.

## 1. Convention

For a finite abelian group `G`, let `D_k(G)` denote the smallest integer `ell` such that every sequence over `G` of length at least `ell` contains `k` pairwise disjoint nonempty zero-sum subsequences.

This is the convention used in the current ORION NQ manuscript and in Qinghai Zhong, *On the Inverse Problem of the k-th Davenport Constants for Groups of Rank 2*, Combinatorica 45 (2025), Article 31.

The ORION finite claims currently awaiting full independent replay are

`D_2(C_5^3)=20`,

`D_3(C_5^3)=25`,

and the tail corridor

`5k+10 <= D_k(C_5^3) <= 5k+11` for `k>=4`.

No corollary in this note may be promoted beyond the authority of those antecedent claims.

## 2. Exact generalized Noether numbers

Cziszter and Domokos introduced generalized Noether numbers `beta_k(G)` for finite groups in non-modular invariant theory. For finite abelian `A`, the established identity is

`beta_k(A)=D_k(A)`.

The field assumption is non-modular: the characteristic does not divide `|A|`. For `A=C_5^3`, this means characteristic different from five (including characteristic zero).

### Corollary NQ-R10.5 — exact early generalized Noether numbers

Conditional only on independent replay of the corresponding ORION Davenport constants, for every field of characteristic different from five,

`beta_2(C_5^3)=20`,

`beta_3(C_5^3)=25`.

The values are not a new invariant-theory proof of the abelian identity; they are exact new numerical consequences if the Davenport values are new.

### Corollary NQ-R10.6 — one-unit Noether corridor

For every `k>=4` for which the current Davenport corridor is licensed,

`5k+10 <= beta_k(C_5^3) <= 5k+11`

in non-modular characteristic.

If a future source-level proof establishes `D_4(C_5^3)=30` and activates the registered propagation theorem, the same propagation gives the corresponding exact eventual generalized-Noether formula.

## 3. What beta_k means algebraically

Let `V` range over finite-dimensional `C_5^3`-modules over a non-modular field and let

`R=F[V]^{C_5^3}`

be the invariant ring with positive-degree ideal `R_+`. The generalized Noether number controls the highest degree that can remain nontrivial modulo the appropriate power of `R_+` in the standard definition of `beta_k`.

Thus the exact values above are degree thresholds in invariant theory, not merely a relabeling of sequence lengths. The manuscript should state the definition used by the cited invariant-theory source and avoid introducing a competing indexing convention.

A submission-ready version must quote/check the exact quotient/power convention directly from the chosen primary source rather than paraphrasing it from secondary literature.

## 4. Exact restricted-kernel packing threshold

The main R10 branch already contains the exact matrix translation in `BINARY_KERNEL_PACKING_TRANSLATION_R10.md`.

For

`H=[h_1 ... h_m] in F_5^{3 x m}`,

a nonempty zero-sum subsequence of the column sequence is exactly a nonzero vector

`z in ker(H) intersect {0,1}^m`.

Disjoint zero-sum subsequences correspond exactly to such vectors with pairwise disjoint supports.

Let `nu_01(H)` be the maximum number of pairwise support-disjoint nonzero vectors in `ker(H) intersect {0,1}^m`.

### Theorem NQ-R10.7 — universal binary-kernel packing form

`D_k(C_5^3)` is the least `m` such that every `3 x m` matrix over `F_5` satisfies

`nu_01(H)>=k`.

This theorem is an exact reformulation and needs no computer-assisted premise.

### Conditional numerical consequences

Once #1383 grants replay authority:

- every `3 x 20` matrix over `F_5` has two support-disjoint nonzero `{0,1}` kernel vectors, while some `3 x 19` matrix does not;
- every `3 x 25` matrix has three such pairwise support-disjoint vectors, while some `3 x 24` matrix does not;
- for `k>=4`, the universal threshold lies in the one-column window `5k+10` or `5k+11`.

This is not the ordinary minimum-distance problem of a linear code. Coefficients are restricted to `{0,1}` inside `F_5`, and several codewords must have disjoint supports. Field rescaling can leave the binary cube and therefore does not preserve the property automatically.

## 5. Hypergraph formulation

For a fixed matrix `H`, define the **binary zero-kernel hypergraph** `Z_01(H)`:

- vertices are the column indices `[m]`;
- a nonempty set `I` is a hyperedge when its incidence vector `1_I` lies in `ker(H)`.

Then

`nu_01(H)`

is exactly the matching number of `Z_01(H)`.

### Corollary NQ-R10.8

The generalized Davenport problem for `C_5^3` is equivalently a universal hypergraph-matching threshold problem for the restricted-kernel hypergraphs arising from `3 x m` matrices over `F_5`.

This does not import arbitrary-hypergraph matching hardness: the hypergraphs have strong algebraic structure. Its value is that matching/cover certificates provide a third independent vocabulary for proof auditing.

## 6. Three structurally distinct replay languages

The final computer-assisted paper should deliberately expose three representations of the same finite theorem.

### A. Zero-sum sequence language

Canonical sequence/orbit generation plus disjoint zero-sum factorization.

### B. Restricted-kernel language

Boolean selectors with modular equations

`H z = 0 mod 5`

and pairwise-disjoint-support constraints, encoded in SAT/CP-SAT/MILP.

### C. Hypergraph language

Generate/check zero-kernel hyperedges and solve exact matching/packing, with independent canonicalization or labelled input.

A publication-strength replay is obtained when at least two genuinely different languages agree on complete partition manifests and a third language independently checks selected positive/negative certificates. Merely using two SAT solvers on identical clauses is not structural independence.

## 7. Factorization-theory significance

Generalized Davenport constants were introduced by Halter-Koch in connection with arithmetical counting functions defined by factorization properties, and modern work continues to cite this motivation. The ORION paper should include this as established significance and not manufacture a new factorization theorem unless the exact convention-to-arithmetic translation is checked from the primary source.

The safe current statement is:

> exact values of `D_k(C_5^3)` determine an established zero-sum invariant that already enters invariant theory and factorization theory; the ORION contribution is the new rank-three value/structure, not the existence of those connections.

## 8. Top-tier mathematical positioning

After a successful independent replay, the strongest NQ manuscript should present one coherent theorem package:

1. exact `D_2(C_5^3)` and `D_3(C_5^3)`;
2. the complete short-zero-sum threshold spectrum used in their proof;
3. the independently reproduced rank-three structural/orbit census;
4. the one-unit all-k tail corridor and conditional propagation mechanism;
5. exact generalized-Noether corollaries;
6. exact restricted-kernel/hypergraph reformulations; and
7. a proof architecture with independently checkable manifests and negative controls.

The paper should **not** wait for `D_4` if items 1--7 survive replay and a specialist novelty audit. `D_4` is a separate potential strengthening, not permission to publish the early constants.

## 9. Remaining gates

- full CR-A/CR-B LUNARC replay of `D_2`, `D_3`, the 98,622 normalized objects and 230,983 extension census;
- independent primary-source search for any previously published exact `D_2(C_5^3)` or `D_3(C_5^3)` value;
- specialist review of normalization/orbit completeness;
- direct check of the generalized-Noether definition/convention in the cited primary invariant-theory paper;
- separate source-level authority for any future `D_4` claim.
