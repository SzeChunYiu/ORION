# Claim disposition — ORION01.CONTEXTUAL_MOVE_COMPLETENESS.v1

Protocol and proof frozen at `6f94cda70` before any outcome was read.
Terminal reached: **T1_QUOTIENT_REPAIRS_COMPLETENESS_ONLY** — the predicted terminal,
and the mixed one.

## Result

| n | registries | source-complete | closed form | frozen R12 count at complexity 1 |
|---|---|---|---|---|
| 2 | 2 | 1 | 1 | 1 |
| 3 | 8 | 3 | 3 | 3 |
| 4 | 64 | 21 | 21 | 21 |
| 5 | 1,024 | 315 | 315 | 315 |
| 6 | 32,768 | 9,765 | 9,765 | 9,765 |

**Theorem A** holds in both directions over all 33,866 registries: no source-complete
registry has terminal complexity other than 1, and no non-source-complete registry has
complexity 1.

**Theorem B**'s closed form `prod_{s=2}^{n} (2^(s-1) - 1)` agrees with the enumeration
and with the count already frozen in the R12 histogram, at every `n`.

**Claim C** was measured, not assumed: 5 distinct optimizer signatures over the
source-complete quotient, exactly one per `n`. The signature varies with `n` and never
with the registry.

## What this repairs, and what it does not

R12 conflated two failures. This separates them.

**Repaired.** Completeness is identifiable on the source-complete quotient, and equals
1 there. Theorem A makes the quotient *coextensive* with completeness rather than merely
correlated with it, so "prove completeness on the source-complete scheduler/context
quotient" is well posed. `r6m_registry_completeness: false` was a statement about the
free registry family, and it remains true of that family.

**Not repaired.** The registry itself stays unidentifiable. The direct optimizer
signature is constant across the quotient, so nothing an observer sees distinguishes one
source-complete registry from another. **`production_transfer: false` is not lifted by
this packet and is not edited by it.**

Reporting A and B without C would have overstated the repair into a transfer result. C
was registered as a claim to be measured before outcomes were read, precisely so it
could not become an afterword.

## Controls

- **K1** — the recomputed count had to match the *already-frozen* R12 histogram at every
  `n`, not merely be internally consistent. This is what distinguishes quotienting the
  frozen object from re-modelling it. Passed at all five `n`.
- **K2** — the iff was checked in **both** directions. One direction would not
  distinguish an equivalence from an implication, and the (⇐) direction is the one
  carrying the content.
- **K3** — a non-source-complete registry with complexity > 1 exists at every `n`, so
  the quotient separates something. A vacuous quotient would prove nothing.
- **K4** — claim C was measured by collecting signatures over the quotient, not read off
  the constructor.

## Limits

The model is the frozen finite one: states `1..n` for `n` in 2..6, all strictly
resource-decreasing candidate moves, registries as arbitrary subsets. The closed form is
proved for all `n`; the exhaustive check covers 2..6, which is the panel R12 froze.
Nothing here speaks to registries outside this model, and the `CANNOT_CHECK` fields on
the R12 record — `external_independence` and `novelty` — are untouched.

## Authority

`MEASUREMENT_AND_PROOF_ONLY`. `scientific_authority_delta: NONE`. No submission
authority. The R12 record and every one of its authority fields stand exactly as frozen.

Outcomes were read once. T1 was reached and the lane closes here.
