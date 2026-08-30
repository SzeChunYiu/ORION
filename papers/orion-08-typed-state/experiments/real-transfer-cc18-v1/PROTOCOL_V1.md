# ORION-08 real-domain transfer on OpenML-CC18 — protocol V1

**Committed before the runner produced any outcome.** No dataset was scored, and
no arm was run, before this file was committed.

## Why this exists

ORION-08's readiness terminal is
`INTERNAL_REVIEW_PASS__EXACT_SYNTHETIC_MECHANISM_CLAIM`, and its own claim
disposition says "Real-domain transfer remains successor". #1701 specifies that
successor precisely, and this executes it on the E2 leg:

> Use E2 OpenML-CC18 for a second structurally different decision family where
> actions/utilities can be frozen objectively. Before outcomes, define coarse
> binding and refined/typed binding. Compute theorem prediction: value iff
> positive-mass coarse fibre contains incompatible optimal actions. Arms: coarse;
> strongest deterministic proxy; generic acquisition/info-gain; typed binding;
> oracle. Require at least one predicted no-value/tie stratum and one value
> stratum. Report fraction of oracle-achievable gap captured and cost.

The paper's theorems are exact statements about fibres, not statistical
tendencies, so a real-domain test is a genuine falsification opportunity rather
than a demonstration:

- **Theorem 1** — a zero-regret policy exists **iff** every positive-mass fibre
  has a common optimal action.
- **Theorem 2** — refinement decreases regret **strictly, exactly when** it splits
  an action-impure fibre.

An "exactly when" fails if a single positive-mass fibre behaves otherwise. One
counterexample refutes it; a thousand agreements do not prove it. Both directions
are recorded.

## Decision family, frozen before outcomes

Binary-target CC18 datasets fetched by `data_id`. Actions are `{predict 0,
predict 1}`. The utility is a frozen asymmetric cost matrix, fixed here and not
tuned per dataset:

```
utility(action=1, y=1) = +1     utility(action=1, y=0) = -1
utility(action=0, y=1) =  0     utility(action=0, y=0) =  0
```

Asymmetry matters: it makes the optimal action depend on `P(y=1 | fibre)` rather
than being constant, so a fibre's optimal action is a real decision and not a
label copy. Under this matrix the optimal action for a fibre is `1` iff
`P(y=1 | fibre) > 0.5`.

## Bindings, frozen before outcomes

A binding is a map from a row to a bound state; its fibres are the preimages.

- **coarse** — the first `k_coarse = 2` features, each discretised into 3
  quantile bins on the training split.
- **refined / typed** — the coarse features plus the next `k_extra = 2` features,
  same binning. The typed binding is a strict refinement of the coarse one by
  construction, which is what Theorem 2 is about.

Bin edges are fitted on training rows only and applied unchanged to evaluation
rows. Feature order is the dataset's own column order, so no feature is chosen
after seeing an outcome.

## Arms

1. `coarse` — best coarse-measurable policy.
2. `refined_typed` — best refined-measurable policy.
3. `proxy_strong` — a gradient-boosted classifier's thresholded prediction used as
   the binding. This is the strongest deterministic competitor and may beat the
   typed binding; that outcome is reportable.
4. `infogain_refine` — refine the coarse binding by adding the single feature with
   the highest mutual information with the target, ignoring the theorem. This is
   the generic-acquisition arm and tests whether the theorem's criterion is doing
   work a standard heuristic does not.
5. `oracle` — the per-row optimal action. Upper bound, not a policy.

## The prediction, computed before its outcome is scored

For each dataset the runner records, **from the training split alone**, whether any
positive-mass coarse fibre is action-impure — that is, whether it contains rows
whose refined-binding optimal actions disagree.

- impure fibre exists → Theorem 2 predicts **strict** regret decrease from coarse
  to refined;
- every coarse fibre pure → Theorem 2 predicts **no** decrease (a tie).

Datasets are then reported in two strata by that prediction. The protocol requires
**at least one dataset in each**, and if the fetched set does not produce both, the
terminal is `CANNOT_CHECK_NO_CONTRAST` — not a quiet report of whichever stratum
appeared.

## Endpoints

- regret per arm, and the fraction of the oracle-achievable gap each arm captures;
- cost per arm: number of distinct bound states, which is what a deployment pays;
- agreement between the theorem's prediction and the observed direction, per
  dataset, both ways.

## Terminals

- `THEOREM_PREDICTS_REAL_TRANSFER` — the prediction matches the observed direction
  on every dataset in both strata.
- `THEOREM_FAILS_ON_REAL_DATA` — any dataset contradicts it. Recorded with the
  dataset and the fibre, and **not** rescued by re-binning or re-weighting.
- `CANNOT_CHECK_NO_CONTRAST` — one stratum is empty.

No terminal here promotes ORION-08's claim beyond its exact-synthetic scope. A
pass makes real-domain transfer *supported on the E2 leg only*; E3 Defects4J
remains separate and untouched.
