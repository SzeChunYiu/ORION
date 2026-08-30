# ORION05.LOCAL_SUPPORT_ONE_OBSTRUCTION.v1 — THEORY

**Paper:** ORION-05 — TARE Expressivity
**Successor id:** `ORION05.LOCAL_SUPPORT_ONE_OBSTRUCTION.v1`
**Candidate source:** PR #1617, `WAVE1_DEEP_UPGRADES_ORION05_14_17_23`, Upgrade A (ranked #1 by expected value)
**Authored:** 2026-08-28
**Status:** `THEORY_PROVED__INDEPENDENTLY_CHECKED`
**Scientific authority delta:** `NONE` — strengthens the explanation of an existing sharp result
**Frozen paper bytes modified:** NONE

---

## 1. Why this successor exists

`MANUSCRIPT_V3_REFINED.md` §"The proof obstruction is the compiler mechanism"
states:

> The zero-sum exchange has exactly four failing ordered class pairs at support
> two.

That is a **count**. The paper does not say *which* four, nor why those four and
no others. The count currently rests on the R6S enumeration
(43,688 odd-`α` class tuples through support eight).

This packet promotes the count into a **complete classification with a proof**,
so the sharpness of `kappa_R6M = 2` is explained rather than merely observed.
Upgrade A is ranked #1 in #1617's cross-paper value table because it is almost
entirely analytic from the existing proof and carries negligible risk.

---

## 2. Setting — definitions taken verbatim from Lemma B

From `HUMAN_PROOF_R6S_2026-08-22.md` §3. Let `R` be one frame Pauli of support
`w`, `R'` its anticommuting partner, `S` the shared Tag. For each
`q in supp(R)`:

```
alpha_q = <R_q, R'_q> in F_2        beta_q = <S_q, R_q> in F_2
c_q     = (alpha_q, beta_q) in F_2^2
```

Global frame anticommutation forces the **odd-alpha constraint**

```
sum_{q in supp(R)} alpha_q = 1  (mod 2).
```

A **descent** at support `w` is a nonempty **proper** subset
`Q ⊆ supp(R)` with `|Q| <= 2` and `sum_{q in Q} c_q = (0,0)`. Lemma B proves a
descent always exists for `w >= 3`; that is what drives the support count down
to two.

A support-`w` frame is **locally exchange-irreducible** when no descent exists.

---

## 3. The theorem

### Theorem (complete local obstruction classification at support two)

At `w = 2`, the locally exchange-irreducible class configurations are exactly the
four ordered pairs

```
( (0,1), (1,0) )    ( (1,0), (0,1) )    ( (0,1), (1,1) )    ( (1,1), (0,1) )
```

that is, exactly **two** unordered types up to swapping the support coordinates:

```
{ (0,1), (1,0) }        and        { (0,1), (1,1) }.
```

**Proof.**

*Step 1 — only singleton deletions are available.* A nonempty proper subset of a
two-element support is a singleton. So a descent at `w = 2` is the deletion of
one coordinate `q`, and it requires `c_q = (0,0)`.

*Step 2 — irreducibility criterion.* Hence a support-two frame is locally
exchange-irreducible **iff neither coordinate has class `(0,0)`**.

*Step 3 — apply the odd-alpha constraint.* `alpha_1 + alpha_2 = 1`, so exactly
one coordinate has `alpha = 0` and the other has `alpha = 1`.

*Step 4 — enumerate.* The `alpha = 0` coordinate must avoid `(0,0)`, and the only
other class with `alpha = 0` is `(0,1)`. The `alpha = 1` coordinate is `(1,0)` or
`(1,1)`, both already nonzero. Taking the two orders of the two positions gives
exactly the four ordered pairs listed, and no others. ∎

### Corollary (structural reading)

Every local obstruction to the support-two descent has the **same form**: a
coordinate that is *redundant for local frame anticommutation* (`alpha = 0`) yet
*load-bearing for the shared Tag syndrome* (`beta = 1`), paired with the
coordinate carrying the odd anticommutation bit.

This is the mechanistic statement the manuscript already gestures at — "a
coordinate can be locally redundant for frame anticommutation while still
carrying shared-Tag syndrome" — now proved to be the **only** possible shape.

