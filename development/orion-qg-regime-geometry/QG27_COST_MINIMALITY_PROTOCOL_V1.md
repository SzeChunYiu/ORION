# QG-27 — QG-26 answered the feasibility question and forbade itself the cost one. This asks it.

Date: 2026-08-22
Lane: ORION-QG / wave 3, successor to QG-26
Branch: `claude/orion-harness-verification-b17qdj`
Base revision: `f280d3e3`
Status: **FROZEN BEFORE ANY OUTCOME-DETERMINING RUN.**

Authority ceiling: **NOT_R6**. `novelty_authority: false`,
`physical_quantum_advantage_claim: false`. No chemistry read. The protected
stretched-N₂ subject is never read. Committed analyzers imported **unmodified**.
Runtime cap **< 15 minutes**; every cap disclosed.

---

## 0. The question QG-26 left on the table, in its own words

QG-26 established that the committed R6I state space is exactly the Nerode index
of its **feasibility** language: rank 10, index 1024, looseness factor 1. Its gate
G3 then forbade the obvious next sentence, and the receipt carries the refusal
verbatim:

> This is a statement about the FEASIBILITY language only. The committed DP is
> min-plus and carries cost; nothing here shows any algorithm is faster, and
> whether the cost DP admits the same reduction is not answered.

That was the right call and it leaves a real question unanswered. **Two states can
be distinguishable for feasibility and still carry identical cost behaviour**, in
which case the min-plus DP is doing redundant work that the feasibility argument
cannot see. This lane asks whether it does.

Unlike QG-26, **this lane is permitted to make an efficiency claim** — but only
under §5's exhibition requirement, never on the strength of a state count.

## 1. Donor search first, and the parent is already known

The question "when may two states of a deterministic weighted automaton be
merged" is **weighted-automaton minimization over the tropical semiring**, and its
standard answer is Mohri's *pushing*: states are equivalent when their residual
cost functions differ by a constant. That is donor property and this lane claims
none of it. `asserts_novelty: false` throughout, checked by calling the committed
`donor_search` validator rather than asserted.

The donor search is still run, with all three query families, because QG-19's
mechanism is that the family you skip is the one that kills you. Its verdict is
expected to be `INSTANCE_OF_KNOWN_GENERAL`, as in QG-25 and QG-26.

**Retrieval ceiling applies.** Per `RETRIEVAL_CEILING_2026-08-22.md`, document
fetch is blocked environment-wide and independently confirmed on three domains.
Every passage will be snippet text with `document_level_verification: false`, and
this lane may not record otherwise.

## 2. Frozen object, and the restriction stated before it can be convenient

The R6I min-plus DP as committed at `f280d3e3`:

* states `F₂^10`, transitions XOR by a letter of the committed alphabet;
* per-letter cost from `max_r6i_exact_rank2_shared_tag_dp._local_table`.

**The committed table is keyed** — it varies with the per-position parameters — so
the automaton is not time-invariant and "cost-to-go for all continuations" is not
well posed against it. This lane therefore freezes **one declared key**, making a
time-invariant weighted automaton, and its result is about **that** automaton.

The key is declared here, before any run: the all-zero parameter key
`(0, 0, 0, 0, 0, 0, 0, 0)`. If that key turns out to be degenerate — the table
infinite everywhere, or the cost constant — the lane reports that as its result
and takes the `BLOCKED` terminal rather than quietly picking a different key.

## 3. Q1 — cost-to-go, computed not assumed

For each horizon `r = 1 … R` (R declared in the receipt, capped by runtime):

1. Backward min-plus recursion `C_r[s] = min_δ ( cost(δ) + C_{r−1}[s ⊕ δ] )` over
   all 1024 states, from `C_0[s] = 0 if s == target else ∞`.
2. Report the horizon actually reached and the wall time, **as a cap, not as
   evidence** — gate G3 below.

## 4. Q2 — the merge relation

Two states `s, s'` are **cost-equivalent up to horizon R** when
`C_r[s] − C_r[s']` is the same finite value for every `r ≤ R`.

* Report the number of equivalence classes at each R, and whether it is still
  falling as R grows.
* A class count that **stays at 1024** for all R is the finding that the cost DP
  is already minimal — a confirmation, and a first-class outcome.
* A class count **below 1024** that is stable across the last several R is a
  candidate reduction, and §5 governs what may then be said.

## 5. Q3 — what an efficiency claim costs here

If classes < 1024, the lane may claim a reduction **only** by exhibiting it:

1. build the quotient automaton explicitly;
2. run the committed DP and the quotient DP on the **same declared instances**;
3. show the optima are **identical on every instance**, not merely close;
4. report both state counts and both wall times, with the timings labelled as
   measurements of our implementations and **not** as evidence about the problem.

**No reduction may be claimed from the class count alone.** Stability up to a
finite R is not a proof that it persists; if no proof of persistence is produced,
the terminal says `UNPROVEN_BEYOND_HORIZON` and means it.

## 6. Terminals, frozen

* `QG27_COST_DP_IS_ALREADY_MINIMAL` — 1024 classes at every R examined. The
  committed DP is tight for cost as well as feasibility.
* `QG27_COST_REDUCTION_EXHIBITED__OPTIMA_IDENTICAL` — classes < 1024, quotient
  built, optima identical on every declared instance.
* `QG27_COST_REDUCTION_CANDIDATE__UNPROVEN_BEYOND_HORIZON` — classes < 1024 and
  stable, but no persistence argument and/or no exhibited quotient.
* `QG27_BLOCKED__FROZEN_KEY_DEGENERATE` — the declared key gives a degenerate
  table. Reported, with no substitute key tried.

## 7. Gates

* **G1** — committed DP imported unmodified; the cost table is read from it,
  never retyped.
* **G2** — the frozen key of §2 is the only key used. Trying a second key after
  seeing the first result is exactly the criterion churn `criterion_binding`
  exists to catch, and any change must go through that record with an exhibited
  rejection.
* **G3** — **no complexity or hardness inference from wall-clock.** Timings are
  reported in a block that says they are measurements of our code.
* **G4** — no efficiency claim without the full §5 exhibition.
* **G5** — `criterion_binding` records emitted for every criterion and validated
  in-run against the committed module with the frozen text passed.
* **G6** — the falsifiability demonstration is validated through
  `orion_research_harness.falsifiability`: every tamper declares the check that
  must catch it, and the assembler refuses to write if any case is caught by a
  different one.
* **G7** — independent from-primitives verifier, demonstrated capable of failing.
* **G8** — determinism: double run byte-identical outside timing.
* **G9** — NOT_R6; protected subject unread; caps disclosed.

## 8. Files this lane may create

1. `research/extensions/orion-qg/qg27_cost_minimality.py`
2. `research/extensions/orion-qg/QG27_COST_MINIMALITY_RESULTS.json`
3. `development/orion-qg-regime-geometry/qg27_generic_verify.py`
4. `development/orion-qg-regime-geometry/QG27_GENERIC_VERIFICATION.json`
5. `development/orion-qg-regime-geometry/QG27_DONOR_SEARCH.md`

## 9. What this lane cannot do

It cannot claim novelty; tropical-semiring minimization is Mohri's. It cannot
generalise beyond the frozen key without running the other keys and saying so. It
cannot claim a speedup from a state count. It cannot edit QG-26's receipt — if
this lane finds the cost DP loose, that does not touch QG-26's feasibility result,
which is about a different language and remains exactly as stated.
