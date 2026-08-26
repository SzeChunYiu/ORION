# Current Prior-Art Boundary for the C5^3 Generalized Davenport Paper — R10

Date: 2026-08-26

Status: living search/audit note, not a novelty certificate.

## 1. Exact object

The manuscript uses the k-th Davenport constant

`D_k(G)=min{ell : every sequence over G of length >=ell contains k pairwise disjoint nonempty zero-sum subsequences}`.

For `G=C_5^3`, the registered ORION targets are exact early values `D_2`, `D_3`, the short-zero-sum spectrum used in the proof, and the one-unit eventual corridor. `D_4` remains a separate unresolved bit.

## 2. Closest current inverse-D_k source

Qinghai Zhong, *On the Inverse Problem of the k-th Davenport Constants for Groups of Rank 2*, Combinatorica 45 (2025), Article 31, DOI 10.1007/s00493-025-00153-3.

This paper:

- uses the same disjoint-zero-sum convention for `D_k`;
- gives the exact rank-two formula `D_k(C_{n_1}⊕C_{n_2})=n_1+k n_2-1`;
- studies the extremal zero-sum sequences at the rank-two threshold that do not factor into `k+1` zero-sum factors;
- reiterates that generalized `D_k` computation/bounding becomes substantially more difficult for elementary p-groups of rank at least three;
- connects `D_k` for abelian groups with generalized Noether numbers.

It is the mandatory nearest inverse-theory comparison for any R10 completion/factorization theorem. The ORION paper must not suggest that inverse generalized-Davenport theory itself is new.

## 3. Stabilization and established general theory

Freeze and Schmid proved eventual affine behavior of generalized Davenport constants: for every finite abelian group,

`D_k(G)=D_0(G)+k exp(G)`

for sufficiently large k (indexing/convention must be checked in the cited source).

Modern surveys/monographs also record exact all-k formulas for rank at most two and selected additional classes. These are donor-owned. The ORION one-unit corridor must therefore be positioned as a sharp rank-three specialization, not as the discovery of eventual linearity.

## 4. Generalized Noether-number bridge

Cziszter and Domokos established the generalized Noether-number framework and, for finite abelian groups in non-modular characteristic, the identity

`beta_k(A)=D_k(A)`.

Therefore any exact `C_5^3` numerical consequence in invariant theory is a corollary of a new zero-sum value, not a new proof of the abelian invariant-theory bridge.

## 5. Rank-three zero-sum context

The ordinary Davenport constant for the p-group `C_5^3` is classical:

`D(C_5^3)=13`.

The short-zero-sum / Property-C literature for `C_5^3` also supplies donor results used by the structural D4 programme, including the exponent-five short-zero-sum threshold and Property C. Those facts and their inverse classifications must remain cited as donor inputs.

The paper's rank-three contribution must therefore be expressed in terms of the new multi-wise packing constants/structure, not the ordinary Davenport constant or Property C.

## 6. Search for the exact early values

Broad current searches on 2026-08-26 included literal and variant forms of:

- `"D_2(C_5^3)"`;
- `"D_3(C_5^3)"`;
- `"C_5^3" "D_2" Davenport`;
- `"C_5^3" "D_3" Davenport`;
- `"C_5^3" "k-th Davenport"`;
- `"C_5^3" generalized Noether 20`;
- `"C_5^3" generalized Noether 25`;
- rank-three / elementary-p-group generalized-Davenport searches.

No accessible source located in these searches stated the numerical identities

`D_2(C_5^3)=20`

or

`D_3(C_5^3)=25`.

This is **not** a novelty certificate. Search-engine indexing is incomplete; notation varies; values may appear in theses, tables, non-indexed papers, or under a shifted `d_k` convention.

## 7. Submission-grade novelty audit still required

Before headline novelty language, the specialist audit should search at least:

1. MathSciNet / zbMATH under generalized/k-th/multi-wise Davenport constants;
2. citations to Freeze–Schmid and generalized Noether-number papers;
3. rank-three elementary-p-group papers and theses;
4. computational zero-sum tables/databases;
5. `d_k(G)=D_k(G)-1` notation variants;
6. invariant-theory `beta_2`, `beta_3` tables for elementary abelian groups;
7. factorization-theory literature using maximum factorization length rather than `D_k` notation.

If an exact prior value is found, the paper must pivot to whichever of the following survives:

- first independently replayable proof;
- stronger short-zero-sum spectrum;
- inverse/orbit classification;
- new one-unit corridor/propagation;
- matching-critical completion/factorization structure;
- source-level D4 progress.

## 8. Current safe novelty sentence

Until the specialist audit closes, the safe language is:

> The registered computations and analytic reductions produce candidate exact early generalized-Davenport values and inverse structure for the rank-three group `C_5^3`; broad current searches did not locate the same numerical identities, but formal novelty authority remains subject to specialist database review and independent replay.
