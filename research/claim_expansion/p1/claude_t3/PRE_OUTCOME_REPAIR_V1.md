# P1-U-T3 pre-outcome protocol repair V1 — guard specification, written before the repaired run

**Date:** 2026-08-21
**Gate:** `P1-U-T3` in `research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json`
**Parent:** #723 / `claude_r6_verification/CROSS_AGENT_VERIFICATION_2026-08-21.md` §2.2
**Precedent:** R4 `PRE_OUTCOME_PROTOCOL_REPAIR__NO_RESULT_AUTHORITY`, in the shape used by
`research/claim_expansion/p1/P1_X_PROTOCOL_V1_AMENDMENT_003.md`.

Outcome of the repaired guards read before this document was written: **NO**.
Frozen source universe touched: **NO**.
Any committed campaign result, receipt or evidence JSON edited: **NO**.

Terminal of this document: `PRE_OUTCOME_PROTOCOL_REPAIR__NO_RESULT_AUTHORITY`.

> **Erratum, added after the repaired run, body text left unedited.** Section 1 says the
> member-level stratifier gives "7 strata" and then enumerates 8. The correct count is **8**:
> the 6 substantive classes, `NO_HIGH_LEVEL_REFORMULATION` and `UNRESOLVED`. This was a
> counting slip in the pre-registration prose; the enumeration and the implemented code are
> both right. Recorded here rather than silently corrected, because a pre-registration that
> can be edited after the fact is not a pre-registration.

---

## 0. Standing rule for every repair below

A repair may only ever **subtract** a claim. Concretely, for each of the three:
if the repaired guard's verdict is *more* permissive than the broken guard's verdict on the
same corpus, the repair is wrong and must be reverted. Each repair below states, in advance,
the direction it is allowed to move the verdict.

## 1. Class noninferiority

### What is broken
The stratifier key is the pair's `adverse_class` for both members, so the
`NO_HIGH_LEVEL_REFORMULATION` stratum does not exist. 22 control episodes are evaluated only
inside a conjunctive pair statistic, never as their own gold class.

### What the repaired guard tests
Two components, checked as a **conjunction**:

- `class_noninferiority_pair_level` — unchanged from the current code. The pair-level selective
  diff `1[ARD correct on both members] - 1[B3 correct on both members]`, averaged within each
  `adverse_class`, must be `>= domain_or_class_noninferiority_floor` in **all 6** strata.
- `class_noninferiority_member_level` — new. Every scored episode's
  `ARD_grs - B3_grs` is filed under **that episode's own `gold_class`**, giving 7 strata:
  the 6 substantive classes (3-4 episodes each, adverse members only),
  `NO_HIGH_LEVEL_REFORMULATION` (22 control episodes) and `UNRESOLVED` (4 episodes).
  Every stratum mean must be `>= domain_or_class_noninferiority_floor`.

`class_noninferiority` is `pair_level AND member_level`.

### What would make it fail
Any one of the 6 pair-level strata below the floor, **or** any one of the 8 member-level strata
below the floor. In particular the guard now fails if ARD is worse than B3 on the control
episodes as a group — a failure mode the broken guard could not express.

### Permitted direction
Strictly stricter. The conjunction can turn PASS into FAIL; it can never turn FAIL into PASS,
because the pre-existing component is retained bit-for-bit as one conjunct.

### Deliberately not changed
`class_means`, `pair_macro_equal_class_orion_native_ard_minus_b3`, `pair_macro_margin`,
`pair_macro_stability_lower_positive` and `at_least_three_nonnegative_classes` continue to be
computed from the **pair-level** `pair_by_class` exactly as before. Re-basing them on the new
stratifier would silently change three other frozen checks under cover of this repair.

## 2. Domain noninferiority — the margin fork

### What is broken
26 strata of 1-2 episodes make `>= -0.10` and `>= 0` the same predicate. The check's name
claims a tolerance the corpus cannot express.

### The fork, and which branch is taken
For `-0.10` to admit one lost episode a stratum needs `n >= 10`. Options:

- **Widen the stratifier.** Requires a grouping of the 26 `actual_domain` values into strata of
  `n >= 10`. No such grouping is frozen anywhere in the protocol, the fixed source set or the
  repository, so adopting one means *inventing* a partition during a pre-outcome repair — a
  researcher degree of freedom on the exact axis the guard scores. Rejected as the primary
  reading.
- **Restate the margin as the rule it actually is.** Taken.

