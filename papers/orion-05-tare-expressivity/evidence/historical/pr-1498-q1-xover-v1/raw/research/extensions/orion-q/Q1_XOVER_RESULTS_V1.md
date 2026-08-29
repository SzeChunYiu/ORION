# Q1-XOVER — exact crossover/resource evaluation over the frozen R6 stack (V1)

Scope: `EXACT_CROSSOVER_RESOURCE_EVALUATION_OVER_FROZEN_R6_STACK__NO_NEW_THEOREM_AUTHORITY`.
This document is authored from the machine receipts
(`Q1_XOVER_RESULTS_V1.json`, `Q1_XOVER_TIMING_V1.json`) per
`Q1_XOVER_PROTOCOL_V1.md` §Outputs. It carries the crossover statement
ORION-05 cites. Protocol sha256 `6eded50c…` is embedded in the receipt.

## Runs

| Run | LUNARC job | Source commit | Verdict |
|-----|------------|---------------|---------|
| 1 | 3544037 | 0b9d0d3f (protocol + runner freeze) | RUN_INCOMPLETE |
| 2 (determinism-checker repair: per-family rng reseed in the double-run) | 3544067 | 24c3e503 | RUN_INCOMPLETE |

Both runs completed on the `hep` partition (run 2: host `cx04`, python 3.11.5,
numpy 2.3.5, 2 h 32 m). `predictions_digest` is byte-identical across runs
(`2647f71c1667a49eb26a575be582f363400fcc6052ef2c2500791ef0d262bb1d`), as are all
six prediction outcomes and the verdict: run 2 reproduces run 1 exactly. The
receipt's own determinism gate (independent double run of the n<=3 core,
per-family reseeds) reports `equal: true`
(projection `fb5df44119e1466777661c7fb44e2e86ded4fd453474cd6bc99a55a91e68d6c7`
both passes).

## Verdict and prediction outcomes

Recorded verdict: `RUN_INCOMPLETE`, retained here exactly as the runner emitted
it. Every integrity gate passed (mode-`x` outputs, module hashes embedded,
in-memory-only guard extension, all witnesses re-verified).

The protocol defines `RUN_INCOMPLETE` as "infrastructure/budget failure after
one revival attempt". Both halves of that definition are recorded here rather
than resolved:

- **Budget precondition — satisfied.** `P6_feasibility_rule` evaluated `false`
  solely through its `timeouts == 0` clause, with 12/12 sampled n=6 cells
  exhausting the 600 s/cell budget. That is a budget outcome.
- **Revival precondition — not satisfied.** Run 2 (job 3544067) was a
  determinism-checker repair (per-family rng reseed), not a budget revival; no
  revival attempt was made.

This discrepancy is recorded, not adjudicated, and the label stands as emitted.
An earlier draft of this section asserted that `RUN_INCOMPLETE` is "the designed
label for P1–P5 confirmed, P6 refuted" and "not an infrastructure failure"; the
protocol's outcome space does not say that, and the claim is withdrawn. See
"P6 outcome — coverage accounting" below, and #1509.

| Prediction | Statement | Outcome |
|------------|-----------|---------|
| P1 all-size theorem | every executed direct A_DXX cell has `C_Dxx == C_DP` | **TRUE** (372/372 EXACT cells, zero cost mismatches) |
| P2 sandwich | `C_DP <= C_Dxx <= C_Dplus` and `C_DP <= C_R6L` everywhere | **TRUE** (all 384 rows) |
| P3 family-size identity | active-core family == unrestricted iff n<=2; strict subset for 3<=n<=20 | **TRUE** (729==729 at n=1, 11390625==11390625 at n=2; 2176782336 < 62523502209 at n=3) |
| P4 witness support | every verified A_DXX witness has six-frame support total <= 12 | **TRUE** (all witnesses verified; support within bound) |
| P5 R6Q identity on fresh subject | `C_DP == min(C_R6L, C_Dplus, f_B)` on all 15 fresh matchings with matching regime labels | **TRUE** (chemistry H4/N2 and fresh-subject cells: all cost matches, all regime matches, all dxx pinches equal) |
| P6 feasibility rule | direct A_DXX attempted iff n<=6; chemistry/fresh cells record `A_PRIORI_INFEASIBLE_N_GT_6` / containment pinch | **`false` as recorded** — reached via the evaluator's `timeouts == 0` clause; all 12 n=6 cells hit the 600 s/cell budget (0 executed). See coverage accounting below. |

## Crossover table (frozen config: seed 20260827, panel 128 instances/family)

Direct exact search completed **every** instance at 1<=n<=5 (372/372 EXACT)
and **no** instance at n=6 (12/12 TIMEOUT at `dxx_budget_s=600`).

Per family and n: distinct cost values over the cell's instances
(critical = instances with `C_Dplus > C_DP`, i.e. the D+ bound alone is
insufficient):

- `uniform`: n=1 C=2–5 (crit 0); n=2 C=5–9 (crit 8); n=3 C_DP=5–12, C_R6L=6–14,
  C_Dplus=6–14 (crit 16); n=4 C_DP=11–16, C_R6L=12–18 (crit 15); n=5 C_DP=15–21,
  C_R6L=16–22 (crit 8); n=6 C_DP=19–25, C_R6L=20–26, C_Dplus=19–26, A_DXX
  TIMEOUT (crit 3). Critical total 50.
- `commuting_symmetric`: n=1 C=3 all bounds equal (crit 0); n=2 C_DP=4–9,
  C_R6L=4–10 (crit 13); n=3 C_DP=7–12, C_R6L/D+=7–13 (crit 8); n=4 C_DP=12–18,
  C_R6L/D+=12–19 (crit 12); n=5 C_DP=11–19, C_R6L/D+=12–20 (crit 7); n=6
  C_DP=22–30, C_R6L=23–31, C_Dplus=23–31, A_DXX TIMEOUT (crit 4). Critical
  total 44.
