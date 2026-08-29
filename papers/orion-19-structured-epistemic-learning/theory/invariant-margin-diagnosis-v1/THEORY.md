# ORION19.INVARIANT_MARGIN_DIAGNOSIS.v1 — THEORY

**Paper:** ORION-19 — Structured Epistemic Learning
**Successor id:** `ORION19.INVARIANT_MARGIN_DIAGNOSIS.v1`
**Candidate source:** PR #1617, Priority A
**Authored:** 2026-08-28
**Status:** `THEORY_PROVED__EXHAUSTIVELY_CHECKED`
**Scientific authority delta:** `NONE`
**Frozen paper bytes modified:** NONE

---

## 1. Why this successor exists

Two ORION-19 adverse boundaries have the same logical shape:

1. **`T4_ATTACK_SUCCEEDED`** — semantics-preserving symbol reminting broke the
   historical serialized-representation margin, proving format-prior sensitivity.
2. **`P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_GATE_NOT_MET`** — one held-out
   accessibility threshold does not transport, and half-draw decisions remain
   `CANNOT_CHECK`.

The candidate note asks for a common protocol covering both. This packet proves
the two theorems that protocol would rest on, and adds a quantitative bound the
note does not have.

---

## 2. Part A — semantic-orbit invariance

Let `G` be a registered set of transformations that preserve scientific semantics
and the gold label, acting on instances `x`. Let `phi` be a representation and
`d` a deterministic downstream decision rule.

### Theorem A1 (invariance transfers)

If `phi(g.x) = phi(x)` for all `g in G`, then `d(phi(g.x)) = d(phi(x))`: decisions
are constant on orbits. **Proof.** `d` is a function; equal inputs give equal
outputs. ∎

### Theorem A2 (the falsifier, contrapositive)

If some registered `g in G` changes a decision, then `phi` is **not**
`G`-invariant, and the decision depends on a coordinate that `G` was declared to
leave semantically irrelevant — a representation/format prior.

Consequently a margin measured **without** controlling for `G` cannot by itself
establish semantic superiority. This is exactly what the reminting attack
demonstrated, and A2 is the reason it counts as a refutation rather than noise.

### Theorem A3 (the orbit-majority bound — new here)

Because a `G`-invariant rule is constant on orbits, its minimum achievable error
on a finite domain is

```
E*_G = (1/N) * sum over orbits of min( n_orbit^0 , n_orbit^1 ).
```

**No `G`-invariant representation, however sophisticated, can beat this floor.**

This is the same fibre/minority-mass object as ORION-09's separator complexity,
ORION-13's semantic separator and ORION-10's explanation gap — orbits are simply
the fibres of the group action.

**Why it matters for the invariant-profile successor.** The successor repairs the
mechanism by making the representation invariant. A3 bounds in advance what that
repair can achieve: if the gold labels are not constant on the registered orbits,
invariance is *guaranteed* to cost accuracy, and the frozen defeat remains
authoritative. The right pre-registration for that successor is therefore to
compute `E*_G` on the registered transformation family **before** running it, so
the achievable ceiling is known rather than discovered.

---

## 3. Part B — threshold transport

Let `s(x)` be a diagnostic score, `I(x) = [lo, hi]` a **predeclared** uncertainty
or drift set, and `tau` a threshold. The disciplined rule is

```
POSITIVE       if lo > tau
NEGATIVE       if hi < tau
CANNOT_CHECK   otherwise (the interval straddles tau)
```

### Theorem B1 (soundness)

If the true score lies in `I(x)`, then every emitted `POSITIVE`/`NEGATIVE`
decision is correct, and `CANNOT_CHECK` is emitted **exactly** when the interval
straddles `tau`. ∎

### Theorem B2 (widening cannot create authority)

Enlarging `I` can only move a decision **to** `CANNOT_CHECK`. It can never turn
`CANNOT_CHECK` into a decision, and never flip `POSITIVE` to `NEGATIVE`. ∎

