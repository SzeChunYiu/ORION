# ORION10.CERTIFICATE_EXPLANATION_GAP.v1 — THEORY

**Paper:** ORION-10 — Certified Static Forecasting
**Successor id:** `ORION10.CERTIFICATE_EXPLANATION_GAP.v1`
**Candidate source:** PR #1617, Priority A
**Authored:** 2026-08-28
**Status:** `THEORY_PROVED__COUNTS_REPRODUCED`
**Scientific authority delta:** `NONE`
**Frozen paper bytes modified:** NONE

---

## 1. Why this successor exists

ORION-10 exhibits a persistent pattern: the exact cost certificate
`C_DP = C_D++` survives while successive compact explanations are refuted —
`f_B`, then the enlarged `f_B'` (refuted by 64 fourth-configuration witnesses
among 740 instances), then the hybrid `B''` (10,481 verified rows, no fifth
configuration), with one pinned comm-`s2` sector still open.

The candidate note asks to **freeze an explanation grammar first**, then either
prove an information lower bound or synthesize an exact formula inside it.

This packet supplies the theorem that makes that instruction precise — and, more
usefully, shows that one half of the proposed grammar freeze is **unnecessary**.
The expression-size budget cannot matter.

---

## 2. Setting

Let `cost(x)` be the exact cost of instance `x`. Let `Psi(x)` be a frozen
explanation vocabulary — the features a human-readable regime explanation may
read. `Psi` partitions instances into **fibres**.

The key observation, which drives everything: the **complete** set of
`Psi`-measurable functions is the set of assignments of one value per fibre.
A formula over `Psi`, whatever its operators, interaction order or length, can
only ever compute a function of `Psi`. Enumerating fibre-assignments therefore
enumerates *every* formula of *every* size in *every* language over `Psi`.

---

## 3. The theorems

### Theorem 1 (exactness is fibre-constancy)

An exact `Psi`-only explanation of `cost` exists **iff** `cost` is constant on
every `Psi`-fibre.

**Proof.** *(⇐)* Assign each fibre its common cost value. *(⇒)* A
`Psi`-measurable function is constant on fibres, so if it equals `cost`
everywhere then `cost` is constant on fibres. ∎

### Theorem 2 (size-independence — the useful one)

If two instances satisfy `Psi(x) = Psi(x')` but `cost(x) != cost(x')`, then **no
function of `Psi` is exact, of any expression size, in any language over `Psi`**.

**Proof.** Immediate from Theorem 1 together with the observation in §2: the
space of candidate formulas is exhausted by fibre-assignments, and a mixed fibre
admits none. Nothing about operators, interaction order or length enters the
argument. ∎

**Consequence for the grammar freeze.** The candidate note proposes freezing
*"allowed primitive predicates, operators, interaction order, expression-size
budget."* Theorem 2 says the last of those — and in fact the operator and
interaction-order choices too — cannot change any exactness verdict. **Only the
primitive predicates matter**, because only they determine the fibres. A grammar
freeze that spends its rigour on a size budget is freezing the wrong thing.

### Theorem 3 (certificate/explanation separation)

Let `C(x)` be the information the exact cost certificate reads. An exact
certificate exists iff `cost` is `C`-measurable. Then an exact certificate can
coexist with the non-existence of an exact `Psi`-explanation **exactly when**
`C` separates some pair that `Psi` merges and on which `cost` differs. ∎

This is ORION-10's situation stated formally: `C_DP = C_D++` holds exactly while
`f_B'` fails, because the certificate's information distinguishes the 64 witness
instances that `B'` merges.

### Corollary (what the 64 witnesses proved)

By Theorem 2, the 64 fourth-configuration witnesses are a proof that **`B'` is
insufficient as a vocabulary**. They are *not* evidence that a longer or cleverer
`B'`-formula was needed. Likewise each subsequent enlargement — phantom homes,
the hybrid family `B''` — is a **vocabulary** enlargement, which is the only kind
of move Theorem 2 permits to close such a gap.

---

## 4. What would actually close the gap

Theorem 2 narrows the space of productive next moves to exactly two:

