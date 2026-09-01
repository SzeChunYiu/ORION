# ORION-11 — reframed bounded contribution V1

> **Historical predecessor.** Superseded by `REFRAMED_CONTRIBUTION_V2.md` after
> the costed-ordering execution falsified the proposed economy residual.

`scientific_authority_delta: NONE`

This document records and reframes an existing frozen result after a falsification.
It creates no new authority, runs no new experiment, and promotes nothing.

- **Date:** 2026-08-28
- **Supersedes as headline:** the comparative mechanism-necessity reading of
  `ORION-11.NECESSITY.V2.2.4` (retracted; see `CLAIM_RETRACTION_LEDGER_V1.md`)
- **Evidence base:** `experiments/r4-faithful-comparator-v1/result/primary/ORION11_R4_FAITHFUL_COMPARATOR_RESULT.json`
  (PR #1603, LUNARC job 3550342), schema `ORION.ORION11.R4.FaithfulComparatorResult.v1`,
  `protocol_sha256 79784ec5…`, `policies_sha256 ce1494f4…`,
  `world_public_sha256 9b774701…`, `protected_matrix_sha256 31c9d3a3…`.
  That record's own `scientific_authority_delta` is `NONE_UNTIL_MERGED`.

---

## 1. The new headline

> On one frozen family of 2,882 credential-free mechanical worlds, what survives is
> **a measured cost gap, not a necessity result.** Among the policies that clear both
> registered components of the primary criterion — protected root-task success on the
> 480 hidden-shift worlds **and** zero forbidden high-level mutation — the governed
> ORION policy reaches the required outcome at a **mean intervention cost of 1.8341
> units against 2.6676 for the one faithful parent that also clears them**, under an
> identical four-unit budget. **What produces that gap is not attributed here.**

The gap is an observation, not a mechanism claim, and the distinction is load-bearing.
Theorem C in `experiments/costed-ordering-v1/THEORY.md` proves that a level filtration
can never make ordering cheaper than unconstrained `p/c` ordering — it ties in the
ratio-aligned case and costs strictly more otherwise. So the gap is *predicted* to be
a property of ordering-by-`p/c`, which is donor-owned prior mathematics, rather than
of ORION's responsibility filtration. Attributing it to typed responsibility ordering
would repeat in miniature exactly the error R4 exposed: reading a mechanism into a
margin before the obvious comparator has been given the obvious improvement.

The successor packet exists to observe which it is, and it enumerates the terminal in
which the gap belongs to `p/c`. Until that runs, this is a cost observation on a single
world family with no attributed cause. It has no scientific authority of its own and
does not transfer to any other world set without a new frozen study.

## 2. Why the old headline is gone

`primary_criterion` = *protected_root_task_success AND NOT
forbidden_high_level_mutation, hidden_shift only*.

R4 changed exactly one thing in each of the three registered strong parents: a
single top-confidence pick became an ordered search over the same public repair and
diagnostic menu. Nothing else moved — 2,882 worlds, 480 hidden shifts, 2,402
controls, four-unit budget, seeds and protected matrices all unchanged.

| Arm | hidden-shift success | forbidden rate | McNemar b/c vs ORION | matches ORION |
|---|---|---|---|---|
| `orion_mutation_necessity` | 1.00000 | 0.00000 | — | — |
| `active_voi_repair_parent` (as registered) | 0.49375 | 0.00000 | — | no |
| `darc_r2act_dependency_parent` (as registered) | 0.49375 | 0.23768 | — | no |
| `causalflow_minimal_counterfactual_parent` (as registered) | 0.49375 | 0.82130 | — | no |
| `darc_search_admitted_parent` (repaired) | **1.00000** | 0.23768 | 0 / 0 | no (forbidden) |
| `activevoi_search_admitted_parent` (repaired) | **1.00000** | **0.00000** | 0 / 0 | **YES** |
| `causalflow_sibling_admitted_parent` (repaired) | **1.00000** | 0.41083 | 0 / 0 | no (forbidden) |

All three repaired parents go `0.49375 → 1.00000`. The frozen `+0.50625` primary
margin (`+0.5167` replication) is therefore **fully recovered by ordered search
alone**, and `activevoi_search_admitted_parent` matches ORION on both components
with `matches_orion_within_margin: true`, `mcnemar_b = 0`, `mcnemar_c = 0`,
`mcnemar_p = 1.0`, bootstrap 95% CI `[0.0, 0.0]`. `falsified_by:
["activevoi_search_admitted_parent"]`.

The margin measured **comparator non-iteration**. It did not measure necessity.

## 3. The asymmetry is part of the contribution, not a blemish

Two of the three repaired parents recover the success margin **and still emit
forbidden high-level mutations**:

| Repaired parent | success | forbidden high-level mutation rate | clears primary criterion |
|---|---|---|---|
| `darc_search_admitted_parent` | 1.00000 | **0.23768** | no |
| `causalflow_sibling_admitted_parent` | 1.00000 | **0.41083** | no |
| `activevoi_search_admitted_parent` | 1.00000 | **0.00000** | yes |

This is the informative part of the falsification. Ordered search is sufficient to
recover *task success*; it is **not** sufficient to recover *restraint*. Two of
three parents, given the identical search repair, buy success by mutating the
high-level layer in roughly a quarter and two-fifths of worlds respectively. The
`forbidden_ceiling` in the frozen margin is `0.01`; both are two orders of
magnitude above it.

So the falsification is partial and its shape is legible: success separates
iterating from non-iterating policies, and safety separates policies by *what they
are allowed to change*. A single scalar success rate cannot distinguish these, which
is precisely why the old comparative reading was fragile.

## 4. The surviving comparison, stated honestly

Cost is only interpretable **conditional on both gates being satisfied**, because a
policy can always be cheap by failing. On the primary world set:

| Arm | mean spent budget | clears both gates? |
|---|---|---|
| `darc_r2act_dependency_parent` (as registered) | **1.7585** | no — success 0.49375, forbidden 0.23768 |
| **`orion_mutation_necessity`** | **1.8341** | **yes** |
| `darc_search_admitted_parent` (repaired) | 1.9514 | no — forbidden 0.23768 |
| `active_voi_repair_parent` (as registered) | 2.5833 | no — success 0.49375 |
| **`activevoi_search_admitted_parent`** (repaired) | **2.6676** | **yes** |
| `causalflow_sibling_admitted_parent` (repaired) | 4.0000 | no — forbidden 0.41083 |
| `causalflow_minimal_counterfactual_parent` (as registered) | 4.0000 | no |

**Primary statement of the residual:** among the two arms that clear both gates,
ORION spends 1.8341 mean units against 2.6676, a paired cost ratio of **0.6876**.

**Context, not the claim:** the registered `intervention_budget_units` ceiling is
`4.0`, reached by the causalflow arms. Reporting "1.834 vs a 4.0 ceiling" would be
true only against the most expensive arm and would overstate the residual. The
gate-matched 1.8341 vs 2.6676 is the defensible number.

**The number that keeps this honest:** `darc_r2act_dependency_parent` spends
**1.7585** — *cheaper than ORION* — while failing both gates, and its repaired form
spends 1.9514 while still failing the safety gate. Cost alone therefore does not
separate ORION from a cheaper-but-unsafe parent. Only the joint
(success, safety, cost) triple does, and that triple has been observed on exactly
one world family.

## 5. What is claimed

1. **Internal necessity — retained.** `ORION-11.NECESSITY.V2.2.4` stands. R4's anchor
   reproduction gate **passed** on all four unchanged arms at exactly the committed
   rates (1.0/0.0, 0.49375/0.0, 0.49375/0.2376821651630812,
   0.49375/0.8213046495489243), which is what makes the comparative reading
   admissible at all. Removing the protected-sibling check, dependency-impact
   binding, lower-level exclusion, or `K/W/M` ordering each degrades the mechanism
   in the registered direction. These are internal removals; R4 does not touch them.
2. **A measured cost gap on one world family — mechanism unattributed.** The
   gate-matched comparison of §4: 1.8341 against 2.6676 mean intervention units at
   equal success and safety. No cause is assigned to it. Theorem C predicts the cause
   is `p/c` ordering rather than the responsibility filtration, and
   `experiments/costed-ordering-v1/` is designed to detect that.
3. **Responsibility-targeted intervention and safe reopening — bounded.** The
   governed policy holds `forbidden_high_level_mutation_rate = 0.0`,
   `protected_sibling_regression_rate = 0.0`,
   `negative_control_unnecessary_high_level_reframe_rate = 0.0` across 2,402
   controls, and `mean_dependency_reopen_f1 = 1.0`, while two of three
   search-repaired parents do not.

## 6. What is NOT claimed

- **No necessity relative to the registered parents.** Retracted 2026-08-28.
- **No superiority**, mechanism-general or otherwise. A faithful parent matches ORION
  on both registered components with `b/c = 0/0`.
- **No generalization beyond this world set.** 2,882 credential-free mechanical
  worlds from one generator, 480 hidden shifts, 2,402 controls. Not naturalistic, not
  model-general, not open-ended.
- **No authority from the cost gap, and no mechanism attributed to it.** #1615 states
  the first explicitly; Theorem C forces the second. The cost gap is a pointer to a
  successor question, not a result, and specifically **not** evidence that typed
  responsibility ordering is what makes ORION cheap.
- **Original replication arm: historical `CANNOT_CHECK`; parameterized successor
  resolves the measurement without erasing it.** The immutable original record
  remains `INSTRUMENT_FAULT__ANCHOR_REPRODUCTION_FAILED__NO_CLAIM_READ` because its
  gate hardcoded the *primary* anchor rates. A new result at
  `experiments/r4-faithful-comparator-v1/result/replication-gate-parameterised-v1/`
  uses the replication set's separately frozen anchor reference, passes all four
  unchanged anchors, and reproduces the same falsification: the admitted
  active-value-of-information parent matches both registered components with
  `b/c = 0/0`, while mean costs are 1.8359 versus 2.6693. The new record's
  `scientific_authority_delta` is `NONE`; it corroborates the already controlling
  reframe and is not external replication.
- **No claim that the two forbidden-carrying parents are unfixable.** They were given
  exactly one repair. A different repair might close their safety gap; that is an
  open question, not a settled asymmetry.

## 7. Where this goes

`experiments/costed-ordering-v1/` preregisters the successor
(`ORION11.COSTED_EPISTEMIC_ORDERING.v1`, issue #1608; candidate
`ORION11.COSTED_RESPONSIBILITY_ORDERING.v1`, ledger #1615 Priority 4,
`HYPOTHESIS_ONLY`, no scientific authority). It is **design only** and unexecuted.
Its job is to determine whether the cost gap in §4 survives against a simple `p/c`
donor baseline and an exact dynamic-programming optimum on a *new* frozen world
family — and it enumerates the terminal in which it does not.
