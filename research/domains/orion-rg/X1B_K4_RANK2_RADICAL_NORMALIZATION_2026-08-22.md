# X1-B k=4 — exact shear/scaling normalization of the rank-2 radical family

Parent: #900.
Committed before exhaustive radical-family enumeration.

## Fixed rank-2 residual coordinates

Use the committed rank-2 factorization of the common 13-position Gram witness. In a convenient two-dimensional base coordinate system the residual position vectors have fixed base rows

```text
position 0:       (2,0)
positions 1..4:   (0,4)
positions 5..8:   (4,4)
positions 9..12:  (1,0)
```

A full three-dimensional realization of the same rank-2 Gram matrix may add an arbitrary radical coordinate `r_j in F_5` to each position:

`y_j=(base_j,r_j)`.

The bilinear form is zero on the radical coordinate, so the global edge equations do not constrain r directly.

## Shear normalization

Consider the invertible kernel-coordinate transformation

`(u,v,w) -> (u,v,w + alpha u + beta v)`.

It preserves the first two base coordinates and is an element of `GL(3,5)`. Applying it simultaneously to the residual realization and to any ten-prefix sequence preserves zero-sum/subset-sum feasibility and sends forbidden sets equivariantly.

For positions 0 and 1 the transformed radical coordinates are

`r_0' = r_0 + 2 alpha`,

`r_1' = r_1 + 4 beta`.

Since 2 and 4 are invertible in `F_5`, there is a unique choice

`alpha=-r_0/2`, `beta=-r_1/4`

that makes

> `r_0'=r_1'=0`.

Thus every radical realization is linearly equivalent to one with the first two radical coordinates zero.

## Radical scaling normalization

After the shear, the transformation

`(u,v,w) -> (u,v,c w)`, `c in F_5^*`,

is also invertible and preserves the rank-2 base Gram data.

If all remaining coordinates `r_2,...,r_12` vanish, retain the all-zero representative.

Otherwise let k be the first index in `2,...,12` with `r_k != 0`; choose `c=r_k^{-1}`. Then the normalized representative has

`r_0=r_1=0`,

all earlier remaining coordinates zero, and

> the first nonzero entry among `r_2,...,r_12` equal to 1.

No position permutation or quotient-orbit symmetry is used.

## Exact normalized count

There are `5^11` assignments to the remaining 11 coordinates after shear normalization. The nonzero assignments fall into free orbits of size 4 under radical scaling. Hence a complete representative set has

`1 + (5^11-1)/4 = 12,207,032`

members.

## Consequence

Any exact feasibility/nonexistence result proved for all 12,207,032 normalized radical assignments is complete for the entire raw `F_5^13` radical family, because every raw realization is related to exactly one normalized scaling orbit after the unique shear normalization.

## Claim boundary

This is an exact symmetry reduction of the finite rank-2 radical realization problem. It carries no C15 theorem or novelty authority by itself.