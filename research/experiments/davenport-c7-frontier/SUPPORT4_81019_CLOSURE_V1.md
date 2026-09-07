# Exact closure of the support-four maximal-atom branch in `(8,10,19)` — V1

Status: **complete bounded elimination with two structurally independent exhaustive verifiers**. This closes only the branch in which the 19-atom has support exactly four. The support-five-and-higher part of `(8,10,19)` remains open.

## 1. Canonical maximal atom

By `SUPPORT4_MAXIMAL_ATOM_WEIGHTS_V1.md`, a support-four maximal atom over `C_7^3` is, up to automorphism and reordering,

`U_a=e1^6 e2^6 e3^a (e3-a^{-1}(e1+e2))^(7-a)`

with

`a in {1,2,3}`.

Thus there are only three maximal-atom types to check.

Let `V` be the 10-atom and `W` the 8-atom in a hypothetical `(8,10,19)` first obstruction.

The known hereditary reductions give:

- `UV` is total-zero of length 29 and is 9-short-zero-free;
- the whole sequence `B=UVW` is total-zero of length 37 and is 7-short-zero-free;
- `W` has length eight and `V` has length ten.

A length-10 zero-sum sequence inside a 9-short-free pair is automatically an atom, and a length-8 zero-sum sequence inside a 7-short-free whole sequence is automatically an atom. Therefore the finite cover does not need a separate atom-minimality filter for `V` or `W`.

## 2. Stage-one exhaustive cover: the 10-atom

For each canonical `U_a`, the primary verifier enumerates every unordered length-10 zero-sum sequence `V` such that `U_aV` contains no nonempty zero-sum subsequence of length at most nine.

The exact counts are:

| `a` | 9-short-free length-10 companions `V` |
|---:|---:|
| 1 | 538 |
| 2 | 24 |
| 3 | 0 |

The `a=3` support-four maximal atom is therefore eliminated already at the two-atom stage.

Since every zero-sum block in a 9-short-free sequence has length at least ten, a length-29 pair product cannot have three disjoint zero-sum blocks. Thus every enumerated pair automatically has `z(U_aV)=2`, as required by hereditary first-failure rigidity.

## 3. Stage-two exhaustive cover: the 8-atom

For each surviving pair `P=U_aV`, the verifier enumerates every unordered length-8 zero-sum sequence `W` such that `PW` is 7-short-zero-free.

The exact counts are:

| `a` | pair candidates admitting at least one `W` | total `(V,W)` completions |
|---:|---:|---:|
| 1 | 229 | 2772 |
| 2 | 6 | 24 |
| 3 | 0 | 0 |

Hence the complete support-four `(8,10,19)` factorization cover contains

`boxed{2796}`

factor triples.

Several triples produce the same underlying length-37 sequence. There are exactly

`boxed{1572}`

distinct multiplicity vectors `B` in the cover.

## 4. Exact four-pack test

Every candidate `B` is 7-short-zero-free. Consequently every nonempty zero-sum block has length at least eight.

In any four-block zero-sum partition of length 37:

- all four block lengths lie in `8..13`;
- at least two block lengths lie in `{8,9}`.

The primary verifier enumerates all zero-sum submultiplicity vectors of lengths `8..13`, chooses two compatible length-8/9 blocks, and searches the remainder for a third zero-sum block leaving at least eight terms. The fourth residual block is automatically zero-sum.

> **Primary receipt:** all 2796 factor triples admit a four-pack.

Therefore none can have packing number three.

## 5. Independent verifier

`verify_support4_81019_independent_v1.cpp` uses a different cover and partition formulation.

### Companion enumeration

Instead of maintaining subset-sum sets by cardinality, it computes, for every group element, the minimum number of terms from the fixed base sequence needed to realize that sum. When a new companion occurrence is appended, it explicitly scans every occurrence subset containing that new term and rejects it exactly when the complementary base depth would create a forbidden short zero-sum.

This occurrence-mask/minimum-depth recursion independently reproduces:

- pair counts `538,24,0`;
- extendable-pair counts `229,6,0`;
- completion counts `2772,24,0`;
- 1572 distinct full sequences.

### Four-pack predicate

The independent four-pack test enumerates all zero-sum count vectors of lengths `8..13`, forms every capacity-compatible unordered pair, and stores its union. A four-pack exists exactly when the complement of one such pair-union is another pair-union.

> **Independent receipt:** all 2796 factor triples four-pack.

Thus the candidate universe and the decisive partition predicate are both replayed with different internal structures.

## 6. Closed branch

Combining the support-four maximal-atom classification with the two exact verifiers gives:

> **Theorem.** No length-37 zero-sum sequence over `C_7^3` with packing number at most three and atom-length corridor `(8,10,19)` can have its 19-atom supported on exactly four group elements.

Equivalently, any surviving `(8,10,19)` obstruction must satisfy

`boxed{|supp(U_19)|>=5.}`

This is an actual corridor reduction, not merely a support-profile count.

## 7. Retained failed receipt

An earlier Python prototype reported only 55 `(V,W)` completions and incorrectly claimed that the `a=2` type had no extension. The prototype restored its incremental subset-sum state incorrectly across recursive branches.

That undercount is explicitly rejected. The corrected primary C++ enumeration gives 2796 completions, and the structurally independent occurrence-mask verifier reproduces the same number. The erroneous `55` count is retained as an engineering failure and must not be propagated.

## 8. Strategic consequence

The maximal-atom corridor now splits sharply:

1. support four is completely closed in `(8,10,19)`;
2. every surviving 19-atom has support at least five;
3. it remains projectively separated, and its 29-term pair with the 10-atom obeys the plane cap 16, line-fiber avoidance, and the Geroldinger--Yang one/two-term representation-depth exclusions.

The same support-four canonical family should be attacked next in `(9,9,19)`, where the pair is only 8-short-free and a separate three-factorization filter is required.

## Boundary

- The theorem does not eliminate support `>=5` maximal atoms.
- It does not eliminate the `(9,9,19)` corridor.
- It does not determine `D_3(C_7^3)`.
- The finite counts authorize only the declared support-four `(8,10,19)` branch.
