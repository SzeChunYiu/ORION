# P1-U R6: role-free identifiers — prospective freeze, V4 (final)

**Supersedes V3, same day.** V1, V2 and V3 stand unedited, as do the three
precondition aborts they produced. **No arm has been scored under any version of
this freeze.** Nothing downstream of an outcome has been touched, because no
outcome exists.

This is the last revision of this precondition. If the check specified here
fails, that is the result and it is reported as a negative.

## What changed, and why

V3 stratified the held-out split by role, which was the right fix, and reported:

| handle prefix length | held-out informedness |
|---|---|
| 1 | **0.4196** |
| 2 … 12 | 0.0 |

V3's ceiling of `0.0` therefore aborted on the 1-character prefix.

The shape of that table is the finding. A longer prefix **strictly refines** the
partition a shorter one induces and carries strictly more information about the
handle. If the handle encoded the pair role, informedness would be
non-decreasing in prefix length. It collapses to zero instead. A signal that
vanishes under refinement is not a signal; it is the majority vote fitting noise
in a coarse partition — sixteen hex buckets, a majority label fitted from about
twenty-four episodes, so roughly one and a half episodes per bucket.

So V3's ceiling was unattainable by construction at length 1, for *any* handle
scheme including a perfect one. That is the failure recorded in
`research/failures/2026-08-handicapped-baseline-unattainable-margin/`: a
threshold no honest candidate could clear is not a strict test, it is a broken
one. It is also precisely the case P4's identifiability register anticipated —
its `digest-prefix` probe is registered as *a noise control on the instrument,
rather than a probe of the battery*, for exactly this reason.

Lowering the ceiling to `0.42` so it passes would be tuning against an outcome
and is not done. Instead the noise floor is **measured**.

## Precondition 2, final form

Same statistic, same stratified held-out split, same prefix range 1–12. The
ceiling is replaced by a permutation null:

1. Compute observed held-out informedness at each prefix length, as in V3.
2. For each prefix length, build a null by randomly permuting the role labels
   **1000 times** (seed `20260821`, fixed here), recomputing held-out
   informedness each time with the split held fixed. Permuting the labels
   destroys any real association while preserving the cue distribution, the
   split, and the class balance, so the null is the distribution of this
   statistic under "the handle carries nothing".
3. The precondition **fails** at a prefix length if the observed value exceeds
   the **99th percentile** of that length's null. It passes otherwise.

A one-sided test at the 99th percentile over 12 lengths is deliberately strict:
under the null roughly one length in a hundred would be expected to exceed it by
chance, so 12 lengths give about a 1-in-8 chance of a spurious failure. That
asymmetry is chosen on purpose — a spurious *failure* costs an investigation, a
spurious *pass* would license a claim.

The report carries the observed value, the null's 99th percentile and the
empirical p-value at every prefix length, whichever way each falls.

Precondition 1 is unchanged: the repaired leakage audit must report zero hits in
every category across all 96 episode-arms.

## Everything else is unchanged

The salt, the handle length, the eight anonymised surfaces, the arms, the
comparator, the corpus, the scoring functions, every evaluator threshold, and
the claim scope from V1 §5 all carry over exactly. No version of this freeze has
altered anything in the scoring path.

## On four versions in one day

Each supersession is recorded rather than edited away, and each was permitted by
the same fact: **no arm had been scored.** V1 fitted and scored a classifier on
the same rows and so reported 1.0 for a cryptographic hash. V2 held it out but
split on a sort that is nearly anti-correlated with the role. V3 stratified the
split correctly and hit a ceiling unattainable at the coarsest prefix. All three
were defects in a precondition, found by running it, and none of them saw an
outcome.

That is the honest account, and it is also the warning: a precondition revised
four times is one revision away from being a precondition tuned to pass. This
version is final. If the permutation test fails, the run is reported as a
precondition failure and the leak stays open.
