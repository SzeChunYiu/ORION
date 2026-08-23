# P1-U-T3 — pre-outcome guard repair, terminal report

**Date:** 2026-08-21
**Gate:** `P1-U-T3`, `research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json`
**Terminal:** `PRE_OUTCOME_PROTOCOL_REPAIR__NO_RESULT_AUTHORITY`
**Authority granted:** none. No adoption, promotion, merge or claim-widening authority. P1's
declared scope stays `BOUNDED_EXACT`.

Files: `PRE_OUTCOME_REPAIR_V1.md` (pre-registration, written before the repaired run),
`PRE_REPAIR_RECORD_V1.md` + `PRE_REPAIR_RECORD_V1.json` (defects reproduced),
`MUTATION_CHECKS_V1.md` (every repair reverted and shown to break a test),
`REPAIRED_GUARD_RUN_V1.json` (what the repaired guards say),
`reproduce_t3_defects.py`, `tests/unit/p1/test_p1_u_t3_repaired_guards.py`.

---

## 1. What was broken

**Class noninferiority never saw the control class.** `evaluate_native.py:338` filed the
pair-level selective diff under the pair's `adverse_class`, one row per pair. Measured: 6
strata, `NO_HIGH_LEVEL_REFORMULATION` absent, 22 control episodes contributing to no stratum of
their own, 0 of 48 episodes filed under its own gold class. The matched control — the entire
point of within-source pairing, and the R4 successor lesson — was never evaluated as a class.

**The domain margin was not a margin.** 26 strata: 22 of size 2, 4 of size 1, 48 episodes.
Per-episode diffs live in `{-1, 0, +1}`, so a stratum of size *n* that loses one net episode
has mean `-1/n`; clearing `-0.10` needs `n >= 10`. No stratum reaches 2. `>= -0.10` and `>= 0`
were the same predicate.

**The leakage guard was fail-open and role-blind.** The predecessor
(`gpt_r6_native_primary.py:211-213`, shadow ref) returned `True` — "no leakage" — when
`request_payloads` was absent or `None`, and its forbidden tuple
`(episode_id, pair_id, query_id, adverse_class, gold_class)` had no pair-role token. On
`evaluate_native.py` in this tree the guard did not exist at all.

## 2. What changed

1. **Class.** Every scored episode now also accumulates under **its own `gold_class`**, giving
   8 strata including `NO_HIGH_LEVEL_REFORMULATION` (n=22) and `UNRESOLVED` (n=4).
   `class_noninferiority` is the **conjunction** of the untouched pair-level check and the new
   member-level check, so it can only ever be stricter. `class_pair_differences`,
   `pair_macro_*` and `at_least_three_nonnegative_classes` were deliberately **not** rebased.
2. **Domain.** `domain_noninferiority` is renamed `domain_zero_loss` and states the rule it
   arithmetically is: *no `actual_domain` stratum may have a negative ARD−B3 mean*. The
   evaluator now **raises** if the frozen `-0.10` predicate and the zero-loss predicate ever
   disagree, so the restatement cannot silently become a different rule. The widened reading is
   computed and reported as a non-governing sensitivity over the partition already frozen in
   the module (`HIGH` / `LOW` / control / unresolved) rather than one invented here.
3. **Leakage.** New `LeakageVerdict` (`PASS` / `FAIL` / `CANNOT_CHECK`) whose `__bool__`
   **raises `TypeError`**, so a two-valued caller crashes instead of reading a `CANNOT_CHECK`
   as clean. Absent, `None`, non-sequence and **empty** payload records are all `CANNOT_CHECK`.
   The token set gains pair role: the episode id is categorised `episode_id_and_pair_role`
   because the frozen id format ends in the `-A`/`-C`/`-U` role suffix, plus the `pair_role`
   literal and a structural role-assignment regex. `no_candidate_metadata_leakage` is `True`
   only when every episode/arm is `PASS`. A new `--payloads-out` writes the raw payloads so a
   finding can be re-audited later with a corrected token set — the predecessor kept only a
   digest and could not be.

