# ORION05.LOCAL_SUPPORT_ONE_OBSTRUCTION.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Terminal:** `THEORY_PROVED__INDEPENDENTLY_CHECKED`
**Scientific authority delta:** `NONE`
**New blocker raised:** none

---

## 1. What changed

One additive directory:

```
papers/orion-05-tare-expressivity/theory/local-obstruction-v1/
```

No manuscript, proof, receipt, ledger or `rounds/` byte was modified.

## 2. What was established

`MANUSCRIPT_V3_REFINED.md` says the zero-sum exchange has *"exactly four failing
ordered class pairs at support two."* That is a count, resting on the R6S
enumeration. This packet turns it into a **proved complete classification**:

```
( (0,1), (1,0) )   ( (1,0), (0,1) )   ( (0,1), (1,1) )   ( (1,1), (0,1) )
```

— four ordered, **two** unordered types up to coordinate swap. The proof is four
lines: only singleton deletions are proper at `w = 2`; a singleton deletion needs
class `(0,0)`; odd-alpha forces one coordinate to `alpha = 0` and one to
`alpha = 1`; the only nonzero `alpha = 0` class is `(0,1)`.

**Structural corollary.** Every local obstruction has the same shape: a
coordinate redundant for local frame anticommutation (`alpha = 0`) but
load-bearing for the shared Tag syndrome (`beta = 1`), paired with the coordinate
carrying the odd anticommutation bit. The manuscript already gestures at this;
it is now proved to be the *only* possible shape.

## 3. Independent verification

The checker imports nothing from the R6S implementation or the generating proof —
only the three Lemma B definitions — and compares the claim against enumeration
rather than filtering by it.

| check | result |
|---|---|
| A — brute force over all 16 ordered pairs | matches the four claimed exactly |
| B — Lemma B's conclusion for `w = 3..8` | `0` irreducible at every support |
| C — odd-alpha tuple count over support 2..8 | **43,688**, equal to the manuscript |
| C′ — support-two failure count | **4**, equal to the manuscript |
| D — negative controls | **4/4 fire** |

Check C matters more than it looks. It validates the **transcription**: if the
class map or descent rule had been copied wrongly, the recomputed tuple count
would not have landed on the manuscript's independently recorded 43,688. A
classification built on a mis-transcribed definition would be worthless, so this
is a precondition rather than a flourish.

## 4. A control failed, and the control was wrong

An initial negative control asserted that the properness restriction on the
deleted subset was load-bearing at `w = 2`. It did not fire. Investigation showed
the **control** was false: odd-alpha forces `alpha_1 + alpha_2 = 1`, so the full
support can never sum to `(0,0)` and properness is vacuous at `w = 2` — though it
remains essential for `w >= 3`, where Lemma B needs the remaining frame nonempty.

The control was replaced with one that does bite, and the finding is recorded as
an observation in `THEORY.md` §3 rather than quietly deleted.

## 5. Adverse and null evidence

All preserved. In particular the support-one insufficiency witness (`5 < 6`) is
untouched — it is what makes `kappa_R6M = 2` sharp, and this packet explains the
obstruction's *shape*, not its global force.

The local/global separation #1617 insists on is stated explicitly as a scope
limit: local irreducibility does **not** imply global support-two optimality.

## 6. Donor boundary and novelty

**No novelty claimed.** The argument is elementary `F_2`-linear algebra over a
four-element class set; finite-group, zero-sum and linear-dependence arguments
own generic parity compression. The ORION-specific content is the exact
classification for this frozen grammar and class map, plus the structural
reading.

## 7. Recommended manuscript action — referred, not taken

`MANUSCRIPT_V3_REFINED.md` §"The proof obstruction is the compiler mechanism"
could replace its bare count with the classification, e.g.:

> "The zero-sum exchange fails at support two on exactly two class configurations
> up to coordinate swap, `{(0,1),(1,0)}` and `{(0,1),(1,1)}` — four ordered pairs
> in total. In every case the obstruction has the same form: a coordinate
> redundant for local frame anticommutation yet load-bearing for the shared Tag
> syndrome, paired with the coordinate carrying the odd anticommutation bit.
> Support two is therefore not merely where the proof stops; it is where the
> grammar admits exactly one structural coupling trade."

This is an explanatory upgrade with no authority change. It is **not taken here**
— manuscript edits belong in their own PR, per #1608.

## 8. Blocker status

`ORION-05 IS NOT BLOCKED BY THIS LANE.` #1617's recommendation for ORION-05 is
*submit rather than expand*; this packet strengthens the explanation of an
already-sharp result without adding a prerequisite.

**Upgrade B — the finite global obstruction-basis conjecture — is explicitly not
started.** It is a separate programme with its own protocol identity and must not
hold the submission lane open.