### Scope limit — stated to prevent over-reading

This is a statement about **local** irreducibility of the exchange step. It does
**not** prove that every occurrence of such a pair forces global support-two
optimality. Local irreducibility and global necessity remain separate, exactly as
#1617 requires. The exact `5 < 6` two-qubit witness is what establishes that
support one is globally insufficient; this theorem explains the *shape* of the
obstruction, not its global force.

### Observation — properness is vacuous at support two

Allowing the deleted subset to be improper (i.e. the whole support) changes
nothing at `w = 2`: odd-alpha forces `alpha_1 + alpha_2 = 1`, so the full support
can never sum to `(0,0)`. Properness is therefore doing no work at `w = 2`,
though it is essential for `w >= 3` where Lemma B needs the remaining frame to be
nonempty. Recorded because a reader could otherwise assume the restriction is
load-bearing here.

---

## 4. Independent verification

`independent_checker/check_local_obstruction.py` imports **nothing** from the R6S
implementation or from the generating proof. It transcribes only the three Lemma
B definitions and enumerates from them. The claimed classification is not used as
a filter; it is compared against what enumeration produces.

| check | result |
|---|---|
| A — derive the support-two irreducible set by brute force over all 16 ordered pairs | **matches** the four claimed pairs exactly; 2 unordered types |
| B — descent exists for every odd-alpha tuple at `w = 3..8` | **0** irreducible at every support `>= 3` |
| C — odd-alpha tuple count over support 2..8 | **43,688** recomputed, equal to the manuscript's recorded 43,688 |
| C′ — support-two failure count | **4**, equal to the manuscript's recorded 4 |
| D — negative controls | **4/4 fire** |

Check C is a genuine independent reproduction of the paper's corroboration
figure: the number of odd-alpha class tuples over support 2..8 is
`(4^2 + ... + 4^8)/2 = 87376/2 = 43688`, and the enumeration returns exactly
that. Check B independently re-derives Lemma B's conclusion over the same range.

Negative controls: removing the odd-alpha constraint changes the answer;
a deliberately wrong classification is rejected; moving the descent target from
`(0,0)` to `(0,1)` changes the answer; and no irreducible pair contains `(0,0)`.

An earlier control asserted that properness was load-bearing at `w = 2`. It
failed, and the **control** was wrong, not the theorem — see §3's observation.
It was replaced rather than deleted, and the finding is recorded.

`CANNOT_CHECK` has exit code `3` and is never reported as a pass.

---

## 5. Strongest falsifier

A support-two odd-alpha class configuration outside the four listed pairs for
which no descent exists, or one of the four for which a descent does exist. Both
are refuted exhaustively — the space has only 16 ordered pairs, of which 8
satisfy odd-alpha, and all are enumerated.

The theorem cannot fail as mathematics. What could fail is **relevance**: if the
class map `c_q` or the descent rule were restated, the classification would need
redoing. Both are transcribed verbatim from Lemma B and the manuscript, and the
transcription is checked against two independently recorded figures (43,688
and 4).

---

## 6. Donor boundary

The argument is elementary `F_2`-linear algebra over a four-element class set.
**No novelty is claimed** for the technique. Finite-group, zero-sum and
linear-dependence arguments own generic parity compression, as #1617 states.

The ORION-specific content is the exact classification for **this** frozen
three-block shared-one-bit-Tag TARE-M2 grammar and its class map, and the
structural reading in §3's corollary.

---

## 7. Authority boundary

`scientific_authority_delta = NONE`.

- `kappa_R6M = 2` is unchanged; this packet does not touch the support number.
- The support-one insufficiency witness (`5 < 6`) is unchanged.
- No claim of support-three necessity, universal two-trade, or physical advantage
  is made or implied.
- The local/global separation demanded by #1617 is preserved explicitly in §3.
- No manuscript, receipt, ledger or `rounds/` byte is modified.

What this earns is **explanatory**, and it is available to the manuscript as a
one-paragraph upgrade replacing a bare count with a classification.
`CLAIM_DISPOSITION.md` records the option; this packet does not take it.