The bare English words `adverse` / `control` are deliberately **not** tokens: two frozen control
dossiers use "quality-control" and "positive-control" as ordinary domain vocabulary. The role
stays fully covered by the episode-id token, which does fire on all 96 episode-arms.

## 3. What the guards say now

| check | before | after |
| --- | --- | --- |
| `class_noninferiority` | True (6 strata, control absent) | **True** (6 pair-level ∧ 8 member-level, control present) |
| `domain_noninferiority` → `domain_zero_loss` | True | **True** (restatement asserted verdict-identical) |
| `no_candidate_metadata_leakage` | *(guard absent)* | **False** |
| all 12 other checks | True | True, unchanged |
| **terminal** | `P1_R6_NATIVE_PRIMARY_PASS_PENDING_2019_REPLICATION` | **`P1_R6_NATIVE_PRIMARY_NOT_SUPPORTED`** |

Member-level class means (ARD−B3 episode GRS), the strata that did not exist before:

| gold class | n | mean |
| --- | --- | --- |
| SEARCH_OR_EVIDENCE | 4 | +1.000 |
| OBJECTIVE_OR_MODEL_CLASS | 4 | +0.750 |
| PROBLEM_BOUNDARY | 3 | +0.667 |
| IMPLEMENTATION_OR_ENVIRONMENT | 4 | +0.500 |
| REPRESENTATION_OR_INTERFACE | 4 | +0.500 |
| **NO_HIGH_LEVEL_REFORMULATION** | **22** | **+0.364** |
| MEASUREMENT_OR_EVALUATOR | 3 | +0.333 |
| UNRESOLVED | 4 | 0.000 |

The control stratum, evaluated for the first time, is non-negative. Underneath it: ARD is
correct on 8/22 controls, B3 on 0/22. So the control-class margin is real but it is a margin
between a weak arm and an arm that never gets the control right — 8/22 is not a good absolute
number, and the guard's job was only ever to check non-inferiority, not adequacy.

### Both readings of the margin question

| reading | stratifier | strata | governing predicate | verdict |
| --- | --- | --- | --- | --- |
| **restated (governing)** | `actual_domain`, 26 strata (22×n=2, 4×n=1) | 26 | no stratum mean `< 0` | **True** |
| frozen floor as written | same | 26 | no stratum mean `< -0.10` | **True**, and provably the same predicate here |
| **widened (sensitivity)** | frozen HIGH / LOW / control / unresolved | 4 | mean `>= -0.10` | **True** |
| widened, at zero loss | same | 4 | mean `>= 0` | **True** |

The verdict is `True` under every reading, which is why choosing between them costs nothing
here and must be stated anyway. The substantive finding is that **no available stratification
makes `-0.10` a margin**: it needs `n >= 10`; `actual_domain` tops out at 2; and even the widest
already-frozen partition (counts 22 / 15 / 7 / 4; one-loss thresholds −0.045 / −0.067 / −0.143 /
−0.25) leaves `-0.10` a zero-loss rule in 2 of its 4 strata. The only place `-0.10` binds as a
margin on 48 episodes is the pooled set, and that is already the separate `episode_margin`
check. Widening was rejected as the governing reading because no `n >= 10` grouping of the 26
domains is frozen anywhere, so adopting one means inventing a partition during a pre-outcome
repair, on the exact axis being scored.

### The leakage finding

96 of 96 episode-arms `FAIL`. Hit categories: `episode_id_and_pair_role` 96/96, `query_id`
96/96, `pair_id` 88/88 (the 8 unresolved episode-arms have no pair id).

Cause: the frozen native core builds `problem_id = f"p1-r6-root:{episode_id}"`, and episode ids
are `R5-<QUERY>-A` / `-C` / `-U`. That string crosses the provider boundary in every request.
The `-C` suffix is a perfect predictor of gold for the 22 control episodes.

