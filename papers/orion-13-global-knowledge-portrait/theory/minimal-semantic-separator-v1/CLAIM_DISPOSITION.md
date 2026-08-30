# ORION13.MINIMAL_SEMANTIC_SEPARATOR.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Terminal:** `THEORY_PROVED__COMPUTED_ON_FROZEN_GOLD__CONFIRMS_EXISTING_SCOPE`
**Scientific authority delta:** `NONE`
**New blocker raised:** none

---

## 1. What changed

One additive directory under
`papers/orion-13-global-knowledge-portrait/theory/`. No manuscript, gold,
evaluation or `journal_package/` byte was modified.

## 2. Headline

On the frozen public-reference gold, the minimum merge-sufficient coordinate set
has size **one**, and the unique reduct is **`{polarity}`**. It survives the
disjoint 32-case confirmatory set with zero collisions (permutation null
`0/20000`).

The reason is that the gold verdict is **perfectly confounded** with polarity
agreement, in both sets:

| set | non-COMPATIBLE cases | all `POSITIVE -> NEGATED`? | all COMPATIBLE agree on polarity? |
|---|---|---|---|
| v1 | 4 | yes, 4/4, one family | yes, 28/28 |
| v1.1 confirmatory | 6 | yes, 6/6, one family | yes, 26/26 |

The two other families present contribute only `COMPATIBLE` cases and so exercise
no discrimination at all.

## 3. This confirms the manuscript; it does not contradict it

`06-results.tex` already states that *"full coordinate necessity [is a] separate
question whose outcome remains undetermined."*

That scoping is **correct**, and this packet supplies the exact reason the paper
does not currently have: there is not one opposite-verdict case that polarity
fails to separate, so no coordinate other than polarity can acquire a collision
witness on this evidence. Necessity is untestable here **in either direction**.

This is a **corpus-design limitation**, not a defect in the mapping rule and not
an overclaim in the manuscript. Recorded explicitly because the finding is easy
to misread as "the other coordinates don't matter." It does not say that. It says
the gold does not test them.

## 4. Independent reproduction of the headline comparison

Flat predicate canonicalization false-merges exactly `6/32 = 0.1875` on the
confirmatory set — the abstract's headline figure, reproduced from the frozen
gold — and that false-merge set **is** the polarity-flip set.

So the entire measured advantage of coordinate-governed mapping over flat
canonicalization *on this corpus* is carried by the polarity coordinate. The
comparison stands and is verified; its mechanism is now named rather than left
implicit. This discharges part of the #1609 ORION-13 line on independent
verification.

## 5. Adverse and null evidence

All preserved. `full coordinate necessity` remains `undetermined`. Raw-text
expert atlas, generated-portrait recoverability and downstream utility remain
undetermined and untouched. The 36-case constructed-corpus `27/36` ceiling is a
separate result and is not touched.

Nothing was promoted. No `CANNOT_CHECK` became a pass.

## 6. Recommended manuscript action — optional, referred, not taken

The manuscript needs **no correction**. Two optional one-line strengthenings are
available, both of which only make existing caution more precise:

1. In Results, after the `0.1875` comparison: note that on this corpus the
   difference is carried by the polarity coordinate.
2. Where full coordinate necessity is declared undetermined: note that it is
   undetermined *because* every opposite-verdict case in both frozen sets is a
   polarity contrast, so no other coordinate has a collision witness.

Both are additive and authority-neutral. Neither is taken here; manuscript edits
belong in their own PR per #1608.

## 7. The constraint is the next study

A coordinate-necessity study needs opposite-verdict cases in the families that
currently contribute none — `different_name_same_referent` and
`valid_invalid_representation_mapping` with non-`COMPATIBLE` gold — plus
`DISTINCT_REFERENT`, `DISTINCT_CONSTRUCT` and `DISTINCT_MEASUREMENT` verdicts.
The case schema already admits all of these; the frozen corpus never instantiates
them.

That corpus must be frozen **before** looking at which coordinates fail. This is
optional successor science and is **not** a submission blocker.

## 8. Donor boundary

**No novelty claimed.** Sufficiency-as-hitting-set and the reduct formulation are
donor-owned rough-set / discernibility theory — the same object as ORION-09's
separator complexity. The ORION-specific content is the exact result on this
frozen gold and the confounding diagnosis.

## 9. Blocker status

`ORION-13 IS NOT BLOCKED BY THIS LANE.`
