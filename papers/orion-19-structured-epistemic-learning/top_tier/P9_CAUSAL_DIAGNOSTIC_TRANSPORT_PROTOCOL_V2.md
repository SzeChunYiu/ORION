# P9 causal-diagnostic transport protocol V2 (pre-registered)

**Programme:** #977
**Registration:** frozen before any V2 execution. Stage-1 attribution measurements
(`revive_p9_nr04_stage1_attribution.py`, evidence JSON in this PR) preceded this
registration; **no V2 outcome was observed before this freeze.** The lever
constants below (`R`, seed formulas) are fixed by formula, not tuned to outcomes.
**Predecessor:** `P9_CAUSAL_DIAGNOSTIC_PROTOCOL_V1.md` (SHA-256 `267df46aff7bd5502180524cd96f82b7951a2ae4c1d567e3b53bea6ce3f86015`)
and its receipt — both remain frozen and binding; V2 does not edit, retune, or
relabel any V1 cell, target, cost, gold, or terminal.

## Defect being repaired (one stage)

V1 transports, from the probe side to the protected side, a **single-split point
accuracy** per intervention arm. On the D-A cell the stage-1 attribution measured:

- representation-repair channel: **bitwise lossless** (`cbrt(x^3) == x`, max
  absolute/relative reconstruction error `0.0`, identical fitted coefficients and
  identical probe/protected accuracies to the native standardized representation);
- evaluation channel: single-split binomial sd `~0.0098` vs decision margin
  `|0.96384 - 0.965| ~= 0.0012` — **noise-to-margin ratio ~8.5**;
- re-draw distribution of the repaired arm's protected accuracy: mean `0.9644`,
  sd `0.0095`, and `50.5%` of draws at or above the target.

So the V1 channel transports a Bernoulli(~0.5) realization across a threshold the
data cannot resolve: the D-A prediction/gold mismatch is channel noise, not a
property of any intervention arm. This is lossy **by construction** in V1 and is
the single stage this protocol repairs. Nothing about the arms, targets, costs,
access classes, or responsibilities changes.

## Lever: ensemble-level transport (general mechanism)

The transported quantity becomes the **quality level** of each intervention arm
on each side, estimated as the mean accuracy over `R = 24` pre-registered
stratified partition re-draws of the same fixed dataset, with the access model
re-fitted on each draw's train split:

- digits: for `k = 0..23`, outer split `train_test_split(..., test_size=0.4,
  random_state=20261101+k, stratify=y)`, inner split
  `train_test_split(..., test_size=0.5, random_state=20261201+k, stratify=yrem)`;
  per draw, the full per-arm pipeline (scaler fit on train, representation,
  intervention, access-class fit) is re-executed; transported probe-side level =
  mean over draws of probe accuracy, protected-side level = mean over draws of
  protected accuracy;
- executable cells: deterministic exact functions of the frozen seed ranges
  (`9100..9199` development, `9900..9999` protected); the V2 channel is the
  identity there and levels equal the V1 values exactly.

`R = 24` is one global protocol constant (same status as the V1 registered costs
`8/2/12`); chosen at registration as an order-of-magnitude increase in partition
realizations over V1's single draw at fixed dataset size, the standard
repeated-stratified-resampling variance reduction. No cell-specific constant is
introduced.

## Decision rule (unchanged in form)

Arm reaches target iff transported level `>=` the cell's frozen target (targets
unchanged: `0.965` D-A, `0.95` D-I, `1.0` B-*). Prediction = lowest-registered-cost
arm reaching target on the probe side; protected gold = same rule on the protected
side; else `CANNOT_CHECK` on that side. Generic comparator unchanged.

## Transport-fidelity metrics (reported, not gated)

1. channel sd before (empirical sd of single-draw accuracy across the 24 draws)
   and after (sd of the mean, estimated from disjoint draw-halves);
2. decision-transport agreement: probe-side decision vs protected-side decision
   per cell under V2;
3. decision stability: recomputing both sides' decisions on disjoint draw-halves
   (draws `0..11` vs `12..23`) — agreement required for the stability claim.

## Positive terminal

`P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_SUPPORTED` requires all of:

- every V1 positive-terminal condition evaluated on V2 transported levels
  (diagnostic accuracy `>= 4/5`, strictly above the generic heuristic, `1.0` on
  the three executable families, at least one digits cell correct, false compute
  escalation at least 50% below generic, target reached by every actionable
  prediction, mean registered-cost regret `<= 1.0`);
- **transport stability:** probe-side and protected-side decisions agree on all
  five cells, and both disjoint draw-half decisions agree with the full-draw
  decision on all five cells.

## Boundary

A cell whose repaired level sits genuinely below its frozen target remains
`CANNOT_CHECK` — V2 makes that verdict *measurable and stable*, not different by
construction. If D-A's transported level stays below `0.965`, the cell stays
`CANNOT_CHECK` and the mechanistic reason (level below target at resolvable
precision) is reported. V2 claims a bounded cross-domain causal diagnostic with a
noise-controlled transport channel; no universal LLM diagnostic claim; the
protected Qwen scaling negative
(`LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED`) is not repaired, re-run, or
touched.
