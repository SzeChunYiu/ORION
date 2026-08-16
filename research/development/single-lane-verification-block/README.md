# The verification blocker is structural, not technical

**Observed:** 2026-08-16, after the discriminating-check registry landed (PR #30).

## Measurement

Grading all 31 committed answer records against the live decomposition, with
the registry loaded:

```
authority:      EVIDENCE_BOUND 31
check outcome:  LANE_NOT_INDEPENDENT 27,  NOT_REGISTERED 4
open questions: 1298 -> 1298,  verified closures: 0
```

Every registered check declares `lane = claude`. Every committed answer record
declares `lane = claude`. `grade_answer` refuses a check that shares a lane with
the answer it would judge, so 27 of 31 answers cannot reach `VERIFIED` no matter
how sound the checks are. The remaining 4 target `FAILURE`, for which no check
is registered.

## Why this is the correct behaviour

The constitution states that a self-improver cannot certify itself by weakening
its evaluator (`docs/00-foundation/README.md`). Lane independence is the
operational form of that rule. A lane that both answers and verifies has an
evaluator inside the thing being evaluated, and every closure it produces is
self-certification — the exact failure the authority ladder exists to prevent.

So the loop is not broken. It is complete and correctly refusing. **The system
is blocked on a governance property: there is currently only one lane supplying
both sides.**

## What would unblock it, and what would not

**Would unblock:**
- another lane (`self-orion/*`, `codex/*`) supplying answer records that the
  existing `claude` checks can judge;
- another lane supplying checks for the existing `claude` answers.

**Would not unblock, and must not be attempted:**
- the `claude` lane registering checks under a different lane label. That is
  lane laundering. It satisfies the string comparison and destroys the property
  the comparison stands for, leaving a system that reports verified closures
  while nothing independent has looked at anything.

The distinction matters because the second option is available, cheap, and
would make the headline number move immediately. That it is available is
precisely why it is written down here as forbidden rather than left to
judgement.

## Honest reading of the current state

At the observed revision, the raw grade/apply seam could close a question but
had never closed one. The protected-transition work subsequently removed that
authority from raw checks: a `PASSED` outcome is retained as diagnostic
appraisal input, while closure requires the separately revisioned relying-party
authorization and atomic commit lifecycle. Therefore adding another lane alone
no longer unblocks `VERIFIED`, and restoring the old promotion would recreate
caller-owned authority. This amendment narrows the historical diagnosis rather
than erasing it.

## Residuals

1. `FAILURE` has four answers and no registered diagnostic check in any lane.
2. Lane separation is currently a string comparison over a self-declared field.
   It is structural, not organizational: nothing prevents a single operator from
   running both lanes. `experience/learning.py` already reaches the same
   conclusion for pattern promotion and fails closed with
   `external_lineage_separation_attestation_required`. The check registry should
   inherit that treatment rather than trusting the label.
