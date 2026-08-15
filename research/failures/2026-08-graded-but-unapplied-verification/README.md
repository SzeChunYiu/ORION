# Graded-but-unapplied verification (grade/apply disagreement)

**Observed:** 2026-08-16, while validating the first discriminating checks against the real kernel (Claude lane).

## Failure

`grade_and_apply` graded each record against a candidate cell built by applying only that record. When the application layer refused the record (evidence-binding mismatch), `_candidate_cell` fell through to the *unchanged* cell. An admissible dimension check that the unchanged cell already satisfied then reported `PASSED`, so the grading said `VERIFIED` for an answer that was never applied: `verified_record_ids` contained a record while `report.residuals` recorded its refusal and the open-question count did not move.

## Failure class

`GRADE_APPLY_DISAGREEMENT` — two subsystems (authority grading, state application) evaluated the same record against different effective states, and the optimistic one was reported.

A second, compounding cause was found by validating the checker before trusting it: form predicates that judge a cell's *accumulated* content pass on pre-existing seed content (universal envelopes, curated candidate formulations), so any record — including junk — landing on an already-rich cell would ride that content to `VERIFIED`.

## Correct response

1. A record that produces no candidate state is graded with checks disabled (nothing can reach `VERIFIED`) and carries its refusal reasons; evidence-grading reasons stay first so guard learning is unchanged.
2. Checks exclude the seed state: at import they capture every (mechanic, entry) pair the pre-answer program carries; only content beyond the seed can satisfy a predicate.
3. Both properties are pinned to CI: a no-false-alarm test asserts no raw program cell passes any registered check, and the cross-lane tests assert refusal and closure move together.

## General lesson candidate

When one pipeline computes a verdict and another computes a state change for the same event, the verdict must be conditioned on the state change actually occurring — grade the transition, not the hoped-for end state. And any new checker must be validated against the real corpus for false positives (including the no-alarm case) before its verdicts are reported; fixtures alone admitted both defects here.
