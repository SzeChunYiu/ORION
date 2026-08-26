# ORION-22 selection-sufficiency theorem V1

**Status:** theorem/falsification contract, frozen before the new abstract-state checker is executed on this branch.

This result is a scientific interpretation of the already-bound NR-13 sequence. It does **not** alter the parent `P12_TRANSFER_ALLOCATOR_V1`, the BROKEN robustness receipt, the price-aware successor, any price regime, case, budget, or success gate.

## 1. Setup

For a finite set of candidate structures `s`, let

- `c_s >= 0` be declared construction weight/cost;
- `r_s >= 0` be the serving charge when `s` is not materialized;
- `t_s >= 0` be the serving charge when `s` is materialized;
- `p_b > 0` and `p_s > 0` be build and serve prices;
- `B >= 0` be the nominal construction budget;
- `X` be a selected subset with `sum_{s in X} c_s <= B`.

The charged objective is

`J(X) = p_b * sum_{s in X} c_s + p_s * [sum_{s in X} t_s + sum_{s not in X} r_s]`.

Define marginal materialization value

`v_s = p_s * (r_s - t_s) - p_b * c_s`.

## 2. Theorem T1 — objective reduction

For every budget-feasible `X`,

`J(X) = p_s * sum_s r_s - sum_{s in X} v_s`.

Therefore minimizing the charged objective is exactly equivalent to maximizing

`sum_{s in X} v_s`

subject to

`sum_{s in X} c_s <= B`.

**Proof.** Expand the definition of `J`, add and subtract `p_s * sum_{s in X} r_s`, and collect the selected-structure terms. The first term is constant in `X`; the remaining selected term is `-v_s`. No statistical assumption is used. QED.

## 3. Theorem T2 — exact price-aware DP is globally optimal

When declared costs and `B` are non-negative integers, the recurrence

`D(i,b) = max(D(i-1,b), D(i-1,b-c_i)+v_i)` when `c_i <= b`, with the not-take branch retained on ties, returns a budget-feasible subset whose total marginal value is globally maximal. By T1, the selected subset globally minimizes the charged objective.

**Proof.** Induct on the first `i` structures. Every feasible optimum either excludes item `i`, in which case its value is bounded by `D(i-1,b)`, or includes it, in which case the residual subset is feasible at `b-c_i` and its value is bounded by `D(i-1,b-c_i)+v_i`. The recurrence takes the larger bound and both branches are achievable by the induction hypothesis. QED.

The tie rule affects which optimum is returned, not optimal objective value.

## 4. Theorem T3 — exact break-even boundary

If `r_s <= t_s`, then `v_s < 0` for every positive price pair and materializing `s` cannot improve the objective.

If `r_s > t_s`, define `rho = p_s/p_b`. Then

`v_s > 0  <=>  rho > c_s/(r_s-t_s)`.

Thus each unconstrained structure has an exact price-ratio phase boundary. With a shared budget, pair/subset competition can add combinatorial transitions, but every transition is still induced by the same marginal-value objective from T1.

## 5. Theorem T4 — price-oblivious impossibility witness

Fix one case and two positive price regimes `a,b`. If the charged objective has a **unique** optimal subset `X_a` in regime `a`, a unique optimal subset `X_b` in regime `b`, and `X_a != X_b`, then no selector that returns one price-oblivious fixed subset for that case can be optimal in both regimes.

**Proof.** A fixed selector returns one subset `Y`. Optimality under uniqueness requires `Y=X_a` in regime `a` and `Y=X_b` in regime `b`; this contradicts `X_a != X_b`. QED.

This is a falsifiable explanation of the parent robustness failure. It is not a claim that *every* price-oblivious rule must fail on *every* case.

## 6. Frozen checker contract

`check_p12_selection_sufficiency_theorem_v1.py` must be implemented independently of the candidate DP recurrence and must fail closed unless all of the following hold:

1. **Abstract reduced-state exhaustive check.** Enumerate all ordered ledgers with 1–4 items drawn from:
   - declared costs `{1,2,3}`;
   - reason-minus-state certificate differences `{-1,0,1,2,3,4,5}`;
   - price pairs `{(1,1),(2,1),(1,2),(4,1),(1,4)}`;
   - budgets `{0,1,2,3,4,5,6}`.
   For each cell, compare the candidate `price_aware_selection` objective value to an independent exhaustive subset oracle. Ties may choose different subsets but not different objective values.
2. **Mutation sensitivity.** At least three wrong selectors must each be rejected by at least one enumerated witness: price-oblivious declared-cost greedy, positive-value-without-budget, and reversed-sign marginal value.
3. **Bound NR-13 replay.** Execute the committed NR-13 runner and require all 195 successor cells to retain zero regret and the parent to retain BROKEN/BROKEN.
4. **T4 real witnesses.** On the committed 27-case expanded battery, enumerate unique oracle optima from the NR-13 runner and count cases for which at least two regimes have different unique optimal subsets. The count is reported without a pre-specified minimum; zero would refute an empirical T4 witness while leaving the mathematical theorem intact.
5. **No authority escalation.** This theorem establishes optimal selection **conditional on additive exact charge certificates**. It does not make those certificates free, prospective, external, or deployment-valid.

## 7. Interpretation

The parent negative is retained as a mechanism result:

> price-oblivious q-greedy selection is not robust to objective prices and shift on the frozen stress battery.

The successor positive is elevated from a battery-specific observation to a structural law:

> under additive charging with exact per-structure charge certificates, materialization is a budgeted marginal-value optimization problem, and the registered price-aware DP is globally optimal for every finite integer-weight ledger.

The next scientific question is information sufficiency: how much prospective/partial charge information is enough to recover this optimum without reading exact realized charge certificates?
