# Negative-to-positive conversion ledger

Live scoring of the reopen adjudication's derived moves. A prediction that fails is
recorded as failed. Authority: development record; converts nothing by itself.

| # | negative | predicted move | lane | outcome |
|---|---|---|---|---|
| N1 | comm-s2 pinned sector open (QG-7c/7d) | FAILED_DECOMPOSITION → change the decomposition, not the menu | QG-7e | **CONVERTED — theorem complete.** But the *prediction was wrong*: E1's decomposition attack was refuted by exact enumeration (10 of 12 states admit no Δ≤0 alternative at all, so it was a local-optimality failure, not a descent failure), and what closed it was a **menu enlargement** — admitting all eight per-block target-permutation subsets where QG-7d realized only the global mirror. Scored against the adjudication. |
| N2 | StabPrep boundary unseparable at any budget | FAILED_DEFINITION → redefine the vocabulary | QG-15c | **PARTIALLY CONVERTED, prediction correct in mechanism.** Redefinition was the right move: diagnosing the collision as an *ordered per-step* property of the donor schedule and freezing a schedule-aware V2 drops the floor 43 → 1 and mixed cells 12 → 1, with the best held-out number in the series (3/120). One pair survives with identical step-cost profiles, and the lane refused to add the discriminant it found post-hoc. Honest negative terminal, near-miss result. |
| N3 | no support-2 phase witness; exact tie on 4,896 at O_nc_out | INACTIVE_NO_ATOM_CONDITION → solve for the tie locus | QG-17b | **CONVERTED, prediction correct.** The ties collapse to exactly two hyperplanes, `O_nc_out` lies exactly on both, and both sign-flip completely — 4,896 crossing witnesses give the first machine-checked points where support 1 provably fails. Bonus discovery: neither hyperplane is proportional to a QG-16 facet, so the true boundary has two faces the certificate does not describe. |
| N4 | prospective forecast refuted at n=4 | FAILED_DEFINITION → make n-dependence explicit | QG-23 | **CONVERTED TO A DIAGNOSED NEGATIVE; prediction correct in mechanism, wrong in payoff.** H0 BORNE_OUT: the support failure is carried *entirely* by the extensive features (intensive+degenerate alone put 0/120 out of support; extensive combined 76/120), so making n-dependence explicit was the right diagnostic move. H1 REFUTED: normalization raises *box* coverage 44→71 but moves the exact-cell measure the predictor actually consumes **0→0**, and the refit lattice is 28/120 against the un-normalized incumbent's 3/120. The predicted payoff — an n-scaling law or certified extrapolation range — did not arrive. Q3 is a flagged `null_result`: error rate flat as coverage runs 0.558→1.000, and abstaining *raises* the raw lattice's error rate. |
| N5 | syndrome rank 5 vs κ_R6I = 1 (sound but loose) | UNRESOLVED → measure rank − κ across families | QG-20 | **MEASURED, hypothesis self-refuted.** `slack == μ` holds on both families under the QG-6 certified ranks (R6I 5−1=4=μ; TARE 2−2=0=μ) — but a diagnostic frozen in §5 *before* the outcome asked whether the ranks are rewrite-aligned with the margins. They are not: the certified ranks use different rewrites (R6M per-slot, R6I per-block) while both margins are measured under block deletion. The margin-aligned R6M block rank is **3**, so TARE gives 3−2=1 ≠ μ=0. The agreement is rewrite-dependent and fails on the rewrite the margins themselves use. Terminal `QG20_PARTIAL__THIRD_FAMILY_NOT_DERIVABLE`. |
| N6 | novelty freezes authored without literature access | DONOR_SUBSUMPTION RISK → hostile external-novelty lane | QG-19 | **CONVERTED, prediction correct, and the risk was real.** Terminal `QG19_SUBSUMPTION_FOUND__NOVELTY_REDUCED`. Six claims attacked, none survived with novelty intact: two SUBSUMED (C-A the headline structural criterion → Wolf 1978's syndrome trellis; C-F digest-custody-≠-correctness → Meyman 2026 'governance laundering', six months older), three INSTANCE_OF_KNOWN_GENERAL, one NEAREST_MISS. Every passage is search-tool text, not a document read — the egress proxy refused all 11 fetches — so each source carries `document_level_verification: false`. |
| W5 | no real-chemistry trade regime found | — | R7 | **EXECUTED — honest negative that confirms prospectively.** Census extended to 180 matchings at 12/14/16 qubits, all donor-exact; six genuinely unread 16q batches admitted. Successor is an O1-style re-freeze, not a harder hunt. |
| W8 | R6B batch selection taken on the receipt's word | — | — | registered by the QG-3 verifier's stated limit |
| W10 | the V2 feature map, not the referee, is what caps this family's reach | — | QG-23 | **REGISTERED.** n=5 is blocked at ~28.4 h by the frozen feature map at ~42 ms/state, ~38× the cap; the Dial-queue referee projects ~338 s, comfortably inside it. Third instance of the binding cost being our own instrumentation rather than the problem. |
| W9 | committed family search does not realize QG-6's own support-capped corollary | — | QG-22 → QG-10 | **PARTIAL PROGRESS.** QG-10's `U_W1` is an uncapped weight-one-frame enumerator machine-checked equal to the committed `dxx_search(max_weight=1)` on all 1,029 instances where the capped version can run (n≤4, 0 mismatches), and it extends `C_D+` to any n. The weight-one case now has a working uncapped enumerator; the support-2 case does not. Original registration: **projected exponential→polynomial implementation win.** QG-6's corollary bounds the certified support-≤2 search at O(n²·16) frame-pair candidates per block; `r6p.dxx_search` instead sweeps an A^{2n} don't-care pattern space plus an A^n−1 Tag sweep, O(n·4^{3n}). The bound is already proved and committed — realizing it is engineering, not a new theorem. |

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


## What QG-22 costs the programme's own headline

QG-7e's all-n classification was the wave-2 headline, and the natural next sentence — the
one this programme was one lane from writing — was that the classification *collapses* the
optimization problem. QG-22 measured both sides and the attribution is false. The
unrestricted syndrome DP referee is **Θ(n)** and predates QG-7e; the QG-7e closed form is
**O(n⁶)**. The referee the closed form characterizes is asymptotically *cheaper* than the
closed form. The exponential collapse that does exist — Θ(4^{7n}) naive enumeration down
to Θ(n) — is effected by the **fixed 9-bit conserved syndrome**, QG-6's meta-theorem
object, not by the classification.

The lane was offered a terminal that would have recorded the flattering reading
(`QG22_NO_SEPARATION__CLASSIFICATION_COLLAPSES_THE_PROBLEM`) and declined it in writing:
*"its name asserts a collapse agent this lane's own measurements contradict."* That is the
second time in this campaign a lane has refuted the premise it was launched on — QG-21
refuted O1's derivability from FT accounting, QG-22 refutes the classification's role as
collapse agent — and both times the refutation is the more transferable result.

What survives, and is stronger than the claim it replaced: a **decidable structural
criterion** for when a compilation family's exact optimum is linear in n (fixed-dimension
conserved syndrome + factorizing configuration space + local-sum objective), with four
named failure modes and one in-programme instance, StabPrep, on the far side of it. An
all-n finite-support classification is **neither necessary nor sufficient** for that
collapse. Every claim in the programme that leans on QG-7e must now say what QG-7e is for
— an all-n theorem about the *shape* of the optimum, and a human-readable optimum — and
must not say it is what makes optimization tractable.


