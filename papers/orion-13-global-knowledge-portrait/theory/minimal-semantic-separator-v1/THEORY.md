# ORION13.MINIMAL_SEMANTIC_SEPARATOR.v1 — THEORY

**Paper:** ORION-13 — Global Knowledge Portrait
**Successor id:** `ORION13.MINIMAL_SEMANTIC_SEPARATOR.v1`
**Candidate source:** PR #1617, Priority A
**Authored:** 2026-08-28
**Status:** `THEORY_PROVED__COMPUTED_ON_FROZEN_GOLD__CONFIRMS_EXISTING_SCOPE`
**Scientific authority delta:** `NONE`
**Frozen paper bytes modified:** NONE

---

## 1. Why this successor exists

The candidate note asks which semantic coordinates are actually indispensable for
the merge verdict on the frozen public-reference cases, rather than asserting
that all of them are. Its stated value is that it *"permits the science to
simplify"*.

ORION-13 already declines the necessity claim. `06-results.tex` states that

> full coordinate necessity [is a] separate question whose outcome remains
> undetermined.

This packet does **not** contradict that. It confirms the scoping decision was
right and supplies the **exact reason** it must stay that way, which the paper
does not currently have.

---

## 2. Setting

Each public-reference case is a pair of projections `(L, R)` with a gold
`meaning_relation`. The case schema supplies the semantic coordinates; the three
identifier fields (`projection_id`, `source_id`, `source_span`) are excluded,
leaving seven:

```
construct_ids   measurement_ids   modality   polarity
predicate       referent_ids      temporal_context_ids
```

Each case contributes one **agreement pattern**: coordinate `j` yields the bit
`[ L_j == R_j ]`. This is the natural encoding for a merge decision, since a
merge rule reads whether the two sides agree on a coordinate, not the values.

### Definition (sufficiency)

A subset `S` is **merge-sufficient** on a case set when no two opposite-verdict
cases share the same agreement pattern restricted to `S`.

### Theorem (hitting-set characterization)

`S` is merge-sufficient iff `S` intersects the discernibility set
`D(x, x') = { j : pattern_j(x) != pattern_j(x') }` of every opposite-verdict
pair. Hence the minimum sufficient sets are the minimum hitting sets of that
family, and the minimal ones are its reducts.

**Proof.** Sufficiency fails exactly when some opposite-verdict pair collides
under `pi_S`, i.e. agrees on every coordinate of `S`, i.e. `S ∩ D(x,x') = empty`. ∎

This is **donor-owned** rough-set / discernibility mathematics — the same object
as ORION-09's separator complexity and ORION-14's promotion reduct. No novelty is
claimed for it.

---

## 3. Results on the frozen gold

Two disjoint frozen sets already exist in the repository, so no challenge set had
to be constructed:

| set | cases | COMPATIBLE | non-COMPATIBLE | shared ids |
|---|---|---|---|---|
| `public-reference-v1` (derivation) | 32 | 28 | 4 | — |
| `public-reference-v1.1-confirmatory` (challenge) | 32 | 26 | 6 | **0** |

Reducts were derived on **v1 only**. The challenge set was not consulted while
choosing them.

### 3.1 `k* = 1`, and the unique reduct is `{polarity}`

Exhaustive enumeration over all `2^7 = 128` subsets gives a single minimal
sufficient subset: **`{polarity}`**. It is also the core. The other six
coordinates — `construct_ids`, `measurement_ids`, `modality`, `predicate`,
`referent_ids`, `temporal_context_ids` — appear in **no** reduct.

### 3.2 It survives the held-out challenge set

`{polarity}` is merge-sufficient on the disjoint 32-case confirmatory set as
well, with **zero** collisions. Structure-free null on the derivation set:
`0 / 20000` random relabellings admit any sufficient singleton.

### 3.3 Why — the gold is perfectly confounded with polarity

This is the load-bearing diagnostic, and it holds in **both** sets:

- every non-COMPATIBLE case is from the `polarity_modality_attribution_context`
  family and is exactly a `POSITIVE -> NEGATED` flip — 4/4 in v1, 6/6 in v1.1;
- every COMPATIBLE case has polarity agreement — 28/28 in v1, 26/26 in v1.1.

So the gold verdict **is** the polarity-agreement bit on this corpus. The other
two families present (`different_name_same_referent`,
`valid_invalid_representation_mapping`) contribute only COMPATIBLE cases and
therefore exercise no discrimination at all.

### 3.4 Independent reproduction of the headline comparison

Flat predicate canonicalization — merge iff predicates agree — false-merges
exactly `6/32 = 0.1875` of the confirmatory set, reproducing the manuscript's
headline figure exactly. That false-merge set **is** the polarity-flip set.

Consequently the entire measured advantage of coordinate-governed mapping over
flat predicate canonicalization *on this corpus* is carried by the **polarity**
coordinate. The comparison stands and is reproduced; its mechanism is now named.

---

## 4. What this does and does not mean

**It does not mean the other six coordinates are useless.** It means the frozen
gold **does not test them**. There is not a single opposite-verdict case that
polarity fails to separate, so no necessity claim for any other coordinate could
be supported by this evidence — in either direction.

This is a **corpus-design limitation**, not a defect in the mapping rule, and not
a defect in the manuscript, which already declines the necessity claim.

**What the paper may say, unchanged:** the scoped C5/C9 mapping result, the zero
false merges, and the `0.1875` comparison — all reproduced here.

**What the paper must continue not to say:** that every typed coordinate is
necessary, or that coordinate-governed mapping's advantage generalizes beyond
polarity contrasts on evidence of this shape.

---

## 5. The constraint is the next study

Any future coordinate-necessity study needs opposite-verdict cases in the
families that currently contribute none. Concretely, it needs
`different_name_same_referent` and `valid_invalid_representation_mapping`
instances whose gold relation is **not** `COMPATIBLE`, plus `DISTINCT_REFERENT`,
`DISTINCT_CONSTRUCT` and `DISTINCT_MEASUREMENT` verdicts — all of which the case
schema already admits but the frozen corpus never instantiates.

Only then can a coordinate other than polarity acquire a collision witness. The
minimum decisive design is: freeze such a corpus **before** looking at which
coordinates fail, then recompute the reduct.

---

## 6. Strongest falsifier

An opposite-verdict case in either frozen set that `{polarity}` fails to
separate. Refuted exhaustively on both sets — 64 cases, zero collisions.

The result is a statement about these two frozen corpora and nothing wider. It
would be falsified as a *general* claim by any corpus in which polarity is not
sufficient, which is precisely what §5 asks someone to build.

---

## 7. Donor boundary and authority

The mathematics is **donor-owned** rough-set / discernibility theory. No novelty
is claimed.

`scientific_authority_delta = NONE`:

- the scoped C5/C9 mapping claim is unchanged;
- the zero-false-merge result and the `0.1875` comparison are unchanged, and both
  are independently reproduced here;
- `full coordinate necessity` remains `undetermined`, exactly as
  `06-results.tex` already states — this packet supplies the reason, not a new
  verdict;
- raw-text/expert/downstream claims remain follow-up, per #1609;
- no manuscript, gold, evaluation or `journal_package/` byte is modified.

**ORION-13 is not blocked by this lane.**