### Theorem B3 (the forbidden move, made explicit)

**Narrowing `I` or moving `tau` after outcome access can convert `CANNOT_CHECK`
into a decision — and that decision carries no validity guarantee**, because B1's
premise (true score inside `I`) is no longer underwritten by anything predeclared.

Demonstrated concretely: with `tau = 0`, the interval `[-1, 1]` gives
`CANNOT_CHECK`; narrowing to `[1, 1]` gives `POSITIVE`; leaving the interval and
moving `tau` to `-2` also gives `POSITIVE`. Neither move added information.

This is why *"post-outcome widening `I` or movement of `tau` cannot create
authority"* is a theorem and not a style preference: the only post-outcome
adjustment that *changes* a terminal in the permissive direction is precisely the
one that voids the guarantee.

---

## 4. Independent verification

`independent_checker/check_invariant_margin.py` imports no ORION-19 module. Both
parts are verified on freshly enumerated finite structures; the frozen evidence
files are read as **data** to confirm the two dispositions and are never
executed.

| check | result |
|---|---|
| A1 — invariant representation gives invariant decisions | holds |
| A2 — a moved decision proves non-invariance | holds |
| A3 — orbit-majority bound holds for every invariant rule | holds |
| Part A exhaustive over | **1,054,472** configurations |
| B1 — emitted decisions are sound | holds |
| B2 — widening only moves toward `CANNOT_CHECK` | holds |
| B3 — post-outcome narrowing manufactures a decision | demonstrated |
| Part B exhaustive over | **196** interval/threshold configurations |
| negative controls | **3/3 fire** |

Bound dispositions, read from the frozen receipts and confirmed unchanged:
`T4_ATTACK_SUCCEEDED` and
`P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_GATE_NOT_MET`, with 5 `CANNOT_CHECK`
terminals present in the transport run.

`CANNOT_CHECK` has exit code `3` and is never reported as a pass.

---

## 5. Strongest falsifiers

- **Against A:** an independently frozen semantics-preserving orbit on which the
  invariant-profile successor still changes decisions. That would show the
  registered `G` is not the operative family.
- **Against B:** a predeclared transport interval wholly separated from the
  threshold on which the registered diagnosis still fails. That would show the
  interval is not a valid containment.

Neither is addressed by this packet, which proves only the calculus. Both remain
the successor's job.

---

## 6. Donor boundary

Group invariance, orbit-constancy of invariant functions, and interval-based
abstention are **donor-owned** (invariance/equivariance theory, conformal and
interval-predictor abstention). **No novelty is claimed.**

The ORION-specific content is the application to the two recorded ORION-19
boundaries, and A3's use of the orbit partition as the fibre object that bounds
the invariant-profile successor in advance.

---

## 7. Authority boundary

`scientific_authority_delta = NONE`.

- `T4_ATTACK_SUCCEEDED` stands. **The frozen defeat remains authoritative**; the
  invariant-profile successor is a bounded constructive response, not a
  reversal, and A3 now bounds what it can achieve.
- `P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_GATE_NOT_MET` stands, and the `CANNOT_CHECK`
  half-draw terminals are preserved as `CANNOT_CHECK` — **none is converted**.
- No threshold, interval or gate is adjusted anywhere by this packet. B3 exists
  precisely to name that move as forbidden.
- No claim about deployed LLM/agent behaviour is made; #1609 keeps ORION-19's
  bounded causal-diagnosis scope, and nothing here widens it.
- No manuscript, protocol, evidence or `top_tier/` byte is modified.

**Content-freeze note.** This additive directory changes ORION-19's paper tree
oid; that pin (`32d3f2597645`) is already among the mismatching ones on `main`
per issue **#1625**, and the freeze scripts re-pin rather than verify, so their
PASS is not evidence either way.

**ORION-19 is not blocked by this lane.**