**Severity bound, measured not assumed:** anonymising the episode id changes **0 of 44** ARD
choices under the frozen deterministic host, which keys only off `problem.scope` and retrieved
item content. The leak is *available* and *unexploited by this host*. That is a property of
this host, not of the protocol — and #723's own next step is a changed, semantic host for the
2019 replication, i.e. exactly the point at which an available leak becomes an exploitable one.
The guard is a boundary guard and reports the boundary.

**Removing the leak was not done and is out of scope here.** Changing `problem_id` alters every
runtime digest, including those in the committed `gpt_r6_dr1/P1_R6_DR1_RECEIPT_V1.json`, and
would convert a guard repair into a repair of the experiment. It needs its own pre-outcome
freeze. This repair's job was to make the leak visible and blocking, and it now is.

## 4. Discipline

- **Pre-outcome.** The pre-registration was written before the repaired evaluator was run; the
  repaired run is `REPAIRED_GUARD_RUN_V1.json`. One counting slip in the pre-registration (7 vs
  8 strata) is recorded as an erratum in that file rather than edited away.
- **Only subtraction.** Two checks kept their verdict; one new check fails; the terminal went
  from `PASS_PENDING` to `NOT_SUPPORTED`. Nothing went from FAIL or CANNOT_CHECK to PASS. The
  class repair is a conjunction with the original check retained bit-for-bit, so it is
  structurally incapable of loosening.
- **Mutation-checked.** Seven mutations, one per repair plus the two anti-trap properties; all
  seven turn a test red; pristine and restored runs green; restored file byte-identical.
  `MUTATION_CHECKS_V1.md`, including the one test that initially failed to catch its mutation
  and what replaced it.
- **Nothing committed was edited.** No campaign result, receipt or evidence JSON was modified.
  The DR1 campaign re-runs to **identical scored fields and identical per-episode choices for
  all three arms on all 48 episodes**; its receipt was not touched. The R6 CI workflow's
  post-run assertions still hold (`schema`, `data.complete`, `policy_outcomes_generated`,
  terminal ∈ the frozen 2-element set); the terminal stayed two-valued for that reason and any
  `CANNOT_CHECK` maps to `NOT_SUPPORTED`, which is fail-closed.

## 5. What this licenses, and what it does not

**Licensed.** `P1-U-T3`'s three specification defects are repaired and the repairs are tested
against reversion. The class guard now evaluates the matched control. The domain guard says
what it does. The leakage guard fails closed, knows about pair role, and its findings can be
re-audited from the artifact.

**Not licensed.** Nothing about the P1-U superiority claim. Specifically:

1. The repaired evaluator's terminal is `NOT_SUPPORTED`. The R6 native 2020 primary does not
   pass its own guards once the leakage guard exists.
2. `P1-U-T3` should move from `BLOCKED_ON_UPSTREAM` to a **new blocker**: the evaluator boundary
   leaks pair role to the candidate provider on 48/48 episodes via `problem_id`. It is
   unexploited under the frozen host and becomes live under the changed host the 2019
   replication requires. Responsibility `IMPLEMENTATION_OR_ENVIRONMENT`; unblock: mint the root
   problem id from a role-free surrogate under its own pre-outcome freeze, then re-run.
3. `P1-U-T2` (no 2019 corpus, hard-wired year/route/count) and `P1-U-T4` are untouched.
   `P1-U-T1` was addressed by the separate R6-DR1 campaign, whose record is unaffected by this
   repair.
4. The control-class margin being positive is a non-inferiority result on a comparator that is
   correct on 0 of 22 controls. It is not evidence that ARD handles matched controls well.

**Observed, not repaired.** The same `domain_noninferiority` shape — a `-0.10` floor over
per-source strata too small to express it — is also in `gpt_r2/evaluate.py:207`,
`gpt_r3/evaluate.py:294` and `gpt_r4/evaluate.py:439`. `P1-U-T3` names the R6 guards, and R4
terminated on acquisition without producing a policy outcome, so none of those was repaired
here. Recorded so the next reader does not have to rediscover it.
