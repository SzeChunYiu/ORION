# P9 M1 — classical candidate-relative learning gate

## Development question

Before adding graph, sheaf, neural-algorithmic, recurrent-latent, probabilistic, binding, or causal machinery, determine how far **simple generic learners** can go on the exact P9 task interface and which residual computations actually remain.

The claim under test is deliberately diagnostic:

> Given the same architecture-neutral P9 tasks and reminted train/dev/test identities, generic classical learners should approach—but never exceed—the exact information ceiling of the declared model view. A gap below an identifying ceiling is evidence about missing learning/computation, not permission to jump directly to a preferred neural architecture.

M1 is not a P9 paper claim.

## Incumbent evidence and negative history

M1 consumes only merged, verified P9 substrate:

- PR #473 — exact hostile structural worlds and information-sufficiency analysis;
- PR #481 — contamination-safe deterministic paired corpus;
- PR #483 — architecture-neutral task/evaluator with preserved pre-outcome V0→V0.1 leakage correction;
- #469/#474–#485 — donor-complete research programme and current atomic research map.

Negative lessons already binding M1:

1. model-visible presentation can leak hidden semantics even when the nominal representation does not;
2. task adapters can accidentally remove or add information relative to a declared view;
3. a learner above an exact view ceiling indicates leakage/evaluator failure;
4. reminted mechanic identities forbid global mechanic-id classification;
5. simple donor mechanisms get first right of refusal;
6. result-bearing features/hyperparameters cannot be added after protected test access without a new protocol version.

## Atomic development fibres

1. Freeze corpus identity, split counts, order seeds, model families, feature families, dev-selection rule, test rule, and statistics before protected test outcomes.
2. Build a generic field/value feature representation that excludes raw opaque identities as reusable categorical values.
3. Build candidate-relative interaction features without embedding domain-specific solution rules.
4. Preserve candidate-id equality only as an equality/overlap relation, not an identity token.
5. Expose transport numeric values only in views that already contain them; never compute the affine cycle residual as a feature.
6. Train mechanic ranking as binary candidate scoring and gluing as fixed-vocabulary multiclass classification.
7. Tune only on train→dev; run one test evaluation per frozen selected configuration.
8. Run deterministic leakage sentinels: order, opaque-id, row-index/family prior, and shuffled labels.
9. Report per-view, per-family, per-task accuracy and exact view ceiling.
10. Distinguish `NON_IDENTIFIABLE`, `LEARNING_GAP`, `SIMPLE_MODEL_SUFFICIENT`, and `LEAKAGE` outcomes.
11. Preserve raw per-example predictions and all tried dev configurations.
12. Produce a routing receipt that decides whether any residual justifies A1–A10 escalation.

## Knowledge/search saturation basis

M1 does not require new neural literature to run. It is a **lower-bound gate** before those donors become relevant. The relevant incumbent families are ordinary linear models, trees/forests, nearest-neighbour/case-based learning, feature hashing/vectorisation, and calibrated classification.

A richer model is justified only by a residual that these simple learners cannot explain after the view is information-identifying.

## Challenge to the basis

Simple models can appear weak for reasons unrelated to architecture:

- the feature map may omit an admissible coordinate;
- a categorical encoder may discard equality structure;
- finite sample size may be the bottleneck;
- a global multiplicative computation may not be linearly representable;
- train/dev selection may favour average accuracy while hiding a family-specific failure;
- model size/hyperparameter search may be unfairly small.

Therefore M1 uses multiple model families, a small frozen train-size curve, per-family metrics, and an explicit ceiling-gap diagnosis.

## Frozen implementation hypothesis

Implement `orion.study.p9.m1` using existing `numpy`/`scikit-learn` candidate dependencies only.

### Generic feature maps

`F0_FIELD_BAG`
- path/value categorical features for non-opaque structural vocabulary;
- numeric scalar features;
- shape/count features;
- opaque ids/surfaces represented only by generic type/count, not raw token value.

`F1_PAIRWISE`
- F0 plus generic context×candidate categorical conjunctions;
- candidate-id appears-in-context equality indicator;
- read/write overlap counts and type-overlap counts where derivable from the visible task payload;
- candidate numeric cost.

`F2_CYCLE_NUMERIC`
- for gluing only and only at CURRENT/SEMANTIC views: directed-cycle transport `(scale, offset)` sequence in canonical visible topology order;
- no hand-coded composition/product/residual/identity calculation.

### Model families

- logistic regression;
- decision tree;
- random forest;
- k-nearest neighbours.

A shallow MLP is not M1; it requires a later explicit escalation.

### Selection

- deterministic small hyperparameter grid;
- maximize dev accuracy; ties break by lower model complexity then lexical config id;
- final selected config evaluated once on protected test;
- train-size curve is diagnostic and uses a predeclared prefix of train pairs, never test tuning.

## RED / hostile tests before implementation completion

- raw opaque ids do not appear as feature names;
- pair orientation/candidate order permutation does not change semantic feature multiset or selected mechanic identity;
- label shuffle collapses performance;
- a deliberately injected hidden-semantic side channel is caught by ceiling violation;
- F0 cannot see history equality when history is not present;
- F1 equality works with reminted ids without learning the id itself;
- F2 exposes raw numeric transports but not cycle-composition residual;
- model predictions remain within exact view ceiling on non-identifying views;
- one test pass is bound to the frozen selected dev configuration;
- rerun is byte/digest reproducible modulo explicitly ignored library metadata.

## Reopen triggers

Reopen M1 if:

- an exact view-ceiling mismatch reveals an adapter/feature leak;
- a strong simple baseline was omitted and materially changes the residual;
- test outcomes are used to redesign features/hyperparameters;
- generated corpus identity changes;
- #484/#485 exact-world extensions are merged before M1 terminal and invalidate the frozen task set.

## Nonclaims

M1 does not establish:

- superiority of ORION structure over language/graph models;
- neural architecture value;
- natural-science ecological validity;
- mechanism discovery;
- causal correctness;
- scientific/adoption authority;
- standalone P9 paper readiness.

The only valid M1 terminal is a bounded diagnostic disposition backed by immutable results.