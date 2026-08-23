# The tightest possible confidence interval, produced by an instrument with no resolution

**Observed:** 2026-08-22, auditing P2's two completed AutoResearchBench Wide
campaigns after finding that the ledger blocker for both pointed at a pull
request that had been closed without merging.

## Failure

`P2_WIDE_OPENAIRE_MATCHED_RESULT_V3.json` reports its paired analysis as

```json
"paired_distinct_question_iou": {
  "n": 399, "ties": 399, "wins": 0, "losses": 0,
  "ci95_low": 0.0, "ci95_high": 0.0,
  "bootstrap_resamples": 10000, "bootstrap_seed": 20260821
}
```

A zero-width 95% interval centred on zero, over three hundred and ninety-nine
matched questions, from ten thousand resamples. Read as a non-inferiority
result that is as strong as a bootstrap can be. It is the opposite. Resampling
399 identical differences returns the same zero-width interval however many
resamples are drawn and at any *n*: the interval would look exactly this
convincing with four questions.

The reason all 399 differences are identical is one layer down and does not need
an invented threshold to state, because the campaign freezes its own:

| campaign | best arm avg IoU | frozen required delta | distinct candidate digests | distinct evaluator digests |
| --- | --- | --- | --- | --- |
| V1 | 0.003924 | 0.03 | **1** of 3 | 1 of 3 |
| V3 | 0.004374 | 0.03 | 3 of 3 | **1** of 3 |

`scientific_rule.required_official_avg_iou_delta` is the difference in average
IoU the frozen rule demands before superiority is supported. In both campaigns
the *entire* measured performance of the best arm is roughly a seventh of that
difference. Deleting a competing arm outright would not reach the threshold. All
three systems retrieve almost nothing, so they tie on nearly every question, so
their aggregate scores are equal, so their evaluator output files are
byte-identical — in V3, from three genuinely different candidate files.

V1 adds a second defect on top: its three arms carry one candidate digest
between them, so that campaign scored a single system against itself three times
and reported the resulting 399 ties as a paired equivalence interval.

## Why it survived

Every guard the campaign had was pointed at custody and transport, and every one
of them worked. V3 correctly terminated `P2_WIDE_EXTERNAL_V3_CANNOT_CHECK`
because provider validity reached 0.716 against a frozen 0.90. The transport
probe was hash-bound, revalidated at score time, and fail-closed on forged URL
digests, gold-access laundering and promotion laundering. Candidate hashes were
frozen before gold and revalidated after scoring. None of that machinery asks
whether the comparison *could have come out differently*.

Two of the four symptoms were already known and written down in the right words
in the wrong file. `scripts/score_wide_comparison.py` refuses the unseeded
`max_iou_at_k` family as "an absent measurement wearing the costume of a number"
and refuses a metric whose denominator is missing. The published result artifacts
came out of a different analyzer, which publishes that family anyway — and in
both campaigns it *decreases* in k, from 0.0044 at k=1 to 0.0 at k=2, which a
maximum over the top k cannot do. Both artifacts also report every runtime total
— tokens, duration, tool calls, turns — as exactly zero.

A rule that lives in one scorer is not a rule.

## Family

This is the vacuous-guard family again, at the level of a whole campaign rather
than a single check:

