# Support-8 one-projective-collision closure — hostile audit V1

Status: **exact audit of an already landed bounded closure**. This file adds no second enumeration and grants no global `D_3(C_7^3)` or novelty authority.

Audited branch head: `6a91f881d3939ae3408d8aec8cdcc52bfd30b56d`.

## 1. Correct frozen count

The support-7 campaign has 14,860 short-free lifts. The support-8 one-projective-collision campaign is different: its current theorem and frozen JSON both record

- 19,114,200 parameterized total-zero lifts;
- 15,844 7-short-zero-free lifts;
- 15,844 lifts with a four-pack;
- zero survivors with packing number at most three.

Any handoff text assigning 14,860 to the one-collision branch is stale and must not be propagated.

## 2. Cover audit

The analytic reduction maps every candidate to one of the existing 54 seven-direction `(7,3)`-arc classes. For a fixed class:

- direction deficits are weak compositions of 5 into 7 parts: 462 profiles;
- the doubled direction has 9 swap-canonical one-dimensional states;
- after matching the doubled-direction occupancy and summing over its 7 possible positions, there are 2,583 profile/local/position states per projective kernel;
- the 54 classes contain 7,400 normalized full-support kernel vectors.

The frozen count is therefore

`7400*2583=19,114,200`.

For elimination, injective orbit counting is unnecessary: a repeated parameterization would only duplicate tests. The load-bearing property is surjective coverage. The scalar/kernel reconstruction in `SUPPORT8_ONE_COLLISION_THEOREM_V1.md` is reversible after a projective representative, doubled direction, local state and normalized nonzero kernel vector are fixed, so no candidate is omitted.

## 3. Short-freeness predicate audit

The primary engine recursively enumerates every eight-coordinate submultiplicity vector of total weight at most 7 and rejects on zero sum.

The independent engine generates a flat list of every eight-coordinate weak composition of lengths 1 through 7, filters by the candidate multiplicities, and evaluates the vector sum.

Both are exhaustive over the same mathematical domain but use different enumeration structures. The independent verifier also freezes all 54 per-class total and short-free counts, preventing a silently changed classification from passing merely because every newly selected candidate still four-packs.

## 4. Four-pack predicate audit

Let `B` be one of the 7-short-zero-free length-37 candidates. In any partition of `B` into four nonempty zero-sum blocks, every block has length at least 8. Sort the four lengths as

`a<=b<=c<=d`, `a+b+c+d=37`.

Then

- `a<=9`, because four blocks of length at least 10 would total at least 40;
- `b<=9`, because `b>=10` would give at least `8+10+10+10=38`;
- `d<=13`, because the other three blocks have total at least 24.

Therefore the primary engine is exact when it enumerates first and second blocks of lengths 8 or 9, a third zero-sum block of length 8 through 13 while reserving at least 8 terms, and accepts when the residual is the fourth block. The residual is automatically zero-sum because the whole sequence and the first three blocks are zero-sum.

The independent engine changes the formulation. It enumerates all zero-sum count vectors of lengths 8 through 13, forms every capacity-compatible unordered pair, and asks whether the complement of one pair is another pair. This is exactly the four-block partition predicate.

## 5. Frozen-array arithmetic

The result file freezes 54 kernel counts summing to 7,400. Multiplying each by 2,583 gives the 54 total-lift counts summing to 19,114,200. Its 54 short-free counts sum to 15,844.

These totals were independently re-summed during this audit.

## 6. CI replay receipt

GitHub Actions run `33787642582` at audited head `6a91f881` completed successfully. In particular:

- all six primary one-collision shards over class intervals `0..9`, `9..18`, `18..27`, `27..36`, `36..45`, `45..54` succeeded;
- all six independent one-collision shards over the same intervals succeeded;
- the analytic-cover and existing support-7 controls also succeeded.

Thus the exact bounded closure is both recorded and replayed at the audited head.

## 7. Authorized conclusion

There is no length-37 zero-sum sequence over `C_7^3` with packing number at most three, support size eight, and exactly seven projective support directions.

Combined with the support-7 closure, any obstruction with support at most eight must have support exactly eight on eight distinct projective directions.

## Boundary

The remaining support-8 branch is Type A: eight distinct projective directions among the 350 projective classes, after the Property-C deficit filters. The three classes with two support-disjoint four-secants are analytically impossible, leaving the declared 347-class scalar/kernel residual. Higher support and the two length-19 corridors also remain open.
