# Do ORION-08's positive contrasts survive family-wise adjustment?

**Answer: yes — all nine of them.** No claim, margin, metric or terminal changes here.
This closes the half of the multiplicity argument the paired-uncertainty table left open.

## The open half

The table's caption states that its intervals are per-comparison and unadjusted for the
twelve comparisons shown, then argues one direction:

> any family-wise adjustment widens them, so rows already containing zero would continue
> to contain zero.

That is correct, and it protects the paper's **null** readings. It says nothing about the
rows that *exclude* zero — which is the direction a referee asks about, because that is
where the positive claims live. Nine of the twelve rows exclude zero.

## Why this is answerable without a re-run

Per-episode differences are not published, so the bootstrap intervals cannot be recomputed
at a family-wise level. They do not need to be. The table publishes
`paired_win_fraction`, `paired_loss_fraction` and `n_pairs` for every comparison, and
those determine an **exact two-sided sign test**; exact p-values admit exact
**Holm-Bonferroni** adjustment across the family of twelve.

The sign test asks a **different and more conservative question** than the registered one:
whether the *direction* of the paired difference is reliable, not whether the *mean*
difference is. It therefore cannot upgrade any row's registered disposition, and is not
used to. It answers only the multiplicity question.

## Result — 11 of 12 survive Holm at α = 0.05

| comparison | win/loss | sign-test *p* | CI excludes 0 | survives Holm |
|---|---|---|---|---|
| N4_E decision VOI vs info gain | 379/9 | 1.6 × 10⁻⁹⁹ | yes | yes |
| N4_F3 mixed typed vs naive | 139/0 | 2.9 × 10⁻⁴² | yes | yes |
| N4_B REOPEN_WASTEFUL scoped vs unscoped | 156/22 | 4.5 × 10⁻²⁶ | yes | yes |
| N4_F3 mixed typed vs re-derivation | 63/0 | 2.2 × 10⁻¹⁹ | yes | yes |
| N4_A typed vs known graph | 164/46 | 9.8 × 10⁻¹⁷ | yes | yes |
| N4_E decision VOI vs LLM proxy | 181/57 | 3.2 × 10⁻¹⁶ | yes | yes |
| N4_B STALE_MATTERS scoped vs unscoped | 103/26 | 4.9 × 10⁻¹² | yes | yes |
| N4_C ORION vs random verification | 104/27 | 7.4 × 10⁻¹² | yes | yes |
| N4_B STALE_MATTERS scoped vs never | 118/42 | 1.5 × 10⁻⁹ | **no** | yes |
| N4_A typed vs uniform-prior VOI | 87/40 | 3.7 × 10⁻⁵ | yes | yes |
| N4_B REOPEN_WASTEFUL scoped vs never | 34/8 | 6.9 × 10⁻⁵ | **no** | yes |
| N4_F3 unnecessary typed vs re-derivation | 0/0 | 1.000 | no | **no** |

**Every row whose interval excludes zero also survives Holm-Bonferroni.** The paper's
positive contrasts are not multiplicity artefacts, and the caption's caveat can now be
stated in both directions rather than one.

## The one non-survivor is the prespecified tie, and it is exact

`N4_F3 unnecessary typed vs re-derivation` is the registered tie regime — the row where a
positive advantage would have *invalidated* the study rather than supported it. Its
paired outcome is **0 wins and 0 losses out of 200**: not a near-tie, an exact one. Its
failure to survive is the correct outcome, and it doubles as a non-degeneracy check that
the test can return a null when a null is true.

## Two rows disagree with their intervals, and they are not upgraded

`STALE_MATTERS scoped vs never` (118/42) and `REOPEN_WASTEFUL scoped vs never` (34/8) have
mean-difference intervals containing zero while their paired directions survive
adjustment. That is not a contradiction: a mean can be uncertain while a direction is
consistent, which is the signature of **heavy-tailed magnitudes** — many modest wins
offset by a few large losses.

Their registered disposition is set on the mean and **remains undetermined**. Recorded
because the pattern is informative about *why* those two are undetermined — dispersion,
not absence of effect — and because a reader comparing the two columns would otherwise
find the disagreement unexplained. Nothing here licenses reading them as supported.

## Reproduce

```
python3 check_familywise_multiplicity_v1.py \
  --source ../../PUBLICATION_PAIRED_ANALYSIS_V1.json \
  --emit FAMILYWISE_MULTIPLICITY_V1.json
```

Reads only the committed analysis artifact. No experiment, no outcome access, no re-run.
