# Exact closure of the support-six maximal-pair face in `(9,9,19)` — V1

Status: **complete bounded elimination with two structurally independent exhaustive verifiers**. This closes only the branch in which the length-19 maximal atom has support four and its pair with one length-9 atom has total support exactly six. It does not close larger pair support or determine `D_3(C_7^3)`.

## 1. Exact pair universe

Let `U` be one of the three canonical support-four maximal atoms over `C_7^3`, and let `V` be a length-9 atom in the `(9,9,19)` corridor.

Hereditary first-failure rigidity requires

- `UV` is 8-short-zero-free; and
- `z(UV)=2`.

The second condition is essential here. A length-28, 8-short-zero-free zero-sum pair can still three-pack, necessarily with block lengths `(9,9,10)`.

Assume the pair support attains the all-corridor lower bound

`|supp(UV)|=6`.

By the support-six normal form, `V` introduces exactly two new actual values and has one of the following shapes:

- support three / rank two, sharing only the light unsaturated value (`s3L`);
- support three / rank two, sharing only the heavy unsaturated value (`s3H`);
- support four / rank three, sharing both unsaturated values (`s4`).

The primary depth-oracle cover and the independent direct short-zero cover both obtain exactly **26** pair candidates after the `z(UV)=2` filter:

| maximal type | `s3L` | `s3H` | `s4` | total |
|---:|---:|---:|---:|---:|
| `a=1` | 12 | 0 | 0 | 12 |
| `a=2` | 4 | 0 | 6 | 10 |
| `a=3` | 2 | 2 | 0 | 4 |
| **total** | **18** | **2** | **6** | **26** |

This is the complete exact-support-six maximal-pair universe for this corridor.

## 2. Extension by the second length-9 atom

For each of the 26 pair candidates, let `W` be the other length-9 atom. The whole length-37 sequence `B=UVW` must be 7-short-zero-free.

The primary verifier enumerates `W` with cardinality-indexed subset-sum state. The independent verifier uses minimum base depth plus occurrence-mask recursion.

Both obtain exactly

`boxed{1634}`

valid factor triples, and all 1634 underlying multiplicity vectors are distinct.

The distribution is:

| maximal type / pair shape | completions |
|---|---:|
| `a=1`, `s3L` | 876 |
| `a=2`, `s3L` | 198 |
| `a=2`, `s4` | 142 |
| `a=3`, `s3L` | 212 |
| `a=3`, `s3H` | 206 |
| **total** | **1634** |

## 3. Four-pack test

Every full candidate is 7-short-zero-free, so every nonempty zero-sum block has length at least 8. In a four-pack of length 37, all block lengths lie in `8..13`, with at least two blocks of length 8 or 9.

The primary verifier enumerates zero-sum count vectors of lengths `8..13`, chooses two compatible 8/9 blocks, and looks for a third block leaving a nonempty zero-sum residual.

The independent verifier instead forms every capacity-compatible union of two zero-sum blocks and detects a four-pack exactly when the complement of one pair-union is another pair-union.

Both return

`boxed{1634/1634}`

four-pack successes.

Therefore no candidate in the exact support-six maximal-pair face can be a length-37 packing obstruction.

## 4. Closed branch

> **Theorem (bounded C7 corridor closure).** No length-37 zero-sum sequence over `C_7^3` with packing number at most three and corridor `(9,9,19)` can simultaneously satisfy
>
> - the 19-atom has support exactly four; and
> - its pair with a 9-atom has total support exactly six.

Equivalently, for any surviving support-four maximal-atom obstruction in `(9,9,19)`, each maximal pair must have support at least seven.

This is a genuine corridor reduction, but it is not yet an elimination of support-four maximal atoms when pair support is seven or higher.

## 5. Independence of the two verifiers

`search_support6_9919_closure_v1.cpp`:

- uses the exact support-four representation-depth formula to test pair 8-short-freeness;
- uses a cardinality-indexed subset-sum recursion for the third atom;
- uses a small-two-block plus third-block four-pack predicate.

`verify_support6_9919_independent_v1.cpp`:

- regenerates the same normal-form support choices but tests pair 8-short-freeness by direct bounded count-vector enumeration, not the depth formula;
- uses a minimum-base-depth / occurrence-mask recursion for the third atom;
- uses pair-union/complement matching for the four-pack predicate.

The pair predicate, extension state, and decisive packing predicate are therefore all replayed with different internal structures.

## 6. Strategic consequence

Both maximal C7 corridors now exclude the smallest support-four pair face:

- `(8,10,19)`: pair support six is empty already at the `19+10` stage, so every compatible maximal pair has support at least seven;
- `(9,9,19)`: the pair support-six face exists (26 pairs), but every 7-short-free completion by the third atom four-packs, so no obstruction survives that face.

The next theorem-level target is therefore not another support-six census. It is a **support-seven / rank-three augmentation statement** that can cover both maximal corridors and then be lifted prime-uniformly.

## Boundary

- No `D_3(C_7^3)` value is claimed.
- Pair support `>=7` remains open in `(9,9,19)`.
- The theorem is finite at `p=7`; no all-prime support-seven statement is inferred from it.
- The exact counts authorize only the declared support-four / pair-support-six face.
