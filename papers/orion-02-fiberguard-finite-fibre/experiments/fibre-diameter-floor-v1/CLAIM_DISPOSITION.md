# Claim disposition — ORION02.FIBRE_DIAMETER_FLOOR.v1

Protocol and proof frozen at `946187ca1` before any outcome was read.
Terminal reached: **T1_FLOOR_HOLDS_EXHAUSTIVELY**.

## Result

| | |
|---|---|
| configurations enumerated | 784 (exhaustive: fibre sizes 2–5 over a 7-value grid) |
| certificates beating `D(z)/2` | **0** |
| intervals narrower than `D(z)/2` covering both diameter ends | **0** |
| miscoverage below 1/2 on a balanced diameter pair | **0** |

All four controls passed. The three theorems in `THEORY.md` are proved analytically;
the search is a check on the proof, not a substitute for it.

## What this establishes

The `D(z)/2` floor is a property of accepted fibre certificates **as such**, not an
artefact of the `A_t/B_t` construction. A certificate accepted on the whole fibre is a
function of `z` alone, so it cannot be right about both ends of the diameter.

That converts `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID` from a tuning failure into a
structural impossibility. On any fibre with `D(z) > 0` no recalibration, better
geometry, or stronger selector can reduce conditional miscoverage below 1/2 on a
balanced diameter-attaining pair, because the certificate cannot see which member it
is being asked about. Raw marginal coverage escapes this only by averaging over
fibres, which is precisely why it cannot substitute for conditional risk control — the
two are separated by the fibre diameter.

## The controls, and one I had to fix

Evidence of the form "we searched and found nothing" is worth exactly as much as the
demonstration that the search can find something. Three controls plant a violation and
require the **same** comparison functions used by the real search to catch it:

- **C1** — a certificate permitted to see the member index achieves worst-case error 0
  and is caught by the same `beats_floor` comparison, 756/756 eligible fibres.
- **C4** — at radius `D/2` the midpoint interval does cover both ends, proving
  `interval_covers_both_ends` can return `True` at all, 756/756.
- **C3** — the achieved optimum equals `D(z)/2` exactly at the midpoint, never merely
  exceeds it; a search returning more would not have searched the admissible set.
- **C2** — silence on the degenerate zero-diameter fibre. A checker that alarms there
  cries wolf and gets switched off.

The first version of C1 was **vacuous** and I caught it before reporting: it computed
`abs(v - v)`, which is identically zero, so it "fired" by tautology without ever
exercising the search. It was rewritten to route a planted violation through the real
comparison. The distinction matters exactly here, where the headline is an absence.

## Limits

The enumeration is exhaustive over a finite family — fibre sizes 2 to 5, target values
on a 7-point integer grid, certificate values on a 0.05 grid widened beyond the fibre
and augmented with the exact midpoint. It is a check on an analytic proof, not an
independent source of generality; the generality comes from the proof.

This packet does **not** re-derive `C-C3` or `C2-C4`. No executable `A_t/B_t`
constructor exists in this repository and the family rests on `B.3(c)`, a cross-gadget
separability lemma the manuscript does not state. Those results are cited exactly as
frozen, conditionality included, and `A_t/B_t` appears only as the instance showing
`D(z)` — and therefore the floor — can be made arbitrarily large.

## Authority

`MEASUREMENT_AND_PROOF_ONLY`. `scientific_authority_delta: NONE`. No submission
authority. `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID` stands unchanged: this explains
the adverse terminal, it does not retract it, and it licenses no revival of any
retracted ORION-02 claim.

Outcomes were read once. T1 was reached and the lane closes here.
