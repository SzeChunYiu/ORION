# Negative-to-positive conversion ledger

Live scoring of the reopen adjudication's derived moves. A prediction that fails is
recorded as failed. Authority: development record; converts nothing by itself.

| # | negative | predicted move | lane | outcome |
|---|---|---|---|---|
| N1 | comm-s2 pinned sector open (QG-7c/7d) | FAILED_DECOMPOSITION → change the decomposition, not the menu | QG-7e | **CONVERTED — theorem complete.** But the *prediction was wrong*: E1's decomposition attack was refuted by exact enumeration (10 of 12 states admit no Δ≤0 alternative at all, so it was a local-optimality failure, not a descent failure), and what closed it was a **menu enlargement** — admitting all eight per-block target-permutation subsets where QG-7d realized only the global mirror. Scored against the adjudication. |
| N2 | StabPrep boundary unseparable at any budget | FAILED_DEFINITION → redefine the vocabulary | QG-15c | **PARTIALLY CONVERTED, prediction correct in mechanism.** Redefinition was the right move: diagnosing the collision as an *ordered per-step* property of the donor schedule and freezing a schedule-aware V2 drops the floor 43 → 1 and mixed cells 12 → 1, with the best held-out number in the series (3/120). One pair survives with identical step-cost profiles, and the lane refused to add the discriminant it found post-hoc. Honest negative terminal, near-miss result. |
| N3 | no support-2 phase witness; exact tie on 4,896 at O_nc_out | INACTIVE_NO_ATOM_CONDITION → solve for the tie locus | QG-17b | **CONVERTED, prediction correct.** The ties collapse to exactly two hyperplanes, `O_nc_out` lies exactly on both, and both sign-flip completely — 4,896 crossing witnesses give the first machine-checked points where support 1 provably fails. Bonus discovery: neither hyperplane is proportional to a QG-16 facet, so the true boundary has two faces the certificate does not describe. |
| N4 | prospective forecast refuted at n=4 | FAILED_DEFINITION → make n-dependence explicit | — | not yet chartered |
| N5 | syndrome rank 5 vs κ_R6I = 1 (sound but loose) | UNRESOLVED → measure rank − κ across families | QG-20 | **MEASURED, hypothesis self-refuted.** `slack == μ` holds on both families under the QG-6 certified ranks (R6I 5−1=4=μ; TARE 2−2=0=μ) — but a diagnostic frozen in §5 *before* the outcome asked whether the ranks are rewrite-aligned with the margins. They are not: the certified ranks use different rewrites (R6M per-slot, R6I per-block) while both margins are measured under block deletion. The margin-aligned R6M block rank is **3**, so TARE gives 3−2=1 ≠ μ=0. The agreement is rewrite-dependent and fails on the rewrite the margins themselves use. Terminal `QG20_PARTIAL__THIRD_FAMILY_NOT_DERIVABLE`. |
| N6 | novelty freezes authored without literature access | DONOR_SUBSUMPTION RISK → hostile external-novelty lane | QG-19 | not yet chartered |
| W5 | no real-chemistry trade regime found | — | R7 | **EXECUTED — honest negative that confirms prospectively.** Census extended to 180 matchings at 12/14/16 qubits, all donor-exact; six genuinely unread 16q batches admitted. Successor is an O1-style re-freeze, not a harder hunt. |
| W8 | R6B batch selection taken on the receipt's word | — | — | registered by the QG-3 verifier's stated limit |

## What N1 costs the method finding

The adjudication's method finding — "all six prior conversions identified the wrong
OBJECT, never merely an insufficient search; enlarging move menus failed repeatedly while
redefinition succeeded repeatedly" — predicted N1 would need a decomposition change. It
did not. A menu enlargement closed it, and the decomposition attack was exactly refuted.

So the finding is a **heuristic with a counterexample**, not a law. The honest refinement:
a negative can be an insufficient search when the search fails to realize a degree of
freedom its own protocol already declares. That is what happened here — `dxx_search`
enumerates the per-block permutation independently per block, QG-7d's protocol says so,
and its menu implemented only 2 of the 8 subsets. Worth checking for in every lane that
stalls: *does our menu realize everything our own protocol claims as free?*

## What QG-20 establishes, and what it refuses to claim

The attractive result was available and the lane declined it. `slack == μ` on both
measured families is a **candidate relation from two points, not a law**, for four
reasons the receipt states: two points leave zero residual degrees of freedom; the μ=0
point only re-tests the qualitative implication QG-18 already proved structurally; the
entire quantitative content is the single point 4=4 with no proposed mechanism; and a
competing account — "μ≥1 ⇒ relocation collapses to κ=1, so slack = rank−1" — fits both
points identically and is therefore not discriminated by any data in hand.

Then the pre-frozen rewrite-alignment diagnostic broke it outright: on the rewrite the
margins are actually measured under, TARE gives slack 1 against μ 0. A relation that
holds only under a rewrite mismatch is not a relation.

**Discriminating prediction, for whoever runs the third family**: it needs a certified
rank R, a two-sided κ, and a measured margin strictly inside 0 < μ < R−1. There H1
predicts κ = R − μ while the competing account predicts κ = 1. A family with μ ∈ {0, R−1}
adds a data point and discriminates nothing — worth knowing before spending a lane on it.

**StabPrep does not supply it.** All three transfer criteria fail, first at T1: its
optimum is a Dijkstra shortest path over the complete stabilizer-state graph, so there is
no per-column DP transition table to difference and the QG-6 rank is **undefined** — not
zero. Likewise μ is undefined, since cost is additive over gates with no
frame-refund/Restore-penalty split; that is categorically different from TARE's μ = 0,
which is a *measured* tie set over 368,640 rows. Distinguishing "undefined" from "zero"
is the whole content of Q3.