- a rate returning `0.0` because its denominator was empty (`study/metrics.py`);
- a differential agreeing 60/60 about a constant `False` (P8's authority calculus);
- `check_reopening` asserting set-algebra tautologies over 130,320 cases (P6);
- `donor_conservativity_violations` comparing a variable to the expression it
  was just assigned (P6);
- a second implementation that diverges on 0 of 320 points because it is a
  syntactic paraphrase of the first (P6).

The shared shape: a number that could only ever have taken one value, presented
in the position where a measurement goes. What is new here is the direction of
the illusion. The others report a *harmless* value — a zero harm rate, a clean
agreement. This one reports the *strongest possible* value, and the tighter the
interval, the more convincing the artifact looks.

## Guard

`orion.study.p2.comparison_resolution` reads a published campaign result and
asks the single question the result does not ask itself: could this campaign
have reported anything else. It reports resolution and takes no view on whether
the systems are equivalent.

Four checks, one root and three symptoms:

0. every arm below the campaign's **own** frozen effect threshold;
1. arms sharing a candidate digest, or distinct candidates sharing one evaluator
   digest;
2. an all-ties paired split, distinguished from a genuinely tight interval —
   `ties == n` with no wins and no losses gives zero width at any *n*, while an
   interval earned from varying differences narrows with *n*;
3. a `max_iou_at_k` family that decreases in k, and runtime totals that are
   uniformly zero.

Findings are split into resolution findings and reporting findings, because
"this comparison could not have produced a different verdict" and "this artifact
publishes a metric its own scorer excludes" are different claims. That split was
forced: the guard's own non-vacuity control failed its first test for publishing
the sampled family while genuinely having resolution.

The control matters more than the findings. A guard that fires on everything
reports the guard, not the subject — which is the exact failure being named, and
there would be no defence against having committed it here. So a campaign that
does have resolution is carried in the module beside the finding, and each of
the four checks is separately tested against a case it must not fire on: a tight
interval earned from real wins and losses, a flat at-k curve, a single zero total
among non-zero ones, and a campaign above its own threshold.

## What is not established

Why retrieval scores near zero on a benchmark whose gold is reachable. The guard
measures the instrument, not the retrieval. That the arms are at the floor is
measured here; the reason they are is not, and finding it out is the work that
has to happen before a fourth transport version is worth running — a fourth
campaign scored at IoU 0.004 would spend the same effort to learn the same
nothing.

---

## Addendum, same day: the ceiling case, in P4

Running the same question — could this have come out differently — over the
other papers' panels found the mirror image, and it is decided rather than
merely reported.

P4's protected V2 panel decides three hypotheses from eleven systems' rates:

| metric | across the panel | hypothesis | declared |
| --- | --- | --- | --- |
| `false_promotion_rate` | 0.0 → 0.917 | H1 | `PASS`, ci95 [-0.553, -0.447] |
| `clean_coverage` | **1.0 for all eleven** | H2 | `PASS`, ci95 [0.0, 0.0] |
| `correct_cannot_check_rate` | **1.0 for all eleven** | H3 | `NOT_SUPPORTED`, ci95 [0.0, 0.0] |

H2 is a non-inferiority guard on a metric that every system in its own
comparator set achieves perfectly. It cannot fail. H3's negative is the same
fact wearing the other sign — and that pairing is the useful part: saturation is
not a bias toward optimism, and looking only at the `PASS` rows would have
missed half of it.

The later identifiable V3 panel repairs one of the two. There
`correct_cannot_check_rate` varies (1.0, 0.5, and 0.0 across the panel), so H3
becomes a real separation. `clean_coverage` is still 1.0 for every system.

### What P4 already knew

This one is not a discovery, and saying so is the point of recording it here.
P4's manuscript states the same finding in prose, with the same counts:

> Clean coverage is 1.0 for all eleven panel systems and for all eight
> ablations, and the correct-`CANNOT_CHECK` rate is 1.0 for all eleven systems
> and is not instrumented in the ablations at all. Only false authority
> promotion varies […] H2's non-inferiority pass and H3's null are statements
> about a battery in which neither quantity was ever observed to move. […] H2
> and H3 should be read as design limits rather than as comparative findings.

So the paper is honest and the numbers were never hidden. Two things were still
wrong. The limitation lived in a limitations paragraph rather than in anything
that could refuse a score, and P4's ledger — the object that decides whether a
terminal has been earned — did not carry it at all; its blocker for the
identifiability gate discussed only H3's label recoverability. A caveat a
careful reader must find is not a gate, and a finding the ledger does not know
about cannot block anything.

The generalisable half is that the check is cheap and general. It needs nothing
but the per-system rates, it would have refused H2 in both of P4's
constructions, and it will fire on a panel whose authors have *not* noticed —
which is the case it exists for.

### The distinction that had to be got right

A zero-width interval has two causes that mean opposite things.

*Saturation.* Every system holds the same value; the difference is constant
because there is nothing to differ about. Nothing is learned.

*Separation.* The systems hold different constants — one at the ceiling, another
at the floor — so the difference is constant and maximal. Something is learned,
and it is the strongest thing the metric can say. What is still not learned is
any measure of uncertainty: the width is zero because the sample is constant,
not because the estimate is precise.

Merging them under "degenerate interval" would either excuse a saturated guard
or condemn a perfect separation. `orion.programme.panel_resolution` reports them
by name, and the case that must stay quiet is tested alongside the case that
must fire — including an interior saturation, a missing rate that must not be
read as zero, and a one-case rate difference (1/360) that must not be absorbed
as float noise.
