# The auditable omission

**Status:** programme methodology note · **Date:** 2026-08-29
**Scope:** result reporting and artifact schema. `scientific_authority_delta: NONE` — this note
creates, upgrades and retracts nothing. It names a practice arrived at under pressure in ORION-13
and states it so the next round applies it deliberately. Sibling of
[the positive-demonstration control](POSITIVE_DEMONSTRATION_CONTROL_V1.md).

---

## The rule

> **When you decline to compute a statistic for a principled reason, record the declination in the
> artifact as a named value. Never as an absent field.**
>
> **And when a check is run, emit its verdict — a check whose result is not written down has not
> been reported, whatever the methods section says.**

An absent field and a deliberate refusal look identical to every reader and every downstream tool.
One is a decision; the other is an oversight. Only writing it down separates them.

## The failure it prevents

Two failures, at opposite ends of the same pipeline.

**At the write end — the silent declination.** A protocol forbids some computation. You honour it,
and the artifact simply has no such field. A later reader cannot tell whether the protocol was
honoured, the analysis was forgotten, or the number was computed and disliked. The most careful
possible action leaves exactly the same trace as the least careful one, so the care is
unrecoverable. Worse, nothing stops the next round from computing it "for completeness" and
reintroducing the violation, because the reason was never written where the numbers live.

**At the read end — the unemitted check.** A methods section commits to an admissibility condition.
The condition is implemented, and even runs. But its verdict is never written into a result
artifact or the manuscript. The commitment is then unfalsifiable: a reader has no way to learn
whether it fired, and no way to learn that the wired form of the check could not have fired.
"Checked and reported, not assumed" degrades to "checked" — and a check nobody can see is worth
what an unrun one is.

## Why "in addition to, not in place of" does not cure it

The tempting escape, when a protocol forbids a statistic, is to report it *alongside* the compliant
figures rather than instead of them, and let the reader weigh it. This does not work when the
objection is to **computing the quantity at all**.

If a protocol declines to pool two sample sets because pooling inflates a confirmatory *n*, then a
pooled p-value violates it no matter which number leads, how it is captioned, or how many caveats
surround it. The pooled *n* is the violation; presentation cannot unwind it. Reporting order is a
remedy for emphasis problems, not for admissibility problems, and reaching for it is a reliable
signal that the wrong question is being answered.

The correct move is to find the claim the evidence *does* support without the forbidden quantity.
That is usually available and usually weaker in form but stronger in standing.

## Worked example — ORION-13, pooled significance

The confirmatory mapping result had discordance counts on two disjoint frozen holdouts: `b=6, c=0`
on the confirmatory set and `b=4, c=0` on the initial one. Pooling gives `b=10, c=0` and an exact
two-sided `p = 0.002` — a clean, favourable number.

ORION-13's own confirmatory protocol states that the strata are *"reported descriptively and not
pooled with the initial 32 cases to inflate the confirmatory sample size."* The pooled test is
precisely that. It was removed.

What replaced it makes the same scientific point without the forbidden quantity: **all ten
discordant pairs across two disjoint frozen holdouts fall the same way, none in reverse.** That is
a statement about *direction*, not about confirmatory sample size, and it needs no p-value. The
per-set exact tests remain the significance evidence — including `initial p = 0.125`, which does
not reach conventional significance alone and is kept visible rather than absorbed into a pooled
figure that would have hidden it.

The declination is then recorded in the artifact as a value:

```json
"pooled_significance_test": "NOT_COMPUTED_BY_PROTOCOL"
```

A reader who wonders why there is no pooled test finds the answer where the numbers are, not in a
commit message or a reviewer thread. A future run that adds one is visibly overwriting a decision
rather than filling a gap.

## Worked example — ORION-11, the unemitted verdict

The mirror case. ORION-11's methods state that arm discrimination is *"checked and reported, not
assumed."* The check is real and implemented in `src/orion/study/p1/arm_validity.py`. But its result
was written nowhere, and the form wired into the campaign was the global one, which fires only when
*every* system shares an outcome vector — so with twelve systems it could not fire at all. A
pairwise form existed, unit-tested and called from no production path.

Running the pairwise form over the same committed records returned `DID_NOT_DISCRIMINATE` for ten of
eleven comparisons. Nothing was miscomputed; the verdict simply had no field to live in, so nobody
could see that the wired check was structurally incapable of returning it.

Had the verdict been an emitted value from the start — one field per comparison — the gap between
the promise and the wired implementation would have been visible on the first run.

## How to apply it

1. **Give every declination a field.** `NOT_COMPUTED_BY_PROTOCOL`, `CANNOT_CHECK`, `WITHHELD_PENDING_<x>`
   — the token matters less than that a token exists where a number would be.
2. **State the reason next to it**, in one sentence, naming the protocol clause. A declination whose
   justification lives only in prose elsewhere decays to an absence at the first copy.
3. **Emit every admissibility verdict**, including the passes. A condition that only writes itself
   down when it fails cannot be distinguished from one that never ran.
4. **Check that the wired form of a check can express the verdict you promised.** A global check
   cannot report a pairwise finding; promising the latter and wiring the former is a real defect
   even when every line of code is correct.
5. **When a protocol blocks a statistic, do not re-present it — replace it.** Find the claim the
   evidence supports without the forbidden quantity, and say plainly that you did.

## Relation to the positive-demonstration control

The positive-demonstration control governs **experiment design**: it asks whether the disfavoured
arm was ever able to exhibit the failure attributed to it. This note governs **reporting**: it asks
whether the decisions taken about the resulting numbers left a trace.

They fail together in a recognisable way. A comparison that is true by construction produces a clean
table; a reporting layer that omits silently ensures nobody can tell the difference from the outside.
The first makes the tautology; the second makes it invisible.
