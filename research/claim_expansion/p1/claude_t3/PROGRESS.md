# P1-U-T3 Guard Repair — Progress Notes

Started: 2026-08-21. Branch `claude/papers-1-10-issues-uqrj2o`.

## Task
Three pre-outcome protocol repairs to `research/claim_expansion/p1/gpt_r6/evaluate_native.py`:
1. Class noninferiority files both pair members under `adverse_class`, so the
   `NO_HIGH_LEVEL_REFORMULATION` control stratum is never evaluated.
2. Domain noninferiority has 26 strata of 1-2 episodes -> -0.10 margin is
   arithmetically a zero-loss rule.
3. `_leakage_free` is fail-open on missing key; pair role not in forbidden tokens.

## Status log
- [ ] 0. Orientation / find R4 PRE_OUTCOME_PROTOCOL_REPAIR precedent
- [ ] 1. Reproduce all three defects with numbers (pre-repair record)
- [ ] 2. Write pre-registration: what each repaired guard tests, what makes it fail
- [ ] 3. Repairs + mutation-checked tests
- [ ] 4. Re-run guards, report both readings of the margin
- [ ] 5. Final report

## Notes
(appended below as work proceeds)

---
## Milestone 0 — orientation (done)

**Precedent found.** `PRE_OUTCOME_PROTOCOL_REPAIR__NO_RESULT_AUTHORITY` is the terminal used by
`research/claim_expansion/p1/P1_X_PROTOCOL_V1_AMENDMENT_003.md` (2026-08-19). Its discipline:
- state, at the top of the amendment, whether protected cases were generated and whether
  protected outcomes were accessed *before* the amendment (both "NO" there);
- enumerate the defects that triggered the repair;
- enumerate the repair, one bullet per defect;
- enumerate explicitly the scientific commitments the amendment does **not** change;
- add hostile tests covering all repairs;
- close with the terminal, which carries no result authority.
The R4 half of the precedent is `gpt_r4/ACQUISITION_TERMINAL_V1.md` (a terminal that generated
no policy outcome) plus the reading in `claude_r6_verification/CROSS_AGENT_VERIFICATION_2026-08-21.md`
section 4: "Items 2 and 3 are pre-outcome protocol repairs. Under the R4 precedent
(PRE_OUTCOME_PROTOCOL_REPAIR__NO_RESULT_AUTHORITY) they may be made without touching the
frozen source universe, provided they land before the outcome is read as a P1-U result."

**Where the three defects actually live.**
- Defects 1+2 (class / domain noninferiority): `research/claim_expansion/p1/gpt_r6/evaluate_native.py`,
  `evaluate()` lines ~338 and ~407-414. Present in this working tree. CONFIRM EMPIRICALLY.
