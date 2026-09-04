# First-corridor generalization checkpoint after the `a=1`, `c=4` closure — V1

Status: **live theorem-development checkpoint; no `D_3` closure claim**.

## New result

For the `a=1` support-three equality normal form

`V=e3^c x^r y^t`,

`A1_LIGHT_SUPPORT3_FOUR_SHARE_ELIMINATION_V1.md` proves for every prime `p>=7` that

`boxed{c!=4}`.

Together with the existing `c=1,2,3` eliminations,

`boxed{c>=5}`

is now necessary for every hypothetical exact-support-six support-three companion of type `a=1`.

The proof is symbolic except for exactly three arithmetic resonances at `p=7,13,17`, all of which are independently empty under the full graded depth test.

## Mechanism learned

Writing the four boundary rows as

`r=q-3+k`, `t=p-1-k`, `0<=k<=3`,

reveals a non-accidental multiplier pattern:

- `k=0,3` are controlled by denominator `c+1=5`;
- `k=1,2` are controlled by denominator `c-1=3`;
- `r>=q+1` is controlled by doubling.

This suggests replacing further layer-by-layer work by a general endpoint/inner-boundary multiplier-existence lemma for arbitrary overlap `c`.

## Current local frontier

The first-corridor support-seven target still requires eliminating:

- `a=1` support-three with `c>=5`;
- `a=2` light-share support-three with `c>=4`;
- rank-three support-four companions, especially the `a=2` model;
- any other support-four type left by the inverse-residue selector.

## Next discriminator

The most valuable next step is to test and prove the following schematic claim.

> For fixed `c`, parameterize the boundary rows by `r=q+1-c+k`, `t=p-1-k`, `0<=k<c`. Multipliers with denominators drawn from `c+1-2k` or its nearest positive symmetric partner should cover all but a bounded resonance set; the interior is covered by a small scalar such as `2`.

The `c=4` proof gives the first complete nontrivial instance: denominators `5,3,3,5`. A discovery checker should synthesize the denominator pattern for `c=5,6,...` before another theorem file is attempted.

## Claim ceiling

No value of `D_3(C_7^3)`, no all-prime multiwise Davenport formula, and no novelty/priority statement is claimed.
