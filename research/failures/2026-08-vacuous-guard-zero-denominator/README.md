# A harm guard that reported a pass because nothing ever pressed it

**Observed:** 2026-08-21, tracing why P2-U-T2 (#650) — "simultaneous
non-inferiority/superiority on false closure" — could be asserted from a campaign
whose own terminal receipt records a negative result.

## Failure

P2's false-closure guard is reported as a count of premature task closures, and
as a rate of those over the tasks in the slice. On the 24-task external Wide
acquisition slice, `P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18.json` records, for
**both** the diversified candidate and the lexical baseline:

```json
"tasks_closed_as_complete": 0,
"tasks_with_open_obligations": 0,
```

Zero premature closures in each arm. Read as a guard, that is a pass, and read
as a comparison it is exact parity — the strongest possible non-inferiority
result. It is neither. Neither arm ever claimed task completeness on any of the
24 tasks, so neither arm ever had an opportunity to claim it falsely. The guard
scored two empty sets against each other.

The zero is manufactured upstream, and correctly so. `orion.study.p2.gold`
replays each stop against the world state at its index and then writes:

```python
premature = bool(outstanding) and remaining_calls > 0
if decision.scope == StopScope.TASK.value and not decision.claimed_complete:
    # Running out of run without claiming completeness is not a closure
    # error. Prematurity is a property of the *claim*, not of stopping.
    premature = False
```

That reasoning is right. Prematurity *is* a property of the claim. The defect is
one layer up, where the metric is formed:

```python
"premature_task_closure": float(
    any(item.premature and item.scope == StopScope.TASK.value for item in self.stop_audits)
),
```

and then averaged over every task in the slice. The numerator is carried; the
denominator is discarded. A system that closed 260 times and was never wrong and
a system that never closed at all both come out as `0.0`.

Measuring the denominator separates them completely. Replaying the frozen
390-task controlled world at seed `20260816`:

| system | closures claimed | false closures | V1 rate over tasks | guard verdict |
| --- | --- | --- | --- | --- |
| `orion_full` | 260 / 390 | 0 | 0.0 | PASS on a real denominator |
| `no_question_conditioned_read_ledger` | 260 / 390 | 0 | 0.0 | PASS |
| `no_content_identity_dedup` | 192 / 390 | 0 | 0.0 | PASS |
| `no_unavailable_route_open_state` | 331 / 390 | 12 | 0.0 | FAIL |
| `adaptive_multiroute_exploratory` | 312 / 390 | 296 | 0.759 | FAIL |
| `bm25_keyword` | 390 / 390 | 390 | 1.0 | FAIL |
| `route_stop_can_close_task` | 390 / 390 | 390 | 1.0 | FAIL |
| external Wide, both arms | 0 / 24 | 0 | 0.0 | **CANNOT_CHECK** |

Four systems publish `premature_task_closure_rate = 0.0` in V1 and they are not
alike: three earned it across denominators of 260, 260 and 192, one fails 12
times, and two more arms have no denominator at all.

The controlled result is not weakened by this; it is strengthened. "Rate 0.0
over 390 tasks" is compatible with never closing. "Declined to close 130 times
and was never wrong on the 260 it did close" is a claim about a mechanism, and
it is the claim the evidence actually supports.

## The same defect, one layer in

The first version of the receipt read `StopAudit.premature` alone and scored
`no_unavailable_route_open_state` a clean pass on all 331 of its closures. The
campaign's own status assignment fails it 12 times.

The evaluator condemns a closure on two grounds, not one:

```python
if any(item.scope == StopScope.TASK.value and item.premature for item in audits):
    return "FAIL", "premature_closure"
if censored and claimed_complete:
    return "FAIL", "premature_closure"
```

The second ground never sets `premature`, because the audit's live-reach
calculation excludes dead routes — so by its arithmetic nothing is outstanding.
That is the exact failure this record is about, reproduced inside the fix for
it: a count read from the wrong place, agreeing with the right answer everywhere
except on the one ablation designed to break it. It was caught by cross-checking
the receipts' numerators against the published `failure_counts.premature_closure`
for every arm, which is now a block in the generated artifact rather than a
thing a reader must redo. `FalseClosureKind` carries the two grounds separately
so they cannot merge back into one boolean.

## Failure class

`VACUOUS_GUARD_ZERO_DENOMINATOR`

A guard reported as a violation count or a violation rate returns the same value
when it held under pressure and when it was never pressed. Where a campaign can
end without exercising the guard, that value is not a verdict.

This is the same shape as `UNREACHABLE_OPERATOR_INERT_ABLATION`
(`research/failures/2026-08-unreachable-operator-inert-ablation/`), one layer
out: there an ablation arm never reached the operator it ablated, so its
independent variable never varied; here a guard never reached the state it
guards against, so its dependent variable never varied. Both produce a number
that reads as measured and is structural. Both were invisible because the
artifact reported the outcome without reporting whether the mechanism ran.

## Correct response

1. Make the denominator part of the verdict's type, not a field a reader may
   reconstruct. `orion.programme.guard_exercise.GuardExercise` carries
   `opportunities` alongside `violations` and requires a written
   `opportunity_definition`; a denominator that cannot be stated in a sentence
   cannot be defended.
2. Return three values, not two. An unexercised guard is
   `Outcome.CANNOT_CHECK`, which blocks a promotion exactly as `FAIL` does.
   `GuardAssessment` refuses at construction to pair `PASS` with any
   vacuity reason, so the substitution cannot be reintroduced by a later edit.
3. Require both arms to be exercised before a non-inferiority claim.
   `assess_non_inferiority` names *which* arm was unexercised rather than
   returning a bare blocked verdict.
4. Give the states that swallow the denominator names.
   `orion.study.p2.closure_receipts.TaskClosureKind` is total, so the state that
   absorbed 24 of 24 external tasks appears in the ledger as
   `STOPPED_WITHOUT_CLOSURE_CLAIM` instead of vanishing into a zero.
5. Refuse outcome access until every cell has a receipt
   (`require_closure_receipts`), so a denominator cannot shrink by omission —
   which is #650's "require route-level and task-level closure receipts" stated
   as a precondition rather than as a report field.

## Recurrences, 2026-08-21

Three more instances of this shape, found the same day, in three different
places. They are recorded together because what they have in common is more
useful than any one of them: **the denominator was never reported, so nobody
could see it was empty.** In each case the check had run for a long time, looked
clean, and had never once had an opportunity to fire.

### 1. A guard that had never had a case at all

`P3.OVERRESOLVED_UNRESOLVED_CASE` reported `0/0` on all three P3 atlases. Not a
bug in the guard: the corpus has no instance of the failure it guards against.
Across 9 coordinates and 88 cases, every coordinate is observed on both sides of
a pair or absent on both, so a partially observed pair — the only situation in
which over-resolution is possible — does not occur anywhere in P3's evidence.

Given a denominator by silencing, on one side only, the coordinate that carries
the decision, the current system over-resolves **12 of 12**, with 8/8 and 28/28
held out. Forty-eight of forty-eight. The paper's `FALSE_SCIENTIFIC_MERGE` pass,
scored on the same decisions, holds only under full observation.

The corpus-design lesson is worth carrying forward on its own: an evaluation set
built by observing every coordinate on both sides cannot exercise any guard about
partial observation, and will report those guards as passing forever.

### 2. Eleven rates that returned the best possible score for "unmeasured"

Every rate in `src/orion/study/metrics.py` divided by the number of non-abstained
cases and returned `0.0` when that count was zero. For a *harm* rate, zero is the
best attainable value, so a metric that measured nothing reported that nothing
went wrong, and any threshold check on it passed.

The test suite had pinned this as intended behaviour, and one pair of tests shows
it exactly: `test_agreement_skips_unresolved` asserted `0.0` for "nothing was
comparable" and `test_agreement_zero_when_disagree` asserted `0.0` for "they
disagreed on everything". Two opposite states, one number, a test for each.

Empty denominators now yield `nan` rather than `0.0`. Deliberately not `None`:
a caller writing `not rate` sees `not None` as `True` and reports clean, which is
worse than the original bug. Every comparison against `nan` is `False`, so the
metric fails closed wherever it is read.

### 3. A differential check that agreed about the constant `False`

While mechanizing P8's authority calculus, a differential check compared the
proved formula against the committed executable model on randomly drawn worlds.
It agreed on 60 of 60 trials — and authorised on **zero** of them. Drawing each
field independently satisfies all seven conjuncts almost never, so the two
implementations were being compared only where both refuse.

This is the same failure wearing a third costume, and it is the most instructive
of the three because the check was *written* to catch a discrepancy and would
have reported "no discrepancy" indefinitely. The fix is not more trials; it is
reporting whether the corpus exercised more than one outcome.
`DifferentialReport.exercised_both_verdicts` is now carried beside the agreement
count in `orion.programme.mechanized`, and the run that followed found a real
defect in the axiomatisation within 120 trials.

### What the three have in common

None of them was found by looking at the guard. Each was found by asking a
different question — "what would have to be true for this to have fired?" — and
discovering the answer was "nothing in this corpus". A guard cannot report its
own vacuity, because from the inside a vacuous guard and a satisfied one produce
identical output. Only the denominator distinguishes them, and only if someone
carries it.

## General lesson candidate

**A guard's zero is evidence only when its denominator is reported with it.**
Every safety metric expressed as "how often did the bad thing happen" needs a
companion "how often could it have happened", and the pair must be carried
together through every aggregation, because the aggregation is where the
denominator gets dropped. When the denominator is zero the honest verdict is
`CANNOT_CHECK`, and a comparison between two zero-denominator arms is not
parity — it is a comparison of two absent measurements.

The general form: **never let a mechanism's report be silent about whether the
mechanism ran.** Every check in this repo that returns a count should be asked
what its denominator was and whether that denominator can be zero.
