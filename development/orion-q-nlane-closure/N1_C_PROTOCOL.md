# ORION-Q N1-C frozen protocol — partial applicability + costly verification (fresh re-execution)

Date frozen: 2026-08-21
Lane: ORION-Q N1 (issue #674), family N1-C
Registered design source: issue #674 body ("N1-C — partial applicability + costly verification")
and issue comment 5355071291 (the original N1-C execution record, never committed).
Status of this document: protocol frozen BEFORE the result-bearing run of
`research/extensions/orion-q/nlanes/n1c_costly_verification_voi.py`.

## Standing

Fresh re-execution of the registered design: 20,000 held-out episodes, 40 opaque candidate method
schemas per episode, verifier-cost budget 6, applicability hidden until verification, prior
failures either current-context (strongly adverse) or stale (reopenable and positively
informative). The thread's original world parameters were not recorded numerically; the generative
parameters below were selected in a pilot **on a pilot seed distinct from the frozen evaluation
seed**, for world-validity only (nontrivial cheapest-first rate; prune not materially better than
cheapest). The ordinal outcome gates below were fixed from the registered design, not from pilot
deltas. Numbers from comment 5355071291 are prior registration, not this run's data. Diagnostic
authority only.

## Frozen generative world (per candidate, i.i.d. within episode)

- Verification cost `c in {1,2,3}` with probabilities `{0.5, 0.3, 0.2}`.
- Visible quality feature `q in {LOW, MED, HIGH}` with probabilities `{0.5, 0.3, 0.2}` and base
  applicability `p0 = {0.03, 0.15, 0.50}`.
- Prior failure record with probability by cost: `P(record | c=1)=0.6, c=2: 0.4, c=3: 0.25`
  (cheap candidates are historically over-tried).
- Given a record, stale (context-changed) with probability `0.55`; otherwise current-context.
- True applicability: fresh `p0`; record+current `0.02*p0`; record+stale `min(0.92, 2.4*p0)`.
- Hidden gold applicability bit drawn once per candidate; owned by the evaluator; readable only by
  spending verifier budget (registered control).
- Episode play: a policy ranks candidates from its visible view, verifies in rank order, skipping
  candidates whose cost exceeds remaining budget; stops on first verified-applicable (solve) or
  when nothing affordable remains. Unverified candidates remain `UNKNOWN` (preserved and counted;
  registered control).

## Frozen sizes and seeds

- Training episodes for learned policies: 5,000. Evaluation episodes: 20,000 (held-out).
- Evaluation/generation seed: `numpy.default_rng(20260821)` consuming train stream then eval stream
  in that fixed order. Bootstrap seed: `20260822`, 2,000 paired resamples, percentile 95% CI.
- Pilot seed used only for world construction: 999001 (never reused here).

## Arms (registered baselines)

1. `CHEAPEST_FIRST`: rank by cost ascending (deterministic index tiebreak).
2. `PERMANENT_PRUNE`: cheapest-first over record-free candidates only (raw negative memory treated
   as permanent refutation — implicit refutations without verification are counted and reported).
3. `LEARNED_UNSCOPED`: cell-mean applicability estimated on training episodes over cells
   `(q, has_record)`; rank by `p_hat / cost`. Same features as typed EXCEPT the scoped
   stale/current relation (registered ablation).
4. `LEARNED_TYPED_SCOPED`: cell means over `(q, {fresh, current, stale})`; rank by `p_hat / cost`.
5. `IDEAL_VOI_PARENT` (donor-complete, first right of refusal): true generative applicability with
   the same typed facts; rank by `p / cost` (greedy expected-success-per-unit-cost index).

## Metrics

Per arm: solve rate, mean verifier cost, mean verifications, false-escalation rate (verifications
spent on current-context-failure candidates; registered), mean UNKNOWN candidates remaining.
Paired per-episode deltas: typed − unscoped and typed − VOI solve rates with bootstrap 95% CIs.

## Prespecified gates

- `G1_WORLD_NONTRIVIAL`: `0.30 <= cheapest_solve <= 0.85`.
- `G2_BUDGET_BINDING`: full verification of all 40 candidates is unaffordable in 100% of episodes
  (min possible total cost 40 > budget 6; asserted).
- `G3_PRUNE_NO_GAIN`: `prune_solve <= cheapest_solve + 0.01` (permanent negative memory does not
  materially help).
- `G4_TYPED_OVER_UNSCOPED`: paired typed−unscoped solve delta > 0 with bootstrap 95% CI lower
  bound > 0.
- `G5_VOI_PARENT_MATCH`: typed−VOI solve delta 95% CI contains 0 or |delta| <= 0.01.

## Terminal rule (frozen)

- G1/G2 fail: `N1C_WORLD_INVALID`.
- G4 passes and G5 holds: `N1C_TYPED_FAILURE_STATE_VALUE__VOI_POLICY_PARENT_SUFFICIENT`
  (the registered dual outcome: bounded P9 typed/scoped failure-state positive; P10 policy-level
  negative — the allocation policy itself is closed by the donor-complete VOI parent).
- G4 passes and typed beats VOI (CI lower bound > 0.005): `N1C_VERIFICATION_ALLOCATION_VALUE`.
- G4 fails: `N1C_VOI_PARENT_SUFFICIENT` (plain negative).

## Claim boundary

Exact-synthetic scope only; the positive (if earned) is for typed scoped failure STATE as decision
information, never for a new verification POLICY, and grants no P10, novelty, or real-quantum
authority. Receipt line `ORIONQ_N1C_COSTLY_VERIFICATION=<canonical sorted json>`; pretty receipt at
`research/extensions/orion-q/nlanes/N1_C_COSTLY_VERIFICATION_RESULTS.json`.
