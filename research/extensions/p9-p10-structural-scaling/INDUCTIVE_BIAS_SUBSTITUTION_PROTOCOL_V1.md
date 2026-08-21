# Inductive-Bias Substitution Protocol V1

Status: **FROZEN BEFORE OUTCOMES**

Frozen: 2026-08-20

## Question

For the same latent relation task, how does sample burden change as the correct structural prior is supplied at different places in the system: nowhere, generic model capacity, sparse regularization, a correct architectural interaction prior, or the input representation itself?

## World

For odd `k`, sample independent uniform

`x,c in {-1,+1}^k`,

with target

`y=1[sum_i x_i c_i>0]`.

All arms receive the same underlying `(x,c)` world. No outcome-specific feature selection is permitted.

## Frozen model/representation arms

### M0 — flat linear

Logistic regression on `concat(x,c)`.

### M1 — generic bilinear L2

Construct every cross interaction

`q_ij=x_i c_j`

for all ordered `(i,j)`, producing `k^2` features. Fit L2 logistic regression.

The correct diagonal interactions are present, but the model is not told which k of the k^2 coordinates are structurally aligned.

### M2 — generic bilinear sparse L1

Use the identical `k^2` bilinear feature matrix but L1-regularized logistic regression with frozen `C=1.0`, `solver='liblinear'`, `max_iter=5000`.

Report selected diagonal and off-diagonal support. This is a separate sparsity-prior test and cannot rescue M1.

### M3 — diagonal bilinear architectural prior

The architecture computes only

`d_i=x_i c_i`

for matching coordinate indices and fits the same L2 logistic regression on the k resulting features.

### M4 — explicit relational representation

Provide the relation vector

`r_i=x_i c_i`

as the input and fit the same L2 logistic regression.

M3 and M4 are numerically the same feature values by construction. Their equality is a provenance/placement control: the correct structural computation can be placed in an architectural adapter or in the representation. Their fitted predictions and metrics must be byte/equality identical or the experiment is invalid.

## Frozen grid

- `k in {9,17,33}`;
- `n_train in {64,128,256,512,1024,2048,4096}`;
- `n_test=16384`;
- three fresh replications per k;
- all seeds distinct from earlier experiments.

## Learner details

M0/M1/M3/M4:

- L2 LogisticRegression;
- `C=1.0`;
- `solver='lbfgs'`;
- `max_iter=5000`.

M2:

- L1 LogisticRegression;
- `C=1.0`;
- `solver='liblinear'`;
- `max_iter=5000`;
- fixed deterministic random state `0` where the implementation exposes it.

No hyperparameter selection is performed.

## Primary endpoints

For every k and arm:

1. mean held-out accuracy by n;
2. minimum frozen n reaching mean accuracy `0.90`, otherwise `NOT_REACHED`;
3. feature dimension;
4. for M2, median selected support size, diagonal support and off-diagonal support.

Derived observed threshold ratios:

- `n*_M1 / n*_M4` generic-capacity tax;
- `n*_M2 / n*_M4` sparse-prior tax;
- `n*_M3 / n*_M4` architecture/representation placement control.

## Frozen primary terminal

`STRUCTURAL_PRIOR_SUBSTITUTION_SUPPORTED_CONTROLLED_CLASS` requires:

1. M3 and M4 predictions/accuracies are identical in every replication/n/k cell;
2. M3/M4 reach mean accuracy `>=0.95` by n=4096 for every k;
3. M0 remains `<=0.65` at n=4096 for every k;
4. M1 reaches 0.90 for at least two k, so a generic-capacity sample threshold is measurable;
5. among k where M1 and M4 both reach 0.90, median `n*_M1/n*_M4 >=2.0`;
6. M1 feature dimension is exactly `k^2`, while M3/M4 feature dimension is exactly k;
7. no generated bilinear coordinate or support selection depends on protected labels except through the declared fitted regularized learner.

## Secondary sparsity-prior terminal

`SPARSITY_PRIOR_REDUCES_GENERIC_DISCOVERY_COST` is separately supported only if:

1. M2 reaches 0.90 for at least two k;
2. on at least two k where both thresholds exist, `n*_M2 <= n*_M1`;
3. at n=4096, median M2 selected off-diagonal support is <50% of all available off-diagonal coordinates for every k;
4. M2 retains at least 80% of diagonal coordinates in median support at n=4096 for every k.

A failed sparsity terminal does not invalidate the primary architecture/representation substitution result.

## Claim if primary terminal is positive

> On an information-identical controlled task, the correct relational computation can be supplied either explicitly in the representation or exactly as an architectural interaction prior, producing identical downstream learning behavior. A generic bilinear model that contains the correct computation among k^2 possibilities pays a measurable feature/sample discovery cost.

This is a restricted learner/feature-map result. It does not imply that transformer architecture and prompt representation are generally interchangeable.