1. **Enlarge `Psi`** with a primitive that separates a currently-mixed fibre. The
   programme has been doing this, correctly, at each rung.
2. **Prove a lower bound** by exhibiting two instances with equal `Psi` and
   different exact cost, for a `Psi` frozen in advance. That is a
   *vocabulary-level* impossibility result and does not depend on formula size.

Route 2 is the one that would convert the current *"improving but not yet an
all-`n` theorem"* status into a permanent statement — a proof that a named
vocabulary can never suffice, rather than another refuted candidate.

What cannot help, and should not be spent on: enlarging the expression-size
budget, enriching the operator set, or raising interaction order, with `Psi`
held fixed.

---

## 5. Independent verification

`independent_checker/check_explanation_gap.py` imports no ORION-10 or QG module.
Theorems 1–3 are verified on freshly enumerated finite structures; the QG-7b
receipt is read as **data** and never executed.

| check | result |
|---|---|
| A — exactness iff fibre-constancy | holds |
| B — size-independence | holds |
| C — certificate/explanation separation | holds |
| exhaustive over | **21,501** `(Psi, cost)` structures |
| D — manuscript counts reproduced from the frozen receipt | **4/4 exact** |
| E — negative controls | **3/3 fire** |

Check D reproduces, from `QG7B_HYBRID_FAMILY_RESULTS.json`:

| quantity | manuscript | receipt |
|---|---|---|
| fourth-configuration witnesses | 64 | **64** |
| instances evaluated in the hostile panel | 740 | **740** |
| verified rows closed by the hybrid family | 10,481 | **10,481** |
| fifth configurations confirmed | 0 | **0** |

Controls: a cost-mixed fibre is inexplicable and splitting it fixes that;
enlarging the *value* alphabet does not rescue a mixed fibre; a pure coarse fibre
stays explicable.

`CANNOT_CHECK` has exit code `3` and is never reported as a pass.

---

## 6. Strongest falsifier

A `(Psi, cost)` pair with a cost-mixed fibre for which some `Psi`-measurable
function is nevertheless exact. Refuted exhaustively — and it is refuted by
construction, since the enumeration covers the complete space of such functions.

The honest limit: Theorem 2 is about functions **of `Psi`**. If a proposed
explanation secretly reads information outside `Psi`, it is not a
`Psi`-explanation and the theorem does not apply to it. Any future grammar freeze
must therefore pin the **primitives** precisely; that, and not the size budget,
is where the rigour belongs.

---

## 7. Donor boundary

Measurability with respect to a partition, and the fact that a function of a
statistic is constant on its level sets, are elementary and **donor-owned**. This
is the same information-sufficiency spine as ORION-09's regime separator
complexity and ORION-13's semantic separator. **No novelty is claimed.**

The ORION-specific content is the application to the certificate/explanation
split, the reading of the 64 witnesses as a vocabulary-insufficiency proof, and
the narrowing of productive next moves in §4.

---

## 8. Authority boundary

`scientific_authority_delta = NONE`.

- No terminal, gate, receipt or count changes. `QG7D`'s
  `all_n_theorem_authority: false` and
  `all_n_identity: UNPROVED_CANNOT_CHECK_FROM_CURRENT_PARENT_QUOTIENT` are
  unchanged.
- `btripleprime: UNFOUND_IN_FROZEN_PADDING_ABLATION` is unchanged — a further
  explanation family was **not** found, and this packet does not supply one.
- The open comm-`s2` sector remains open.
- `novelty_authority: false` and `physical_quantum_advantage_claim: false` are
  unchanged.
- No manuscript byte is modified; the §4 reading is offered, not inserted.

**ORION-10 is not blocked by this lane.** The proposed lower-bound route is
optional successor science.

**Content-freeze note.** This additive directory changes ORION-10's paper tree
oid. That pin (`63529ebe91cc`) is already among the mismatching ones on `main`
per issue **#1625**, so nothing newly breaks; and the freeze scripts re-pin
rather than verify, so their PASS is not evidence either way. Stated for
completeness.
