# QG-25 — the located candidate: does hardness actually live where QG-22 said it does?

Date: 2026-08-22
Lane: ORION-QG / wave 3
Branch: `claude/orion-harness-verification-b17qdj`
Base revision: `ccbd708b`
Status: **FROZEN BEFORE ANY OUTCOME-DETERMINING RUN.**

Authority ceiling: **NOT_R6**. `novelty_authority: false`,
`physical_quantum_advantage_claim: false`. No chemistry read. The protected
stretched-N₂ subject is never read. Committed analyzers imported **unmodified**.
Runtime cap **< 45 minutes per run**; every cap disclosed.

---

## 0. The one thing this programme located and never tested

QG-22 established that unit-cost TARE has no complexity separation to state: the
exact optimum is affine in n, and the collapse agent is the **fixed-dimension
conserved syndrome**, not any classification. It then located where hardness
might actually live, and labelled it honestly:

> hardness for families without a conserved syndrome — **CONJECTURE**. Basis:
> StabPrep's 2^{Θ(n²)} state space and QG-15's `NO_CLEAN_PREDICATE` /
> `COST_FORECAST_REFUTED` terminals; **no reduction, no lower bound.**

That CONJECTURE is the last unexercised claim in the programme's own component
table, and StabPrep is its named in-programme instance. This lane tests it.

**It cannot be settled by measuring our own runtimes, and this protocol forbids
trying.** QG-22's sharpest methodological finding was that every exponential it
observed was a property of an algorithm we wrote — `r6p.dxx_search`, the naive
enumerator — never of a problem. Gate G3 below refuses any hardness inference
from wall-clock.

## 1. Donor search first, enforced

`orion_research_harness.donor_search.validate_donor_search` is called on every
claim record, **with the query log passed** so the passage-occurrence check
(residual W11) is exercised rather than skipped. All three query families
mandatory.

**Prior expectation, frozen before searching.** Optimal stabilizer-state
preparation and Clifford synthesis are worked areas (Aaronson–Gottesman, Bravyi
et al., Maslov, the CNOT-count and Clifford-depth literature). This lane expects
its structural claims to be **SUBSUMED or INSTANCE_OF_KNOWN_GENERAL**, exactly as
QG-19 and QG-24 were. A subsumed claim is a successful outcome.

## 2. Frozen objects

* Family: **StabPrep** as committed in QG-15/15b/15c — H/S/SDG cost 1, CNOT cost
  3, exact Dijkstra referee over the complete stabilizer-state graph,
  |S_n| = 6, 60, 1080, 36720 at n = 1..4.
* The property under test, stated so it can fail: StabPrep admits **no
  fixed-dimension conserved syndrome** in QG-22's sense — no homomorphism from
  its configuration space into a finite abelian group of order 2^D with D
  independent of n, whose fibres decide feasibility.

## 3. Q1 — prove the absence, do not assume it

QG-22 asserted StabPrep has no conserved syndrome from its state-space size.
Size is not absence. So:

1. Take QG-6's own syndrome-inference machinery — the procedure that *found* the
   9-bit syndrome for TARE — and **run it on StabPrep**, unmodified.
2. Report what it returns: a syndrome with its dimension, or a failure with the
   reason. If it returns one of fixed dimension, **QG-22's premise is refuted**
   and that is this lane's result.
3. If it fails, report the exact obstruction, and measure the *minimum* D for
   which a feasibility-deciding homomorphism exists at n = 1, 2, 3 by exhaustive
   search over candidate quotients. A D that grows with n is the positive
   evidence; a D that does not is a refutation.

## 4. Q2 — the separation QG-22 could not state, stated or refused

With Q1's D(n) in hand:

* If D(n) grows, exhibit the consequence *structurally*: the min-plus DP that
  makes TARE affine requires 2^{2D} states per position, so a growing D removes
  the collapse **by construction, not by observation**. State the resulting bound
  and its exact domain.
* Then state plainly what is still missing for a hardness result: a reduction
  from a known-hard problem, or a lower bound. **This lane may not supply
  either by assertion.** If neither is produced, the terminal says so.

## 5. Q3 — the honest comparison

Report, for TARE and StabPrep side by side on the domains where both are
computable: syndrome dimension, exact-optimum cost as measured, and whether the
optimum is decidable by a local-sum DP. This is the table QG-22's Q3 wanted and
could not fill.

## 6. Terminals, frozen

* `QG25_NO_CONSERVED_SYNDROME_PROVED__COLLAPSE_MECHANISM_ABSENT` — Q1 proves no
  fixed-D syndrome exists and D(n) grows; the collapse mechanism is structurally
  unavailable. **Still not a hardness theorem**, and §4 must say so.
* `QG25_PREMISE_REFUTED__STABPREP_HAS_A_FIXED_DIMENSION_SYNDROME` — QG-6's
  machinery finds one. QG-22's located candidate evaporates and the programme's
  last CONJECTURE is false.
* `QG25_PARTIAL__D_MEASURED_BUT_GROWTH_UNDECIDED` — D measured at small n with
  no defensible extrapolation.
* `QG25_BLOCKED__MACHINERY_DOES_NOT_TRANSFER` — QG-6's inference cannot be run
  on StabPrep at all, with the measured reason.

## 7. Gates

* **G1** — donor search validated by the committed module **with the log passed**,
  before any novelty claim.
* **G2** — QG-6's syndrome inference imported unmodified; any adaptation is
  disclosed line by line and its effect on the result stated.
* **G3** — **no hardness inference from wall-clock.** Timing may be reported;
  it may not appear in any argument. QG-22 showed every exponential we have
  observed was ours, not the problem's.
* **G4** — no reduction and no lower bound may be claimed unless exhibited in
  full and checkable.
* **G5** — complete enumeration at each declared n, or the size named as not
  attempted with its measured obstacle. No sampling presented as enumeration.
* **G6** — QG-22's and QG-15's receipts are not edited; qualifications live here.
* **G7** — independent from-primitives verifier, demonstrated capable of failing
  on tampered copies whose digests are recomputed to be self-consistent.
* **G8** — determinism: double run byte-identical outside timing.
* **G9** — NOT_R6; protected subject unread; caps disclosed.

## 8. Files this lane may create

1. `research/extensions/orion-qg/qg25_no_syndrome_family.py`
2. `research/extensions/orion-qg/QG25_NO_SYNDROME_FAMILY_RESULTS.json`
3. `development/orion-qg-regime-geometry/qg25_generic_verify.py`
4. `development/orion-qg-regime-geometry/QG25_GENERIC_VERIFICATION.json`
5. `development/orion-qg-regime-geometry/QG25_DONOR_SEARCH.md`

## 9. What this lane cannot do

It cannot prove anything is hard. It cannot claim novelty. It cannot revise
QG-22's or QG-15's receipts. It cannot read the protected subject. If it ends
with "no conserved syndrome exists", that is a statement about a mechanism being
absent — **not** a statement that the problem is intractable, and the results
file must carry that sentence.