The one coarser partition that is already frozen (`HIGH` / `LOW` in `evaluate_native.py`, plus
the protocol's `control_class` and `unresolved_class`) is computed and reported as a
**sensitivity**, not as the governing check. Its strata are LOW-adverse 15, HIGH-adverse 7,
control 22, unresolved 4; `-1/7 = -0.143` and `-1/4 = -0.25` are both below `-0.10`, so even
that widening leaves `-0.10` a zero-loss rule in 2 of its 4 strata. This is reported whatever
its verdict.

### What the repaired guard tests
- `domain_zero_loss` (governing, replaces `domain_noninferiority` in the checks dict) — no
  `actual_domain` stratum has a **negative** mean `ARD_grs - B3_grs`. Stated as the zero-loss
  rule, with the floor recorded as `0.0` and the frozen `-0.10` recorded alongside as
  `equivalent_on_this_corpus: true` plus the arithmetic that makes it so.
- `domain_level_noninferiority_sensitivity` (reported, non-governing) — the same floor applied
  to the frozen 4-way responsibility-level partition, with each stratum's size and its own
  one-loss threshold `-1/n` printed next to it.

### What would make it fail
Any domain stratum with a negative mean, i.e. any domain where ARD loses more episodes to B3
than it wins. Identical predicate to the broken check; only the name and the reported semantics
change.

### Permitted direction
Exactly neutral by construction, and it must be *shown* to be neutral: the repaired result
carries `domain_restatement_is_verdict_identical`, computed by evaluating both predicates on
the same stratum means and asserting equality. If they ever differ the repair is wrong.

## 3. Leakage guard

### What is broken
On the shadow ref, `_leakage_free` returns `True` when `request_payloads` is absent, and its
forbidden token set omits pair role. In this tree the guard does not exist at all.

### What the repaired guard tests
A three-valued audit over the payloads actually presented to the candidate's provider boundary
(`FrozenNativeProviderHost.__call__` requests, captured by a recording wrapper that appends and
delegates and changes no decision), per scored episode and per arm:

- `CANNOT_CHECK` — no payload record was captured for that episode/arm. Absence is explicit.
- `FAIL` — at least one forbidden token occurs in the captured payloads.
- `PASS` — payloads were captured and contain no forbidden token.

Forbidden token set, per episode: the episode id, the pair id, the query id, the source id, the
adverse class literal, the episode's own gold class literal, every P1 class label, and — new —
**pair role**: the literals `adverse`, `control`, `pair_role`, and the role suffixes `-A`, `-C`,
`-U` as they terminate the episode id.

`checks["no_candidate_metadata_leakage"]` is `True` **only** when every episode/arm verdict is
`PASS`. `CANNOT_CHECK` is not `PASS`.

### The `not None is True` trap, and how it is closed
The verdict is not `None`, and it is not a `bool`. It is a `LeakageVerdict` whose `__bool__`
raises `TypeError`. A two-valued caller that writes `if row["leakage"]:` or
`int(not row["leakage"])` therefore crashes instead of silently scoring a `CANNOT_CHECK` as
clean. Callers must branch on `verdict.status` explicitly. A test asserts the `TypeError`.

### What would make it fail
Any forbidden token in any captured payload (FAIL), or any episode/arm for which no payload was
captured (CANNOT_CHECK). Both block `no_candidate_metadata_leakage`.

### Expected direction, stated in advance
**Red.** The pre-repair record already measured that the frozen core embeds the episode id —
and therefore the pair-role suffix — in `problem_id`, on every episode. A guard that tests what
its name says is therefore expected to report `FAIL`, not `PASS`. If the repaired guard reports
`PASS`, the token set has been quietly weakened and the repair is wrong.

### Explicitly out of scope
**Removing the leak is not part of this repair.** Changing `problem_id` would alter every
runtime digest, including those in the committed `gpt_r6_dr1/P1_R6_DR1_RECEIPT_V1.json`, and
would convert a guard repair into a repair of the experiment. It needs its own pre-outcome
freeze. This repair's job is to make the leak *visible and blocking*.

## 4. Terminal handling

The result terminal stays two-valued
(`P1_R6_NATIVE_PRIMARY_PASS_PENDING_2019_REPLICATION` /
`P1_R6_NATIVE_PRIMARY_NOT_SUPPORTED`) so that
`.github/workflows/p1-u-r6-native-runtime.yml`'s assertion remains valid. Any `CANNOT_CHECK`
guard maps to `NOT_SUPPORTED`, which is fail-closed. The three-valued detail is carried in a
new `guard_verdicts` block so `FAIL` and `CANNOT_CHECK` stay distinguishable in the artifact.

## 5. Unchanged scientific commitments

This repair does **not** change: the frozen source universe; the 22-pair / 4-unresolved corpus;
`FIXED_SOURCE_SET_V1.json`; the provider host, keyword table, responsibility mapping, probe
priority or budget; `_score`, `_mean`, `_bootstrap`, `_b3`, `_verify_native_lineage`,
`fixed_corpus` or `validate_fixed_corpus` (all imported by `gpt_r6_dr1/run_dr1_campaign.py`);
any threshold in `NATIVE_PROTOCOL_V1.json`; the episode, pair-micro and pair-macro margins or
their bootstraps; `at_least_three_nonnegative_classes`; the false-high-level, lower-level-skip,
control-harm or false-resolution guards; or the result or novelty authority of P1
(`BOUNDED_EXACT`, unchanged).

## 6. Mutation checks required before this repair is reported as landed

Each repaired guard must have a test that goes **red** when the repair is reverted:

1. revert `pair_by_class` to member-blind accumulation -> member-level class test fails;
2. revert `domain_zero_loss` to the `-0.10` string without the equivalence assertion -> the
   verdict-identity test fails;
3. revert `_leakage_free` to `native.get("request_payloads", [])` -> the fail-closed test fails;
4. drop pair role from the forbidden set -> the role-token test fails;
5. return `None` instead of a `LeakageVerdict` -> the `__bool__`-raises test fails.

Each is to be performed by actually applying the mutation and recording the failing test name.
