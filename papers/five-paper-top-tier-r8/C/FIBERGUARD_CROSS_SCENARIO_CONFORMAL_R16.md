# FiberGuard R16 — cross-scenario probabilistic action certificates after exact-transfer failure

Date: 2026-08-26

Status at protocol commit: **prospective protocol and analytic bridge only; SAT16/SAT18/SAT20 outcomes have not been computed or admitted.**

Parent: R15 head `e431e9f187667431858f42e236bd74e57f658c31`.

## 1. Why R16 changes the certificate class

R14 prospectively refuted exact equality as an inductive policy key on SAT12-ALL. The training-selected exact policy had only 3.2% official-fold recurrence and 5.1% recurrence under a zero-family-overlap split, while a transparent learned selector using the same information performed much better. R15 then proved that paid policies incur an exact coverage tax and that a finite training fibre cannot upper-bound an unseen same-signature state without an additional structural premise.

R16 does not tune a coarsening on the R14 test outcomes. It moves to three later, untouched SAT solver-selection scenarios and evaluates a different authority class:

- a learned regret predictor supplies broad action proposals;
- split conformal calibration supplies a finite-sample **marginal** upper certificate for the proposed action;
- the controller deploys the learned action only when that upper bound is below a frozen tolerance;
- otherwise it uses a robust fallback;
- feature cost is paid in the same oracle-relative total-excess objective.

This is not a deterministic complete-fibre certificate. The distinction is explicit in every result and terminal.

## 2. Portable representation

The development, validation, and test scenarios are respectively:

- `SAT16-MAIN`;
- `SAT18-EXP`;
- `SAT20-MAIN`.

The scenarios have different solver portfolios. R16 transfers a representation/certificate **construction**, not a solver identity or fitted action policy. Each scenario refits its own regret predictor using only that scenario's proper-training folds.

The portable feature set is defined before outcomes as the intersection of deterministic features supplied by the declared paid acquisition step in all three scenarios. Feature names are canonicalized by removing the SAT20 `BASE` prefix, deleting non-alphanumeric characters, and uppercasing. Any collision fails closed. At least 40 common features are required.

The declared paid step is `ALL` for SAT16 and SAT18 and `BASE` for SAT20. Missing values receive proper-training median imputation plus explicit missingness indicators; numeric columns use proper-training mean/std scaling; feature-step runstatus is one-hot encoded.

## 3. Nested fold custody

For official test fold `f` in repetition 1:

- fold `1+(f mod 10)` is calibration;
- the other eight folds are proper training;
- fold `f` is test.

The learned predictor and robust fallback use proper-training outcomes only. The calibration fold computes the conformal quantile. Test outcomes are not used for fitting, calibration, model selection, or threshold selection.

SAT16 is the only development subject. It selects one model family, model hyperparameter tuple, miscoverage level `alpha`, and tolerance fraction `epsilon/cutoff` from the frozen finite menu. SAT18 validates that fixed tuple without retuning. SAT20 is the untouched final test.

## 4. Selected-action split-conformal certificate

Let `D_train`, `D_cal`, and a future point be exchangeable after the model/configuration has been fixed. Proper training produces predicted action regrets `rhat_a(x)` and the proposal

`ahat(x)=argmin_a max(0,rhat_a(x))`.

For a calibration point define

`s_i = R(ahat(x_i),x_i) - max(0,rhat_ahat(x_i)(x_i))`.

Let `q_alpha` be the split-conformal upper quantile with rank

`ceil((n_cal+1)(1-alpha))`,

using `+infinity` when the rank exceeds the calibration denominator. Define

`U(x)=max(0, max(0,rhat_ahat(x)(x)) + q_alpha)`.

### Theorem C-R16.1 — marginal selected-action upper certificate

Under exchangeability and with the predictor, proposal rule, and `alpha` fixed before calibration/test labels,

`P(R(ahat(X),X) <= U(X)) >= 1-alpha`.

#### Proof

Conditional on the proper-training data, the learned predictor and action proposal are fixed functions. The calibration scores and the future score

`R(ahat(X),X)-max(0,rhat_ahat(X)(X))`

are exchangeable. The standard split-conformal rank argument bounds the probability that the future score exceeds the finite-sample upper quantile by `alpha`. Clipping the resulting upper bound at zero can only enlarge it because regret is nonnegative. ∎

The theorem is classical split-conformal reasoning applied to the proposed downstream action. Split conformal prediction itself receives no novelty credit.

## 5. From an upper certificate to a safe-deployment event

Fix a tolerance `epsilon` before the target scenario. Deploy the learned action only if `U(x)<=epsilon`; otherwise use the frozen proper-training robust fallback.

### Corollary C-R16.2 — joint false-certificate control

Under the assumptions of Theorem C-R16.1,

`P(deploy and R(ahat(X),X)>epsilon) <= alpha`.

#### Proof

On the deployment event, `U(X)<=epsilon`. Therefore

`deploy and R(ahat(X),X)>epsilon`

