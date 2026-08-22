# Every formal core and audit, run end to end — 2026-08-22

Twenty computations, executed rather than described. The point of running all of
them at once is that a checker which reports nothing and a checker which reports
that nothing is wrong print the same thing when you only run the ones you expect
to pass.

## What ran clean

| computation | time |
|---|---|
| P6 separation calculus (SMT) | 1s |
| P6 reopening calculus (SMT) | 0s |
| P6 certificate as dependency graph | 101s |
| P7 composition calculus (SMT) | 10s |
| P7 donor stack as transformation family | 39s |
| P8 authority calculus (SMT) | 2s |
| P8 terminal audit | 1s |
| P14 specification conformance | 0s |

The three calculus lifts and the two interpretation results reproduce. Read
against the superiority ledger, this settles which half of the proof-blocked
terminals is outstanding: for P6-U-T4, P7-U-T5 and P8-U-T5 the unblock reads
"mechanize the core proofs, *then* arrange the review", and the mechanization
half runs here. What is missing is the reviewer, which is not something a
repository can produce for itself.

## What blocks, and why each one is a real finding

### P6 refutation audit — FAIL

Five of the shipped mechanized checks refute **none** of their declared false
theories:

| checker | check | refuted | survived |
|---|---|---|---|
| certificate lifting (320 points) | `donor_conservativity_violations` | 0 | 8 |
| certificate lifting | `ideal_product_mismatches` | 0 | 8 |
| finite models (1,536 points) | `t1_violations` | 0 | 7 |
| finite models | `t4_violations` | 0 | 7 |
| finite models | `t5_countermodels` | 0 | 7 |

A check that accepts every false theory put to it is not evidence about the true
one. Two further facts sharpen it: the `donor` axis in the lifting checker is
**inert** — 0 of 640 sibling pairs change any verdict, so its five values only
multiply the case count by five — and one false theory,
`science_lifts_without_donor`, survives the entire lifting battery, so the
battery's coverage is 7 of 8 rather than complete.

This is what `P6-U-T5` asks to be worked: a surviving counterexample is a
candidate missing primitive, and the repair is to extend the semantics rather
than to add an exception.

### P7 premise audit — FAIL

Two distinct defects, and the second is the more serious.

`bridge_match` is **supplied, not decided**: all 25 enumerated cases accept every
value of it, so 33,554,432 deciding rules are admissible — including the constant
ones. The model carries `left_donor` and `right_donor`, which is what the
premise should be decided from.

`target_ambiguous_if_missing` is `UNDECIDABLE_IN_MODEL`: free on all 64 cases,
because it must be decided from `admissible_target_completions`, which is not an
axis of the enumerated space. No rule written against this model could decide
it, so the check's case count is a count of the mapping downstream of a decision
the model never makes.

The `donor` axis is inert here too, 0 of 640.

### P9 transfer audit — CANNOT_CHECK

The protected vocabulary mostly does not survive fitting. `TRANSCRIPT_BAG` keeps
3 of 515 protected feature keys, leaving **one distinct protected row** — a
denominator of one is not a measurement. And the D1 exact typed-relational
comparator agrees with the D1 evaluator gold on 512 of 512 points with **0
divergent**, which is the zero-refutation-capacity shape again: a comparator that
cannot disagree is not a comparator.

### P11 attack audit — FAIL

The decoder-family share of the published n=64 gap is 13.3% in one cell and
44.6% in the other. Most of the published gap is state, not decoder. Two of the
three decoder arms flip the terminal, so the arm axis is not inert — the verdict
depends on which decoder family is used, and the published number does not say
so.

### P10 publication membership — FAIL

20 of 571 files under the lane roots are unenrolled, and they are not
incidental: six experiment runners (`run_phase2a.py`, `run_phase2b_goal_effect.py`,
`run_v1.py`, `run_v2.py`, `run.py`), seven Lean corpus extracts, the lane README,
the local closure verification script, and the publication manifest itself. Twelve
files are named only by a digest file nothing reads, and ten digests in that
unread file disagree with the bytes on disk.

### P9 frontier grid — grid declared, no cell executed

0 of 1,344 cells carry an outcome. This one is genuinely external: the ladder
needs real model scales, and the freeze explicitly refuses a surrogate on the
ground that a classical-learner capacity ladder is not a model-scale ladder and
would answer a different question. That refusal is correct and should not be
worked around.

### P14 gate audit — exits 3, as designed

Reports P14A's two thresholds as unattainable. Already classified and answered
at unchanged thresholds on P14C's benchmark; the non-zero exit is the audit
doing its job, not an open item.

## Upstream blockers, verified rather than assumed

`P9-U-T1` and `P10-U-T1` both record that they wait on PR #729, the protected
runtime evidence transport repair. Checked directly: #729 is **open, unmerged,
and targets a shadow branch** rather than the default branch. The ledger
statements are accurate and neither terminal has quietly become actionable.

## The shape these findings share

Six of the seven are the same defect wearing different clothes: a check whose
verdict cannot be moved by the thing it is supposed to be checking. An inert
axis, a premise supplied instead of decided, a comparator with zero divergence, a
denominator of one, a false theory no check rejects. Each prints a passing
character for a measurement that was never taken, which is precisely what the
three-valued discipline exists to keep apart — and each is stated here as a
denominator rather than left to be inferred from a silence.