## What QG-19 costs the whole programme

Six novelty claims went into the hostile lane. **None came out intact.** The lane was
built so that finding us scooped was the success condition, and it succeeded.

The one that matters most is C-A. QG-22 had just replaced a refuted separation claim with
a structural criterion for when a compilation family's exact optimum is linear in n, and
that criterion was, at the time, the campaign's best transferable object. It is the
**syndrome trellis** — Wolf 1978, maximum-likelihood decoding of an arbitrary linear block
code by Viterbi over ≤ q^{n−k} states — with our fixed-dimension syndrome being the case
where the state count stops growing. It is also, three times over and more generally, the
generalized distributive law, bucket elimination, and Gomory's group relaxation.

There is a pattern across all six, and it is the transferable lesson: **every novelty
freeze authored without literature access was wrong in the same direction.** A clean
structural statement about dynamic programming over a bounded state has a parent in coding
theory, constraint satisfaction, or integer programming. The default assumption must be
that the parent exists, with the burden on us to find it *before* the freeze.

The corrections are not optional and not cosmetic. The receipt issues seven required
actions binding on the closure packet and the paper series, and one has been executed
immediately: `corroboration.py`'s docstring narrated the custody finding as discovered on
2026-08-21, and now names Meyman 2026, replication laundering, Leek & Peng 2015 and ACM
artifact badging instead. What stays local is the incident and the enforcement point, not
the distinction.

**What this lane does not touch.** The exact values on named families under a frozen cost
model — κ_R6I = 1, κ_TARE = 2, the all-n TARE classification, the tie locus and its two
hyperplanes, the StabPrep feature-determination floor — are measurements, and no source
found here computes them. The frameworks around them are borrowed; the register now says
from whom. That is a smaller programme than the one we thought we had, and an honest one.


## The pattern across N1–N6, now that all six have run

Every one of the six standing negatives has been through a chartered lane. The adjudication
predicted a conversion move for each. Scoring them honestly:

| negative | move predicted | move that worked | prediction |
| --- | --- | --- | --- |
| N1 | change the decomposition | **menu enlargement** | **WRONG** |
| N2 | redefine the vocabulary | redefinition (floor 43 → 1, one pair left) | right in mechanism |
| N3 | solve for the tie locus | solving for the tie locus | **right** |
| N4 | make n-dependence explicit | diagnosis yes, payoff no | right in mechanism |
| N5 | measure rank − κ across families | measured, then self-refuted | right in mechanism |
| N6 | hostile external-novelty lane | subsumption found on all six claims | **right, and costly** |

Two of six predictions were right outright, three right about the mechanism but not the
payoff, one flatly wrong. The adjudication's headline method finding — *the negative always
identified the wrong OBJECT, never merely an insufficient search* — has one clean
counterexample (N1) and one case where identifying the right object bought a diagnosis
rather than a result (N4). **It is a heuristic with a known failure mode, and it should be
cited as one.**

The more durable finding is the one N6 produced, and it costs more: **every novelty freeze
authored without literature access was wrong in the same direction.** Six for six.
