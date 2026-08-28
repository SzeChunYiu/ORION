# ORION-05/06 negative-revival R1 execution receipt (2026-08-28)

Lane: claude/r1-revival-orion05-06-20260828 (absorbs codex/revive-orion05-06-20260827 at 506b84e6: frozen protocols + harnesses, merged over origin/main 3cf53d6e). The codex lane froze protocols and built harnesses but executed nothing; this packet executes all three frozen revival protocols on LUNARC and records receipts.

## Executions

1. ORION-05 R13 parent-certificate ordering — Slurm 3550256 (cn063), 24/24 held-out cells, protocol hash 41559a96..., raw attempts sha256 216d67c4...
2. ORION-05 XOVER one-cell budget revival — Slurm 3550257 (cn063), frozen cell uniform/n=6/instance 0, 1800 s budget, legacy direct D++ unchanged.
3. ORION-06 negative coverage recompute — pure verification, exit 0.

## ORION-05 amended verdicts

| Claim (recorded negative) | Old verdict | Failure stage attribution | Lever exercised | New verdict | Evidence |
|---|---|---|---|---|---|
| R12 support-two production value (ROUND_2_NULL: 6/6 full-subject timeouts at 120 s) | ORION05_R12_EXACT_BUT_NO_PRODUCTION_VALUE | CANDIDATE_ENUMERATION_ORDER (exhaustive order starves the first valid candidate) | PARENT_CERTIFICATE_GUIDED_FIRST_CANDIDATE_ORDERING, parent fully charged | IMPROVED — completion-only: 24/24 held-out cells valid support-two witness at parent exact cost; hybrid/parent wall ratio 1.0023-1.0033 => zero standalone value; R12 production null RETAINED | rounds/r13-parent-certificate-ordering/result/ |
| Q1 XOVER panel (12/12 n=6 cells timed out at 600 s) | RUN_INCOMPLETE | EXHAUSTIVE_SEARCH_COMPUTE_BUDGET | MATCHED_BUDGET_EXTENSION 600 s -> 1800 s on the lexicographically first frozen cell | RETAINED_NEGATIVE — D++ timed out again at 1800 s (wall 1800.11 s, peak RSS ~1.4 GiB) while the parent DP solves the same cell at C=19; one-cell budget evidence, not a universal infeasibility proof; whole-panel RUN_INCOMPLETE immutable | rounds/xover-budget-revival-v1/result/ |
| Q1-C literature subtraction | NOVELTY_NOT_ESTABLISHED (bounded same-lane search cannot establish novelty; submission-date rerun required) | SEARCH_DATE/COVERAGE | bounded submission-date rerun (3 angles, 2026-08-28): TARE still v4, no exact-solver/sharp-threshold equivalent, no Symphony-line update | IMPROVED-CONDITIONAL — theorem-level residual now backed by R11 theorem + re-dated rerun with no direct equivalent; programme-level novelty authority still NOT ESTABLISHED (independent review required) | evidence/convergence-v1/Q1_C_LITERATURE_SUBTRACTION_RERUN_20260828.json |
| Q1V2-C4 uniform support-one sufficiency | EXACT_COUNTEREXAMPLE / REFUTED (C_DP=5 < C_D+=6 at R6O n=2 idx 16) | none — exact witnessed counterexample, no estimator/statistic/sample defect | verification only (witness cross-check retained) | RETAINED_NEGATIVE (load-bearing for R6S support-two and R11) | CLAIM_LEDGER_V2.md row Q1V2-C4 |

## ORION-06 amended verdicts

| Claim (recorded negative) | Old verdict | Failure stage attribution | Lever / disposition | New verdict | Evidence |
|---|---|---|---|---|---|
| R2 known-operator transfer | negative (exact 1.0 tie, all four folds, held-out support fully seen) | exact tie = donor absorption; mechanistically stopped inside frozen claim | none possible without new donor-blind task family | RETAINED_NEGATIVE | revival/ORION06_NEGATIVE_COVERAGE_RESULT.json |
| R3B joint obligation binding | negative (1.0 on 4800 exact-synthetic; local-view candidate cannot) | same — exact absorption | none | RETAINED_NEGATIVE | same |
| N1C typed failure state | negative (typed scoped learner ties ideal VOI parent, paired delta 0.0) | same | none | RETAINED_NEGATIVE | same |
| R4C H2 regime-limited | regime-limited negative | explicit next attack (Restore/outer-SELECT Pareto accounting) has no frozen executed successor | UNFINISHED (per frozen rule: never UNSOLVABLE without mechanistic proof) | same |
| R5B proof outer replay | sign-flips across projections | named controlled-SELECT-aware new-successor attack unexecuted | UNFINISHED | same |
| R6I exact rank-2 | zero strict wins both subjects | method-language inadequacy localized | UNFINISHED | same |
| R6K exact restore factor | zero strict wins after joint Tag/Restore factoring | method-language inadequacy localized | UNFINISHED | same |
| Cross-domain general-method effectiveness | CANNOT_CHECK | EXTERNAL_COMPARATIVE_EVALUATION (no admitted non-quantum programme with matched budgets exists) | precondition external | CANNOT_CHECK (does not block bounded single-programme record) | same |

Denominator recompute exact: 51 = 23 included + 28 excluded, 13 asserted edges, 7-node standalone set matched exactly.

## Boundary

scientific_authority_delta NONE; no threshold retuned; no adverse record erased; original whole-panel XOVER verdict immutable; no freeze; no merge.
