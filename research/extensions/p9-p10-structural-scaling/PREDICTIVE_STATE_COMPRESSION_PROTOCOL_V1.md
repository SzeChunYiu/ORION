# Predictive-State Compression Protocol V1

Status: **FROZEN BEFORE OUTCOMES**

Frozen: 2026-08-20

## Question

When a compact statistic is exactly sufficient for the decision target, does retaining task-irrelevant world state impose a measurable sample/access cost on a fixed bounded learner?

This is **not** a same-information comparison. The compact arm deliberately discards nuisance information that is irrelevant to `Y`; its claim is about predictive sufficiency and nuisance burden, not full-state equivalence.

## World

For odd `k`, sample independent uniform

`x,c in {-1,+1}^k`,

set relation vector `r=x*c`, and target

`y=1[sum_i r_i>0]`.

Because `y` is a deterministic function of `r`, `r` is exactly sufficient for the target under this generator:

`P(Y|X,C,R)=P(Y|R)`.

## Representation arms

- `S0_MINIMAL = r` — target-sufficient relation state only, dimension `k`.
- `S1_FULL = concat(x,r)` — bijective full structured state, dimension `2k` because `c=x*r`.
- `S2_PADDED = concat(x,r,z)` — S1 plus `4k` independent nuisance signs `z`, total dimension `6k`.

The nuisance vector is generated independently of `(x,c,y)` from a separately frozen seed stream. It cannot carry label or domain identity.

## Frozen grid

- `k in {17,33,65}`;
- `n_train in {32,64,128,256,512,1024,2048,4096}`;
- protected `n_test=16384`;
- three fresh replications per k;
- all seeds distinct from previous controlled experiments.

## Learner

Same linear logistic regression in every arm:

- `C=1.0`;
- `solver='lbfgs'`;
- `max_iter=5000`;
- no tuning.

## Endpoints

For each k/arm:

1. mean held-out accuracy by training size;
2. minimum frozen training size at which mean accuracy reaches `0.90`;
3. mean log loss at each sample size;
4. feature dimension.

Report ratios

`n*_FULL/n*_MINIMAL`

and

`n*_PADDED/n*_MINIMAL`

whenever both thresholds exist.

## Frozen positive terminal

`PREDICTIVE_STATE_COMPRESSION_ADVANTAGE_SUPPORTED` requires:

1. S0 reaches mean accuracy `>=0.95` by 4096 for every k;
2. S0 reaches the 0.90 threshold no later than S1 for every k where S1 reaches it;
3. S0 reaches the 0.90 threshold no later than S2 for every k where S2 reaches it;
4. median `n*_FULL/n*_MINIMAL >=1.5` across comparable k;
5. median `n*_PADDED/n*_MINIMAL >=2.0` across comparable k;
6. at the smallest shared n=32, S0 mean log loss is no worse than S1 and S2 for at least two of three k;
7. nuisance-generation correlation with y has absolute empirical Pearson correlation `<0.04` for every generated nuisance coordinate on the protected test sets, or the experiment is invalid and must be reissued prospectively.

The `0.04` independence sentinel was calibrated **before execution** to be conservative under the planned family of roughly 2,300 nuisance-coordinate checks: a normal/Bonferroni 5% family-wise reference at `n=16384` is approximately `0.0332`. The sentinel is not a scientific endpoint and cannot be relaxed after outcomes.

## Claim if positive

> In a controlled sequential-state analogue with an exact predictive sufficient statistic, retaining decision-irrelevant world coordinates increases the observed sample burden of a fixed linear learner, and adding independent nuisance state increases it further.

This does not imply that shorter prompts are universally better, nor that `r` is a sufficient state for natural-language reasoning or Lean proof search. It motivates directly testing whether P9/P10 structured states function as approximate predictive sufficient statistics.
