# Controlled Semantic-Orbit Stability Protocol V1

Status: **FROZEN BEFORE OUTCOMES**

Frozen: 2026-08-20

## Question

Does explicit relational representation make a fixed bounded learner more stable under semantics-preserving surface transformations than an information-equivalent flat representation with interaction capacity?

## World

For odd `k`, sample independent uniform `x,c in {-1,+1}^k` and target

`y = 1[sum_i x_i c_i > 0]`.

Representations:

- `FLAT = concat(x,c)` with a degree-2 interaction expansion before logistic regression;
- `RELATIONAL = concat(x,x*c)` with linear logistic regression.

The latent information is identical because `c=x*(x*c)`.

## Frozen grid

- `k in {9,17,33}`;
- `n_train=1024`;
- `n_test=4096`;
- one frozen train/test world per `k` using seeds not used by V1.1, V2 or V3 A/B;
- 32 frozen semantic-orbit transformations per `k`.

## Semantic-orbit transformations

Each transformation chooses:

1. a permutation `pi` of the `k` entity coordinates;
2. a sign-renaming vector `s in {-1,+1}^k`.

Apply simultaneously

`x'_i = s_i x_{pi(i)}`

`c'_i = s_i c_{pi(i)}`.

Then

`x'_i c'_i = x_{pi(i)} c_{pi(i)}`,

so the multiset of pairwise relations and the target are unchanged exactly. No labels or model outputs are used to create transformations.

Models are trained **once on canonical training data**. They are not retrained for orbit members.

## Metrics

For every test item and model, collect predictions over all 32 orbit members.

Define item orbit inconsistency

`OIR(x)=1-max_y count(prediction=y)/32`.

Report:

- canonical held-out accuracy;
- mean accuracy over all orbit members;
- mean OIR;
- 95th percentile OIR;
- fraction of items with any prediction change;
- fraction of orbit predictions differing from the canonical prediction.

Accuracy and stability are separate endpoints. A stable wrong model cannot be called robust reasoning.

## Frozen primary success terminal

`RELATIONAL_SEMANTIC_ORBIT_STABILITY_SUPPORTED_CONTROLLED_CLASS` requires:

1. relational canonical accuracy `>=0.95` for all three `k`;
2. relational mean orbit accuracy `>=0.95` for all three `k`;
3. relational mean OIR `<=0.02` for all three `k`;
4. relational mean OIR is no worse than flat-quadratic mean OIR for at least two of three `k`;
5. mean across-k OIR advantage `(flat_quadratic - relational) >=0.005`;
6. every generated transformation passes the exact target-preservation check.

If only conditions 1-3 and 6 pass, retain a bounded relational-stability result but do not claim superiority over the flat quadratic learner.

## Claim boundary

This is a controlled symmetry/generalization experiment. It is not evidence that an LLM is invariant to natural-language paraphrase, graph serialization, or Lean alpha-renaming. Those require their own model/runtime experiments under the V3 C protocol.
