# ORION22.REGRET_MARGIN_ROBUSTNESS.v1

## Question

When an exact adaptive-state decision has a unique loss-minimizing action, how much perturbation of the action losses can occur before that decision is no longer certified to remain optimal?

## Definitions

For one finite decision class let `A` be the feasible actions and `L(a)` the exact loss. Assume the optimum is unique:

`a* = argmin_a L(a)`.

Define the **decision margin**

`Delta = min_{a != a*} (L(a) - L(a*)) > 0`.

Let a perturbed loss table `L_tilde` satisfy the uniform bound

`|L_tilde(a) - L(a)| <= epsilon` for every `a in A`.

## Theorem 1 — sharp stability radius

If `epsilon < Delta / 2`, then `a*` remains the unique minimizer of `L_tilde`.

### Proof

For any competitor `a != a*`,

`L_tilde(a) - L_tilde(a*)`

`>= (L(a) - epsilon) - (L(a*) + epsilon)`

`= (L(a)-L(a*)) - 2 epsilon`

`>= Delta - 2 epsilon > 0`.

So every competitor remains strictly worse. QED.

## Theorem 2 — the factor one-half is sharp

At `epsilon = Delta/2`, an admissible perturbation can create a tie: increase the optimal loss by `Delta/2` and decrease a nearest competitor by `Delta/2`. For any `epsilon > Delta/2`, the same construction with a slightly larger shift can reverse the ordering.

Therefore no larger universal stability radius follows from the margin alone.

## Corollary 2.1 — portfolio stability radius

For finitely many decision classes `i` with unique margins `Delta_i`, all decisions remain unchanged under a common uniform perturbation bound whenever

`epsilon < (1/2) min_i Delta_i`.

This is an exact worst-case guarantee; no independence or distributional approximation is required.

## Corollary 2.2 — zero regret plus uniqueness is not yet a robustness certificate

A recorded optimum with `actions_attaining_floor = 1` proves that the exact finite table has some positive margin. It does **not** quantify the stability radius unless the nearest-competitor gap is serialized or exactly recomputable.

This distinction matters for ORION-22. The existing observation-regret result reports unique floor attainment on its finite classes, but the committed summary does not expose a per-class `Delta` field. Therefore this theorem does not infer a numeric robustness radius from absent bytes.

## Minimal local completion

For each frozen class, emit without changing the decision rule:

1. `best_action`;
2. `best_loss`;
3. `second_best_loss`;
4. `decision_margin = second_best_loss - best_loss`;
5. exact provenance binding to the action-loss table.

Then the paper can report the classwise radius `Delta_i/2` and the global frozen-panel radius `(1/2) min_i Delta_i`. If the action-loss table cannot reconstruct the second-best value, the correct terminal is `CANNOT_CHECK_MARGIN_FROM_COMMITTED_EVIDENCE` rather than an imputed radius.

## Relation to transfer

This result strengthens internal finite-decision robustness. It does not establish that the same margins occur on an untouched task family, that the loss model is externally correct, or that exact zero regret generalizes. Those remain empirical transfer questions.

## Claim boundary

Earned deductive claim:

> A unique exact decision with margin `Delta` is invariant to arbitrary jointly dependent per-action loss perturbations bounded by any `epsilon < Delta/2`, and this threshold is sharp.

Not earned:

- a numeric ORION-22 panel radius before margins are serialized/recomputed;
- untouched-domain transfer;
- population-level zero-regret authority.

`scientific_authority_delta: NONE`