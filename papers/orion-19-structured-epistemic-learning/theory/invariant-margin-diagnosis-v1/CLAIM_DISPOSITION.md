# ORION19.INVARIANT_MARGIN_DIAGNOSIS.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Terminal:** `THEORY_PROVED__EXHAUSTIVELY_CHECKED`
**Scientific authority delta:** `NONE`
**New blocker raised:** none

---

## 1. What changed

One additive directory under
`papers/orion-19-structured-epistemic-learning/theory/`. No manuscript, protocol,
evidence or `top_tier/` byte was modified.

## 2. What was established

Two ORION-19 adverse boundaries share one logical shape, and this packet proves
the calculus behind both.

**Part A — orbit invariance.** An invariant representation gives orbit-invariant
decisions (A1); a decision that moves under a registered semantics-preserving
transformation therefore proves the representation is **not** invariant and the
margin contains a format prior (A2). That is why the reminting attack counts as a
refutation rather than noise.

**Theorem A3 is new relative to the candidate note:** no `G`-invariant rule can
beat the orbit minority-mass floor

```
E*_G = (1/N) * sum over orbits of min( n_orbit^0 , n_orbit^1 ).
```

This is the same fibre object as ORION-09, ORION-13 and ORION-10 — orbits are the
fibres of the group action.

**Part B — threshold transport.** Emitted decisions are sound whenever the
interval contains the true score (B1); widening the interval can only move a
decision **to** `CANNOT_CHECK` (B2); and narrowing it, or moving the threshold,
after outcome access manufactures a decision with **no** validity guarantee (B3).

## 3. Why A3 is the useful part

The invariant-profile successor repairs the mechanism by making the
representation invariant. A3 bounds in advance what that repair can achieve: if
the gold labels are not constant on the registered orbits, invariance is
*guaranteed* to cost accuracy.

So the right pre-registration is to **compute `E*_G` on the registered
transformation family before running the successor**, making the ceiling known
rather than discovered. That converts an open-ended repair attempt into one with
a declared achievable maximum.

## 4. Why B3 matters

*"Post-outcome widening of `I` or movement of `tau` cannot create authority"* is
usually stated as discipline. B3 makes it a theorem, and sharpens it: the only
post-outcome adjustment that moves a terminal in the permissive direction is
exactly the one that voids B1's guarantee.

Demonstrated concretely: at `tau = 0`, `[-1,1]` gives `CANNOT_CHECK`; narrowing
to `[1,1]` gives `POSITIVE`; moving `tau` to `-2` also gives `POSITIVE`. Neither
move added information.

**This packet performs neither move, and would be self-refuting if it did.**

## 5. Adverse and null evidence

All preserved. `T4_ATTACK_SUCCEEDED` **stands and remains authoritative** — this
packet bounds the successor, it does not reverse the defeat.
`P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_GATE_NOT_MET` stands, and the five
`CANNOT_CHECK` half-draw terminals are preserved as `CANNOT_CHECK`; **none is
converted**. No threshold or interval is adjusted anywhere.

## 6. Independent verification

No ORION-19 module imported. Part A exhaustive over **1,054,472** configurations,
Part B over **196** interval/threshold configurations, **3/3** negative controls
fire, and both frozen dispositions are confirmed unchanged by reading the
receipts as data.

## 7. Donor boundary

**No novelty claimed.** Group invariance, orbit-constancy of invariant functions
and interval-based abstention are donor-owned. The ORION-specific content is the
application to the two recorded boundaries and A3's use of the orbit partition to
bound the successor in advance.

## 8. Blocker status

`ORION-19 IS NOT BLOCKED BY THIS LANE.` The common protocol described in #1617
remains optional successor science, and #1608's separation of UT3/model-scale
work from the bounded paper is respected.
