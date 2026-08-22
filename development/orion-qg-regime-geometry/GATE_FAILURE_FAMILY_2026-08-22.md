# Sixteen defects in one day, one shape: something computed and then not allowed to matter

Date: 2026-08-22
Branch: `claude/orion-harness-verification-b17qdj`
Status: **retrospective on the author's own work.** Every defect below is mine.

---

## Why this file exists

Three harness gates were added to this repository today — `criterion_binding`,
`falsifiability`, and the coverage requirement inside it. Each was justified in
its own commit message, which means the justification is scattered across a
branch nobody will read commit by commit. The pattern is the useful artifact,
and it is worth one file.

It is also worth being exact. In four separate summaries during this session I
described the count as "seven", then "eleven", then "twelve". **The number is
sixteen**, and I was under-counting each time by summarising from memory instead
of from the log. That is a small instance of the same failure being catalogued:
a number stated without being recomputed.

## The shape

> **Something is computed, recorded, and then not allowed to affect anything.**

The value is right there in the artifact. Nothing reads it. The record looks
complete, the count goes up, and the gap is invisible precisely because the
shape of a working check and the shape of a decorative one are identical from
the outside.

## The sixteen

**A. A conclusion that does not depend on its evidence**

| # | where | what |
|---|---|---|
| 1 | `criterion_churn_retrospective` | the `finding` was a fixed string asserting both lanes cleared, written regardless of the gate results it had just computed |
| 2 | same | it also asserted "the gate is silent on QG-23" while nothing checked QG-23 took the non-gated path |

**B. A gate outcome recorded and not enforced**

| # | where | what |
|---|---|---|
| 3 | both assemblers | G7 and G8 computed, written into the artifact, and never checked — the artifact was written and the run exited 0 regardless |
| 4 | QG-26 verifier | the `criterion_binding` block was never looked at; a tampered one was ACCEPTed |
| 5 | `criterion_binding` + two verifiers | setting `applied_criterion_digest` equal to the frozen one skipped every gated check — concealment was the cheapest bypass |
| 6 | QG-27 analyzer | `validate_criterion_binding` called without the frozen text, so gate G5's digest-against-protocol check silently did not run |

**C. A tamper that rejects for the wrong reason**

| # | where | what |
|---|---|---|
| 7 | QG-24 `T6` | mutated a field the verifier does not read; the copy was **ACCEPTed** and the suite reported six-for-six anyway |
| 8 | QG-24 `T5` | located its target by searching for any key containing `"hit"` — right answer by luck |
| 9 | QG-27 `T9` | tripped the terminal-consistency check instead of the churn gate it was named after, leaving the core hazard with no tamper at all |
| 10 | QG-25 `T7` | flipped two flags where one would do, so an `or` bug in the check it targeted was masked |

**D. A check that cannot fail**

| # | where | what |
|---|---|---|
| 11 | QG-27 verifier | separation "verified" by reachability to one accepting state — implied by the span, so vacuous. The terminal was right; the check never tested it |
| 12 | QG-27 verifier | the check added to fix #11 asserted that the phrase `"vacuous pass"` appeared in prose |
| 13 | QG-25 verifier | `fibres_decide` computed `X == X` |
| 14 | QG-25 verifier | the same claim was then read from the receipt rather than the value just computed |
| 15 | QG-25 verifier | `document_level_verification_declared_false` joined its conditions with `or`, so a false top-level flag cleared a record claiming the opposite |

**E. A terminal that cannot be reached**

| # | where | what |
|---|---|---|
| 16 | QG-27 analyzer | the `BLOCKED` branch raised `NameError` on five unbound names instead of writing its receipt |

## Who found them

Eleven by **Cursor Bugbot**. Two by the `falsifiability` gate refusing to write an
artifact — including one in `criterion_binding`, three commits after that module
was written to close this family. One by the `criterion_binding` gate refusing
its author's own lane, hours after its author wrote it. Two by re-deriving rather
than re-labelling a verification artifact.

**None by reading the code back after writing it.** That is the finding about
method: attention does not catch this class, because the defective and the
working versions look the same. Only something that *executes* the check against
an input built to break it can tell them apart.

## What was done about it

Not sixteen fixes. Three enforcement points:

1. **`criterion_binding`** — a PASS under a criterion changed after the outcome
   must disclose the deviation, record what the frozen criterion would have
   returned, and, when that would have failed, bind an exhibited rejection.
   Concealment by equal digests is refused.
2. **`falsifiability`** — every tamper declares the check that must catch it, and
   a demonstration is refused when a case is caught by a different one, when a
   copy was not resealed, or when the suite is empty.
3. **Coverage, inside the same gate** — a check no tamper exercises must be named
   explicitly. It does not demand a tamper per check; it demands the gap be
   stated.

All three fail closed. All three name their parent literature rather than
claiming it: preregistration and HARKing, mutation testing, the vacuous pass.
**None asserts novelty.**

## What this does not establish

That the family is closed. Three gates catch three variants of one shape, and
the shape is more general than the gates. Defect #12 — the decorative check added
while fixing a vacuous one — happened **after** two of the three gates existed
and was caught by neither, because grepping prose is not something a gate about
tamper coverage can see. The coverage requirement was added in response and would
catch that particular instance now.

The honest summary is that the rate of finding these is a property of how hard
something is looking, not of how many remain.
