# The A6 composition route — the one top-tier path that has not been tried

**Status:** `CANDIDATE_COMPOSED_THEOREM__UNPROVED`
**Scientific authority delta:** `NONE`. Nothing is claimed proved here. This identifies a
target and argues it is worth attempting.

## Why the subtraction verdict was premature

`A6_DONOR_SUBTRACTION_V1.md` and its two adversarial follow-ups examined ORION-16 and
ORION-18 **separately** and found eleven of twelve results inherited. That conclusion is
correct about each paper alone, and it led me to recommend a second-tier formal-methods
venue.

It skipped the thing A6 actually asks for. The programme is titled *"certificate lifting +
non-amplifying scientific authority"*, and its first Phase 1 task is **"merge theorem
objects before writing a merged narrative"**. I subtracted two papers; I never composed
them.

## The papers are formally disjoint, and that is the opportunity

Measured over both formal cores:

| | mentions of repair / revalidate / reopen | mentions of authority / authorization |
|---|---|---|
| ORION-16 `FORMAL_CORE_V2_1` | **13** | 4 |
| ORION-18 `FORMAL_CORE_V2_1` | **0** | 29 |

**Cross-references between them: zero, in both directions.**

ORION-16 is dependency repair with no authority notion. ORION-18 is authority with no
repair notion. They are adjacent papers in one programme that never touch.

The donor fields have the same gap, and this is why the composition is not obviously
inherited:

- **Truth maintenance / abstract interpretation** supply repair, invalidation and
  optimality. They have **no notion of authority** — a JTMS re-derives a belief; it does
  not ask by what right the re-derivation licenses anything.
- **Deontic logic / authorization calculi** supply permission, obligation and
  non-amplification. They have **no notion of dependency repair** — they do not model a
  mechanism that re-certifies claims after a change.

So each half is donor-owned and the *composition* is owned by neither.

## The composed claim worth attempting

> **Candidate.** Selective revalidation is not an authority-amplification channel: for any
> change `X` and affected set `Aff_D(E,X)`, the authority carried by certificates after
> repair is bounded by the authority available before the change together with whatever
> the revalidation's own root class supplies — and in particular, repeated repair cannot
> increase it.

**Why this is a real question rather than a restatement.** ORION-16's repair *re-certifies*
claims. Re-certification produces a new certificate. If re-derivation after a change is
cheaper, or draws on a weaker root class, than the original derivation, then **repair is a
laundering channel**: run a change, repair it, and emerge with authority that the original
premises never licensed. Nothing in either paper currently forbids this, because ORION-16
has no authority to track and ORION-18 has no repair to constrain.

That is a genuine vulnerability in the composed system, and it is the kind neither donor
field would have found — TMS never asks it because it has no authority; deontic logic never
asks it because it has no repair.

## Why this is the top-tier shape and the separate papers are not

A top-tier contribution here is not "we proved a new theorem about permission" — that
attempt died with Proposition 12. It is:

*a mechanism and a normative constraint, composed, with a proof that the mechanism cannot
violate the constraint.*

That has the right form. It is falsifiable — exhibit a repair sequence that amplifies
authority and the claim dies. It is checkable — ORION-18's hostile-mutation machinery
already tests non-amplification, and ORION-16's already tests repair minimality; the
composed property is testable with both. And it answers the review's charge directly:
composition is not decision theory, and no decision-theoretic account produces it.

## What must happen, honestly

1. **Merge the theorem objects.** ORION-16's certificate-aware repair (Theorem 3) and
   ORION-18's root classes (Definition 21) must be stated over one signature. Neither paper
   currently has the vocabulary to express the other's premise.
2. **State the amplification property precisely**, which requires a measure of authority
   that repair could increase. ORION-18's `Perm` is three-valued, not ordered, so
   "amplification" needs defining — this is real work and it may be where the claim dies.
3. **Attempt the proof, and attempt the counterexample first.** Given that two of my three
   earlier candidates fell, the counterexample deserves the first hour: construct a repair
   sequence that promotes `CANNOT_CHECK` to `AUTHORIZED` without new protected evidence. If
   one exists, that is a finding about the composed system and a stronger paper than a
   proof would have been.
4. **Only then write the merged narrative.** A6 puts the merge before the narrative for
   exactly this reason.

## Revised recommendation

My earlier advice — retarget 16/18 to formal methods now — was **premature**. It was
correct about the papers as they stand and wrong about the programme, because it assessed
two papers that were never meant to stand alone.

The composition is the top-tier attempt, it has not been made, and it is buildable without
external corpora, live models or adjudicators. It should be tried before expectations are
adjusted.

If the composed claim falls the way Proposition 12 did, the formal-methods route remains
and nothing is lost but the time. If it holds, it is the one result in this programme that
no donor field contains.
