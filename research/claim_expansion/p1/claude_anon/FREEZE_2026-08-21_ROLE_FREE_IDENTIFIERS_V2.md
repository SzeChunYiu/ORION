# P1-U R6: role-free identifiers — prospective freeze, V2

**Supersedes `FREEZE_2026-08-21_ROLE_FREE_IDENTIFIERS_V1.md`, same day.**
V1 stands unedited beside this file, and the run it produced —
`ROLE_FREE_RERUN_V1.json`, a precondition abort with no arm scored — stands as
the record of what V1 specified. This document exists because V1's precondition 2
was wrong, and the anti-tuning clause in V1 §6 requires a change to a frozen
parameter to be a supersession rather than an edit.

## What changed, and why

V1 precondition 2 required that a majority-vote classifier fitted on any prefix
of the handle score informedness `0.0` for the pair role. Run on the 48
episodes, it reported **1.0 at every prefix length from 2 to 12**, and `0.42` at
length 1.

That is not leakage. It is the classifier memorising an identifier. The handles
are 48 distinct values; a 2-character hex prefix has 256 possible values, so
almost every episode has a unique prefix, and a majority vote fitted and scored
on *the same* 48 rows reproduces the training labels exactly. Any injective cue
scores 1.0 under that instrument, including a cue with no information about
anything.

This is a known shape in this repository and it has cost time before. P4's
identifiability register hit it in probe 9, which counted character classes over
raw bodies containing seed-derived hex: it fingerprinted each case individually,
generalised to nothing, and reported a clean `-0.03` on a construction whose
label a plain character count actually recovers at `1.0`. The register's fix was
to make the probe coarse enough to generalise. The same correction applies here,
in the opposite direction: **a probe too fine to generalise cannot distinguish a
real cue from an identifier, so it reports whichever answer its polarity makes
convenient.**

What the precondition should ask is whether the handle lets someone who has
*not* already seen the mapping predict the role. That is a generalisation
question and it needs held-out data.

## Precondition 2, restated

Fit the majority-vote classifier on one half of the episodes and score it on the
other half, never on the rows it was fitted on. The split is by sorted episode
id, alternating, so it is determined by the corpus and not chosen: even indices
fit, odd indices score. Both halves must contain all three roles, and the runner
aborts if either does not — a held-out split that omits a role cannot detect
that role being predicted, which would be this same failure a third time.

The ceiling is unchanged: **held-out informedness must be `0.0` at every prefix
length from 1 to 12.** A cryptographic hash of the episode id carries no
recoverable role signal, so `0.0` is the honest expectation rather than a
generous threshold; a non-zero value here would mean the handle scheme really
does sort by role and the repair is not a repair.

Precondition 1 is unchanged: the repaired leakage audit must report zero hits in
every category across all 96 episode-arms.

## Everything else is unchanged

The salt, the handle length, the eight anonymised surfaces, the arms, the
comparator, the corpus, the scoring functions, every threshold in the evaluator,
and the claim scope in V1 §5 are all carried over exactly. Nothing about the
scoring path is touched by this supersession; the only edit is to a precondition
that was measuring the wrong thing.

## Anti-tuning, restated

If this precondition is changed again after an outcome is seen, this document is
superseded by a further dated one, and both prior results stand beside it. The
result produced under V1 is a precondition abort, and it stays in the record as
such.