implies `R(ahat(X),X)>U(X)`, whose probability is at most `alpha`. ∎

This is an unconditional joint false-certificate bound. It is not conditional coverage among deployed cases. If deployment coverage is `kappa`, the conditional error can only be bounded from this theorem by `alpha/kappa`, capped at one. R16 reports both the guaranteed joint estimand and the empirical conditional rate without conflating them.

### Corollary C-R16.3 — no worst-case or family-shift promotion

The split-conformal guarantee does not imply:

- worst-case fibre regret;
- pathwise safety for a randomized action;
- validity after arbitrary covariate or family shift;
- selected-subgroup conditional coverage.

Those require separate assumptions or methods. Any family-shift panel is empirical stress evidence only.

## 6. Paid selective decision value

Let `G` be the event `U(X)<=epsilon`, `a_L` the learned action, and `a_0` the robust fallback. The deployed action is `a_L` on `G` and `a_0` otherwise. With acquisition charge `c(X)`, total excess is

`L_sel(X)=c(X)+1_G R(a_L,X)+1_notG R(a_0,X)`.

### Theorem C-R16.4 — selective coverage-tax identity

Relative to the zero-feature fallback loss `L_0(X)=R(a_0,X)`,

`E[L_sel-L_0] = E[c] - P(G) E[R(a_0,X)-R(a_L,X) | G]`.

#### Proof

The deployed and fallback actions agree off `G`. The proof is therefore the R15 coverage-tax identity with the certificate-deployment event replacing exact-signature recurrence. ∎

A valid probabilistic certificate may still have no operational value if deployment coverage is too low or acquisition cost is too high. Conversely, a useful learned selector may fail the certificate gate. R16 measures certificate validity and decision value separately.

## 7. Frozen development search

The model menu is fixed before outcomes:

- distance-weighted kNN with `k in {4,8,16,32}`;
- ExtraTrees with 128 trees, leaf size in `{1,2,4,8}`, and feature fraction in `{0.5,1.0}`;
- RandomForest with 128 trees, leaf size in `{1,4}`, and feature fraction in `{0.5,1.0}`.

Candidate miscoverage levels are `0.05, 0.1, 0.2`. Candidate tolerances are `0.01, 0.05, 0.2, 1.0` times the scenario cutoff.

SAT16 selects the feasible tuple with minimum selective mean total excess. Feasibility requires deployment coverage at least 10%, selective mean and p95 no worse than fallback, and catastrophic wrong-action rate strictly below the corresponding full learned model. Ties are fully deterministic. If no tuple is feasible, the global objective minimum is retained but development failure remains visible.

SAT18 and SAT20 may not retune this tuple.

## 8. Frozen arms and gates

Every scenario reports:

1. proper-training single-best solver;
2. proper-training global robust solver;
3. frozen 16-NN full selector;
4. frozen ExtraTrees full selector;
5. development-selected full learned selector;
6. development-selected conformal selective selector.

All learned/selective arms pay the declared feature-step cost. Every arm uses the same statewise virtual-best PAR10 oracle.

A validation/test scenario passes only when:

- the selected full model has strictly lower mean total excess than fallback;
- the selective policy's mean overhead is at most 10% of the full model's gain over fallback;
- selective catastrophic wrong-action rate is strictly lower than the full model's;
- selective p95 is no larger than fallback;
- deployment coverage is at least 10%;
- empirical joint false-certificate rate is at most `alpha+0.02`.

The strongest terminal requires both SAT18 and the untouched SAT20 test to pass. A SAT18 pass followed by SAT20 failure is a first-class refutation.

## 9. Prior-art boundary

Donor-owned mechanisms include:

- split conformal prediction and finite-sample marginal coverage;
- selective prediction, abstention, and false-coverage control;
- covariate-shift and weighted conformal methods;
- kNN, random forests, ExtraTrees, and automated algorithm-selection systems such as AutoFolio;
- algorithm-selection robustness under distribution shift;
- generic feature acquisition and budgeted prediction.

Recent work explicitly studies automatic algorithm-selection robustness and explainability under marginal shifts, while modern conformal work addresses post-selection and distribution shift. R16 cannot claim those mechanisms generically.

The residual FiberGuard candidate is the integration of one common oracle-relative solver-action loss, paid feature acquisition, exact transductive fibre authority, prospective coverage-tax refutation, and a fail-closed probabilistic extension whose certificate and decision-value estimands remain separate.

## 10. Authority boundary

Even the strongest R16 terminal would establish only:

- method/configuration transfer from SAT16 to SAT18/SAT20;
- marginal split-conformal action-certificate evidence under official-fold exchangeability;
- paid decision value on three pinned public SAT portfolios.

It would not establish deterministic worst-case fibre safety, arbitrary family-shift validity, external reproduction, strongest-baseline completeness, production deployment value, novelty, or journal authority. AutoFolio/current robust-selector comparison and independent reproduction remain mandatory top-tier gates.