- Defect 3 (`_leakage_free`): **not in this working tree.** `_leakage_free` lives in
  `research/claim_expansion/p1/gpt_r6_native_primary.py`, which exists only on the shadow ref
  `origin/shadow/p1-u-gpt-r6-native-runtime-20260820` (an archived copy of that tree is in this
  session's scratchpad at `scratchpad/r6/`). `evaluate_native.py` has **no leakage guard at all**.
  So the repair here is: implement the guard in `evaluate_native.py`, three-valued and fail-closed,
  with pair role as a forbidden token. The fail-open defect is still reproduced first, against the
  exact shadow-branch source of `_leakage_free`.

**Downstream consumers of `evaluate_native.py` I must not break:**
- `tests/unit/p1/test_p1_u_r6_native_evaluator.py`
- `.github/workflows/p1-u-r6-native-runtime.yml` (runs `evaluate_native.py --out ...`; asserts
  `schema`, `data.complete`, `policy_outcomes_generated`, and terminal in a 2-element set)
- `research/claim_expansion/p1/gpt_r6_dr1/run_dr1_campaign.py` imports
  `EVAL.{fixed_corpus, validate_fixed_corpus, _b3, _verify_native_lineage, _score, _mean, _bootstrap, UNRESOLVED, NATIVE}`.
  It does **not** call `evaluate()`. Its receipt `P1_R6_DR1_RECEIPT_V1.json` is committed and
  MUST NOT be edited. => I may change `evaluate()`; I must not change the semantics of those helpers.

**Outcome status of the thing I am repairing.** No committed result artifact from
`evaluate_native.py` exists in the tree (`gpt_r6/` holds only protocol + code). The DR1 campaign
read an outcome, but its checks do not include class or domain noninferiority. So the two
noninferiority guards have not been read as a P1-U result, and the repairs are genuinely
pre-outcome for them.

## Milestone 1 — defects reproduced (done)
Numbers in `PRE_REPAIR_RECORD_V1.md`. Headlines:
- D1: 6 strata, `NO_HIGH_LEVEL_REFORMULATION` absent, 22 control episodes filed under adverse class.
- D2: 26 strata, 22x size 2 + 4x size 1; `-1/n >= -0.10` requires n>=10; no stratum qualifies.
- D3: `_leakage_free({}, toks)` returns True (fail-open); pair role absent from token tuple.
  NEW measured finding: the frozen core embeds the episode id (and hence the -A/-C/-U role
  suffix), the pair id and the query id in `problem_id`, which reaches the candidate provider
  payload. So a correct guard is expected to go RED here.

## Milestone 2 — pre-registration written (done)
`PRE_OUTCOME_REPAIR_V1.md`. Terminal `PRE_OUTCOME_PROTOCOL_REPAIR__NO_RESULT_AUTHORITY`.
Decisions locked in before running anything:
- class: conjunction of old pair-level check AND new member-level-by-gold-class check.
  Strictly stricter; old `class_means` / macro / `at_least_three_nonnegative_classes` untouched.
- domain: **restate** as `domain_zero_loss` (no negative domain mean); the widened reading is
  reported as a non-governing sensitivity over the already-frozen HIGH/LOW/CONTROL/UNRESOLVED
  partition, whose strata are 15/7/22/4 -> `-0.10` is STILL a zero-loss rule for 2 of 4.
  Verdict-identity of old vs restated predicate is asserted in the result.
- leakage: three-valued `LeakageVerdict` with `__bool__` raising TypeError; pair role added;
  absence -> CANNOT_CHECK; expected verdict RED.
- terminal stays two-valued so the CI workflow assertion keeps holding.

## NEXT: milestone 3 — baseline run of the UNREPAIRED evaluator, then the repairs.

## Milestone 3 — repairs applied and first repaired run (done)
Baseline (unrepaired, `--out` to scratch): all 14 checks True, terminal
`P1_R6_NATIVE_PRIMARY_PASS_PENDING_2019_REPLICATION`, episode ARD-B3 = +0.4583.
Repaired run: terminal `P1_R6_NATIVE_PRIMARY_NOT_SUPPORTED`.

| check | baseline | repaired |
| --- | --- | --- |
| class_noninferiority | True (6 strata, no control) | True (6 pair-level AND 8 member-level, control included) |
| domain_noninferiority -> domain_zero_loss | True | True (restatement asserted verdict-identical) |
| no_candidate_metadata_leakage | (absent) | **False** — 96/96 episode-arms FAIL |
| everything else | True | True (unchanged) |

Member-level class means (new): SEARCH 1.0, OBJECTIVE 0.75, BOUNDARY 0.667,
IMPLEMENTATION 0.5, REPRESENTATION 0.5, NO_HIGH_LEVEL_REFORMULATION **+0.364 (n=22)**,
MEASUREMENT 0.333, UNRESOLVED 0.0 (n=4). Control stratum now exists and is non-negative.

Leakage: 96/96 FAIL. Hit categories: `episode_id_and_pair_role` 96, `query_id` 96, `pair_id` 88.
Every episode's provider payload carries `problem_id = "p1-r6-root:R5-<QUERY>-<ROLE>"`.

Domain: min stratum size for -0.10 to admit one lost episode = 10; largest domain stratum = 2;
`any_stratum_large_enough = False`. Widened sensitivity (frozen HIGH/LOW/CONTROL/UNRESOLVED):
counts 7/15/22/4, one-loss thresholds -0.143/-0.067/-0.045/-0.25; only CONTROL and
LOWER_LEVEL_ADVERSE are big enough for -0.10 to be a margin. Both readings verdict True.

**ERRATUM to PRE_OUTCOME_REPAIR_V1.md section 1:** it says the member-level stratifier gives
"7 strata" and then lists 8. The correct count is 8 (6 substantive + control + unresolved).
Counting slip in the pre-registration, not in the code. Recorded rather than silently amended.

## NEXT: milestone 4 — tests + mutation checks.

## Milestone 4 — tests + mutation checks (done)
`tests/unit/p1/test_p1_u_t3_repaired_guards.py`, 15 tests, all green.
7 mutations applied and reverted; all 7 go red; pristine + restored both green and the
restored file byte-identical. Record in `MUTATION_CHECKS_V1.md`.
Note: the first conjunction test did NOT catch M2 (both conjuncts are True on the real
corpus). Replaced with a synthetic "comparator that only wins on controls" case, which is
exactly the failure the broken guard could not express. Documented rather than hidden.

Runner check: `reproduce_t3_defects.py` has `main(argv)` + `__main__` guard and was invoked as
a subprocess successfully; wrote `PRE_REPAIR_RECORD_V1.json`.
`evaluate_native.py` converted to `main(argv) -> int` + `raise SystemExit(main(sys.argv[1:]))`.

## NEXT: milestone 5 — regression suite, workflow check, final report.

## Milestone 5 — regression + final report (done)
- `tests/unit/p1/` : 50 passed (49 pre-existing + the new module's 16, minus overlap => full dir green).
- DR1 campaign re-run to scratch: ALL scored fields identical to the committed receipt, and
  48/48 identical per-episode choices for ARD/BASE/B3. Committed receipt NOT touched.
- CI workflow post-run assertions re-simulated against the repaired output: pass
  (terminal `P1_R6_NATIVE_PRIMARY_NOT_SUPPORTED` is in the frozen 2-element set).
- `ruff check` clean on all three touched/added python files. No `ruff --fix` over a glob.
- Severity bound measured and pinned as a test: anonymising the episode id changes 0/44 ARD
  choices under the frozen host => leak is available but unexploited by THIS host.
- Final report: `T3_REPAIR_TERMINAL_V1.md`.

## Deliverables produced
1. `PROGRESS.md` (this file)
2. `PRE_REPAIR_RECORD_V1.md` + `PRE_REPAIR_RECORD_V1.json` + `reproduce_t3_defects.py`
3. `PRE_OUTCOME_REPAIR_V1.md` (pre-registration, with erratum)
4. repairs in `gpt_r6/evaluate_native.py`; `tests/unit/p1/test_p1_u_t3_repaired_guards.py`;
   `MUTATION_CHECKS_V1.md`
5. `REPAIRED_GUARD_RUN_V1.json`
6. `T3_REPAIR_TERMINAL_V1.md`