- `lowweight`: n=1 C=2–5 all equal (crit 0); n=2 C=5–9 all equal (crit 8);
  n=3 C_DP/D+/Dxx=7–11, C_R6L=7–12 (crit 9); n=4 C_DP/D+/Dxx=7–12, C_R6L=7–13
  (crit 5); n=5 C_DP/Dxx=9–13, C_R6L/D+=10–13 (crit 4); n=6 C_DP/D+=10–12,
  C_R6L=10–12, A_DXX TIMEOUT (crit 1). Critical total 27.

DP witness frame support on the n=1 commuting cells: 6 (min==max), i.e. the DP
referee's witnesses are frame-supported and unbounded a priori, as predicted.

## Crossover statement (for ORION-05)

For the frozen ordered antipermuting wt<=2 grammar over the R6 stack: exact
direct verification (A_DXX) is feasible for every sampled instance through
n=5 at a 600 s/cell budget on LUNARC `hep` hardware, with the all-size theorem
`C_Dxx == C_DP` holding on every executed cell and the sandwich
`C_DP <= C_Dxx <= C_Dplus`, `C_DP <= C_R6L` holding on all 384 rows. At n=6
direct exact search exceeded the budget on all 12 sampled instances, while the
DP referee and both analytic bounds remained cheap. The feasibility crossover
for exhaustive direct verification therefore lies strictly between n=5 and n=6
under this budget; the DP/R6L/D+ certificates continue to cover all n. No DP
acceleration claim is made.

## P6 outcome — coverage accounting

**Recorded value: `prediction_outcomes.P6_feasibility_rule = false`.** That is
the evaluator's output; it stands unmodified, and nothing in this section
re-evaluates it.

`evaluate_predictions` computes P6 as a two-clause conjunction: (i)
`timeouts == 0` across the panel, and (ii) for any cell with
`n > DIRECT_DXX_MAX_N`, a status of `A_PRIORI_INFEASIBLE_N_GT_6` or
`CONTAINMENT_PINCH_EQUAL_ENDPOINTS`. In this run:

- Clause (i) is **false**: 12 timeouts — the 4 sampled n=6 instances in each of
  the three families.
- Clause (ii) **never fires**: panel cell `n` values are `[1..6]` and
  `DIRECT_DXX_MAX_N = 6`, so no panel cell satisfies `n > 6`.

The recorded `false` is therefore produced entirely by clause (i). No cost
mismatch, witness failure, or bound violation occurred; the failing clause is
resource exhaustion at the budget frontier.

**Coverage limit on the registered statement.** P6 is registered as "direct
A_DXX attempted iff n<=6; chemistry/fresh cells record
`A_PRIORI_INFEASIBLE_N_GT_6` (or containment pinch where endpoints are equal)".
Clause (i) has no counterpart in that text, and clause (ii) is evaluated over
`panel` rather than over the chemistry/fresh cells the text names — which in
this receipt sit at n=8 (`H4`) and n=12 (`N2`, `fresh_subject`). The registered
structural claim was thus **not evaluated in the regime where it applies**. For
the record, those cells carry 30/30 `CONTAINMENT_PINCH_EQUAL_ENDPOINTS` and
`fresh_subject` reports `all_dxx_pinched_equal: true`. That is recorded as
coverage information only; it is **not** a re-evaluation of P6, which remains
`false` as emitted.

Whether the divergence warrants a corrected re-emission is deferred to #1509
(defect-only frozen rerun, requiring external authorization) and #1508 (guard
asserting each prediction's evaluator matches its registered statement). Neither
is actioned here: the protocol and the runner are both hash-pinned inside this
receipt (`protocol_sha256`, `integrity.module_hashes`), so V1 cannot be amended
in place — any correction must emit a new receipt and retain V1 as provenance.

**The empirical finding is independent of the labelling question and stands as
recorded:** exact direct A_DXX exhausts the 600 s/cell budget at n=6 on 12/12
sampled instances, against 372/372 completing at n<=5.

Consumers note: in this receipt `verdict` and `prediction_outcomes` describe the
outcome differently, so a tool keying on **either field alone** will get a wrong
answer about this study. Read both and reconcile.

## Integrity receipts

- `guard_extensions`: committed `r6p.EXPECTED_PAIR_COUNTS` covers n in {1,2,3}
  (6/120/666); the runner independently recounted the ordered wt<=2
  anticommuting pair counts for n=4..6 (1968/4350/8136), asserted n=4 equals
  `r6s.PAIR_COUNTS_SUPPORT2[4]=1968`, and set the recounted values in memory
  only — the committed file is untouched.
- Module hashes for every registered `research/extensions/orion-q/` module
  imported at runtime are embedded in the receipt; imports did not modify them.
- Outputs written mode `x`; source archive sha256
  `5dcaab2daa86c6436995a40ba13b03cc5a2e0ef1eb689e0342436466b62f9e10` recorded
  in `SUBMISSION.json` before submission and re-verified by the runner.
- Receipt sha256 `05eb59f6635ebccd8ebcebc79f3b9646aab6fce1d9852735c67d01f9cd3821f1`
  (timing receipt `1949a1174c318a643cbe47740438f22f25ff4db96e69dac0e44ffbb4e66bd4b7`).
- Job logs archived under `development/q1-xover-lunarc-2026-08-27/`
  (runs 3544037 and 3544067).

## Claim boundary

Exact crossover/resource table for the frozen grammar only; no DP acceleration
claim; active-core wall-clock losses are reported as losses; registered modules
imported unmodified.
