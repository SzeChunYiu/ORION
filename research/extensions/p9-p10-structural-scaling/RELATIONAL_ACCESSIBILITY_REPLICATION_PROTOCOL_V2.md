# Relational Accessibility Replication Protocol V2

Status: **FROZEN AFTER V1.1, BEFORE V2 OUTCOMES**

Frozen: 2026-08-20

## 1. Why V2 exists

V1.1 produced a large information-equivalent relational-versus-flat effect at every frozen dimension, but its positive terminal was correctly blocked because one fixed shuffled-label control exceeded an absolute `0.65` threshold. The V1.1 artifact and failed terminal remain immutable.

The post-V1.1 diagnosis is that a one-draw threshold is an inadequately calibrated randomization control when low-dimensional relational inputs have a small finite pattern space with many repeated rows. V2 changes both the outcome sample seeds and the hostile-control design. It does not reinterpret V1.1 as positive.

## 2. Unchanged task and representations

For odd `d`, sample uniform independent `x,c in {-1,+1}^d` and define

`y = 1[sum_i x_i c_i > 0]`.

- `FLAT = concat(x,c)`.
- `RELATIONAL = concat(x, x*c)`.

The transformation remains bijective because `c = x*(x*c)`.

## 3. Fresh replication grid

Dimensions:

`d in {3,5,9,17,33,65}`.

For each dimension run three independent replications `r in {0,1,2}`.

Each replication uses:

- `n_train = 4096`;
- `n_test = 16384`;
- train seed `5100001 + 10007*d + 101*r`;
- test seed `6100001 + 20011*d + 103*r`.

None of these train/test seeds were used by V1.1.

## 4. Fixed learner

Same primary learner as V1.1:

- scikit-learn LogisticRegression;
- `C=1.0`;
- `solver='lbfgs'`;
- `max_iter=5000`;
- no tuning.

## 5. Distributional label-randomization null

For every `(d,r)` cell, freeze 64 independent shuffled-label draws with seeds

`7100001 + 30011*d + 1009*r + j`, `j=0,...,63`.

Each draw permutes the training labels and refits the RELATIONAL learner while leaving features and the protected test set fixed.

Report all 64 accuracies, their mean, standard deviation, median, maximum, and the empirical one-sided randomization value

`p_emp = (1 + #{null_accuracy >= observed_accuracy}) / 65`.

This finite randomization value is descriptive for each cell; V2 does not claim asymptotic significance from it.

## 6. Other hostile controls

For every `(d,r)` cell:

1. exact relational-to-candidate reconstruction failures must be zero;
2. cyclic broken-relation test accuracy must be `<0.65`;
3. a jointly applied frozen coordinate permutation must change each canonical representation's accuracy by `<0.03`.

## 7. Primary replication terminal

V2 supports `RELATIONAL_ACCESSIBILITY_REPLICATED_CONTROLLED_CLASS` only if **all 18 fresh cells** satisfy:

1. RELATIONAL accuracy `>=0.95`;
2. FLAT accuracy `<=0.65`;
3. RELATIONAL-minus-FLAT accuracy delta `>=0.30`;
4. observed RELATIONAL accuracy is strictly greater than the maximum of all 64 shuffled-label null accuracies;
5. empirical randomization value is therefore exactly `1/65`;
6. broken-relation accuracy `<0.65`;
7. reconstruction failure count `0`;
8. surface-permutation absolute change `<0.03` for both representations.

Additionally, across the 18 cells:

- median RELATIONAL-minus-FLAT delta must be `>=0.45`;
- the minimum RELATIONAL-minus-FLAT delta must be reported;
- no cell may be excluded.

## 8. Secondary capacity result

V2 does not repeat the full V1.1 sample-size curve. It carries forward V1.1's sample-complexity curve only as historical evidence and uses the fresh replications to test whether the large 4096-example accessibility gap generalizes to new sampled worlds.

## 9. Claim if positive

Only if the full terminal passes:

> Across 18 fresh controlled replications spanning six dimensions, a bijectively information-equivalent relational reparameterization makes the alignment decision nearly perfectly accessible to the same fixed linear learner while the flat encoding remains near chance, and the observed relational performance exceeds every frozen shuffled-label null fit in every replication.

This remains a restricted controlled-class result. It does not establish an LLM scaling law or explain the empirical P9 D1 effect causally.

## 10. Determinism

The output JSON contains no timestamp. CI must execute V2 twice and require byte-identical result bytes before terminal evaluation.
