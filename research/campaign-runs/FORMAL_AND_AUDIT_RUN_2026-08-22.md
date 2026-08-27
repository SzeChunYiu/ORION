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

---

# Follow-up: what has closed, and what P15 turns out to be

## Closed since the run above

**P10 publication membership: FAIL → PASS.** 20 of 571 files inside the
manifest's own declared scope were named by no digest any gate opens; now 0 of
571. Thirteen were the lane's `experiments/` directory — `results/` was a
generator root and `experiments/` was not, so the manifest pinned every committed
number and none of the six drivers that computed them. Four were excluded by an
allowlist of eight file extensions, among them a Lean toolchain pin and a native
shim that decide what the acceptance receipts compile to; the filter is now build
output only. Three were lane-root files the generator names one by one and had
not been told about.

**P7 supplied premise: FAIL → CANNOT_CHECK.** `bridge_match` went from free on
25 of 25 cases with 33,554,432 admissible deciding rules to decided on every one
of 50 with exactly one. The case count went *up* because 50 is what the shipped
block actually asserts; the audit had folded two rows that disagree into a single
case. No published verdict moved — 50 of 50 agreement, and
`canonical_rows_sha256` still reproduces.

**P6 refutation capacity: FAIL → PASS on both checkers.** Every check now
refutes some declared false theory, and the registers grew rather than shrank —
7 to 8 and 8 to 9. The `t4` repair is the clearest: it had been comparing
`ideal_product` against `scientific_admissible`, which is the same expression, so
its zero violations were a property of the expression.

## P15 is not a negative result; it has no results

`papers/paper-15-orion-research-harness/` contains one file, a README, and
declares `DIRECTORY_OPENED / NO_PROTECTED_RESULT`. It carries no scientific
superiority claim and grants no authority, and it says plainly what it still
needs: a paper issue, a claim ledger, a donor matrix against existing
research-execution and workflow-provenance systems, and a protocol freeze, none
of which exists.

That is an honest state rather than a defect, and it should not be counted as a
negative to be driven positive — there is nothing to drive. What *is* checkable
is the guarantee surface the README points at, and it was checked rather than
taken on the README's word: all six named test files exist, and
`packages/orion-research-harness/tests` runs **151 passed**. The load-bearing
separation the paper would claim — a host or capability failure is reported
without being recorded as a scientific result — is under test today.

## P11 is the remaining one, and it is not a measurement gap

The attack audit's `FAIL` does not come from a missing denominator. P11G froze
three decoder arms *and* a best-of-arms combination rule, then published a gate
read from a single arm. Applying P11C's own frozen rule to P11G's own frozen data
does not leave the gate standing.

The arm axis is not inert — 2 of 3 comparable pairs change the verdict, and the
two ends are `P11G_DETERMINISTIC_TREE_DECODER_GAP_NOT_MET` under `UNIVERSAL_L1`
and `..._SUPPORTED` under `UNIVERSAL_EXTRA_TREES`. So this is the mirror image of
P6's inert donor: an axis the terminal genuinely depends on, present in the
published receipt with exactly one value.

The decomposition is more favourable than that sounds and should be reported
either way: holding the decoder fixed and moving only the representation,
the state half carries 86.7% of the published gap in one cell and 55.4% in the
other. The placement claim is not empty. What is not established is the terminal
as published, because the protocol's own combination rule was frozen and then not
applied.

Resolving this honestly means one of two things, and not a third: establish with
evidence that the best-of-arms rule does not govern P11G, or report the terminal
under the frozen rule and run a successor that can carry the claim. Reporting a
single-arm verdict as if the arm were not a choice is the option that is closed.
