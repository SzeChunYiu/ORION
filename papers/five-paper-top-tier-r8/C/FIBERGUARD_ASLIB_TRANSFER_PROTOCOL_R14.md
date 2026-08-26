# FiberGuard R14 — prospectively frozen held-out transfer protocol

Date frozen: 2026-08-26

Source parent: `6c23a3fe4ccf415bc3a73794878d72583ed48eb2`

Status at this commit: **protocol and executable frozen before any R14 aggregate outcome is read**. The positive R11 same-corpus result and the R12/R13 deterministic/randomized adaptive theorems are inherited evidence, not R14 transfer evidence.

## Scientific question

Can a representation and robust solver policy chosen from training outcomes retain decision value on instances whose runtimes were not available during representation selection or policy fitting?

R11 established an exact corpus-complete static optimum on pinned ASlib `SAT12-ALL`. That result is not a generalization result. Exact equality fibres built from continuous-valued features may be almost singleton, and a policy can appear oracle-like on a training singleton while having no justified action for a new signature. R14 therefore treats unseen or insufficiently supported cells as a first-class fallback event rather than silently borrowing the held-out label.

## Frozen upstream subject

- repository: `coseal/aslib_data`;
- commit: `551b22beef8df17de59286b4822ef720e0aa4d6f`;
- scenario: `SAT12-ALL`;
- `cv.arff` Git blob: `63d3922abaae67e690f31a74c7daa1be6981fb70`;
- algorithm/feature/value/cost/status blobs remain those bound by R11.

The solver portfolio, 1200-second cutoff, PAR10 treatment, repetition aggregation, feature-step dependency graph, feature-cost fallback, and statewise virtual-best oracle baseline are unchanged from R11.

## Two outcome-blind split schemes

### A. Source-supplied CV

Use exactly `cv.arff` repetition 1 and folds 1–10. For outer fold `f`, all instances with fold `f` are held out. No held-out runtime may influence the representation, quartile thresholds, fallback action, cell action, or support decision for that fold.

### B. Balanced path-prefix groups

Define the group key as the first four slash-delimited components of the immutable instance identifier. Sort groups by decreasing size, then SHA-256/name tie break, and assign each group greedily to the currently lightest of ten folds. This uses identifiers and group sizes only, never algorithm runtimes or feature outcomes. A group cannot cross folds.

This split is a leakage-resistant structural control. The first-four-component prefix is **not** claimed to be domain-expert family ground truth, so a positive result still does not establish universal family transfer.

## Frozen representations and policies

Every policy uses the same total-excess loss

`feature acquisition time + selected-solver PAR10 runtime - statewise virtual-best PAR10 runtime`.

The absolute feature charge and terminal action regret therefore share both one unit and one statewise oracle baseline.

### Exact-value control

The R11-selected step set `{Pre,lobjois}` is evaluated with its exact feature values and runstatus. It is a deliberately post-selection control: the step set was discovered using the full R11 corpus. On an outer fold, its solver map is nevertheless fit from outer-training runtimes only. A test signature absent from training uses the no-feature fallback.

### Quartile transfer map

For each outer fold and each raw numeric feature, compute nearest-rank training quartiles at 25%, 50%, and 75%. Test values are binned with those frozen thresholds; missingness remains a separate symbol and feature-step runstatus remains in the signature. No test runtime is used to set thresholds.

A cell-specific action is permitted only when the outer-training cell has at least two members. Otherwise the policy uses the outer-training no-feature robust action. This support threshold is fixed at two before outcomes.

### Training-selected primary arm

Enumerate all 513 dependency-closed feature-step sets. On the outer-training data, fit the support-gated quartile policy for each set. Select the set minimizing exact training robust total excess; ties prefer fewer steps and then the lexical step tuple. Refit nothing on the test fold: apply the frozen thresholds, cell map, and fallback directly.

## Registered arms

For each split and fold:

1. no features;
2. R11 `{Pre,lobjois}` with exact values and support one;
3. R11 `{Pre,lobjois}` with training quartiles and support two;
4. all feature steps with training quartiles and support two;
5. the training-selected dependency-closed quartile representation with support two.

The virtual-best solver remains a descriptive oracle only.

## Exact authority theorems

### Theorem R14.1 — empirical fibre values are lower bounds, not upper bounds

Let `S subseteq X` and let `F_y(S)` be the observed states in representation cell `y`. For deterministic or ex-ante randomized action regret,

`rho(F_y(S)) <= rho(F_y(X))`

whenever the observed cell is nonempty.

**Proof.** Enlarging the adversary's state set cannot decrease the maximum loss of any fixed action or action distribution. Minimizing over policies preserves the inequality. ∎

Thus an exact R11 or training-cell certificate cannot upper-bound an unseen extension of that cell without a separate completeness or outer-set certificate.

### Theorem R14.2 — exact held-out coverage decomposition

For a frozen support-gated policy, partition the held-out fold into rows where a supported training-cell action is used and rows routed to fallback. The exact held-out robust total excess is the maximum of the two subset maxima, with the empty subset omitted.

This decomposition distinguishes two failure modes: action drift inside represented cells and representation-support failure. It grants no distribution-free guarantee; it is an exact finite test receipt.

## Frozen outputs

For every arm, split, and fold, emit:

- selected steps and training robust value;
- quartile-threshold and policy digests;
- training fibre and eligible-fibre counts;
- held-out robust, mean, median, and p95 total excess;
- mean and maximum feature cost;
- seen-signature rate, supported-cell-policy rate, and fallback count;
- one out-of-fold prediction row per corpus instance.

Also emit the source-CV prefix leakage audit and the prefix-group assignment receipt.

## Outcome interpretation

The primary arm survives this tranche only if it strictly improves robust held-out total excess over both no features and all-feature quartile policies on **both** split schemes. A source-CV-only improvement is retained as split-sensitive evidence, not broad transfer. A null or adverse result is retained without changing the representation, support threshold, split, PAR10 convention, or fallback after outcome access.

The exact-value R11 arm cannot independently close transfer because its step set is post-selected. A low supported-cell-use rate is substantive evidence that exact equality fibres fail to transport.

## Authority boundary

A positive R14 result would establish prospectively frozen out-of-fold value on one public ASlib scenario under two declared splits. It would not establish:

- an independently curated external corpus;
- domain-expert family separation;
- a learned neural selector advantage;
- distribution-free or unseen-domain safety;
- deployment value;
- novelty; or
- journal authority.

R12/R13 adaptive and randomized policies remain unexecuted on ASlib until this transfer gate is interpreted. Generic cross-validation, quantile binning, support gating, algorithm selection, and cost-sensitive feature acquisition are donor-owned.
