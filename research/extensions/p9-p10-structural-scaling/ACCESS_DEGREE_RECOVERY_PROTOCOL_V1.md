# Access-Degree Recovery Protocol V1

Status: **FROZEN BEFORE OUTCOMES**

Frozen: 2026-08-20

## Question

When an invertible coordinate map hides a linearly accessible target behind higher-degree monomials, can increasing the interaction degree of a fixed classifier systematically recover the lost accessibility?

This experiment is downstream of, but outcome-independent from, the completed invertible-obfuscation ladder. It uses fresh worlds and a smaller dimension chosen for tractable exhaustive polynomial expansions through degree 4.

## World and encoding

Sample uniform `r in {-1,+1}^13` with target

`y = 1[sum_i r_i > 0]`.

For block length `b`, encode each block by

- `u_1=r_1`;
- `u_j=r_j r_{j-1}` for later positions.

The exact inverse is `r_j=product_{i=1}^j u_i` inside a block, so the map is bijective and the maximum explicit inverse-coordinate degree is the block length.

## Frozen grid

- dimension `k=13`;
- block lengths `b in {1,2,4,8,13}`;
- polynomial interaction degrees `d in {1,2,3,4}`;
- `n_train=4096`;
- `n_test=16384`;
- three independent fresh replications per block length;
- all seeds fixed in code and distinct from earlier controlled experiments.

## Learner

For each degree, generate all interaction-only monomials of degrees `1..d` using a frozen deterministic polynomial feature map, then fit the same logistic regression:

- `C=1.0`;
- `solver='lbfgs'`;
- `max_iter=5000`;
- no tuning.

The degree-1 arm is ordinary linear logistic regression.

## Exact representability landmarks

For block length `b<=4`, a polynomial threshold of degree `b` exists exactly because every recovered latent coordinate in the score `sum_i r_i` has degree at most `b` in `u`.

This is an existence statement, not a guarantee that finite-sample logistic regression will recover the exact separator.

## Primary endpoints

For every `(b,d)`:

1. mean held-out accuracy over the three replications;
2. feature dimension;
3. minimum tested degree reaching mean accuracy `0.90`, otherwise `NOT_REACHED`.

Also report, for `b=2` and `b=4`, the gain of the exact-representability degree over degree 1.

## Frozen positive terminal

`ACCESS_DEGREE_RECOVERY_SUPPORTED_CONTROLLED_CLASS` requires all of:

1. zero decode failures in every replication;
2. `b=1,d=1` mean accuracy `>=0.95`;
3. `b=2,d=2` mean accuracy `>=0.95` and exceeds `b=2,d=1` by at least `0.10`;
4. `b=4,d=4` mean accuracy `>=0.90` and exceeds `b=4,d=1` by at least `0.10`;
5. at `b=4`, degree 4 exceeds degree 2 by at least `0.05`;
6. the minimum tested degree reaching `0.90` is `1` at `b=1`, no less than `2` at `b=2`, and no less than `3` at `b=4`;
7. feature dimension is strictly increasing with polynomial degree.

No condition is imposed that `d<=4` must solve `b=8` or `b=13`; those cells test the unresolved side of the capacity frontier and remain visible regardless of sign.

## Claim if positive

> In a controlled bijective encoding family, lost accessibility can be recovered by increasing model interaction order: the degree required by a generic polynomial learner tracks the algebraic access degree induced by the representation, while higher-obfuscation cells remain harder when the tested model degree is insufficient.

This is a restricted polynomial-class result. It is not a theorem about transformer depth, parameters, chain-of-thought length, or general computational complexity.
